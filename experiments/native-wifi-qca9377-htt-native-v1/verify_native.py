"""Actual native CE4/CE1/2 ownership model; Yukabox only, no hardware."""
import importlib.util,sys,subprocess,hashlib,json,os
from pathlib import Path
import htt_build as build
ROOT=build.ROOT;RX=build.RX;BASE=build.BASE
spec=importlib.util.spec_from_file_location('checked_rx_verifier',RX/'verify_native.py');prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
sha=lambda b:hashlib.sha256(b).hexdigest()
def fixture(text):
 s=prior.fixture(text);s='#include "htt_native.h"\n'+s
 s=build.one(s,'static unsigned rx_scenario;','static unsigned rx_scenario;static unsigned htt_scenario,htt_started,htt_posts;static QcaHttNative query,rival;')
 s=build.one(s,'assert(argc==7);rx_scenario=','assert(argc==8);htt_scenario=(unsigned)atoi(argv[7]);assert(htt_scenario<=20);rx_scenario=')
 marker='  if(main_done&&qca_persistent_view()->life.phase==QCA_RADIO_ACTIVE&&(id==1||id==2)&&index==0x40){'
 s=build.one(s,marker,r'''
  if(main_done&&qca_persistent_view()->life.phase==QCA_RADIO_ACTIVE&&id==4&&index==0x3c&&query.attempted){
   htt_posts++;assert(htt_posts==1&&query.attempted==1);
   const QcaPersistentNative*p=qca_persistent_view();const uint8_t*b=hosts[9];
   assert(b[0]==p->startup->operating->control.session.htt.endpoint&&!b[1]&&b[2]==4&&!b[3]);
   assert(!b[8]&&!b[9]&&!b[10]&&!b[11]);
   unsigned ri=(value-1)&7;assert((hosts[8][ri*8+6]|((unsigned)hosts[8][ri*8+7]<<8))==(unsigned)b[0]*4);
   if(htt_scenario!=1)registers[4][0x44/4]=value;
   if(htt_scenario==3){QcaInitAdapter*a=p->startup->operating->boot->board->setup->read.full.adapter;a->channels.rings[4].cookie[ri]^=1;}
   if(htt_scenario==4)hosts[8][ri*8]^=1;
   if(htt_scenario==5)hosts[8][ri*8+4]^=1;
   if(htt_scenario==6)registers[4][0x44/4]=(value+1)&7;
   if(htt_scenario==2)return 1;return 0;
  }
'''+marker)
 helper=r'''
static void deliver_htt(unsigned kind){
 deliver_rx(1,1);const QcaPersistentNative*p=qca_persistent_view();
 QcaInitAdapter*a=p->startup->operating->boot->board->setup->read.full.adapter;unsigned ri=a->channels.rings[1].read;
 uint8_t*b=hosts[3];memset(b,0,24);b[0]=p->startup->operating->control.session.htt.endpoint;b[2]=4;
 b[8]=0;b[9]=4;b[10]=3;
 if(kind==20)b[10]=2;if(kind==7)b[10]=9;if(kind==8)b[11]=1;if(kind==9)b[0]=3;
 if(kind==10)b[2]=12,b[1]=2,b[4]=8,b[12]=1,b[13]=4,b[16]=1,b[17]=1;
 if(kind==11)b[2]=12,b[1]=2,b[4]=8,b[12]=1,b[13]=4,b[16]=2,b[17]=1;
 unsigned n=(kind==10||kind==11)?20:12;
 hosts[2][ri*8+4]=(uint8_t)n;hosts[2][ri*8+5]=0;
}
'''
 s=build.one(s,'static void upload_fixture(const char*dir){',helper+'\nstatic void upload_fixture(const char*dir){')
 marker='   if(active_ticks==20&&rx_scenario){'
 code=r'''
   if(active_ticks==10){
    assert(!qca_htt_native_begin((QcaHttNative*)p,(QcaPersistentNative*)p,3,ms*1000));
    if(htt_scenario==12)deliver_htt(0);
    assert(qca_htt_native_begin(&query,(QcaPersistentNative*)p,3,ms*1000)||htt_scenario==2||htt_scenario==3||htt_scenario==4||htt_scenario==5||htt_scenario==6);
    htt_started=1;assert(query.binding.endpoint==2&&query.attempted==1);
    assert(!qca_htt_native_begin(&rival,(QcaPersistentNative*)p,3,ms*1000)&&!rival.phase);
   }
   if(htt_started&&!query.stop_requested){
    if(active_ticks==12&&htt_scenario!=15&&htt_scenario!=14){deliver_htt(htt_scenario);}
    if(active_ticks==11&&(htt_scenario==13||htt_scenario==14)){deliver_rx(1,1);deliver_rx(2,1);}
    if(active_ticks==13&&htt_scenario==14){deliver_rx(1,1);deliver_rx(2,1);}
    if(active_ticks==14&&htt_scenario==14){deliver_rx(2,1);}
    if(active_ticks==12&&htt_scenario==16)a->channels.buffers[9].valid=0;
    if(active_ticks==12&&htt_scenario==18)((QcaPersistentNative*)p)->epoch++;
    if(active_ticks==12&&htt_scenario==19)((QcaHtcSession*)&p->startup->operating->control.session)->htt.max_bytes=128;
    int rc=qca_htt_native_poll(&query,htt_scenario==17&&active_ticks==12?ms*1000-2000:ms*1000);
    (void)rc;
   }
'''
 s=build.one(s,marker,code+marker)
 s=build.one(s,'if(active_ticks==200){','if(active_ticks==200000){')
 s=build.one(s,'assert(active_ticks==200||(rx_scenario>=3&&rx_scenario<=9)||rx_scenario==12||rx_scenario==13);','assert(htt_started&&active_ticks>=10);')
 s=build.one(s,'if(!persistent_fault&&(rx_scenario<3||rx_scenario==10||rx_scenario==11)){','if(qca_persistent_unload_safe(p)){')
 s=build.one(s,'assert(stopped&&p->life.phase==QCA_RADIO_CLOSED','assert(query.stop_requested&&p->life.phase==QCA_RADIO_CLOSED')
 s=build.one(s,'assert(qca_rx_clear((QcaPersistentRx*)&p->rx,&p->life));','assert(query.stop_requested);')
 s=build.one(s,'assert(qca_rx_poll((QcaPersistentRx*)&p->rx,&p->life,60000000)==-1);','assert(qca_rx_poll((QcaPersistentRx*)&p->rx,&p->life,60000000)==0);')
 s=build.one(s,'persistent_fault||rx_scenario||(w->phase==2','htt_started||persistent_fault||rx_scenario||(w->phase==2')
 s=build.one(s,'persistent_fault||rx_scenario||(o->phase==2','htt_started||persistent_fault||rx_scenario||(o->phase==2')
 s=build.one(s,'(rx_scenario||((o->control.credit.available==','(htt_started||rx_scenario||((o->control.credit.available==')
 marker=' printf("PERSISTENT_MOCK active_ticks='
 s=build.one(s,marker,r'''
 assert(query.stop_requested&&htt_posts==1&&query.attempted==1);
 assert(!qca_htt_native_begin(&query,(QcaPersistentNative*)p,3,60000000));
 (void)qca_htt_native_poll(&query,60000000);
 if(htt_scenario==0||htt_scenario==10||htt_scenario==13||htt_scenario==20){assert(query.phase==QCA_HTTN_RELEASED&&query.version_seen&&query.dma_completed&&query.version.major==(htt_scenario==20?2:3)&&query.version.minor==4);}
 else {assert(query.error&&query.phase==QCA_HTTN_FAULT);}
 if(htt_scenario==1||htt_scenario==15)assert(query.error==7);
 if(htt_scenario==12)assert(query.error==10&&query.response.completion<=query.watermark);
 if(htt_scenario==13)assert(query.archive_count==2&&query.archive[0].endpoint==0&&query.archive[1].endpoint==1);
 if(htt_scenario==16||htt_scenario==18||htt_scenario==19)assert(!qca_persistent_unload_safe(p));
 if(htt_scenario==18)assert(query.error==4);
 if(htt_scenario==19)assert(query.error==6);
 if(htt_scenario==1)assert(query.version_seen&&!query.dma_completed);
 assert(o->control.credit.available==o->control.credit.total-(htt_scenario==10?0u:(startup_fault==1?1u:0u))&&!o->control.credit.reserved);
 assert(o->control.credit.outstanding==(htt_scenario==10?0u:(startup_fault==1?1u:0u)));
 for(unsigned slot=0;slot<6;slot++){
  QcaRxEvent before,after;int present=qca_htt_native_export(&query,slot,&before,sizeof before);
  assert(!qca_htt_native_export(&query,slot,&after,sizeof after-1));
  assert(!qca_htt_native_export(&query,slot,(QcaRxEvent*)&query,sizeof before));
  assert(!qca_htt_native_export(&query,slot,(QcaRxEvent*)&p->rx,sizeof before));
  if(present){assert(before.completion&&before.bytes<=2040&&before.raw_bytes>=8&&before.raw_bytes<=2048);assert(qca_htt_native_export(&query,slot,&after,sizeof after));assert(!memcmp(&before,&after,sizeof before));}
 }
 assert(!qca_htt_native_export(&query,6,(QcaRxEvent*)&query.response,sizeof(QcaRxEvent)));
 printf("HTT_NATIVE scenario=%u posts=%u DMA=%u version=%u error=%u archive=%u all14released=%u\n",htt_scenario,htt_posts,query.dma_completed,query.version_seen,query.error,query.archive_count,qca_init_adapter_released(p->startup->operating->boot->board->setup->read.full.adapter));
 printf("PERSISTENT_MOCK active_ticks=''')
 return s
