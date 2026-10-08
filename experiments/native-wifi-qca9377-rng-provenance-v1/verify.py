"""Run only on Yukabox. Injected firmware memory is not physical provenance."""
import hashlib,json,subprocess,sys
from pathlib import Path
assert sys.platform.startswith('linux'), 'native C/ASAN/COFF only Yukabox'
r=Path(__file__).resolve().parent;o=r/'runs';o.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs={str(p.relative_to(r)):sha(p) for p in r.rglob('*') if p.is_file() and 'runs' not in p.parts and 'evidence' not in p.parts and p.suffix in {'.c','.h','.py'}}
logs=[]
def run(cmd):
 p=subprocess.run(cmd,cwd=r,text=True,capture_output=True,timeout=60)
 logs.append(json.dumps(cmd)+'\n'+p.stdout+p.stderr);(o/'full.log').write_text('\n'.join(logs))
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 return p.stdout
cmd=['gcc','-std=c11','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-omit-frame-pointer','-Ireference','provenance.c','test_provenance.c','reference/sha256.c','-o',str(o/'test')]
run(cmd);result=run([str(o/'test')])
for f in ('provenance.c','reference/sha256.c'):
 run(['x86_64-w64-mingw32-gcc','-std=c11','-Os','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-ffreestanding','-fno-builtin','-fno-stack-protector','-mno-red-zone','-Ireference','-c',f,'-o',str(o/(Path(f).name+'.obj'))])
assert inputs=={str(p.relative_to(r)):sha(p) for p in r.rglob('*') if p.is_file() and 'runs' not in p.parts and 'evidence' not in p.parts and p.suffix in {'.c','.h','.py'}}
report={'status':'PUBLIC-PROVENANCE-INJECTED-BOUNDARY-ASAN-UBSAN-COFF-PASS','result':result,'source_sha256':inputs,'log_sha256':sha(o/'full.log'),'coff_sha256':{p.name:sha(p) for p in o.glob('*.obj')},'entropy_approved':False,'physical_provenance_identified':False,'physical_delivery_admitted':False,'GetRNG_RDSEED_MSR_calls':0}
(o/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(result.strip())
