"""Pinned actual-C semantic bridge, synthetic evidence never physical admission."""
from pathlib import Path
import json,hashlib,importlib.util,sys
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent.parent;ORACLE=REPO/'experiments/native-wifi-qca9377-native64-host-oracle-v1/evidence/2026-10-09'
REPORT='7d688aee27bab84090b0164536f1a1fa605310ce70df18de5faa6d6d7e3f41d2'
CAPTURES={0:'2f020ea5f883d735d3133665b4612d457b85200c2b6b42fa7066b79c92f7ba52',4:'3add47aeec4eb8ca73b57e6aaf9d5b44902b9cb9cb9904de5c77c657872db85b',8:'aa8319914ac0d3a1adc9ce3f5f5429047ecff99f8f8583b00cf53b28065d0171',9:'cc0bb70cee58e8ecc2e8c7fd46e129479b68299f02a2425bf5cfdba0f72785f9',2:'94b1bc577ceaea9b11a80d6a4e0349e01c106607e17f6bd5d3f8a936e07f48e9'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
 if not v:raise ValueError(m)
def checked():
 need(sha(ORACLE/'report.json')==REPORT,'actual-C oracle report changed');r=json.loads((ORACLE/'report.json').read_text());need(r['native_report_sha256']=='1689fc687e78f23c752be7dd35a8b14e8c8ea6fa3e4f24ec7cabe3ac58bac86c' and r['native_payload_sha256']=='d40efd8c0b08a9289f0caaa64d931519a253559c53ef732af8961ed91ad49965','actual producer64 identity')
 producer=REPO/'experiments/native-wifi-qca9377-filter64-native-v1/runs/native-host'
 for n,h in r['unchanged_production_inputs_sha256'].items():
  p=Path(n);need(not p.is_absolute() and '..' not in p.parts,'unsafe input');need(sha(producer/p)==h,'actual native oracle input changed')
 scope=REPO/'experiments/native-wifi-qca9377-filter64-observer-v1';proof=json.loads((scope/'evidence/host-proof.json').read_text())
 for n in ('decode_filter.py','scan_decode.py','htc_codec.py'):need(sha(scope/n)==proof['source_sha256'][n],'frozen decoder input changed')
 saved={n:sys.modules.get(n) for n in ('scan_decode','htc_codec')};paths=list(sys.path)
 try:
  sys.path.insert(0,str(scope));
  for n in saved:sys.modules.pop(n,None)
  spec=importlib.util.spec_from_file_location('_owned64_oracle_decode',scope/'decode_filter.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d);cases=[]
  for case,h in CAPTURES.items():
   p=ORACLE/f'capture-scan0-filter{case}.json';need(sha(p)==h,'capture changed');c=json.loads(p.read_text());need(c['fixture_kind']=='synthetic-actual-C-producer','synthetic label missing');got=d.decode_capture(c);need(got['pipeline_completed']==got['target_observed']==got['owned_filter_version_verified']==(case in (0,4,8)),'wrong actualC success/failure meaning');cases.append({'case':case,'capture_sha256':h,'pipeline_completed':got['pipeline_completed'],'target_observed':got['target_observed'],'timing':got['pipeline']['timing'],'physical':False})
 finally:
  sys.path[:]=paths
  for n,value in saved.items():
   if value is None:sys.modules.pop(n,None)
   else:sys.modules[n]=value
 return {'status':'FROZEN64-ACTUAL-C-TIMING-SEMANTIC-ORACLE-GATE-PASS','report_sha256':REPORT,'cases':cases,'physical_admission':False,'device_operations':0}
if __name__=='__main__':print(json.dumps(checked(),indent=2))
