import hashlib,json,subprocess,sys,ssl
from pathlib import Path
r=Path(__file__).resolve().parent;o=r/'evidence';o.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs={p.name:sha(p) for p in r.iterdir() if p.is_file() and p.name!='freeze.json'}
p=subprocess.run([sys.executable,str(r/'test_auth.py')],text=True,capture_output=True,timeout=60)
(o/'full.log').write_text(p.stdout+p.stderr)
assert p.returncode==0,p.stdout+p.stderr
assert inputs=={p.name:sha(p) for p in r.iterdir() if p.is_file() and p.name!='freeze.json'}
d={'status':'MAC-PUBLIC-PAIR-AUTH-FIXTURE-PASS','source_sha256':inputs,'result':p.stdout.strip(),'log_sha256':sha(o/'full.log'),'openssl':ssl.OPENSSL_VERSION,'physical_admission':False,'human_fullSPKI_confirmation':False,'owner_authorization':False,'credentials_read':False,'actual_BLE':False}
(o/'report.json').write_text(json.dumps(d,indent=2)+'\n');print(d['result'])
