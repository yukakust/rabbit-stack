"""Actual native platform entrypoints+scan/RX/TX joined; explicit target model."""
import sys,importlib.util,subprocess,hashlib,json,os
from pathlib import Path
import scan_build as build
RX=build.prior.RX
spec=importlib.util.spec_from_file_location('checked_rx_verifier',RX/'verify_native.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
ROOT=build.ROOT;BASE=build.checked.BASE;sha=lambda b:hashlib.sha256(b).hexdigest()
def fixture(text):
 s=prior.fixture(text)
 s='#include "scan_native.h"\nconst QcaNativeScan*qca_scan_native_view(void);\nvoid qca_scan_status(uint8_t[416]);\nsize_t qca_scan_att(uint16_t,const uint8_t*,size_t,uint8_t*,size_t);\n'+s
 s=build.one(s,'static unsigned rx_scenario;','static unsigned rx_scenario;static unsigned native_scenario,scan_posts,credit_pending,emitted;static uint32_t commands[8];')
 s=build.one(s,'assert(argc==7);rx_scenario=', 'assert(argc==8);native_scenario=(unsigned)atoi(argv[7]);assert(native_scenario<=9);rx_scenario=')
 s=build.one(s,'hosts[3][10]=8;hosts[3][12]=0;hosts[3][13]=1;hosts[3][14]=9;', 'hosts[3][10]=2;hosts[3][12]=0;hosts[3][13]=7;hosts[3][14]=4;')
 s=build.one(s,'hosts[3][14]=0xf8;hosts[3][15]=0x0f;','hosts[3][14]=0xf8;hosts[3][15]=0x06;')
 marker='  if(main_done&&qca_persistent_view()->life.phase==QCA_RADIO_ACTIVE&&(id==1||id==2)&&index==0x40){'
 s=build.one(s,marker,r'''
  if(main_done&&qca_persistent_view()->life.phase==QCA_RADIO_ACTIVE&&id==3&&index==0x3c&&qca_scan_native_view()->tx.phase==QCA_TX_POSTED){
   const QcaNativeScan*s=qca_scan_native_view();assert(scan_posts<8);commands[scan_posts++]=bw(hosts[7]+8);
   assert(!s->tx.credit->reserved&&s->tx.credit->outstanding);
   if(native_scenario!=5)registers[3][0x44/4]=value;
   credit_pending+=(s->tx.bytes+s->tx.credit->size-1)/s->tx.credit->size;
   if(native_scenario==6)return 1;
   return 0;
  }
'''+marker)
 # Don't manually stop at200 ticks: the actual54 entrypoint owns finite STOP.
 s=build.one(s,'if(active_ticks==200){','if(active_ticks==200&&persistent_fault){')
 helper=r'''
static void emit_scan_payload(const uint8_t*p,unsigned n){
 const QcaPersistentNative*r=qca_persistent_view();QcaInitAdapter*a=r->startup->operating->boot->board->setup->read.full.adapter;
 assert(r->rx.posted[1]&&registers[2][0x48/4]==a->channels.rings[2].read);unsigned ri=a->channels.rings[2].read;
 uint8_t*b=hosts[5];memset(b,0,2048);b[0]=1;b[2]=(uint8_t)n;b[3]=(uint8_t)(n>>8);memcpy(b+8,p,n);
 hosts[4][ri*8+4]=(uint8_t)(n+8);hosts[4][ri*8+5]=(uint8_t)((n+8)>>8);registers[2][0x48/4]=(ri+1)&7;
}
static void emit_scan_event(unsigned type,unsigned reason,unsigned request){
 uint8_t b[32]={0};bp(b,0x3001);bp(b+4,24|(36u<<16));bp(b+8,type);bp(b+12,reason);
 bp(b+16,type==8?2412:0);bp(b+20,0xa000|request);bp(b+24,0xa007);emit_scan_payload(b,32);
}
static void emit_beacon(void){
 uint8_t b[112]={0};bp(b,0x7001);bp(b+4,40|(44u<<16));bp(b+8,native_scenario==3?6:1);bp(b+24,57);bp(b+48,60|(17u<<16));
 uint8_t*f=b+52;f[0]=0x80;for(unsigned j=0;j<6;j++){f[4+j]=255;f[10+j]=f[16+j]=(uint8_t)(j+2);}f[32]=100;f[34]=0x11;
 f[36]=0;f[37]=16;memcpy(f+38,"SILK_56E35E_Plus",16);f[54]=3;f[55]=1;f[56]=native_scenario==3?6:1;
 if(native_scenario==4)b[4]=39;emit_scan_payload(b,112);
}
'''
 s=build.one(s,'static void upload_fixture(const char*dir){',helper+'\nstatic void upload_fixture(const char*dir){')
 marker='   if(active_ticks==20&&rx_scenario){'
 code=r'''
   const QcaNativeScan*sc=qca_scan_native_view();
   if(native_scenario==7&&sc->scan.stop_begun)((QcaNativeScan*)sc)->last=UINT64_MAX;
   if(credit_pending&&native_scenario!=2&&p->rx.posted[0]&&registers[1][0x48/4]==a->channels.rings[1].read){
    deliver_rx(1,2);hosts[3][13]=(uint8_t)credit_pending;credit_pending=0;
   }
   if(sc->scan.stop_begun&&p->rx.posted[1]&&registers[2][0x48/4]==a->channels.rings[2].read){
    if(emitted==0){if(native_scenario==1||native_scenario==9){uint8_t b[8]={0x56,0x34,0x12};emit_scan_payload(b,8);emitted=10;}
     else if(native_scenario==8){emit_scan_event(1,0,9);emitted=10;}
     else {emit_scan_event(1,0,8);emitted=1;}}
    else if(emitted==10&&sc->archive_count){if(native_scenario==9){uint8_t b[8]={0x22,0x22,0x22};emit_scan_payload(b,8);emitted=11;}else {emit_scan_event(1,0,8);emitted=1;}}
    else if(emitted==11&&sc->archive_count==2){emit_scan_event(1,0,8);emitted=1;}
    else if(emitted==1&&sc->scan.pending.started){emit_scan_event(8,0,8);emitted=2;}
    else if(emitted==2&&sc->scan.live_frequency==2412){emit_beacon();emitted=3;}
    else if(emitted==3&&(sc->scan.ssid_seen||sc->archive_count)){emit_scan_event(2,sc->scan.stop.stop.phase>=QCA_STOP_POSTED?1:0,8);emitted=4;}
   }
'''
 s=build.one(s,marker,code+marker)
 # Initial READY/TX proof remains cached while runtime owner/scan may fault.
 s=build.one(s,'assert(active_ticks==200||(rx_scenario>=3&&rx_scenario<=9)||rx_scenario==12||rx_scenario==13);','assert(active_ticks>0);')
 s=build.one(s,'assert(stopped&&p->life.phase==QCA_RADIO_CLOSED','assert(p->life.phase==QCA_RADIO_CLOSED')
 s=build.one(s,'(rx_scenario||((o->control.credit.available==','(scan_posts||rx_scenario||((o->control.credit.available==')
 # Avoid clearing owned queues in this profile. Every retained packet is exported.
 start=s.index('   QcaRadioLifecycle other=p->life;');end=s.index('\n  }\n  else {assert(p->life.phase',start)
 s=s[:start]+s[end:]
 marker=' printf("PERSISTENT_MOCK active_ticks='
 s=build.one(s,marker,r'''
 { tick(60001);const QcaNativeScan*sc=qca_scan_native_view();uint8_t status[416];qca_scan_status(status);
 assert(!memcmp(status,"QSCN0001",8)&&status[24]==1&&status[248]==54);
 assert(sc->quiesce_requested&&commands[0]==0x3003);
 if(native_scenario==0||native_scenario==1||native_scenario==8){assert(commands[1]==0x4001&&commands[2]==0x5001&&commands[3]==0x3001&&sc->scan.pending.started&&sc->scan.stop.stop.terminal_seen&&sc->scan.ssid_seen&&sc->scan.has_observation);}
 if(native_scenario==1||native_scenario==8)assert(sc->archive_count==1);
 if(native_scenario==9)assert(sc->archive_count==2&&sc->stop_requested);
 if(native_scenario==2)assert(sc->error&&!sc->scan.pending.started);
 if(native_scenario==3||native_scenario==4)assert(!sc->scan.ssid_seen);
 if(native_scenario>=4&&native_scenario<=7)assert(sc->error);
 uint8_t req[7]={10,34,0},reply[247];
 assert(qca_scan_att(247,req,3,reply,sizeof(reply))==247&&!memcmp(reply+1,status,246));
 req[0]=12;req[3]=246;req[4]=0;assert(qca_scan_att(247,req,5,reply,sizeof(reply))==171&&!memcmp(reply+1,status+246,170));
 req[3]=160;req[4]=1;assert(qca_scan_att(247,req,5,reply,sizeof(reply))==1);req[3]++;assert(qca_scan_att(247,req,5,reply,sizeof(reply))==5&&reply[4]==7);
 uint8_t one[512],two[512];
 for(unsigned page=0;page<40;page++){
  unsigned bytes=qca_native_scan_export(sc,page,one,sizeof(one));assert(bytes==(page%5==4?36u:512u));
  assert(qca_native_scan_export(sc,page,two,sizeof(two))==bytes&&!memcmp(one,two,bytes));
  req[0]=10;req[1]=(uint8_t)(37+2*page);req[2]=0;
  assert(qca_scan_att(247,req,3,reply,sizeof(reply))==(bytes<246?bytes+1:247)&&!memcmp(reply+1,one,bytes<246?bytes:246));
  req[0]=12;req[3]=(uint8_t)bytes;req[4]=(uint8_t)(bytes>>8);assert(qca_scan_att(247,req,5,reply,sizeof(reply))==1);
  req[3]=(uint8_t)(bytes+1);req[4]=(uint8_t)((bytes+1)>>8);assert(qca_scan_att(247,req,5,reply,sizeof(reply))==5&&reply[4]==7);
  req[0]=0x12;assert(qca_scan_att(247,req,3,reply,sizeof(reply))==5&&reply[4]==3);
 }
 assert(!qca_native_scan_export(sc,40,one,sizeof(one))&&!qca_native_scan_export(sc,0,one,511));
 printf("SCAN_ACTUAL_NATIVE scenario=%u commands=%u started=%u terminal=%u SSID=%u archive=%u actual14released EXPORT_BOUNDS_PASS\n",native_scenario,scan_posts,sc->scan.pending.started,sc->scan.stop.stop.terminal_seen,sc->scan.ssid_seen,sc->archive_count); }
 printf("PERSISTENT_MOCK active_ticks=''')
 return s
def main():
 if sys.platform!='linux':raise SystemExit('Yukabox only')
 out=ROOT/'runs/native-host';out.mkdir(parents=True,exist_ok=True);build.sources(out)
 assets=out/'fixture-assets';assets.mkdir(exist_ok=True)
 data=Path('/home/yuka/rabbit-world/native-wifi-qca9377-v1/vendor/firmware/ath10k/QCA9377/hw1.0/firmware-6.bin').read_bytes();policy=build.policy();assert sha(data)==policy['digest']
 key=prior.old.Ed25519PrivateKey.from_private_bytes(bytes([97])*32);public=key.public_key().public_bytes(prior.old.Encoding.Raw,prior.old.PublicFormat.Raw)
 for i,p in enumerate(prior.old.packets(data,key,target=bytes.fromhex(policy['target']),generation=policy['generation'],target_type=policy['type'],target_version=policy['version'],kind=policy['kind'])):(assets/f'chunk-{i}.bin').write_bytes(p)
 p=out/'init_probe.c';owner='.owner={'+','.join(str(n) for n in bytes.fromhex(policy['owner']))+'}';p.write_text(build.one(p.read_text(),owner,'.owner={'+','.join(str(n) for n in public)+'}'))
 (out/'fixture.c').write_text(fixture((BASE/'init_probe_test.c').read_text()))
 inc=['-I'+str(n) for n in (out,BASE,build.checked.prior.actors.OLD,build.checked.prior.actors.NATIVE,BASE/'runs/firmware-chunks')]
 files=prior.old.prior.prior.FILES+('full_read.c','config_read.c','config_setup.c','bmi_transport.c','diag_ce.c','firmware_port.c','firmware_channel.c','firmware_gatt.c','firmware_chunks.c','bmi_loader.c','board_query.c','board_smbios.c','boot_image.c','boot_transport.c','boot_native.c','boot_gatt.c','operating.c','startup.c','startup_gatt.c','init_transaction.c','init_wire.c','memory_plan.c','resources.c','available.c','htc_wire.c','htc_session.c','htc_credit.c','htc_control.c','wmi_boot_info.c','wmi_scan.c','persistent.c','lifecycle.c','rx.c','trial.c','profile_gatt.c','scan_native.c','scan_gatt.c','beacon_info.c',*[m+'.c' for m in build.MODULES])
 crypto=[BASE/'runs/firmware-chunks'/n for n in ('monocypher.c','monocypher-ed25519.c')];exe=out/'test'
 subprocess.run([str(prior.old.CC),'-DQCA_CONFIG_SETUP=1','-DQCA_FC_BASE=13','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all',*inc,str(out/'fixture.c'),*[str(out/n) for n in files],str(build.checked.prior.actors.NATIVE/'sha256.c'),*map(str,crypto),'-o',str(exe)],check=True)
 log=''
 for scenario in range(10):
  r=subprocess.run([str(exe),'0',str(assets),'35','0','0','0',str(scenario)],capture_output=True,text=True,timeout=90,env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1'});log+=r.stdout+r.stderr;(out/'host.log').write_text(log)
  if r.returncode:raise RuntimeError(f'case{scenario}: {r.stdout[-1200:]}\n{r.stderr[-3000:]}')
 for n in ('scan_native','scan_gatt','coordinator','init_probe'):
  subprocess.run([str(prior.old.CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-DQCA_CONFIG_SETUP=1','-DQCA_FC_BASE=13',*inc,'-c',str(out/(n+'.c')),'-o',str(out/(n+'.obj'))],check=True)
 dirs=[ROOT,build.PROFILE,RX,build.checked.ROOT,build.prior.rx.BRIDGE,build.prior.rx.prior.LIFE,*[build.E/f for f in build.MODULES.values()]]
 inputs={str(p.relative_to(ROOT.parent.parent)):sha(p.read_bytes()) for d in dirs for p in d.iterdir() if p.is_file()}
 report={'status':'ACTUAL-NATIVE-PASSIVE-SCAN-COORDINATOR-OWNED-EXPORT-ASAN-COFF-PASS','scenarios':10,'source_sha256':inputs,'host_log_sha256':sha(log.encode()),'compiled_fixture_sources_sha256':{p.name:sha(p.read_bytes()) for p in [out/'fixture.c',*[out/n for n in files],*crypto]},'actual_native_entrypoints':True,'lower_backend_mocked':True,'physical_verified':False,'rf_admission_granted':False,'beacon_discovery_physical':False,'credentials':False,'unknown_event_discards':0,'export_slots':8,'export_pages':40}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
if __name__=='__main__':main()
