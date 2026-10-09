"""Only Yukabox; public synthetic owner fixture, never hardware admission."""
import hashlib,json,subprocess,sys,os
from pathlib import Path
assert sys.platform.startswith('linux'), 'native C/ASAN/COFF only Yukabox'
r=Path(__file__).resolve().parent;o=r/'runs';o.mkdir(exist_ok=True);tmp=o/'tmp';tmp.mkdir(exist_ok=True)
env=dict(os.environ,TMPDIR=str(tmp));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs={str(p.relative_to(r)):sha(p) for p in r.rglob('*') if p.is_file() and not set(p.parts)&{'runs','evidence','__pycache__'}}
logs=[]
def run(cmd):
 p=subprocess.run(cmd,cwd=r,text=True,capture_output=True,timeout=120,env=env);logs.append(json.dumps(cmd)+'\n'+p.stdout+p.stderr);(o/'full.log').write_text('\n'.join(logs))
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 return p.stdout
files=['panel.c','test_panel.c','reference/qrcodegen.c']
run(['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-omit-frame-pointer','-I.','-Ireference',*files,'-o',str(o/'test')]);result=run([str(o/'test')])
for f in ['panel.c','reference/qrcodegen.c']:
 run(['x86_64-w64-mingw32-gcc','-std=c11','-Os','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-fno-stack-protector','-mno-red-zone','-I.','-Ireference','-c',f,'-o',str(o/(Path(f).name+'.obj'))])
assert inputs=={str(p.relative_to(r)):sha(p) for p in r.rglob('*') if p.is_file() and not set(p.parts)&{'runs','evidence','__pycache__'}}
d={'status':'PUBLIC-FULL-SPKI-QR-PANEL-ASAN-UBSAN-COFF-PASS','source_sha256':inputs,'result':result,'log_sha256':sha(o/'full.log'),'coff_sha256':{p.name:sha(p) for p in o.glob('*.obj')},'Dell_identity_authority':False,'actual_physical_QR_pairing':False,'physical_admission':False,'whole_native_parent_integrated':False}
(o/'report.json').write_text(json.dumps(d,indent=2)+'\n');print(result.strip())
