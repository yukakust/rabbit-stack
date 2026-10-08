"""NEW unsigned phase-owned47-resource prototype; counter64 is NOT reserved.
No signing/hardware admission. RX_RING_CFG/TX/network pumps not enabled yet.
"""
from pathlib import Path
import importlib.util,sys,os,tempfile,struct,json,hashlib,shutil
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent/'native-wifi-qca9377-filter64-native-v1'
spec=importlib.util.spec_from_file_location('runtime_phase_frozen64',BASE/'filter64_build.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
HOOK=r'''
#ifdef RABBIT_PREFIX_DRIVER_MODEL
const QcaHttPhaseOwner*runtime_phase_model(void){return &runtime_phase;}
#endif
int runtime_rng_public(RngPublicDiagnostic*out){
 if(!out||!runtime_phase.arena||!runtime_phase.arena->rng.attempted)return 0;
 *out=runtime_phase.arena->rng.diagnostic;return 1;
}
static int runtime_extra_stop(void*context){
 QcaHttRuntime*r=context;
 /* Target configuration needs a real target halt backend, not CE-only proof. */
 if(r->ring.cfg_posted||r->callback_owners||r->rx_copy_owners||r->tx_owners)return -1;
 return qca_ce_bus_released(&adapter.bus);
}
int runtime_extra_prepare(QcaInitAdapter*a){
 if(a!=&adapter||!runtime_phase.arena)return -1;
 QcaHttRuntime*r=&runtime_phase.arena->runtime;
 /* Initial read-only probe may close all extra maps before firmware acquisition.
  * Reuse only before filter/query/scan has begun, with every extra owner closed. */
 if(r->phase==HTT_RUNTIME_CLOSED){
  if(!qca_htt_runtime_detachable(r)||filter.phase||pipeline_phase||native_scan.phase||htt_query.phase)return -1;
  for(size_t j=0;j<sizeof(*r);j++)((uint8_t*)r)[j]=0;
 }
 if(!r->phase&&!qca_htt_runtime_begin(r,&port,a->channels.buffers,persistent.epoch?persistent.epoch:1,runtime_extra_stop,r))return -1;
 if(r->phase==HTT_RUNTIME_ALLOCATING){int rc=qca_htt_runtime_allocate_one(r);if(rc<0)return -1;return r->phase==HTT_RUNTIME_MAPPED?1:0;}
 return r->phase==HTT_RUNTIME_MAPPED&&qca_htt_runtime_inventory(r)?1:-1;
}
int runtime_extra_retained(QcaChannels*c){
 if(c!=&adapter.channels)return 0;
 if(!runtime_phase.arena)return port.dma_users==14;
 QcaHttRuntime*r=&runtime_phase.arena->runtime;
 if(!r->phase||r->phase==HTT_RUNTIME_CLOSED)return port.dma_users==14;
 return r->phase==HTT_RUNTIME_MAPPED&&qca_htt_runtime_inventory(r);
}
int runtime_extra_cleanup(QcaInitAdapter*a){
 if(a!=&adapter)return -1;
 if(!runtime_phase.arena)return 1;
 QcaHttRuntime*r=&runtime_phase.arena->runtime;
 if(!r->phase||r->phase==HTT_RUNTIME_CLOSED)return 1;
 if(r->ring.cfg_posted)return -1; /* No target-halt fabrication. */
 if(!qca_htt_runtime_close_one(r))return -1;
 return r->phase==HTT_RUNTIME_CLOSED?1:0;
}
int runtime_extra_snapshot(QcaPersistentNative*p,QcaRadioOwners*out){
 if(p!=&persistent||!out||!runtime_phase.arena)return 0;
 QcaHttRuntime*r=&runtime_phase.arena->runtime;
 if(!r->phase)return 0;
 QcaRadioOwners next;if(!qca_htt_owner47_snapshot(r,out,&next))return 0;*out=next;return 1;
}
int runtime_phase_retire(void){
 if(!runtime_phase.arena)return !runtime_phase.uncertain;
 if(runtime_phase.capture_readers||!qca_htt_runtime_detachable(&runtime_phase.arena->runtime)||!qca_htt_public_rng_cleanup(&runtime_phase.arena->rng))return 0;
 /* Captured queue remains readable until this explicit retirement. This
  * original clear primitive admits only CLOSED actual all-owner lifecycle. */
 if(persistent.rx.phase&&!qca_rx_clear(&persistent.rx,&persistent.life))return 0;
 if(!qca_htt_phase_detach(&runtime_phase,&htt_query))return 0;
 return qca_htt_phase_release(&runtime_phase);
}
'''
def sources(out):
 b.driver_sources(out)
 extras=[]
 for p in [ROOT/n for n in ['dma_runtime.c','dma_runtime.h','guarded_dma.c','guarded_dma.h','runtime_pool.c','runtime_pool.h','owner47.c','owner47.h','lifecycle47.h','phase_arena.c','phase_arena.h','rng_inventory_join.c','rng_inventory_join.h']]+list((ROOT/'protected').glob('*'))+[ROOT/'dependencies/ring.c',ROOT/'dependencies/ring.h',ROOT/'dependencies/rx_decode.c',ROOT/'dependencies/rx_decode.h']:
  shutil.copyfile(p,out/p.name)
  if p.suffix=='.c':extras.append(out/p.name)
 # Existing lifecycle API names but new strict47 policy; original64 untouched.
 (out/'lifecycle.c').write_text((ROOT/'lifecycle47.c').read_text().replace('qca_radio47_','qca_radio_'))
 p=out/'init_probe.c';s=p.read_text().replace('#include "scan_native.h"','#include "scan_native.h"\n#include "phase_arena.h"\n#include "owner47.h"')
 s=s.replace('static QcaNativeScan native_scan;','static QcaHttPhaseOwner runtime_phase;\n#define native_scan (runtime_phase.arena->scan)')
 s=s.replace('static QcaFilterBarrier filter;','#define filter (runtime_phase.arena->filter)')
 s=b.one(s,'void qca_start(SystemTable*st,uint64_t ms){','''void qca_start(SystemTable*st,uint64_t ms){
 if(!stage&&!runtime_phase.arena){QcaHttPoolBoot boot_api;
  if(!qca_htt_pool_boot(st,&boot_api)||!qca_htt_phase_acquire(&runtime_phase,&boot_api,1)){failed=0x7e01;stage=7;telemetry();return;}}
 if(runtime_phase.arena&&!runtime_phase.arena->rng.attempted){
  /* No self-code hash is invented. Zero means unresolved code-artifact provenance. */
  static const uint8_t inventory_code[32]={INVENTORY_CODE};
  (void)qca_htt_public_rng_inventory(&runtime_phase.arena->rng,st,runtime_phase.epoch,inventory_code);
 }

'''.replace('INVENTORY_CODE',','.join('0' for _ in range(32))))
 s=b.one(s,'static void qca_filter64_step(uint64_t now){','static void qca_filter64_step(uint64_t now){\n if(!runtime_phase.arena)return;')
 s=b.one(s,'const QcaNativeScan*qca_scan_native_view(void){return &native_scan;}','const QcaNativeScan*qca_scan_native_view(void){return runtime_phase.arena?&native_scan:0;}')
 s=b.one(s,'return qca_native_scan_export(&native_scan,page,out,cap);','return runtime_phase.arena?qca_native_scan_export(&native_scan,page,out,cap):qca_htt_phase_empty_raw(page,out,cap);')
 s=b.one(s,'void qca_filter64_status(uint8_t out[544]){','''void qca_filter64_status(uint8_t out[544]){
 if(!runtime_phase.arena){qca_htt_phase_empty_pipeline(out,64);out[398]=10;const uint8_t plan[10]={'i','P','h','o','n','e',' ','(','9',')'};for(unsigned i=0;i<10;i++)out[400+i]=plan[i];return;}
''')
 s=b.one(s,'void qca_scan_status(uint8_t out[416]){','''void qca_scan_status(uint8_t out[416]){
 if(!runtime_phase.arena){for(unsigned i=0;i<416;i++)out[i]=0;const uint8_t magic[8]={'Q','S','C','N','0','0','0','1'};for(unsigned i=0;i<8;i++)out[i]=magic[i];out[248]=64;out[252]=13;for(unsigned j=0;j<32;j++){out[264+j]=scan_policy.reviewed_digest[j];out[296+j]=scan_policy.ruleset_digest[j];out[328+j]=scan_policy.location_digest[j];}return;}
''')
 s+=HOOK;p.write_text(s)
 p=out/'channels_core.c';s=p.read_text();s='#include "channels_core.h"\n#include "owner47.h"\nextern int runtime_extra_retained(QcaChannels*);\n'+s;s=b.one(s,'if(p->dma_users!=14)return -1;','if(!runtime_extra_retained(c))return -1;');p.write_text(s)
 p=out/'init_adapter.c';s=p.read_text();s='#include "init_adapter.h"\n#include "phase_arena.h"\nextern int runtime_extra_prepare(QcaInitAdapter*);extern int runtime_extra_cleanup(QcaInitAdapter*);\n'+s
 s=b.one(s,'int rc=qca_channels_prepare_step(&a->channels);','int rc=a->channels.phase==QCA_CHANNEL_READY?1:qca_channels_prepare_step(&a->channels);\n  if(rc>0)rc=runtime_extra_prepare(a);')
 s=b.one(s,'int rc=qca_channels_close_step(&a->channels);','int extra=runtime_extra_cleanup(a);if(extra<0)return retain(a,0x7e02);if(!extra)break;\n  int rc=qca_channels_close_step(&a->channels);');p.write_text(s)
 p=out/'persistent.c';s=p.read_text();s='extern int runtime_extra_snapshot(QcaPersistentNative*,QcaRadioOwners*);\n'+s if False else s
 s=b.one(s,'static int snapshot(QcaPersistentNative*s,QcaRadioOwners*o){','extern int runtime_extra_snapshot(QcaPersistentNative*,QcaRadioOwners*);\nstatic int snapshot(QcaPersistentNative*s,QcaRadioOwners*o){')
 s=b.one(s,' if(p->claimed){',' if(!runtime_extra_snapshot(s,o))return -1;\n if(p->claimed){');p.write_text(s)
 p=out/'driver.c';s=p.read_text();s=b.one(s,'static Status EFIAPI connected_unload(void*h){(void)h;return radio_port.bound||qca_stop()?EFI_ERROR(6):0;}','extern int runtime_phase_retire(void);\nstatic Status EFIAPI connected_unload(void*h){(void)h;if(radio_port.bound||qca_stop()||!runtime_phase_retire())return EFI_ERROR(6);return 0;}');p.write_text(s)
 for name in ['ring.c','rx_decode.c','platform.c','rng_port.c']:
  p=out/name;raw=p.read_bytes();p.write_bytes(b'#pragma GCC diagnostic push\n#pragma GCC diagnostic ignored "-Wmisleading-indentation"\n#pragma GCC diagnostic ignored "-Warray-parameter"\n'+raw+b'\n#pragma GCC diagnostic pop\n')
 return extras
def main():
 if not sys.platform.startswith('linux'):raise SystemExit('Yukabox native only')
 out=ROOT/'runs/phase-native-prototype';out.mkdir(parents=True,exist_ok=True);tmp=out/'tmp';tmp.mkdir(exist_ok=True);os.environ['TMPDIR']=str(tmp);tempfile.tempdir=str(tmp);a=b.checked.prior.actors;_,_,crypto=a.engine.prepare(out,bytes.fromhex('29acbae141bccaf0b22e1a94d34d0bc7361e526d0bfe12c89794bc9322966dd7'));extra=sources(out)
 files=[out/'driver.c',out/'city_core.c',out/'pci_collect.c',out/'pci_identity.c',*[out/n for n in b.FILES],out/'usb_port.c',out/'bt_event_stream.c',out/'ble_recovery_link.c',out/'diagnostic_gatt.c',a.LINK/'file_core.c',a.NATIVE/'sha256.c',*crypto,*extra,ROOT/'chkstk_bridge.S']
 payload=a.compile_efi(out,'phase-runtime-prototype',files,driver=True,definitions=('SCENE_REVISION=1','QCA_CONFIG_SETUP=1','QCA_FC_BASE=13'));(out/'payload.efi').write_bytes(payload);o=struct.unpack_from('<I',payload,60)[0];mapped=struct.unpack_from('<I',payload,o+80)[0]
 report={'status':'NEW-PHASE-ARENA-47-RESOURCE-NATIVE-PROTOTYPE-COMPILE-ONLY','file_bytes':len(payload),'mapped_bytes':mapped,'fits':len(payload)<=262144 and mapped<=4194304,'payload_sha256':hashlib.sha256(payload).hexdigest(),'counter_not_reserved':True,'signing_admitted':False,'physical':False,'actual_native_models_passed':False,'HTT_RX_RING_CFG_published':False,'data_plane_ready':False,'GetRNG_calls':0};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