def main():
 if sys.platform!='linux':raise SystemExit('Yukabox-only C checks')
 out=ROOT/'runs/native-host';out.mkdir(parents=True,exist_ok=True);build.sources(out)
 assets=out/'fixture-assets';assets.mkdir(exist_ok=True)
 data=Path('/home/yuka/rabbit-world/native-wifi-qca9377-v1/vendor/firmware/ath10k/QCA9377/hw1.0/firmware-6.bin').read_bytes();policy=build.prior.checked.policy();assert sha(data)==policy['digest']
 key=prior.old.Ed25519PrivateKey.from_private_bytes(bytes([97])*32);public=key.public_key().public_bytes(prior.old.Encoding.Raw,prior.old.PublicFormat.Raw)
 for i,p in enumerate(prior.old.packets(data,key,target=bytes.fromhex(policy['target']),generation=policy['generation'],target_type=policy['type'],target_version=policy['version'],kind=policy['kind'])):(assets/f'chunk-{i}.bin').write_bytes(p)
 p=out/'init_probe.c';owner='.owner={'+','.join(str(n) for n in bytes.fromhex(policy['owner']))+'}';p.write_text(build.one(p.read_text(),owner,'.owner={'+','.join(str(n) for n in public)+'}'))
 (out/'fixture.c').write_text(fixture((BASE/'init_probe_test.c').read_text()))
 inc=['-I'+str(n) for n in (out,BASE,build.prior.checked.prior.actors.OLD,build.prior.checked.prior.actors.NATIVE,BASE/'runs/firmware-chunks')]
 files=prior.old.prior.prior.FILES+('full_read.c','config_read.c','config_setup.c','bmi_transport.c','diag_ce.c','firmware_port.c','firmware_channel.c','firmware_gatt.c','firmware_chunks.c','bmi_loader.c','board_query.c','board_smbios.c','boot_image.c','boot_transport.c','boot_native.c','operating.c','startup.c','startup_gatt.c','init_transaction.c','init_wire.c','memory_plan.c','resources.c','available.c','htc_wire.c','htc_session.c','htc_credit.c','htc_control.c','wmi_boot_info.c','wmi_scan.c','persistent.c','lifecycle.c','rx.c','version.c','htt_native.c')
 crypto=[BASE/'runs/firmware-chunks'/n for n in ('monocypher.c','monocypher-ed25519.c')];exe=out/'test'
 input_paths=[p for d in (ROOT,RX,build.VERSION,build.CHECKED,build.BRIDGE,build.prior.prior.LIFE) for p in d.iterdir() if p.is_file()]
 frozen_inputs={str(p.relative_to(ROOT.parent.parent)):sha(p.read_bytes()) for p in input_paths}
 compiled_paths=[out/'fixture.c',*[out/n for n in files],*out.glob('*.h'),*crypto,*[BASE/'runs/firmware-chunks'/n for n in ('monocypher.h','monocypher-ed25519.h')],build.prior.checked.prior.actors.NATIVE/'sha256.c']
 compiled_hashes={p.name:sha(p.read_bytes()) for p in compiled_paths}
 subprocess.run([str(prior.old.CC),'-DQCA_CONFIG_SETUP=1','-DQCA_FC_BASE=13','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all',*inc,str(out/'fixture.c'),*[str(out/n) for n in files],str(build.prior.checked.prior.actors.NATIVE/'sha256.c'),*map(str,crypto),'-o',str(exe)],check=True)
 log=''
 for scenario in range(21):
  r=subprocess.run([str(exe),'0',str(assets),'35','1' if scenario==10 else '0','0','0',str(scenario)],capture_output=True,text=True,timeout=90,env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1'})
  log+=r.stdout+r.stderr;(out/'host.log').write_text(log)
  if r.returncode:raise RuntimeError(f'case{scenario}: {r.stdout[-1000:]}\n{r.stderr[-3000:]}')
 for name in ['htt_native','rx','version']:
  subprocess.run([str(prior.old.CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-DQCA_CONFIG_SETUP=1','-DQCA_FC_BASE=13',*inc,'-c',str(out/(name+'.c')),'-o',str(out/(name+'.obj'))],check=True)
 inputs={str(p.relative_to(ROOT.parent.parent)):sha(p.read_bytes()) for p in input_paths};assert inputs==frozen_inputs
 assert compiled_hashes=={p.name:sha(p.read_bytes()) for p in compiled_paths}
 report={'status':'HTT-VERSION-CE4-COMBINED-CE1-CE2-ACTUAL-NATIVE-ASAN-COFF-PASS','scenarios':21,'build_host':'yukabox','source_sha256':inputs,'host_log_sha256':sha(log.encode()),'compiled_fixture_sources_sha256':compiled_hashes,'actual_native_entrypoints':True,'physical_verified':False,'signing_admitted':False,'whole_efi_candidate':False,'request_is_rf':False,'native_version_query_implemented':True,'htt_dataplane_ready':False,'wmi_credit_debit_for_htt':False,'duplicate_ce1_owner':False,'retained_export_slots':6}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
if __name__=='__main__':main()
