from pathlib import Path
import sys,subprocess,os,hashlib,json
assert sys.platform.startswith('linux'),'Native tests only Yukabox'
r=Path(__file__).resolve().parent;o=r/'runs/checked';o.mkdir(parents=True,exist_ok=True);cc=sys.argv[1];logs=[]
inc=['-I'+str(r),'-I'+str(r/'vendor/include'),'-DMBEDTLS_CONFIG_FILE="config.h"'];src=['entropy.c','seed_source.c','native.c','vendor/library/aes.c','vendor/library/ctr_drbg.c','vendor/library/platform.c','vendor/library/platform_util.c']
def run(c):
 p=subprocess.run(c,text=True,capture_output=True,env=dict(os.environ,TMPDIR=str(o)));logs.extend([json.dumps(c),p.stdout,p.stderr]);(o/'full.log').write_text('\n'.join(logs));assert not p.returncode,p.stderr;return p.stdout
run([cc,'-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all',*inc,*[str(r/p) for p in src],str(r/'test_entropy.c'),'-Wl,--wrap=trusted_cpu_native','-Wl,--wrap=trusted_rdseed64_native','-o',str(o/'test')]);result=run([str(o/'test')]);print(result)
for name in [*src,'memory_bridge.c']:
 run([cc,'-target','x86_64-pc-win32-coff','-U_WIN32','-U_WIN64','-U_MSC_VER','-Oz','-ffreestanding','-fno-stack-protector','-mno-red-zone','-I'+str(r/'freestanding'),*inc,'-c',str(r/name),'-o',str(o/(Path(name).stem+'.obj'))])
report={'status':'TRUSTED-EXECUTION-RDSEED-MATURE-CTRDRBG-ASAN-COFF-SOFTWARE-PASS','hardware_samples':0,'physical_admission':False,'synthetic_cpu_clock_CF_only':True,'result':result,'coff_units':len(src)+1,'source_sha256':{str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest() for p in r.rglob('*') if p.is_file() and 'runs' not in p.parts and 'evidence' not in p.parts},'artifacts':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in o.iterdir() if p.is_file() and p.name!='report.json'}};(o/'report.json').write_text(json.dumps(report,indent=2)+'\n')
