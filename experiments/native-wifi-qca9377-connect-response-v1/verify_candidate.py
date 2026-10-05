#!/usr/bin/env python3
"""Repeated full EFI and real supervisor/QEMU/city/GATT, not physical admission."""
import json,hashlib,shutil,time
from pathlib import Path
import operating_build as build
import verify_boot_profile,verify_init_profile
ROOT=build.ROOT
sha=lambda b:hashlib.sha256(b).hexdigest()
def fixture(source):
 s=verify_boot_profile.fixture(source)
 marker='say("BOOT SERVICE20..22 READ ONLY; RAM SERVICE PRESERVED; CITY RETAINED");'
 extra=r'''
 uint8_t op_service[7]={0x10,23,0,255,255,0,0x28};
 if(att(op_service,7,0x11)||diagnostic_reply_size!=22||diagnostic_reply[2]!=23||diagnostic_reply[4]!=25||diagnostic_reply[6]!=0x24)return 1;
 uint8_t op_status[3]={0x0a,25,0};if(att(op_status,3,0x0b)||diagnostic_reply_size!=209||!same(diagnostic_reply+1,(const uint8_t*)"QWOP0002",8))return 1;
 for(unsigned i=9;i<209;i++)if(diagnostic_reply[i])return 1;
 uint8_t op_write[4]={0x12,25,0,0};if(att(op_write,4,1)||diagnostic_reply_size!=5||diagnostic_reply[4]!=3)return 1;
 uint8_t op_blob[5]={0x0c,25,0,208,0};if(att(op_blob,5,0x0d)||diagnostic_reply_size!=1)return 1;
 op_blob[3]=209;if(att(op_blob,5,1)||diagnostic_reply_size!=5||diagnostic_reply[4]!=7)return 1;
 say("OPERATING SERVICE23..25 READ ONLY; ABSENT TARGET DOES NOT CLAIM SERVICE READY OR WIFI");
 '''+marker
 return build.one(s,marker,extra)
def main():
 out=ROOT/'runs/operating-profile';out.mkdir(parents=True,exist_ok=True)
 paths=[p for d in (build.BASE,build.SESSION) for p in d.iterdir() if p.is_file() and p.suffix in ('.c','.h','.py','.json')]+[p for p in ROOT.iterdir() if p.is_file()]
 inputs={str(p.relative_to(ROOT.parent.parent)):sha(p.read_bytes()) for p in paths}
 _,_,crypto=build.prior.actors.engine.prepare(out,bytes.fromhex('29acbae141bccaf0b22e1a94d34d0bc7361e526d0bfe12c89794bc9322966dd7'))
 payload=build.compile_driver(out,crypto);assert payload==build.compile_driver(out,crypto)
 (out/'candidate.efi').write_bytes(payload)
 for name in ('actors-qemu','actors-empty-boot-qemu'):
  old=out/name
  if old.exists():shutil.move(str(old),str(out/(name+'.previous-'+str(time.time_ns()))))
 gates=[verify_init_profile.prior.actors_gate.qemu_gate(out,payload,test_transform=fixture),verify_init_profile.prior.actors_gate.qemu_gate(out,payload,True,test_transform=fixture)]
 assert inputs=={n:sha((ROOT.parent.parent/n).read_bytes()) for n in inputs}
 response=ROOT/'runs/response-host/report.json';rr=json.loads(response.read_text());assert rr['status']=='ACTUAL-CONNECT-RESPONSE-PINNED-CORE-ASAN-COFF-PASS' and rr['checks']==5186
 for n,v in rr['source_sha256'].items():assert inputs[n]==v
 host=ROOT/'runs/operating-host/report.json';h=json.loads(host.read_text())
 assert h['status']=='NATIVE-OPERATING-CE-HANDSHAKE-SERVICE-READY-ASAN-COFF-PASS' and h['scenarios']==27
 for n,v in h['source_sha256'].items():assert inputs[n]==v
 report={'status':'OPERATING-CANDIDATE-TWO-REBUILDS-UEFI-QEMU-PASS','build_host':'yukabox','payload_sha256':sha(payload),'payload_bytes':len(payload),'source_sha256':inputs,'response_report_sha256':sha(response.read_bytes()),'operating_report_sha256':sha(host.read_bytes()),'initial_report_sha256':sha((ROOT/'runs/initial-host/report.json').read_bytes()),'receiver_policy':build.policy(),'receiver_policy_sha256':sha((ROOT/'receiver-policy.json').read_bytes()),'gates':gates,'physical_signing_admitted':False,'physical_verified':False,'current_world_reproduction_checked':False,'scan':False,'wifi_connected':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],len(payload),sha(payload))
if __name__=='__main__':main()
