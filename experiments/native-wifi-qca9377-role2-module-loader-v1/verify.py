from pathlib import Path
import subprocess,platform,json,hashlib,os,sys
assert platform.system()=='Linux','Native tests only Yukabox'
r=Path(__file__).resolve().parent;o=r/'runs/checked';o.mkdir(parents=True,exist_ok=True);cc=sys.argv[1];logs=[]
sources=['artifact.c','loader.c','parent.c','reference/sha256.c','reference/monocypher.c','reference/monocypher-ed25519.c'];env=dict(os.environ,TMPDIR=str(o))
def run(cmd):
 p=subprocess.run(cmd,text=True,capture_output=True,env=env);logs.extend([json.dumps(cmd),p.stdout,p.stderr]);(o/'full.log').write_text('\n'.join(logs));assert p.returncode==0,p.stderr;return p.stdout
run([cc,'-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all','-I'+str(r),*[str(r/s) for s in sources],str(r/'test_module.c'),'-o',str(o/'test')]);result=run([str(o/'test')]);print(result)
for s in sources:run([cc,'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Oz','-I'+str(r),'-c',str(r/s),'-o',str(o/(Path(s).stem+'.obj'))])
report={'status':'MODULE-ARTIFACT-OWNER-VERIFY-UEFI-MOCK-ASAN-COFF-PASS','physical_admission':False,'physical_calls':0,'synthetic_firmware':True,'result':result,'coff_units':len(sources),'source_sha256':{str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest() for p in r.rglob('*') if p.is_file() and 'runs' not in p.parts and 'evidence' not in p.parts},'artifact_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in o.iterdir() if p.is_file() and p.name!='report.json'}}
(o/'report.json').write_text(json.dumps(report,indent=2)+'\n')
