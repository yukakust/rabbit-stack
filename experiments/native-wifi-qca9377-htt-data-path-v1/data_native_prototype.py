"""NEW unsigned transport producer. No device/signing/native64 edits."""
from pathlib import Path
import importlib.util,hashlib,sys,shutil
ROOT=Path(__file__).resolve().parent;RUNTIME=ROOT.parent/'native-wifi-qca9377-htt-persistent-runtime-v1'
spec=importlib.util.spec_from_file_location('frozen_runtime_resource_generator',RUNTIME/'runtime_native_prototype.py');runtime=importlib.util.module_from_spec(spec);spec.loader.exec_module(runtime)
b=runtime.b
ADD=r'''
static QcaHttDataPath*data_path;static void*data_pool_raw;static size_t data_pool_bytes;static unsigned data_pool_uncertain;
static int data_overlap(const void*a,size_t n,const void*b,size_t m){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;return x<y?y-x<n:x-y<m;}
static int data_pool_prepare(SystemTable*st){
 if(data_path)return 1;
 if(data_pool_raw||data_pool_uncertain)return 0;
 QcaHttPoolBoot boot_api;if(!qca_htt_pool_boot(st,&boot_api))return 0;
 data_pool_bytes=sizeof(QcaHttDataPath)+_Alignof(QcaHttDataPath)-1;
 if(data_pool_bytes>131072)return 0;
 void*raw=0;Status rc=boot_api.allocate(2,data_pool_bytes,&raw);data_pool_raw=raw;
 uintptr_t v=(uintptr_t)raw;
 if(rc||!raw||v>UINTPTR_MAX-data_pool_bytes){data_pool_uncertain=raw!=0;return 0;}
 uintptr_t old=(uintptr_t)runtime_phase.raw;size_t n=runtime_phase.bytes;
 if(old&&((v<old&&old-v<data_pool_bytes)||(v>=old&&v-old<n))){data_pool_uncertain=1;return 0;}
 if(data_overlap(raw,data_pool_bytes,&runtime_phase,sizeof(runtime_phase))||data_overlap(raw,data_pool_bytes,&port,sizeof(port))||data_overlap(raw,data_pool_bytes,st,sizeof(*st))||data_overlap(raw,data_pool_bytes,&boot_api,sizeof(boot_api))||data_overlap(raw,data_pool_bytes,&data_path,sizeof(data_path))||data_overlap(raw,data_pool_bytes,&data_pool_raw,sizeof(data_pool_raw))||data_overlap(raw,data_pool_bytes,&data_pool_bytes,sizeof(data_pool_bytes))||data_overlap(raw,data_pool_bytes,&data_pool_uncertain,sizeof(data_pool_uncertain))){data_pool_uncertain=1;return 0;}
 QcaHttRuntime*r=&runtime_phase.arena->runtime;
 for(unsigned j=0;j<14+33;j++){QcaDmaBuffer*d=j<14?&r->ce[j]:&r->extra[j-14];if(d->host&&data_overlap(raw,data_pool_bytes,d->host,(size_t)d->bytes)){data_pool_uncertain=1;return 0;}}
 uintptr_t aligned=(v+_Alignof(QcaHttDataPath)-1)&~(uintptr_t)(_Alignof(QcaHttDataPath)-1);
 data_path=(QcaHttDataPath*)aligned;for(size_t i=0;i<data_pool_bytes;i++)((volatile uint8_t*)raw)[i]=0;return 1;
}
#ifdef RABBIT_PREFIX_DRIVER_MODEL
QcaHttDataPath*data_model_view(void){return data_path;}
unsigned data_model_uncertain(void){return data_pool_uncertain;}
#endif
static int data_pool_retire(void){
 if(data_pool_uncertain)return 0;
 if(!data_pool_raw)return !data_path;
 if(!data_path||data_pool_bytes!=sizeof(QcaHttDataPath)+_Alignof(QcaHttDataPath)-1||port.claimed||port.dma_users)return 0;
 for(size_t i=0;i<sizeof(*data_path);i++)if(((const uint8_t*)data_path)[i])return 0;
 QcaHttPoolBoot api;if(!qca_htt_pool_boot(ram_system,&api))return 0;
 /* Revoke the only native callback getter before wipe/free. */
 data_path=0;for(size_t i=0;i<data_pool_bytes;i++)((volatile uint8_t*)data_pool_raw)[i]=0;
 if(api.release(data_pool_raw)){data_pool_uncertain=1;return 0;}data_pool_raw=0;data_pool_bytes=0;return 1;
}
static void data_native_step(uint64_t now){
 if(!data_path)return;
 if(pipeline_phase==6){
  if(data_path->phase==QDP_FILLING){
   for(unsigned i=0;i<16&&data_path->runtime->ring.fill<1023;i++)if(!qdp_refill_initial(data_path,now)){qdp_quarantine(data_path,100);return;}
   if(data_path->runtime->ring.fill==1023&&qdp_publish_cfg(data_path,now)<0)return;
  }
  if(data_path->phase==QDP_CFG_POSTED||data_path->phase==QDP_AGGR_POSTED||data_path->tx_posted)(void)qdp_poll_dma(data_path,now);
  if(data_path->phase==QDP_RX_ACTIVE&&!data_path->aggr_done){(void)qdp_publish_aggr(data_path,now);return;}
  if(data_path->phase==QDP_RX_ACTIVE){
   if(!native_scan.phase&&!qca_native_scan_begin(&native_scan,&persistent,now)){qdp_quarantine(data_path,103);return;}

   if(persistent.rx.count){const QcaRxEvent*e=&persistent.rx.events[persistent.rx.head];
    if(e->pipe==1&&e->endpoint==data_path->binding.endpoint&&e->bytes&&(e->payload[0]==7||e->payload[0]==0x12)){
     int rc=qdp_receive(data_path,e,now);if(!rc)return; /* targeted HTT head remains owned under output backpressure */
     if(rc){QcaRxEvent copy;if(!qca_rx_take(&persistent.rx,e->completion,&copy,sizeof(copy))){qdp_quarantine(data_path,101);return;}}
    }
   }
   (void)qdp_copy_one(data_path,now);
   if(native_scan.phase!=QCA_NATIVE_SCAN_LIVE_DONE){int rc=qca_native_scan_poll(&native_scan,now);if(rc<0||native_scan.error){qdp_quarantine(data_path,104);return;}}

  }
 }
}
'''
def sources(out):
 extra=runtime.sources(out)
 for n in ['data_path.c','data_path.h'] :shutil.copyfile(ROOT/n,out/n)
 extra.append(out/'data_path.c')
 p=out/'init_probe.c';s=p.read_text();s=s.replace('#include "phase_arena.h"','#include "phase_arena.h"\n#include "data_path.h"')
 # Definitions after all frozen scalar owners and before the pipeline step.
 s=b.one(s,'static uint32_t pipeline_phase,pipeline_error,filter_attempted;', 'static uint32_t pipeline_phase,pipeline_error,filter_attempted;\n'+ADD)
 s=b.one(s,'static void qca_filter64_step(uint64_t now){\n if(!runtime_phase.arena)return;', 'static void qca_filter64_step(uint64_t now){\n if(!runtime_phase.arena)return;\n if(qca_radio_accepts_work(&persistent.life)&&!data_pool_prepare(port.system)){pipeline_fault(190,now);return;}\n if(pipeline_phase==6){data_native_step(now);return;}')
 s=b.one(s,'if(rc){\n   if(!qca63_query_handover', 'if(rc<0){\n   if(!qca63_query_handover')
 s=b.one(s,'if(!htt_query.response_completion||!qca_native_scan_begin(&native_scan,&persistent,now)){pipeline_fault(115,now);return;}\n   pipeline_phase=3;', 'if(!qdp_begin(data_path,&runtime_phase.arena->runtime,&persistent,&htt_query,&native_scan,now)){if(htt_query.response&&!qca63_query_handover(&native_scan,&htt_query)){pipeline_fault(192,now);return;}pipeline_fault(191,now);return;}\n   pipeline_phase=6;')
 # NEW absent-radio retirement guard, never patch completed feasibility.
 s=b.one(s,'if(runtime_phase.capture_readers||!qca_htt_runtime_detachable(&runtime_phase.arena->runtime)||!qca_htt_public_rng_cleanup', 'if(runtime_phase.capture_readers||!data_runtime_retirable(&runtime_phase.arena->runtime)||!qca_htt_public_rng_cleanup')
 s=b.one(s,'int runtime_phase_retire(void){', '''static int data_runtime_retirable(const QcaHttRuntime*r){
 if(r->phase)return qca_htt_runtime_detachable(r);
 for(size_t i=0;i<sizeof(*r);i++)if(((const uint8_t*)r)[i])return 0;
 return 1;
}
int runtime_phase_retire(void){''')
 # No target-stop backend exists; keep callbacks/map owners and quarantine.
 s=b.one(s,'if(r->ring.cfg_posted||r->callback_owners||r->rx_copy_owners||r->tx_owners)return -1;', 'if(data_pool_uncertain||r->ring.cfg_posted||r->callback_owners||r->rx_copy_owners||r->tx_owners)return -1;')
 s=b.one(s,'int runtime_phase_retire(void){\n if(!runtime_phase.arena)', 'int runtime_phase_retire(void){\n if(!data_pool_retire())return 0;\n if(!runtime_phase.arena)')
 p.write_text(s)
 p=out/'scan_native.h';t=p.read_text();t=b.one(t,'QCA_NATIVE_SCAN_FAULT};','QCA_NATIVE_SCAN_FAULT,QCA_NATIVE_SCAN_LIVE_DONE};');p.write_text(t)
 p=out/'scan_native.c';t=p.read_text();t=b.one(t,'if(s->quiesce_requested)return 0;', 'if(s->phase==QCA_NATIVE_SCAN_LIVE_DONE)return 0;\n if(s->quiesce_requested)return 0;')
 t=b.one(t,'if(rc>0)return halt(s,0);', 'if(rc>0){s->phase=QCA_NATIVE_SCAN_LIVE_DONE;return 1;} /* SCAN complete; live47 ownership preserved. */')
 p.write_text(t)
 p=out/'driver.c';t=p.read_text();t='#include "data_path.h"\nstatic void*volatile data_linked_methods[]={qdp_submit_raw,qdp_submit_mgmt,qdp_take_frame,qdp_quarantine};\n'+t
 t=b.one(t,'uint64_t __attribute__((ms_abi)) module_entry(', 'uint64_t __attribute__((ms_abi)) module_entry(') if False else t
 # Force retained native API code into measured image; no method is called or authorized.
 marker='Status EFIAPI module_entry('
 if marker not in t:marker='Status __attribute__((ms_abi)) module_entry('
 at=t.index('module_entry(');brace=t.index('{',at);t=t[:brace+1]+'\n (void)data_linked_methods[0];'+t[brace+1:];p.write_text(t)
 return extra
