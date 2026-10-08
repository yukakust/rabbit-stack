from pathlib import Path
import subprocess,json,hashlib,sys,os
assert sys.platform.startswith('linux')
r=Path(__file__).resolve().parent;o=r/'runs/parent-model';o.mkdir(parents=True,exist_ok=True);cc=sys.argv[1];logs=[]
src=['artifact.c','loader.c','module_platform.c','inventory.c','reference/sha256.c','reference/monocypher.c','reference/monocypher-ed25519.c','test_parent.c']
# module_platform's unused GetInfo wrapper requires actual mature RNG source; no fake stub.
ref=Path('/home/yuka/rabbit-world/parallel-filter64-native-v1/source/experiments/native-wifi-qca9377-city-presentation-v1/runs/native-projection/rng_port.c')
def run(cmd):
 p=subprocess.run(cmd,text=True,capture_output=True,env=dict(os.environ,TMPDIR=str(o)));logs.extend([json.dumps(cmd),p.stdout,p.stderr]);(o/'full.log').write_text('\n'.join(logs));assert not p.returncode,p.stderr;return p.stdout
run([cc,'-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all','-I'+str(r),*[str(r/p) for p in src],str(ref),'-Wl,--wrap=inv_cpuid_native','-o',str(o/'test')]);result=run([str(o/'test')]);print(result)
for p in ['artifact.c','loader.c','module_platform.c','inventory.c','parent_glue.c']:run([cc,'-target','x86_64-pc-win32-coff','-Oz','-ffreestanding','-fno-stack-protector','-mno-red-zone','-I'+str(r),'-c',str(r/p),'-o',str(o/(Path(p).stem+'.obj'))])
report={'status':'ACTUAL-PARENT-GLUE-ASAN-COFF-SYNTHETIC-PASS','physical_admission':False,'actual_cpuid_calls':0,'GetRNG_calls':0,'result':result,'source_sha256':{str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest() for p in r.rglob('*') if p.is_file() and 'runs' not in p.parts and 'evidence' not in p.parts and '__pycache__' not in p.parts},'reference_rng_port_sha256':hashlib.sha256(ref.read_bytes()).hexdigest(),'artifact_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in o.iterdir() if p.is_file() and p.name!='report.json'}};(o/'report.json').write_text(json.dumps(report,indent=2)+'\n')
