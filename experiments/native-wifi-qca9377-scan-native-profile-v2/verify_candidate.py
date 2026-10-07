"""Repeated full scan54 EFI/QEMU/world17 proof; no RF/hardware admission."""
import importlib.util,json,hashlib,sys
from pathlib import Path
import scan_build as build
ROOT=build.ROOT;REPO=ROOT.parent.parent
spec=importlib.util.spec_from_file_location('checked_profile_candidate',build.PROFILE/'verify_candidate.py')
parent=importlib.util.module_from_spec(spec);spec.loader.exec_module(parent)
base_fixture=parent.fixture
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def fixture(text):
 s=base_fixture(text).replace('i==185?53:0','i==185?55:0')
 marker='say("BOUNDED RX SERVICE29..31 READ ONLY; ABSENT RADIO CLAIMS NO READY OR ACTIVE OWNERS");'
 d=json.loads((REPO/'experiments/native-wifi-qca9377-regulatory-policy-v1/evidence/2026-10-07/policy-proposal.json').read_text())
 body=r'''
 uint8_t scan_service[7]={0x10,32,0,255,255,0,0x28};
 if(att(scan_service,7,0x11)||diagnostic_reply_size!=22||diagnostic_reply[2]!=32||diagnostic_reply[4]!=34||diagnostic_reply[6]!=0x2a)return 1;
 uint8_t scan_read[3]={10,34,0};if(att(scan_read,3,11)||diagnostic_reply_size!=247||!same(diagnostic_reply+1,(const uint8_t*)"QSCN0001",8))return 1;
 for(unsigned i=9;i<247;i++)if(diagnostic_reply[i])return 1;
 uint8_t scan_blob[5]={12,34,0,246,0};if(att(scan_blob,5,13)||diagnostic_reply_size!=171)return 1;
 if(diagnostic_reply[3]!=55||diagnostic_reply[7]!=13)return 1;
 static const uint8_t policy_refs[96]={POLICY_BYTES};
 if(!same(diagnostic_reply+19,policy_refs,96))return 1;
 scan_blob[3]=160;scan_blob[4]=1;if(att(scan_blob,5,13)||diagnostic_reply_size!=1)return 1;
 scan_blob[3]++;if(att(scan_blob,5,1)||diagnostic_reply_size!=5||diagnostic_reply[4]!=7)return 1;
 uint8_t scan_write[4]={0x12,34,0,0};if(att(scan_write,4,1)||diagnostic_reply_size!=5||diagnostic_reply[4]!=3)return 1;
 uint8_t export_read[3]={10,37,0};if(att(export_read,3,11)||diagnostic_reply_size!=247||!same(diagnostic_reply+1,(const uint8_t*)"QEXP0001",8))return 1;
 for(unsigned i=9;i<247;i++)if(diagnostic_reply[i])return 1;
 uint8_t export_blob[5]={12,37,0,0,2};if(att(export_blob,5,13)||diagnostic_reply_size!=1)return 1;
 export_blob[3]=1;if(att(export_blob,5,1)||diagnostic_reply_size!=5||diagnostic_reply[4]!=7)return 1;
 for(unsigned slot=0;slot<22;slot++){export_read[1]=(uint8_t)(37+10*slot);
  if(att(export_read,3,11)||diagnostic_reply_size!=247||!same(diagnostic_reply+1,(const uint8_t*)"QEXP0001",8)||diagnostic_reply[9]!=slot)return 1;
  for(unsigned j=10;j<247;j++)if(diagnostic_reply[j])return 1;
  for(unsigned page=1;page<5;page++){export_read[1]=(uint8_t)(37+10*slot+2*page);
   if(att(export_read,3,11)||diagnostic_reply_size!=(page==4?37u:247u))return 1;
   for(unsigned j=1;j<diagnostic_reply_size;j++)if(diagnostic_reply[j])return 1;
  }
 }
 say("SCAN55 STATUS32..34 AND OWNED EXPORT35..255 READ ONLY; ABSENT RADIO NO RF CLAIMS");
'''
 digest=bytes.fromhex(hashlib.sha256((REPO/'experiments/native-wifi-qca9377-regulatory-policy-v1/evidence/2026-10-07/policy-proposal.json').read_bytes()).hexdigest()+d['ruleset_signed_db_sha256']+d['location_sha256'])
 body=body.replace('POLICY_BYTES',','.join(str(n) for n in digest))
 return build.one(s,marker,body+marker)
