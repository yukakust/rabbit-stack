#!/usr/bin/env python3
"""Actual bounded whole native owner/RX trial model; Yukabox only."""
import sys,importlib.util,subprocess,json,hashlib,os
from pathlib import Path
import profile_build as build
spec=importlib.util.spec_from_file_location('reviewed_rx_verify',build.RX/'verify_native.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
ROOT=build.ROOT;BASE=build.checked.BASE;sha=lambda b:hashlib.sha256(b).hexdigest()
def fixture(text):
 s=prior.fixture(text)
 s='#include <stddef.h>\n#include "trial.h"\nvoid qca_profile_status(uint8_t[192]);\nsize_t qca_profile_att(uint16_t,const uint8_t*,size_t,uint8_t*,size_t);\nconst QcaBoundedTrial*qca_profile_trial_view(void);\n'+s
 s=build.one(s,'static unsigned rx_scenario;','static unsigned rx_scenario;static unsigned trial_fault;')
 s=build.one(s,'assert(argc==7);rx_scenario=', 'assert(argc==8);trial_fault=(unsigned)atoi(argv[7]);assert(trial_fault<=2);rx_scenario=')
 s=build.one(s,'if(active_ticks==200){','if(active_ticks==200&&persistent_fault){')
 s=build.one(s,'if(active_ticks==20&&rx_scenario){', '''if(active_ticks==200&&trial_fault==1)((QcaBoundedTrial*)qca_profile_trial_view())->last=UINT64_MAX;
   if(active_ticks==200&&trial_fault==2)((QcaBoundedTrial*)qca_profile_trial_view())->started=0;
   if(active_ticks==20&&rx_scenario){''')
 s=build.one(s,'assert(active_ticks==200||(rx_scenario>=3&&rx_scenario<=9)||rx_scenario==12||rx_scenario==13);',
  'assert(active_ticks>=200||(rx_scenario>=3&&rx_scenario<=9)||rx_scenario==12||rx_scenario==13);')
 # Timer is the normal stop requester; no manually fabricated closure.
 s=build.one(s,'assert(stopped&&p->life.phase==QCA_RADIO_CLOSED&&qca_persistent_unload_safe(p));',
  'assert(p->life.phase==QCA_RADIO_CLOSED&&qca_persistent_unload_safe(p));')
 marker=' fprintf(stderr,"PERSISTENT_FINAL'
 start=s.index(marker)
 s=s[:start]+r'''
 { tick(60001);uint8_t status[192];qca_profile_status(status);
 assert(!memcmp(status,"QWRX0001",8)&&status[24]==1&&status[184]==53);
 assert(status[20]==1); /* checked stop requested */
 if(!persistent_fault&&!rx_scenario&&!trial_fault){assert(status[8]==QCA_TRIAL_DONE&&!status[12]&&status[16]==1&&active_ticks>=10000);}
 if(trial_fault==1)assert(status[8]==QCA_TRIAL_FAULT&&status[12]==1&&!status[16]);
 if(trial_fault==2)assert(status[8]==QCA_TRIAL_DONE&&!status[12]&&status[16]);
 uint8_t request[7]={0x10,29,0,255,255,0,0x28},reply[247];
 assert(qca_profile_att(247,request,7,reply,sizeof(reply))==22&&reply[2]==29&&reply[4]==31&&reply[6]==0x28);
 request[0]=0x0a;request[1]=31;
 assert(qca_profile_att(247,request,3,reply,sizeof(reply))==193&&!memcmp(reply+1,status,192));
 request[0]=0x12;assert(qca_profile_att(247,request,3,reply,sizeof(reply))==5&&reply[4]==3);
 request[0]=0x52;assert(!qca_profile_att(247,request,3,reply,sizeof(reply)));
 request[0]=0x0c;request[3]=192;request[4]=0;assert(qca_profile_att(247,request,5,reply,sizeof(reply))==1);
 request[3]=193;assert(qca_profile_att(247,request,5,reply,sizeof(reply))==5&&reply[4]==7); }
'''+s[start:]
 # Standalone RX suite intentionally clears its FIFO after owner release; the
 # status still shows real completion counts and zero actual owner inventory.
 return s
def main():
 if sys.platform!='linux':raise SystemExit('Yukabox only')
 out=ROOT/'runs/native-host';out.mkdir(parents=True,exist_ok=True);build.sources(out)
 assets=out/'fixture-assets';assets.mkdir(exist_ok=True)
 data=Path('/home/yuka/rabbit-world/native-wifi-qca9377-v1/vendor/firmware/ath10k/QCA9377/hw1.0/firmware-6.bin').read_bytes();policy=build.policy();assert sha(data)==policy['digest']
 key=prior.old.Ed25519PrivateKey.from_private_bytes(bytes([97])*32);public=key.public_key().public_bytes(prior.old.Encoding.Raw,prior.old.PublicFormat.Raw)
 for i,p in enumerate(prior.old.packets(data,key,target=bytes.fromhex(policy['target']),generation=policy['generation'],target_type=policy['type'],target_version=policy['version'],kind=policy['kind'])):(assets/f'chunk-{i}.bin').write_bytes(p)
 p=out/'init_probe.c';owner='.owner={'+','.join(str(n) for n in bytes.fromhex(policy['owner']))+'}'
 p.write_text(build.one(p.read_text(),owner,'.owner={'+','.join(str(n) for n in public)+'}')+'\nconst QcaBoundedTrial*qca_profile_trial_view(void){return &trial;}\n')
 (out/'fixture.c').write_text(fixture((BASE/'init_probe_test.c').read_text()))
 inc=['-I'+str(n) for n in (out,BASE,build.checked.prior.actors.OLD,build.checked.prior.actors.NATIVE,BASE/'runs/firmware-chunks')]
 # Match reviewed actual native entrypoint source set, plus timer/diagnostic.
 files=prior.old.prior.prior.FILES+('full_read.c','config_read.c','config_setup.c','bmi_transport.c','diag_ce.c','firmware_port.c','firmware_channel.c','firmware_gatt.c','firmware_chunks.c','bmi_loader.c','board_query.c','board_smbios.c','boot_image.c','boot_transport.c','boot_native.c','operating.c','startup.c','startup_gatt.c','init_transaction.c','init_wire.c','memory_plan.c','resources.c','available.c','htc_wire.c','htc_session.c','htc_credit.c','htc_control.c','wmi_boot_info.c','wmi_scan.c','persistent.c','lifecycle.c','rx.c','trial.c','profile_gatt.c')
 crypto=[BASE/'runs/firmware-chunks'/n for n in ('monocypher.c','monocypher-ed25519.c')];exe=out/'test'
 subprocess.run([str(prior.old.CC),'-DQCA_CONFIG_SETUP=1','-DQCA_FC_BASE=13','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all',*inc,str(out/'fixture.c'),*[str(out/n) for n in files],str(build.checked.prior.actors.NATIVE/'sha256.c'),*map(str,crypto),'-o',str(exe)],check=True)
 cases=[(s,0,0,0) for s in (0,1,15,22)]+[(0,f,0,0) for f in range(1,6)]+[(1 if r in (2,5,10) else 0,0,r,0) for r in range(1,14)]+[(0,0,0,f) for f in (1,2)]
 log=''
 for startup,pf,rx,tf in cases:
  r=subprocess.run([str(exe),'0',str(assets),'35',str(startup),str(pf),str(rx),str(tf)],capture_output=True,text=True,timeout=90,env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1'})
  log+=r.stdout+r.stderr;(out/'host.log').write_text(log)
  if r.returncode:raise RuntimeError(f'case{startup}/{pf}/{rx}/{tf}: {r.stdout[-1000:]}\n{r.stderr[-3000:]}')
 for n in ('trial','profile_gatt','init_probe'):
  subprocess.run([str(prior.old.CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-DQCA_CONFIG_SETUP=1','-DQCA_FC_BASE=13',*inc,'-c',str(out/(n+'.c')),'-o',str(out/(n+'.obj'))],check=True)
 inputs={str(p.relative_to(ROOT.parent.parent)):sha(p.read_bytes()) for d in (ROOT,build.RX,build.checked.ROOT,build.rx.BRIDGE,build.rx.prior.LIFE) for p in d.glob('*') if p.is_file()}
 report={'status':'BOUNDED-PERSISTENT-PROFILE-NATIVE-ASAN-COFF-PASS','scenarios':len(cases),'source_sha256':inputs,'host_log_sha256':sha(log.encode()),'compiled_fixture_sources_sha256':{p.name:sha(p.read_bytes()) for p in [out/'fixture.c',*[out/n for n in files],*crypto]},'physical_verified':False,'signing_admitted':False,'actual_native_entrypoints':True,'bounded_us':10000000,'generation':53,'rf_transmit':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
if __name__=='__main__':main()