def main():
 if not sys.platform.startswith('linux'):raise SystemExit('Native C Yukabox only')
 import os,tempfile,struct,json
 out=ROOT/'runs/native-image';out.mkdir(parents=True,exist_ok=True);tmp=out/'tmp';tmp.mkdir(exist_ok=True);os.environ['TMPDIR']=str(tmp);tempfile.tempdir=str(tmp);a=b.checked.prior.actors;_,_,crypto=a.engine.prepare(out,bytes.fromhex('29acbae141bccaf0b22e1a94d34d0bc7361e526d0bfe12c89794bc9322966dd7'));extra=sources(out)
 files=[out/'driver.c',out/'city_core.c',out/'pci_collect.c',out/'pci_identity.c',*[out/n for n in b.FILES],out/'usb_port.c',out/'bt_event_stream.c',out/'ble_recovery_link.c',out/'diagnostic_gatt.c',a.LINK/'file_core.c',a.NATIVE/'sha256.c',*crypto,*extra,RUNTIME/'chkstk_bridge.S']
 payload=a.compile_efi(out,'data-runtime-prototype',files,driver=True,definitions=('SCENE_REVISION=1','QCA_CONFIG_SETUP=1','QCA_FC_BASE=13'));(out/'payload.efi').write_bytes(payload);at=struct.unpack_from('<I',payload,60)[0];mapped=struct.unpack_from('<I',payload,at+80)[0]
 report={'status':'NEW-HTT-DATA-PATH-UNSIGNED-NATIVE-COMPILE-ONLY','file_bytes':len(payload),'mapped_bytes':mapped,'fits':len(payload)<=262144 and mapped<=4194304,'payload_sha256':hashlib.sha256(payload).hexdigest(),'counter_not_reserved':True,'signing_admitted':False,'physical':False,'target_halt_backend_integrated':False,'published_ring_release_allowed':False,'association_authority':False,'IP_authority':False,'GetRNG_calls':0};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