def main():
 # Reuse frozen profile's whole-driver baseline closure and exact QEMU/world
 # execution while substituting ONLY isolated54 build/fixture. Then add every
 # new compiler unit/header and authenticated policy proof to closure.
 # Accept OUR actual-native proof status, not the old timer-only proof.
 text=(build.PROFILE/'verify_candidate.py').read_text().replace("'BOUNDED-PERSISTENT-PROFILE-NATIVE-ASAN-COFF-PASS'","'SCAN55-ACTUAL-PHYSICAL54-REGRESSION-PREFIX28-ARCHIVE16-ASAN-COFF-PASS'")
 text=text.replace('/home/yuka/rabbit-world/parallel-persistent-profile-v1/world.rup','/home/yuka/rabbit-world/parallel-scan-native-profile-v2/world.rup')
 text=text.replace('build.rx.prior.LIFE,ROOT)','build.rx.prior.LIFE,build.PREVIOUS,build.EVENT,build.PROFILE,*[build.E/f for f in build.MODULES.values()],ROOT)')
 exec(compile(text,str(build.PROFILE/'verify_candidate.py'),'exec'),parent.__dict__)
 saved_build=parent.build;parent.ROOT=ROOT;parent.build=build;parent.fixture=fixture
 build.RX=build.prior.prior.RX;build.rx=build.prior.prior.rx
 try:parent.main()
 finally:parent.build=saved_build
 out=ROOT/'runs/checked-candidate';p=out/'report.json';r=json.loads(p.read_text())
 closure=r['source_sha256']
 for folder in build.MODULES.values():
  for f in (build.E/folder).iterdir():
   if f.is_file():closure[str(f.relative_to(REPO))]=sha(f)
 for f in (build.EVENT).iterdir():
  if f.is_file():closure[str(f.relative_to(REPO))]=sha(f)
 for f in build.PREVIOUS.iterdir():
  if f.is_file():closure[str(f.relative_to(REPO))]=sha(f)
 for f in ROOT.iterdir():
  if f.is_file():closure[str(f.relative_to(REPO))]=sha(f)
 proofs=[ROOT/'runs/policy-binding/binding.json',ROOT/'runs/policy-binding/report.json',ROOT/'runs/policy-binding/host.log',ROOT/'runs/policy-binding/policy-proposal.json']
 for f in proofs:closure[str(f.relative_to(REPO))]=sha(f)
 evidence=build.E/'native-wifi-qca9377-regulatory-policy-v1/evidence/2026-10-07'
 for f in evidence.iterdir():
  if f.is_file():closure[str(f.relative_to(REPO))]=sha(f)
 model=json.loads((ROOT/'runs/native-host/report.json').read_text())
 for n,h in model['source_sha256'].items():assert closure[n]==h
 r['status']='SCAN55-REPEATED-FULL-EFI-QEMU-WORLD17-OWNED-EXPORT-PASS'
 r['source_sha256']=closure;r['rf_admission_granted']=False;r['signing_admitted']=False;r['physical_verified']=False
 r['raw_slots']=22;r['raw_pages']=110;r['bounded_us']=25000000;r['authenticated_policy_binding_sha256']=sha(proofs[0]);r['actual_native_model_scenarios']=model['scenarios'];r['physicalSSID_discovery']=False
 r.pop('rf_transmit',None);r['rf_operation_candidate']=True;r['probe_absence_physically_verified']=False
 p.write_text(json.dumps(r,indent=2)+'\n');print(r['status'],r['payload_bytes'],r['payload_sha256'],len(closure))
if __name__=='__main__':main()
