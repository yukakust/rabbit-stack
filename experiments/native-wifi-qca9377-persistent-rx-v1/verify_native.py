#!/usr/bin/env python3
"""Yukabox-only actual native RX entrypoint model, no physical claims."""
import importlib.util,json,os,subprocess,sys,hashlib
from pathlib import Path
import rx_build as build
fixture_spec=importlib.util.spec_from_file_location('startup_fixture',build.CHECKED/'startup_fixture.py')
startup_fixture=importlib.util.module_from_spec(fixture_spec)
sys.modules['startup_fixture']=startup_fixture;fixture_spec.loader.exec_module(startup_fixture)
sys.path.insert(0,str(build.BRIDGE))
spec=importlib.util.spec_from_file_location('reviewed_verify',build.BRIDGE/'verify_native.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
ROOT=build.ROOT;BASE=build.checked.BASE
sha=lambda b:hashlib.sha256(b).hexdigest()
def fixture(source):
 checked_fixture=old.startup_fixture.fixture
 try:
  old.startup_fixture.fixture=lambda text:checked_fixture(text).replace('||startup_fault==22','')
  s=old.fixture(source)
 finally:old.startup_fixture.fixture=checked_fixture
 s=s.replace('startup_fault==0||startup_fault==1||startup_fault==15','startup_fault==0||startup_fault==1||startup_fault==15||startup_fault==22')
 s=build.one(s,'static unsigned persistent_fault,active_ticks,stopped;','static unsigned persistent_fault,active_ticks,stopped;static unsigned rx_scenario;')
 s=build.one(s,'assert(argc==6);persistent_fault=', 'assert(argc==7);rx_scenario=(unsigned)atoi(argv[6]);assert(rx_scenario<=13);persistent_fault=')
 # Mock target explicitly stays quiet after READY unless this test injects RX.
 marker='  if(main_done&&qca_wmi_startup_view()->phase==1){'
 s=build.one(s,marker,'''  if(main_done&&qca_persistent_view()->life.phase==QCA_RADIO_ACTIVE&&(id==1||id==2)&&index==0x40){
   if(rx_scenario==13&&active_ticks>=20&&id==2)return 1;
   return 0;
  }
'''+marker)
 # Variables above are declared before memwrite in the derived fixture.
 helper=r'''
static void deliver_rx(unsigned pipe,unsigned kind){
 const QcaPersistentNative*p=qca_persistent_view();QcaPersistentRx*x=(QcaPersistentRx*)&p->rx;
 QcaInitAdapter*a=p->startup->operating->boot->board->setup->read.full.adapter;
 QcaCeRing*r=&a->channels.rings[pipe];assert(x->posted[pipe-1]);unsigned ri=r->read;
 uint8_t*b=hosts[2*pipe+1];memset(b,0,2048);unsigned n=16;
 b[0]=pipe==1?0:1;b[2]=8;bp(b+8,0x123456);bp(b+12,0xcafebabe);
 if(pipe==1){b[2]=2;b[8]=9;n=10;}
 if(kind==2||kind==5||kind==10){
  memset(b,0,24);b[1]=2;b[2]=8;b[4]=8;b[8]=1;b[9]=4;b[12]=1;b[13]=kind==5?3:1;n=16;
 }
 if(kind==3)b[2]=7;
 if(kind==4)b[0]=2;
 if(kind==6){b[2]=4;bp(b+8,2);n=12;}
 if(kind==7)r->cookie[ri]^=1;
 if(kind==8)hosts[2*pipe][ri*8]^=1;
 if(kind==9)n=2049;
 hosts[2*pipe][ri*8+4]=(uint8_t)n;hosts[2*pipe][ri*8+5]=(uint8_t)(n>>8);
 if(kind==10)hosts[2*pipe][ri*8+4]=hosts[2*pipe][ri*8+5]=0;
 registers[pipe][0x48/4]=kind==12?(ri+2)&7:(ri+1)&7;
}
'''
 # Insert after hardware simulator/host arrays are defined, before upload loop.
 s=build.one(s,'static void upload_fixture(const char*dir){',helper+'\nstatic void upload_fixture(const char*dir){')
 marker='   if(active_ticks==200){'
 code=r'''
   assert(!qca_rx_clear((QcaPersistentRx*)&p->rx,&p->life));
   if(active_ticks==20&&rx_scenario){
    if(rx_scenario==11){deliver_rx(1,1);deliver_rx(2,1);}
    else deliver_rx(rx_scenario==2||rx_scenario==5||rx_scenario==10?1:2,rx_scenario);
   }
   if(active_ticks==21&&rx_scenario==10){
    assert(!p->rx.completed);unsigned ri=a->channels.rings[1].read;
    hosts[2][ri*8+4]=16;hosts[2][ri*8+5]=0;
   }
   if(active_ticks==30&&(rx_scenario==1||rx_scenario==11)){
    assert(p->rx.count==(rx_scenario==11?2:1));
    const QcaRxEvent*e=&p->rx.events[p->rx.head];uint32_t id=e->completion;QcaRxEvent copy;
    assert(!qca_rx_take((QcaPersistentRx*)&p->rx,id+100,&copy,sizeof(copy)));
    assert(!qca_rx_take((QcaPersistentRx*)&p->rx,id,&copy,sizeof(copy)-1));
    uint32_t posts=p->rx.posted_count,done=p->rx.completed;
    if(rx_scenario==11){assert(p->rx.backpressure&&posts==1&&done==2);}
    assert(qca_rx_take((QcaPersistentRx*)&p->rx,id,&copy,sizeof(copy)));
    assert(copy.completion==id&&copy.payload[0]==(copy.pipe==1?9:0x56));
    assert(!qca_rx_take((QcaPersistentRx*)&p->rx,id,&copy,sizeof(copy)));
   }
   if(active_ticks==40&&rx_scenario==11){
    const QcaRxEvent*e=&p->rx.events[p->rx.head];QcaRxEvent copy;
    assert(p->rx.count==1&&e->pipe==2&&e->payload[0]==0x56);
    assert(qca_rx_take((QcaPersistentRx*)&p->rx,e->completion,&copy,sizeof(copy)));
   }
   if(active_ticks==50&&(rx_scenario==2||rx_scenario==10)){
    assert(p->rx.completed==1&&!p->rx.count);
    assert(p->startup->operating->control.credit.available==p->startup->operating->control.credit.total);
    assert(!p->startup->operating->control.credit.outstanding);
   }
'''
 s=build.one(s,marker,code+marker)
 # Runtime RX faults differ from initial READY rejection and revoke policy.
 s=build.one(s,'assert(active_ticks==200);','assert(active_ticks==200||(rx_scenario>=3&&rx_scenario<=9)||rx_scenario==12||rx_scenario==13);')
 s=build.one(s,'if(!persistent_fault){assert(stopped&&p->life.phase==QCA_RADIO_CLOSED&&qca_persistent_unload_safe(p));}',
  '''if(!persistent_fault&&(rx_scenario<3||rx_scenario==10||rx_scenario==11)){
   assert(stopped&&p->life.phase==QCA_RADIO_CLOSED&&qca_persistent_unload_safe(p));
   QcaRadioLifecycle other=p->life;
   assert(!qca_rx_clear((QcaPersistentRx*)&p->rx,&other));
   assert(qca_rx_clear((QcaPersistentRx*)&p->rx,&p->life));
   assert(qca_rx_poll((QcaPersistentRx*)&p->rx,&p->life,60000000)==-1);
  }''')
 # Shared credit state may change only in explicitly injected runtime trailers.
 s=build.one(s,'o->control.credit.available==(o->control.credit.total-(startup_fault==0?0u:1u))&&o->control.credit.outstanding==(startup_fault==0?0u:1u)',
  '(rx_scenario||((o->control.credit.available==(o->control.credit.total-(startup_fault==0?0u:1u)))&&o->control.credit.outstanding==(startup_fault==0?0u:1u)))')
 s=build.one(s,'persistent_fault||(w->phase==2','persistent_fault||rx_scenario||(w->phase==2')
 s=build.one(s,'persistent_fault||(o->phase==2','persistent_fault||rx_scenario||(o->phase==2')
 s=build.one(s,'printf("PERSISTENT_MOCK active_ticks=',r'''
 if((rx_scenario>=3&&rx_scenario<=9)||rx_scenario==12||rx_scenario==13){
  assert(p->rx.phase==QCA_RX_FAULT&&p->rx.error&&!qca_rx_clear((QcaPersistentRx*)&p->rx,&p->life));
  assert(p->rx.completed==(rx_scenario==13?1u:0u));
  assert(o->control.credit.available==o->control.credit.total-(startup_fault==1?1u:0u));
  assert(o->control.credit.outstanding==(startup_fault==1?1u:0u));
 }
 printf("PERSISTENT_MOCK active_ticks=''')
 return s
def main():
 if sys.platform!='linux':raise SystemExit('Yukabox-only native C verification')
 out=ROOT/'runs/native-host';out.mkdir(parents=True,exist_ok=True);build.sources(out)
 assets=out/'fixture-assets';assets.mkdir(exist_ok=True)
 data=Path('/home/yuka/rabbit-world/native-wifi-qca9377-v1/vendor/firmware/ath10k/QCA9377/hw1.0/firmware-6.bin').read_bytes();policy=build.checked.policy();assert sha(data)==policy['digest']
 key=old.Ed25519PrivateKey.from_private_bytes(bytes([97])*32);public=key.public_key().public_bytes(old.Encoding.Raw,old.PublicFormat.Raw)
 for i,p in enumerate(old.packets(data,key,target=bytes.fromhex(policy['target']),generation=policy['generation'],target_type=policy['type'],target_version=policy['version'],kind=policy['kind'])):(assets/f'chunk-{i}.bin').write_bytes(p)
 native=out/'init_probe.c';oldowner='.owner={'+','.join(str(n) for n in bytes.fromhex(policy['owner']))+'}'
 native.write_text(build.one(native.read_text(),oldowner,'.owner={'+','.join(str(n) for n in public)+'}'))
 (out/'fixture.c').write_text(fixture((BASE/'init_probe_test.c').read_text()))
 inc=['-I'+str(n) for n in (out,BASE,build.checked.prior.actors.OLD,build.checked.prior.actors.NATIVE,BASE/'runs/firmware-chunks')]
 files=old.prior.prior.FILES+('full_read.c','config_read.c','config_setup.c','bmi_transport.c','diag_ce.c','firmware_port.c','firmware_channel.c','firmware_gatt.c','firmware_chunks.c','bmi_loader.c','board_query.c','board_smbios.c','boot_image.c','boot_transport.c','boot_native.c','operating.c','startup.c','startup_gatt.c','init_transaction.c','init_wire.c','memory_plan.c','resources.c','available.c','htc_wire.c','htc_session.c','htc_credit.c','htc_control.c','wmi_boot_info.c','wmi_scan.c','persistent.c','lifecycle.c','rx.c')
 crypto=[BASE/'runs/firmware-chunks'/n for n in ('monocypher.c','monocypher-ed25519.c')];exe=out/'test'
 subprocess.run([str(old.CC),'-DQCA_CONFIG_SETUP=1','-DQCA_FC_BASE=13','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all',*inc,str(out/'fixture.c'),*[str(out/n) for n in files],str(build.checked.prior.actors.NATIVE/'sha256.c'),*map(str,crypto),'-o',str(exe)],check=True)
 log='';cases=[(s,0,0) for s in range(23)]+[(0,f,0) for f in range(1,6)]+[(1 if r in (2,5,10) else 0,0,r) for r in range(1,14)]
 for startup,fault,rx in cases:
  r=subprocess.run([str(exe),'0',str(assets),'35',str(startup),str(fault),str(rx)],capture_output=True,text=True,timeout=90,env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1'})
  log+=r.stdout+r.stderr;(out/'host.log').write_text(log)
  if r.returncode:raise RuntimeError(f'case{startup}/{fault}/{rx}: {r.stdout[-1500:]}\n{r.stderr[-4000:]}')
 for n in ('persistent','lifecycle','rx','init_probe'):
  subprocess.run([str(old.CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-DQCA_CONFIG_SETUP=1','-DQCA_FC_BASE=13',*inc,'-c',str(out/(n+'.c')),'-o',str(out/(n+'.obj'))],check=True)
 inputs={str(p.relative_to(ROOT.parent.parent)):sha(p.read_bytes()) for d in (ROOT,build.CHECKED,build.BRIDGE,build.prior.LIFE) for p in d.glob('*') if p.is_file()}
 report={'status':'PERSISTENT-RX-ACTUAL-NATIVE-ASAN-COFF-PASS','scenarios':len(cases),'source_sha256':inputs,'host_log_sha256':sha(log.encode()),'compiled_fixture_sources_sha256':{p.name:sha(p.read_bytes()) for p in [out/'fixture.c',*[out/n for n in files],*crypto]},'actual_native_entrypoints':True,'physical_verified':False,'signing_admitted':False,'rx_pump_implemented':True,'station_ready':False,'rf_transmit':False,'owned_events':2,'max_completions_per_poll':2,'credits_only_real_validated_trailers':True,'runtime_dispatcher_implemented':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
if __name__=='__main__':main()
