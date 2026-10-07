"""Production native55 loop and authenticated container IE6; host-only."""
import importlib.util,sys,subprocess,hashlib,json,os
from pathlib import Path
import profile_build as build
ROOT=build.ROOT;BASE=build.checked.BASE
spec=importlib.util.spec_from_file_location('reviewed_htt_verify',build.NATIVE/'verify_native.py');prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
sha=lambda b:hashlib.sha256(b).hexdigest()
def fixture(text):
 s=prior.fixture(text)
 s='#include "htt_native.h"\n#include "firmware_op.h"\nconst QcaHttNative*qca_htt_native_view(void);\nconst QcaHttFirmwareProof*qca_htt_firmware_view(void);\nvoid qca_htt_status(uint8_t[320]);\nunsigned qca_htt_profile_export(unsigned,uint8_t*,unsigned);\nsize_t qca_htt_profile_att(uint16_t,const uint8_t*,size_t,uint8_t*,size_t);\n#define query (*((QcaHttNative*)qca_htt_native_view()))\nstatic unsigned htt_stale_injected,htt_response_delivered;static void deliver_htt(unsigned);\n'+s
 s=build.one(s,'static QcaHttNative query,rival;','static QcaHttNative rival;')
 s=build.one(s,'htt_scenario<=20','htt_scenario<=23')
 start=s.index('   if(active_ticks==10){');end=s.index('   if(htt_started&&!query.stop_requested){',start)
 s=s[:start]+'   htt_started=1;\n   if(query.attempted)assert(!qca_htt_native_begin(&rival,(QcaPersistentNative*)p,3,ms*1000));\n'+s[end:]
 old='    int rc=qca_htt_native_poll(&query,htt_scenario==17&&active_ticks==12?ms*1000-2000:ms*1000);\n    (void)rc;'
 s=build.one(s,old,'    /* Actual production qca_poll services the owner, not this fixture. */')
 s=build.one(s,'if(active_ticks==12&&htt_scenario!=15&&htt_scenario!=14){deliver_htt(htt_scenario);}', 'if(active_ticks>=12&&!htt_response_delivered&&htt_scenario!=15&&htt_scenario!=14&&p->rx.posted[0]){htt_response_delivered=1;deliver_htt(htt_scenario);}')
 # Actual CE1 completion exists before production request publication.
 pos=s.index('static Status EFIAPI mem_read(');brace=s.index('{',pos)+1
 s=s[:brace]+r'''
 if(htt_scenario==12&&!htt_stale_injected&&!query.attempted&&off==0x34848&&qca_persistent_view()->life.phase==QCA_RADIO_ACTIVE){htt_stale_injected=1;deliver_htt(0);}
'''+s[brace:]
 # Corrupt only the model's authenticated pinned RAM after INIT publication.
 marker='  if(main_done&&qca_persistent_view()->life.phase==QCA_RADIO_ACTIVE&&id==4&&index==0x3c&&query.attempted){'
 s=build.one(s,marker,r'''
  if(main_done&&id==3&&index==0x3c&&htt_scenario>=21){
   const QcaBootNative*b=qca_boot_view();QcaFirmwareChunks*a=b->asset;
   if(htt_scenario==21)a->memory[0]^=1;
   if(htt_scenario==22){for(unsigned at=12;at<a->policy.total;){unsigned tag=getle(a->memory+at),n=getle(a->memory+at+4);at+=8;if(tag==6){a->memory[at]^=1;break;}at+=(n+3)&~3u;}}
   if(htt_scenario==23)((QcaBootNative*)b)->plan.assets.main++;
  }
'''+marker)
 # Local 32bit reader avoids relying on an invented firmware parser callback.
 s=s.replace('static unsigned htt_stale_injected,htt_response_delivered;static void deliver_htt(unsigned);','static unsigned htt_stale_injected,htt_response_delivered;static void deliver_htt(unsigned);static unsigned getle(const uint8_t*p){return p[0]|((unsigned)p[1]<<8)|((unsigned)p[2]<<16)|((unsigned)p[3]<<24);}')
 s=build.one(s,'  tick(ms);const QcaBootNative*b=qca_boot_view();','  if(htt_scenario==17&&active_ticks==12)tick(ms-2);else tick(ms);const QcaBootNative*b=qca_boot_view();')
 s=build.one(s,'assert(htt_started&&active_ticks>=10);','assert(query.attempted==1||htt_scenario>=21);')
 s=build.one(s,'assert(query.stop_requested&&htt_posts==1&&query.attempted==1);','assert(query.stop_requested&&htt_posts==(htt_scenario>=21?0u:1u)&&query.attempted==(htt_scenario>=21?0u:1u));')
 s=build.one(s,'if(htt_scenario==18)assert(query.error==4);','if(htt_scenario==18)assert(query.error==4);\n if(htt_scenario>=21)assert(query.error==30&&!qca_htt_firmware_view()->valid);')
 # Production handles the once-stop and genuine closure itself; no synthetic
 # firmware proof/READY or direct begin call in fixture.
 marker=' printf("HTT_NATIVE scenario='
 check=r'''
 {
  uint8_t status[320],request[7]={0x10,29,0,255,255,0,0x28},reply[247],page[512],again[512];
  qca_htt_status(status);assert(!memcmp(status,"QHTT0001",8)&&getle(status+224)==55&&getle(status+24)==1);
  assert(getle(status+8)==query.phase&&getle(status+12)==query.error);
  if(htt_scenario<21){assert(qca_htt_firmware_view()->valid&&getle(status+80)==3&&getle(status+100)==55);}
  else assert(qca_htt_firmware_view()->error==(htt_scenario==23?8u:2u));
  assert(qca_htt_profile_att(247,request,7,reply,sizeof(reply))==22&&reply[2]==29&&reply[4]==31&&reply[6]==0x2e);
  request[0]=0x0a;request[1]=31;assert(qca_htt_profile_att(247,request,3,reply,sizeof(reply))==247&&!memcmp(reply+1,status,246));
  request[0]=0x0c;request[3]=246;request[4]=0;assert(qca_htt_profile_att(247,request,5,reply,sizeof(reply))==75&&!memcmp(reply+1,status+246,74));
  request[3]=65;request[4]=1;assert(qca_htt_profile_att(247,request,5,reply,sizeof(reply))==5&&reply[4]==7);
  for(unsigned index=0;index<30;index++){
   unsigned n=qca_htt_profile_export(index,page,sizeof(page));assert(n==((index%5)==4?56:512));
   assert(qca_htt_profile_export(index,again,sizeof(again))==n&&!memcmp(page,again,n));
   assert(!qca_htt_profile_export(index,again,511));
   request[0]=0x0a;request[1]=(uint8_t)(34+2*index);request[2]=0;
   assert(qca_htt_profile_att(247,request,3,reply,sizeof(reply))==(n>246?247:n+1)&&!memcmp(reply+1,page,n>246?246:n));
   request[0]=0x12;assert(qca_htt_profile_att(247,request,3,reply,sizeof(reply))==5&&reply[4]==3);
   request[0]=0x52;assert(!qca_htt_profile_att(247,request,3,reply,sizeof(reply)));
   for(unsigned offset=0;offset<n;offset+=246){request[0]=0x0c;request[3]=(uint8_t)offset;request[4]=(uint8_t)(offset>>8);unsigned take=n-offset;if(take>246)take=246;
    assert(qca_htt_profile_att(247,request,5,reply,sizeof(reply))==take+1&&!memcmp(reply+1,page+offset,take));}
  }
  assert(!qca_htt_profile_export(30,page,sizeof(page)));
 }
'''+marker
 s=build.one(s,marker,check)
 return s
