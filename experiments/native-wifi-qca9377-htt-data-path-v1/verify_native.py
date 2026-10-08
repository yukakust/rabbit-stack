"""Yukabox-only actual NEW producer full boot + real fake-PCI/CE data model."""
from pathlib import Path
import importlib.util,sys,os,tempfile,subprocess,shutil,json,hashlib
import data_native_prototype as model
import oracle
ROOT=model.ROOT;RUNTIME=model.RUNTIME;b=model.b
sys.path.insert(0,str(RUNTIME))
spec=importlib.util.spec_from_file_location('frozen_resource_model',RUNTIME/'verify_producer.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
HOOK=r'''
static void emit_htt(const uint8_t*p,unsigned n){
 const QcaPersistentNative*r=qca_persistent_view();QcaInitAdapter*a=r->startup->operating->boot->board->setup->read.full.adapter;
 assert(r->rx.posted[0]&&registers[1][0x48/4]==a->channels.rings[1].read);unsigned ri=a->channels.rings[1].read;
 uint8_t*raw=hosts[3];memset(raw,0,2048);raw[0]=2;raw[2]=(uint8_t)n;memcpy(raw+8,p,n);hosts[2][ri*8+4]=(uint8_t)(n+8);hosts[2][ri*8+5]=(uint8_t)((n+8)>>8);registers[1][0x48/4]=(ri+1)&7;
}
static unsigned data_step,tx_delay;static uint8_t public_mgmt[24]={0xb0};
static void data_tick(void){
 QcaHttDataPath*s=data_model_view();if(!s){if(data_case==15||data_case==16){uint8_t status[544];qca_filter64_status(status);if(bw(status+8)==5){const QcaHttPhaseOwner*po=runtime_phase_model();assert(bw(status+12)==190&&data_model_uncertain()&&!runtime_phase_retire()&&po->arena->runtime.port->dma_users==47);puts("ACTUAL AUX POOL ALIAS/ERROR POINTER RETAINS47 WITHOUT WRITE/FREE PASS");exit(0);}}return;}
 if(s->phase==QDP_QUARANTINED){
  assert(data_case>=2&&data_case<=18&&s->runtime->port->dma_users==47&&s->runtime->callback_owners==1&&!qca_radio_accepts_work(&s->radio->life)&&!qca_htt_runtime_close_one(s->runtime)&&!runtime_phase_retire());
  if(data_case==2)assert(s->error==4&&s->runtime->ring.fill==1023);
  if(data_case==3||data_case==9||data_case==10)assert(s->error==20);
  if(data_case==4||data_case==6)assert(s->error==13&&s->runtime->ring.fill==1023&&s->runtime->owners[0].state==1);
  if(data_case==5)assert(s->error==17&&s->pending_valid&&s->runtime->rx_copy_owners==1&&s->rejected_bytes==2048&&!s->output_count);
  if(data_case==8||data_case==11)assert(s->error==11);
  if(data_case==17||data_case==18)assert(s->error==21&&s->rejected_bytes==2048&&!s->output_count&&s->runtime->rx_copy_owners==1);
  printf("ACTUAL PRODUCER NEGATIVE CASE%u retained47/error%u PASS; SYNTHETIC ONLY\n",data_case,s->error);exit(0);
 }
 if(data_case==1){uint8_t status[544];qca_filter64_status(status);if(bw(status+8)==5){assert(bw(status+12)==191);const QcaHttPhaseOwner*po=runtime_phase_model();assert(!po->arena->runtime.ring.cfg_posted&&!po->arena->runtime.callback_owners&&htt_posts==1);puts("ACTUAL SERVICE65 MISSING FAILS BEFORE RING/PUBLISH PASS; SYNTHETIC ONLY");exit(0);}return;}
 if(s->phase!=QDP_RX_ACTIVE||!s->aggr_done)return;
 if(data_case==22&&qca_scan_native_view()->phase!=QCA_NATIVE_SCAN_LIVE_DONE)return;
 if(data_case==22)assert(qca_radio_accepts_work(&s->radio->life)&&s->runtime->port->dma_users==47&&!qca_scan_native_view()->quiesce_requested);
 assert(s->radio==qca_persistent_view()&&s->runtime->port->dma_users==47&&s->runtime->ring.cfg_posted&&s->runtime->callback_owners==1);
 if(data_case==7){
  static unsigned sent,drained;const QcaPersistentNative*pr=s->radio;QcaInitAdapter*a=pr->startup->operating->boot->board->setup->read.full.adapter;
  if(sent<5&&s->output_count==(sent<4?sent:4)&&pr->rx.posted[0]&&registers[1][0x48/4]==a->channels.rings[1].read){
   uint8_t*raw=(uint8_t*)s->runtime->extra[0].host+sent*2048;memset(raw,0,2048);bp(raw+4,0x80000000u);bp(raw+12,0x70000000u);bp(raw+24,24);bp(raw+56,0xc000);raw[300]=8;raw[302]=(uint8_t)sent;
   uint8_t ind[16]={0x12,16,1,0,0,0,1,0};bp(ind+8,s->runtime->owners[sent].paddr);ind[12]=24;emit_htt(ind,16);sent++;return;
  }
  if(sent==5&&!drained&&s->output_count==4&&pr->rx.count&&pr->rx.events[pr->rx.head].pipe==1&&pr->rx.events[pr->rx.head].payload[0]==0x12){
   const QcaRxEvent*e=&pr->rx.events[pr->rx.head];assert(e->payload[0]==0x12&&bw(e->payload+8)==s->runtime->owners[4].paddr&&s->runtime->owners[4].state==1&&!s->pending_valid&&s->runtime->ring.fill==1023);
   QRxFrame f;uint64_t id;assert(qdp_take_frame(s,&f,&id)&&f.payload[2]==0);drained=1;return;
  }
  if(drained&&s->output_count==4&&!pr->rx.count){
   for(unsigned i=1;i<5;i++){QRxFrame f;uint64_t id;assert(qdp_take_frame(s,&f,&id)&&f.payload[2]==i);}
   assert(s->runtime->ring.fill==1023&&!s->runtime->rx_copy_owners);qdp_quarantine(s,91);assert(!qca_htt_runtime_close_one(s->runtime)&&s->runtime->port->dma_users==47);
   puts("ACTUAL RX OUTPUT BACKPRESSURE RETAINS OWNED CE EVENT; DRAIN RESUMES COPY/REFILL WITHOUT DROP PASS");exit(0);
  }return;
 }
 if(data_step==0){
  uint8_t*raw=s->runtime->extra[0].host;memset(raw,0,2048);bp(raw+4,data_case==5?0:0x80000000u);bp(raw+12,0x70000000u);bp(raw+24,24);bp(raw+56,0xc000);raw[300]=8;if(data_case==17)bp(raw+12,0x60002000u);if(data_case==18)raw[301]=0x40;
  uint8_t inord[24]={0x12,16,1,0,0,0,1,0};bp(inord+8,s->runtime->owners[0].paddr+(data_case==4?8:0));inord[12]=24;
  if(data_case==6){inord[6]=2;memcpy(inord+16,inord+8,8);}emit_htt(inord,data_case==6?24:16);data_step=1;return;
 }
 if(data_step==1&&s->output_count){
  QRxFrame frame;uint64_t completion;assert(qdp_take_frame(s,&frame,&completion)&&frame.bytes==24&&frame.payload[0]==8&&completion>s->floor);
  assert(s->runtime->ring.fill==1023&&s->runtime->owners[0].state==1&&*(uint32_t*)((uint8_t*)s->runtime->extra[0].host+4)==0);
  if(data_case==9)tx_delay=1;if(data_case==14){uint8_t raw_data[24]={8};assert(qdp_submit_raw(s,raw_data,24,1,0,16,now_us)==1);primary_tx_assert(hosts[9],(uint32_t)s->runtime->ce[9].address,raw_data,24,1,0,16);assert(hosts[9][25]==7&&bw(hosts[9]+32)==s->runtime->ce[9].address&&bw(hosts[9])==s->runtime->ce[9].address+1024&&bw(hosts[9]+4)==24);}else{assert(qdp_submit_mgmt(s,public_mgmt,24,1,0,now_us)==1);primary_tx_assert(hosts[9],(uint32_t)s->runtime->ce[9].address,public_mgmt,24,1,3,17);assert(hosts[9][25]==0x67&&bw(hosts[9]+32)==s->runtime->ce[9].address+1024);}assert(s->tx_posted&&s->runtime->tx_owners==1);data_step=2;return;
 }
 if(data_step==2&&s->tx_dma_done){
  assert(!s->tx_htt_done&&s->runtime->tx_owners==1&&!qdp_submit_mgmt(s,public_mgmt,24,2,0,now_us));if(data_case==10)return;uint8_t done[6]={7,128,1,0,1,0};if(data_case==8)done[4]=99;emit_htt(done,6);data_step=3;return;
 }
 if(data_step==3&&!s->tx_posted){
  assert(s->tx_dma_done&&s->tx_htt_done&&!s->tx_status&&!s->runtime->tx_owners);
  if(data_case==11){uint8_t done[6]={7,128,1,0,1,0};emit_htt(done,6);data_step=99;return;}tx_delay=1;assert(qdp_submit_mgmt(s,public_mgmt,24,2,0,now_us));uint8_t done[6]={7,130,1,0,2,0};emit_htt(done,6);data_step=4;return;
 }
 if(data_step==4&&s->tx_htt_done){
  assert(!s->tx_dma_done&&s->tx_posted&&s->runtime->tx_owners==1&&!qdp_submit_mgmt(s,public_mgmt,24,3,0,now_us));QcaInitAdapter*a=s->radio->startup->operating->boot->board->setup->read.full.adapter;registers[4][0x44/4]=a->channels.rings[4].write;data_step=5;return;
 }
 if(data_step==5&&!s->tx_posted){
  assert(s->tx_dma_done&&s->tx_htt_done&&s->tx_status==2&&!s->runtime->tx_owners);
  assert(!qdp_submit_mgmt(s,public_mgmt,24,2,0,now_us));public_mgmt[1]=0x40;assert(!qdp_submit_mgmt(s,public_mgmt,24,3,0,now_us));public_mgmt[1]=0;
  qdp_quarantine(s,90);assert(s->phase==QDP_QUARANTINED&&!qca_htt_runtime_close_one(s->runtime)&&s->runtime->port->dma_users==47&&!runtime_phase_retire());
  printf("DATA_PATH_BYTES=%zu aligned_pool=%zu maps=%u\n",sizeof(*s),sizeof(*s)+_Alignof(QcaHttDataPath)-1,s->runtime->port->dma_users);
  puts("ACTUAL NEW PRODUCER: SERVICE65+47DMA+CFG+OWNED_INORD+COPY+REFILL+MGMT_TYPE3+DMA_FIRST+HTT_FIRST+NOACK+RETAINED_TARGET_STOP_GAP PASS; SYNTHETIC ONLY");exit(0);
 }
}
'''
def fixture(old):
 s=base.fixture(old);s='#include "data_path.h"\nQcaHttDataPath*data_model_view(void);\nunsigned data_model_uncertain(void);\nstatic void data_tick(void);\nstatic unsigned tx_delay,data_case;\n#include "primary_oracle.h"\n'+s
 s=s.replace('assert(argc==10);', 'assert(argc==11);data_case=(unsigned)atoi(argv[10]);')
 s=s.replace('assert(!prefix_driver_model_poll(ms));}', 'assert(!prefix_driver_model_poll(ms));data_tick();}')
 s=s.replace('static unsigned data_step,tx_delay;', 'static unsigned data_step;')
 marker='static const uint8_t physical54_0[]='
 i=s.index(marker);s=s[:i]+HOOK+s[i:]
 # Explicit synthetic SERVICE65 positive. Original physical bytes remain frozen.
 s=s.replace('memcpy(p,captured,256);memset(p+256,0,64);', 'memcpy(p,captured,256);memset(p+256,0,64);bp(p+252,data_case==1?0:2);')
 oldbranch='const uint8_t*b=hosts[9];assert(!htt_posts&&b[0]==2&&!b[1]&&b[2]==4&&!b[3]&&!bw(b+8));'
 newbranch='''const uint8_t*b=hosts[9];QcaHttDataPath*dp=data_model_view();
   if(dp&&dp->phase==QDP_CFG_POSTED){assert(b[0]==2&&b[2]==40&&b[8]==2&&b[9]==1);if(data_case==2){unsigned slot=(value-1)&7;hosts[8][slot*8+4]=47;}if(data_case!=3)registers[4][0x44/4]=value;return 0;}
   if(dp&&dp->phase==QDP_AGGR_POSTED){assert(b[0]==2&&b[2]==3&&b[8]==5&&b[9]==1&&b[10]==1);registers[4][0x44/4]=value;return 0;}
   if(dp&&dp->tx_posted){assert(b[16]==2&&b[24]==1);if(!tx_delay)registers[4][0x44/4]=value;return 0;}
   assert(!htt_posts&&b[0]==2&&!b[1]&&b[2]==4&&!b[3]&&!bw(b+8));'''
 assert oldbranch in s;s=s.replace(oldbranch,newbranch)
 s=s.replace('static void*phase_pool,*inventory_pool;', 'static void*phase_pool,*inventory_pool,*data_pool;')
 s=s.replace(' if(kind==4)return ram_allocate(kind,n,out);', ''' if(kind==4)return ram_allocate(kind,n,out);
 if(kind==2&&n==sizeof(QcaHttDataPath)+_Alignof(QcaHttDataPath)-1){assert(!data_pool);if(data_case==15){*out=data_pool=hosts[7];return 0;}*out=data_pool=malloc((size_t)n);assert(*out);if(data_case==16){memset(*out,0xa5,(size_t)n);return EFI_ERROR(7);}return 0;}''')
 s=s.replace('allocations==47&&dma_frees==47&&unmaps==47);free(p);', '(allocations==47&&dma_frees==47&&unmaps==47)||(allocations==0&&!dma_frees&&!unmaps));free(p);')
 s=s.replace('qca_start(&port_system,0);tick(1);', r'''if(data_case==13){qca_controller=0;qca_start(&port_system,0);const QcaHttPhaseOwner*po=runtime_phase_model();assert(po->arena&&!po->arena->runtime.phase&&!allocations);QcaHttRuntime*rt=(QcaHttRuntime*)&po->arena->runtime;rt->allocated=1;assert(!runtime_phase_retire()&&phase_pool&&!phase_frees);rt->allocated=0;assert(runtime_phase_retire()&&phase_frees==1&&!phase_pool&&!qca_scan_native_view());puts("ACTUAL ABSENT RADIO UNUSED POOL + NONCANONICAL RETAIN + CANONICAL DETACH FREE PASS");exit(0);}qca_start(&port_system,0);tick(1);''')
 return s

def main():
 if sys.platform!='linux':raise SystemExit('Native C Yukabox only')
 out=ROOT/'runs/native-proof';out.mkdir(parents=True,exist_ok=True);tmp=out/'tmp';tmp.mkdir(exist_ok=True);os.environ['TMPDIR']=str(tmp);tempfile.tempdir=str(tmp)
 extra=model.sources(out);(out/'primary_oracle.h').write_text(oracle.header());sys.path.insert(0,str(b.BASE));import verify_port
 old=RUNTIME/'runs/producer-proof';(out/'fixture.c').write_text(fixture((b.ROOT/'runs/native-host/fixture.c').read_text()))
 p=out/'init_probe.c';s=p.read_text();owner='.'.join([])
 original=(old/'init_probe.c').read_text();start=original.index('.owner={');end=original.index('}',start)+1;replacement=original[start:end];start=s.index('.owner={');end=s.index('}',start)+1;s=s[:start]+replacement+s[end:];p.write_text(s)
 for n in ('monocypher.c','monocypher-ed25519.c','monocypher.h','monocypher-ed25519.h','file_core.c','sha256.c'):shutil.copyfile(old/n,out/n)
 inc=['-I'+str(x) for x in (out,RUNTIME,b.BASE,b.checked.prior.actors.OLD,b.checked.prior.actors.NATIVE,b.BASE/'runs/firmware-chunks',b.checked.prior.actors.LINK,ROOT.parent/'x86-64-uefi-connected-supervisor-v1')]
 files=list(b.FILES)+['driver.c','city_core.c','pci_identity.c','usb_port.c','bt_event_stream.c','ble_recovery_link.c','diagnostic_gatt.c','file_core.c','sha256.c','monocypher.c','monocypher-ed25519.c']
 subprocess.run([str(verify_port.CC),'-DRABBIT_PREFIX_DRIVER_MODEL','-DQCA_CONFIG_SETUP=1','-DQCA_FC_BASE=13','-DSCENE_REVISION=1','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all',*inc,str(out/'fixture.c'),*[str(out/n) for n in files],*map(str,extra),'-o',str(out/'test')],check=True)
 log='';cases=[0,1,2,3,4,5,6,7,8,9,10,11,13,14,15,16,17,18,22]
 for case in cases:
  run=subprocess.run([str(out/'test'),'0',str(b.ROOT/'runs/native-host/fixture-assets'),'35','0','0','0','0',str(ROOT.parent/'native-wifi-qca9377-scan61-native-v1/runs/world19.rup'),'0',str(case)],capture_output=True,text=True,timeout=120);log+=run.stdout+run.stderr;(out/'host.log').write_text(log)
  if run.returncode:raise RuntimeError(f'case{case}: '+run.stdout[-1200:]+'\n'+run.stderr[-5000:])
 for n in ['data_path','init_probe','channels_core','init_adapter','persistent','lifecycle','driver','dma_runtime','guarded_dma','owner47','phase_arena','runtime_pool','rng_inventory_join','rx','ce_ring']:
  subprocess.run([str(verify_port.CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-DQCA_CONFIG_SETUP=1','-DQCA_FC_BASE=13',*inc,'-I'+str(RUNTIME/'dependencies'),'-c',str(out/(n+'.c')),'-o',str(out/(n+'.obj'))],check=True)
 sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 report={'status':'ACTUAL-NEW-HTT-DATA-PRODUCER-PRIMARY-ORACLE-ASAN-COFF-PASS','fixture_kind':'synthetic-actual-C-producer','cases':cases,'physical':False,'real_model_maps':47,'target_halt_backend':False,'published_ring_release_authority':False,'actualIP_authority':False,'GetRNG_calls':0,'test_sha256':sha(out/'test'),'host_log_sha256':sha(out/'host.log'),'coff_objects_sha256':{p.name:sha(p) for p in out.glob('*.obj')},'source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in ROOT.rglob('*') if p.is_file() and 'runs' not in p.parts and '__pycache__' not in p.parts},'compiled_sources_sha256':{p.name:sha(p) for p in [out/'fixture.c',*[out/n for n in files],*extra,*out.glob('*.h')]}}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
if __name__=='__main__':main()
