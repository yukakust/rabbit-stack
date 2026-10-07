#!/usr/bin/env python3
"""Host model of actual CE3 owner+shared RX ledger; Yukabox only, no candidate."""
import importlib.util,sys,subprocess,hashlib,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parent;RX=ROOT.parent/'native-wifi-qca9377-persistent-rx-v1'
sys.path.insert(0,str(RX));import rx_build as build
spec=importlib.util.spec_from_file_location('checked_rx_verifier',RX/'verify_native.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
BASE=build.checked.BASE;sha=lambda b:hashlib.sha256(b).hexdigest()
def fixture(text):
 s=prior.fixture(text)
 s='#include "tx.h"\n'+s
 s=build.one(s,'static unsigned rx_scenario;','static unsigned rx_scenario;static unsigned tx_scenario,tx_started,tx_stopped,tx_posts;static QcaPersistentTx publisher;')
 s=build.one(s,'assert(argc==7);rx_scenario=', 'assert(argc==8);tx_scenario=(unsigned)atoi(argv[7]);assert(tx_scenario<=15);rx_scenario=')
 marker='  if(main_done&&qca_persistent_view()->life.phase==QCA_RADIO_ACTIVE&&(id==1||id==2)&&index==0x40){'
 s=build.one(s,marker,r'''
  if(main_done&&qca_persistent_view()->life.phase==QCA_RADIO_ACTIVE&&id==3&&index==0x3c&&publisher.phase==QCA_TX_POSTED){
   tx_posts++;const QcaPersistentNative*p=qca_persistent_view();
   const uint8_t*b=hosts[7];assert(publisher.attempted==tx_posts&&b[0]==p->startup->operating->control.credit.endpoint&&b[1]==1);
   assert((b[2]|((unsigned)b[3]<<8))==publisher.bytes-8&&b[8]==0x34&&b[9]==0x12);
   unsigned ri=(value-1)&7;assert((hosts[6][ri*8+6]|((unsigned)hosts[6][ri*8+7]<<8))==(unsigned)b[0]*4);
   assert(!p->startup->operating->control.credit.reserved&&p->startup->operating->control.credit.outstanding);
   if(tx_scenario!=1)registers[3][0x44/4]=value;
   if(tx_scenario==3){QcaInitAdapter*a=p->startup->operating->boot->board->setup->read.full.adapter;a->channels.rings[3].cookie[ri]^=1;}
   if(tx_scenario==4)hosts[6][ri*8]^=1;
   if(tx_scenario==5)hosts[6][ri*8+4]^=1;
   if(tx_scenario==6)registers[3][0x44/4]=(value+1)&7;
   if(tx_scenario==2)return 1;
   return 0;
  }
'''+marker)
 # Inject an ambiguous hardware completion-index read only in its actual owner.
 marker='static Status EFIAPI mem_read('
 pos=s.index(marker);body=s.index('{',pos)+1
 s=s[:body]+'''\n if(tx_scenario==14&&publisher.phase==QCA_TX_POSTED&&off==0x35044)return 1;\n'''+s[body:]
 marker='   if(active_ticks==20&&rx_scenario){'
 code=r'''
   if(!tx_started){assert(qca_tx_begin(&publisher,(QcaPersistentNative*)p,ms*1000));tx_started=1;}
   if(active_ticks==5){
    uint8_t body[4088]={0x34,0x12};uint32_t id=0;QcaPersistentTx before=publisher;QcaHtcCredit credit=*publisher.credit;
    assert(!qca_tx_submit(&publisher,body,3,ms*1000,20000,&id));
    assert(!qca_tx_submit(&publisher,body,12,ms*1000,0,&id));
    assert(!qca_tx_submit(&publisher,body,12,UINT64_MAX,100,&id));
    assert(!qca_tx_submit(&publisher,body,12,ms*1000,10000001,&id));
    assert(!qca_tx_submit(&publisher,body,12,ms*1000,20000,&publisher.request));
    unsigned too_big=(unsigned)publisher.credit->total*publisher.credit->size-7;
    if(too_big<=publisher.credit->max_bytes)assert(!qca_tx_submit(&publisher,body,too_big,ms*1000,20000,&id));
    body[3]=1;assert(!qca_tx_submit(&publisher,body,12,ms*1000,20000,&id));
    assert(!memcmp(&before,&publisher,sizeof(before))&&!memcmp(&credit,publisher.credit,sizeof(credit)));
   }
   if(active_ticks==10){
    uint8_t body[4088]={0x34,0x12};uint32_t id=0;
    unsigned n=tx_scenario==9||tx_scenario==10?publisher.credit->max_bytes:12;
    if(n+8>(unsigned)publisher.credit->size*publisher.credit->total)n=(unsigned)publisher.credit->size*publisher.credit->total-8;
    assert(qca_tx_submit(&publisher,body,n,ms*1000,20000,&id)&&id==1);
    body[4]=0xee;assert(!publisher.frame[12]);
    assert(!qca_tx_submit(&publisher,body,n,ms*1000,20000,&id));
   }
   if(active_ticks==11&&tx_scenario==8){assert(publisher.phase==QCA_TX_RESERVED);assert(qca_tx_cancel(&publisher,1,ms*1000));}
   if(active_ticks==12&&tx_scenario==7){assert(publisher.phase==QCA_TX_POSTED);assert(qca_tx_poll(&publisher,ms*1000-2000)==-1);}
   if(active_ticks==12&&tx_scenario==12){assert(publisher.phase==QCA_TX_POSTED);assert(qca_stop());tx_stopped=1;}
   if(active_ticks==11&&tx_scenario==13){a->channels.routes[3].pipe=0;}
   if(active_ticks==11&&tx_scenario==15){a->channels.buffers[7].valid=0;assert(!qca_tx_cancel(&publisher,1,ms*1000));}
   if(active_ticks==15&&(tx_scenario==0||tx_scenario==9||tx_scenario==10)){
    fprintf(stderr,"TX_DEBUG phase=%u error=%u bytes=%u max=%u size=%u total=%u available=%u reserved=%u out=%u\n",publisher.phase,publisher.error,publisher.bytes,publisher.credit->max_bytes,publisher.credit->size,publisher.credit->total,publisher.credit->available,publisher.credit->reserved,publisher.credit->outstanding);
    assert(publisher.phase==QCA_TX_DMA_DONE&&publisher.completed==1);
    unsigned cost=(publisher.bytes+publisher.credit->size-1)/publisher.credit->size;
    assert(publisher.credit->outstanding==cost); /* NO refund on DMA. */
    assert(!qca_tx_cancel(&publisher,1,ms*1000));assert(!qca_tx_retire(&publisher,2));
    assert(qca_tx_poll(&publisher,ms*1000)==1&&publisher.completed==1);
    assert(qca_tx_retire(&publisher,1));uint8_t body[4088]={0x34,0x12};uint32_t id=0;
    unsigned n=tx_scenario==0?12:publisher.credit->max_bytes;
    if(n+8>(unsigned)publisher.credit->size*publisher.credit->total)n=(unsigned)publisher.credit->size*publisher.credit->total-8;
    assert(qca_tx_submit(&publisher,body,n,ms*1000,20000,&id)&&id==2);
   }
   if(active_ticks==18&&tx_scenario==10){
    assert(publisher.phase==QCA_TX_WAIT_CREDIT&&publisher.credit->outstanding);
    deliver_rx(1,2);hosts[3][13]=(uint8_t)publisher.credit->outstanding;
   }
   if(!tx_stopped){
    int rc=qca_tx_poll(&publisher,ms*1000);
    if(rc<0){assert(qca_stop());tx_stopped=1;}
   }
   if(active_ticks==60&&!tx_stopped){assert(qca_stop());tx_stopped=1;}
   assert(!qca_tx_clear(&publisher));
'''
 s=build.one(s,marker,code+marker)
 s=build.one(s,'assert(active_ticks==200||(rx_scenario>=3&&rx_scenario<=9)||rx_scenario==12||rx_scenario==13);','assert(tx_started&&active_ticks>=11);')
 s=build.one(s,'if(!persistent_fault&&(rx_scenario<3||rx_scenario==10||rx_scenario==11)){','if(qca_persistent_unload_safe(p)){')
 s=build.one(s,'assert(stopped&&p->life.phase==QCA_RADIO_CLOSED','assert(tx_stopped&&p->life.phase==QCA_RADIO_CLOSED')
 # Native caller stop has real quiesce effects; inherited cached startup guards
 # may be faulted while validated pre-publication READY evidence remains.
 s=build.one(s,'persistent_fault||rx_scenario||(w->phase==2','tx_started||persistent_fault||rx_scenario||(w->phase==2')
 s=build.one(s,'persistent_fault||rx_scenario||(o->phase==2','tx_started||persistent_fault||rx_scenario||(o->phase==2')
 s=build.one(s,'(rx_scenario||((o->control.credit.available==','(tx_started||rx_scenario||((o->control.credit.available==')
 marker=' printf("PERSISTENT_MOCK active_ticks='
 s=build.one(s,marker,r'''
 assert(tx_stopped&&!qca_tx_submit(&publisher,(const uint8_t*)"bad!",4,60000000,1000,&tx_started));
 assert(!publisher.credit->reserved||tx_scenario==13||tx_scenario==15);
 if(tx_scenario==0||tx_scenario==10)assert(tx_posts==2&&publisher.completed==2);
 if(tx_scenario==9)assert(tx_posts==1&&publisher.completed==1&&publisher.error==3);
 if(tx_scenario==8)assert(!tx_posts&&publisher.phase==QCA_TX_CANCELLED&&!publisher.credit->outstanding&&publisher.credit->available==publisher.credit->total);
 if(tx_scenario==1)assert(publisher.phase==QCA_TX_FAULT&&publisher.error==3&&publisher.credit->outstanding);
 if(tx_scenario==2)assert(publisher.phase==QCA_TX_FAULT&&publisher.error==6&&publisher.credit->outstanding);
 if(tx_scenario==15)assert(!tx_posts&&publisher.phase==QCA_TX_FAULT&&publisher.credit->reserved==1);
 uint16_t outstanding=publisher.credit->outstanding;
 if(qca_persistent_unload_safe(p)){assert(qca_tx_clear(&publisher)&&publisher.phase==QCA_TX_CLEARED);assert(publisher.credit->outstanding==outstanding);}
 else assert(!qca_tx_clear(&publisher));
 printf("TX_SHARED_NATIVE scenario=%u posts=%u DMA_done=%u credit_outstanding=%u SAFE_RELEASE_PASS\n",tx_scenario,tx_posts,publisher.completed,outstanding);
 printf("PERSISTENT_MOCK active_ticks=''')
 return s
def main():
 if sys.platform!='linux':raise SystemExit('Yukabox-only C checks')
 out=ROOT/'runs/native-host';out.mkdir(parents=True,exist_ok=True);build.sources(out)
 for n in ('tx.h','tx.c'):(out/n).write_bytes((ROOT/n).read_bytes())
 assets=out/'fixture-assets';assets.mkdir(exist_ok=True)
 data=Path('/home/yuka/rabbit-world/native-wifi-qca9377-v1/vendor/firmware/ath10k/QCA9377/hw1.0/firmware-6.bin').read_bytes();policy=build.checked.policy();assert sha(data)==policy['digest']
 key=prior.old.Ed25519PrivateKey.from_private_bytes(bytes([97])*32);public=key.public_key().public_bytes(prior.old.Encoding.Raw,prior.old.PublicFormat.Raw)
 for i,p in enumerate(prior.old.packets(data,key,target=bytes.fromhex(policy['target']),generation=policy['generation'],target_type=policy['type'],target_version=policy['version'],kind=policy['kind'])):(assets/f'chunk-{i}.bin').write_bytes(p)
 p=out/'init_probe.c';owner='.owner={'+','.join(str(n) for n in bytes.fromhex(policy['owner']))+'}';p.write_text(build.one(p.read_text(),owner,'.owner={'+','.join(str(n) for n in public)+'}'))
 (out/'fixture.c').write_text(fixture((BASE/'init_probe_test.c').read_text()))
 inc=['-I'+str(n) for n in (out,BASE,build.checked.prior.actors.OLD,build.checked.prior.actors.NATIVE,BASE/'runs/firmware-chunks')]
 files=prior.old.prior.prior.FILES+('full_read.c','config_read.c','config_setup.c','bmi_transport.c','diag_ce.c','firmware_port.c','firmware_channel.c','firmware_gatt.c','firmware_chunks.c','bmi_loader.c','board_query.c','board_smbios.c','boot_image.c','boot_transport.c','boot_native.c','operating.c','startup.c','startup_gatt.c','init_transaction.c','init_wire.c','memory_plan.c','resources.c','available.c','htc_wire.c','htc_session.c','htc_credit.c','htc_control.c','wmi_boot_info.c','wmi_scan.c','persistent.c','lifecycle.c','rx.c','tx.c')
 crypto=[BASE/'runs/firmware-chunks'/n for n in ('monocypher.c','monocypher-ed25519.c')];exe=out/'test'
 subprocess.run([str(prior.old.CC),'-DQCA_CONFIG_SETUP=1','-DQCA_FC_BASE=13','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all',*inc,str(out/'fixture.c'),*[str(out/n) for n in files],str(build.checked.prior.actors.NATIVE/'sha256.c'),*map(str,crypto),'-o',str(exe)],check=True)
 log=''
 for scenario in range(16):
  r=subprocess.run([str(exe),'0',str(assets),'35','0','0','0',str(scenario)],capture_output=True,text=True,timeout=90,env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1'})
  log+=r.stdout+r.stderr;(out/'host.log').write_text(log)
  if r.returncode:raise RuntimeError(f'case{scenario}: {r.stdout[-1000:]}\n{r.stderr[-3000:]}')
 subprocess.run([str(prior.old.CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-DQCA_CONFIG_SETUP=1','-DQCA_FC_BASE=13',*inc,'-c',str(out/'tx.c'),'-o',str(out/'tx.obj')],check=True)
 inputs={str(p.relative_to(ROOT.parent.parent)):sha(p.read_bytes()) for d in (ROOT,RX,build.CHECKED,build.BRIDGE,build.prior.LIFE) for p in d.iterdir() if p.is_file()}
 report={'status':'SERIALIZED-WMI-CE3-SHARED-RX-CREDIT-ACTUAL-NATIVE-ASAN-COFF-PASS','scenarios':16,'source_sha256':inputs,'host_log_sha256':sha(log.encode()),'compiled_fixture_sources_sha256':{p.name:sha(p.read_bytes()) for p in [out/'fixture.c',*[out/n for n in files],*crypto]},'actual_native_entrypoints':True,'physical_verified':False,'signing_admitted':False,'firmware_ack_invented':False,'rf_permission_admitted':False,'model_only_runtime_command':True,'dma_refunds_credit':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
if __name__=='__main__':main()
