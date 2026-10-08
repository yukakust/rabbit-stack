"""Pure host read-only review; temporary tampered reports are never hardware evidence."""
import pathlib,hashlib,json,importlib.util,sys,copy,tempfile,shutil,struct
ROOT=pathlib.Path(__file__).resolve().parent;REPO=ROOT.parents[1]
NATIVE=REPO/'experiments/native-wifi-qca9377-htt62-native-v1';OBSERVER=REPO/'experiments/native-wifi-qca9377-htt62-observer-v1'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
sys.path.insert(0,str(OBSERVER));d=module('review_frozen_htt_decode',OBSERVER/'decode_htt.py');sys.modules['decode_htt']=d;f=module('review_frozen_htt_fixture',OBSERVER/'fixtures.py');gate=module('review_frozen_technical_gate',NATIVE/'checks/admission_gate.py')
def main():
 out=ROOT/'evidence';out.mkdir(exist_ok=True);runs=ROOT/'runs';runs.mkdir(exist_ok=True);findings=[];g=gate.check();findings.append({'case':'actual_technical_gate','result':g['status'],'physical_admission':g['physical_admission']})
 for major in (2,3):
  raw=f.capture(major);assert d.decode_capture(raw,f.CONTAINER.read_bytes())['version_only_pass']
  pages=[bytes.fromhex(x) for x in raw['pages_hex'][0]];record=bytearray(b''.join(pages[:5]));assert struct.unpack_from('<I',record,48)[0]==int.from_bytes(bytes([0,1,major,0]),'little');struct.pack_into('<I',record,48,0)
  pages[:5]=[bytes(record[i:i+512]) for i in range(0,2104,512)];raw['pages_hex']=[[p.hex() for p in pages]]*2
  try:d.decode_capture(raw,f.CONTAINER.read_bytes())
  except ValueError as e:assert str(e)=='HTC raw metadata join';findings.append({'case':'actual_production_HTT_event0_major'+str(major),'unexpected_rejection':str(e),'fixture_inconsistency_reproduced':True})
  else:raise AssertionError('expected frozen decoder mismatch')
 baseline=NATIVE/'runs/checked-candidate';negative=[];gaps=[]
 with tempfile.TemporaryDirectory(dir=runs) as td:
  staged=pathlib.Path(td)/'candidate';shutil.copytree(baseline,staged);original=json.loads((staged/'report.json').read_text());rep0=(staged/'reproduction.json').read_bytes()
  mutations=[('generation',lambda r:r.update(native_counter=61)),('world',lambda r:r.update(world_package_sha256='00'*32)),('physical_fixture',lambda r:r.update(physical_verified=True)),('signing',lambda r:r.update(signing_admitted=True)),('payload',lambda r:r.update(payload_sha256='00'*32)),('source',lambda r:r['source_sha256'].update({next(iter(r['source_sha256'])):'00'*32})),('generated',lambda r:r['generated_compiler_sources_sha256'].update({next(iter(r['generated_compiler_sources_sha256'])):'00'*32}))]
  for name,mutate in mutations:
   r=copy.deepcopy(original);mutate(r);(staged/'report.json').write_text(json.dumps(r));
   try:gate.check(staged)
   except (AssertionError,ValueError,KeyError):negative.append(name)
   else:raise AssertionError('corruption accepted:'+name)
  # These demonstrate why this technical checker MUST sit behind an exact frozen-report digest gate.
  for name in ['receiver_policy_kind_mismatch','duplicate_normal_QEMU','empty_source_manifest']:
   r=copy.deepcopy(original);(staged/'reproduction.json').write_bytes(rep0)
   if name=='receiver_policy_kind_mismatch':r['receiver_policy']['kind']=99
   elif name=='duplicate_normal_QEMU':r['gates']=[r['gates'][0],r['gates'][0]]
   else:
    r['source_sha256']={};rep=json.loads(rep0);rep['inputs']={};(staged/'reproduction.json').write_text(json.dumps(rep));r['reproduction_sha256']=h(staged/'reproduction.json')
   (staged/'report.json').write_text(json.dumps(r));gate.check(staged);gaps.append({'mutation':name,'technical_gate_accepts':True,'outer_exact_report_hash_required':True,'physical_admission':False})
 report={'status':'READ-ONLY-HTT62-REVIEW-OBSERVER-MISMATCH-REPRODUCED','source_sha256':{str(p.relative_to(REPO)):h(p) for p in [ROOT/'test_review.py',NATIVE/'checks/admission_gate.py',NATIVE/'htt_build.py',NATIVE/'components/rx.c',NATIVE/'components/htt_native.c',NATIVE/'components/version.c',NATIVE/'components/lifecycle.c',OBSERVER/'decode_htt.py',OBSERVER/'fixtures.py']},'candidate_report_sha256':h(baseline/'report.json'),'candidate_payload_sha256':original['payload_sha256'],'checks':findings,'rejected_corruptions':negative,'technical_checker_limits':gaps,'physical_admission':False,'device_operations':0,'credential_reads':0,'native_edits':0}
 (out/'test-report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],'negative',len(negative),'knownlimits',len(gaps));print('REPORT',h(out/'test-report.json'))
if __name__=='__main__':main()
