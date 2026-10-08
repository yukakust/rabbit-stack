from pathlib import Path
import subprocess,platform,json,hashlib,sys,os
assert platform.system()=='Linux'
r=Path(__file__).resolve().parent;o=r/'runs/checked';o.mkdir(parents=True,exist_ok=True);cc=sys.argv[1];logs=[]
def run(cmd):
 p=subprocess.run(cmd,text=True,capture_output=True,env=dict(os.environ,TMPDIR=str(o)));logs.extend([json.dumps(cmd),p.stdout,p.stderr]);(o/'full.log').write_text('\n'.join(logs));assert p.returncode==0,p.stderr;return p.stdout
run([cc,'-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all',str(r/'inventory.c'),str(r/'test.c'),'-o',str(o/'test')]);result=run([str(o/'test')]);print(result);run([cc,'-target','x86_64-pc-win32-coff','-Oz','-ffreestanding','-fno-stack-protector','-mno-red-zone','-c',str(r/'inventory.c'),'-o',str(o/'inventory.obj')]);size=run(['objdump','-h',str(o/'inventory.obj')]);(o/'size.log').write_text(size)
report={'status':'PUBLIC-CPUID-INVENTORY-MOCK-ASAN-COFF-PASS','physical_admission':False,'actual_cpuid_calls':0,'msr_reads_writes':0,'rng_calls':0,'entropy_approved':False,'result':result,'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in r.iterdir() if p.is_file()},'artifact_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in o.iterdir() if p.is_file() and p.name!='report.json'}};(o/'report.json').write_text(json.dumps(report,indent=2)+'\n')
