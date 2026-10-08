from pathlib import Path
import sys,subprocess,json,hashlib
assert sys.platform.startswith('linux'),'Native C/ASAN/COFF only Yukabox'
import derive
R=Path(__file__).resolve().parent;O=R/'runs/derived';original=derive.derive(O)
subprocess.run([sys.executable,str(O/'run_hardened.py')],check=True)
logs={}
for mode in ['failure','zero']:
 a=subprocess.run([str(O/'runs/hardened/fixture'),mode],capture_output=True,text=True,check=True,timeout=20);logs[mode]=a.stdout.strip()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base_report=json.loads((O/'runs/hardened/report.json').read_text())
report={'status':'SYNTHETIC-FALLIBLE-RNG-LWIP-LEASE-TCP-ASAN-COFF-PASS','build_host':'yukabox','original_inputs':original,'derived_report':base_report,'derived_report_sha256':sha(O/'runs/hardened/report.json'),'entropy_cases':logs,'source_sha256':{p.name:sha(p) for p in [R/'derive.py',R/'entropy_fixture.inc',R/'run.py']},'physical_proved':False,'entropy_authority_proved':False,'native_integrated':False,'generation_reserved':False,'signing_admitted':False};(R/'runs/report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(logs))