def main():
 if sys.platform!='linux':raise SystemExit('Yukabox-only C checks')
 out=ROOT/'runs/native-host';out.mkdir(parents=True,exist_ok=True);build.sources(out)
 assets=out/'fixture-assets';assets.mkdir(exist_ok=True)
 data=Path('/home/yuka/rabbit-world/native-wifi-qca9377-v1/vendor/firmware/ath10k/QCA9377/hw1.0/firmware-6.bin').read_bytes();policy=build.policy();assert sha(data)==policy['digest']
 key=prior.prior.old.Ed25519PrivateKey.from_private_bytes(bytes([97])*32);public=key.public_key().public_bytes(prior.prior.old.Encoding.Raw,prior.prior.old.PublicFormat.Raw)
 for i,p in enumerate(prior.prior.old.packets(data,key,target=bytes.fromhex(policy['target']),generation=policy['generation'],target_type=policy['type'],target_version=policy['version'],kind=policy['kind'])):(assets/f'chunk-{i}.bin').write_bytes(p)
 p=out/'init_probe.c';owner='.owner={'+','.join(str(n) for n in bytes.fromhex(policy['owner']))+'}';p.write_text(build.one(p.read_text(),owner,'.owner={'+','.join(str(n) for n in public)+'}'))
 (out/'fixture.c').write_text(fixture((BASE/'init_probe_test.c').read_text()))
 inc=['-I'+str(n) for n in (out,BASE,build.checked.prior.actors.OLD,build.checked.prior.actors.NATIVE,BASE/'runs/firmware-chunks')]
 files=prior.prior.old.prior.prior.FILES+('full_read.c','config_read.c','config_setup.c','bmi_transport.c','diag_ce.c','firmware_port.c','firmware_channel.c','firmware_gatt.c','firmware_chunks.c','bmi_loader.c','board_query.c','board_smbios.c','boot_image.c','boot_transport.c','boot_native.c','operating.c','startup.c','startup_gatt.c','init_transaction.c','init_wire.c','memory_plan.c','resources.c','available.c','htc_wire.c','htc_session.c','htc_credit.c','htc_control.c','wmi_boot_info.c','wmi_scan.c','persistent.c','lifecycle.c','rx.c','version.c','htt_native.c','firmware_op.c','profile_gatt.c')
 crypto=[BASE/'runs/firmware-chunks'/n for n in ('monocypher.c','monocypher-ed25519.c')];exe=out/'test'
 input_paths=[p for d in (ROOT,build.NATIVE,build.native.RX,build.native.VERSION,build.native.CHECKED,build.native.BRIDGE,build.native.prior.prior.LIFE) for p in d.iterdir() if p.is_file()]
 frozen_inputs={str(p.relative_to(ROOT.parent.parent)):sha(p.read_bytes()) for p in input_paths}
 compiled_paths=[out/'fixture.c',*[out/n for n in files],*out.glob('*.h'),*crypto,*[BASE/'runs/firmware-chunks'/n for n in ('monocypher.h','monocypher-ed25519.h')],build.checked.prior.actors.NATIVE/'sha256.c']
 compiled_hashes={p.name:sha(p.read_bytes()) for p in compiled_paths}
 subprocess.run([str(prior.prior.old.CC),'-DQCA_CONFIG_SETUP=1','-DQCA_FC_BASE=13','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all',*inc,str(out/'fixture.c'),*[str(out/n) for n in files],str(build.checked.prior.actors.NATIVE/'sha256.c'),*map(str,crypto),'-o',str(exe)],check=True)
 log=''
 for scenario in range(24):
  r=subprocess.run([str(exe),'0',str(assets),'35','1' if scenario==10 else '0','0','0',str(scenario)],capture_output=True,text=True,timeout=90,env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1'})
  log+=r.stdout+r.stderr;(out/'host.log').write_text(log)
  if r.returncode:raise RuntimeError(f'case{scenario}: {r.stdout[-1000:]}\n{r.stderr[-3000:]}')
 for name in ['htt_native','rx','version','firmware_op','profile_gatt','init_probe']:
  subprocess.run([str(prior.prior.old.CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-DQCA_CONFIG_SETUP=1','-DQCA_FC_BASE=13',*inc,'-c',str(out/(name+'.c')),'-o',str(out/(name+'.obj'))],check=True)
 inputs={str(p.relative_to(ROOT.parent.parent)):sha(p.read_bytes()) for p in input_paths};assert inputs==frozen_inputs
 assert compiled_hashes=={p.name:sha(p.read_bytes()) for p in compiled_paths}
 report={'status':'HTT55-PRODUCTION-AUTHENTICATED-IE6-RAW-EXPORT-ACTUAL-NATIVE-ASAN-COFF-PASS','scenarios':24,'build_host':'yukabox','source_sha256':inputs,'host_log_sha256':sha(log.encode()),'compiled_fixture_sources_sha256':compiled_hashes,'actual_native_entrypoints':True,'physical_verified':False,'signing_admitted':False,'whole_efi_candidate':False,'request_is_rf':False,'native_version_query_implemented':True,'production_loop':True,'authenticated_firmware_ie6':True,'htt_dataplane_ready':False,'wmi_credit_debit_for_htt':False,'duplicate_ce1_owner':False,'retained_export_slots':6}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
if __name__=='__main__':main()
