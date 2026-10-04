from pathlib import Path
import sys,subprocess,json,hashlib,platform
if platform.system()!='Linux':raise SystemExit('Run this baseline only on Yukabox/Linux, never compile native code on Mac')
sys.path.insert(0,'experiments/native-wifi-qca9377-v1')
import verify_init_probe as v
out=v.ROOT/'runs/init-probe-host';old=v.ROOT/'runs/init-profile-applied29/warm_core.c';exe=Path('/tmp/rabbit-warm7-slow-baseline')
inc=['-I'+str(p) for p in (out,v.ROOT,v.build.actors.OLD,v.build.actors.NATIVE)]
subprocess.run(['gcc','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',*inc,str(v.ROOT/'init_probe_test.c'),*[str(old if n=='warm_core.c' else out/n) for n in v.FILES],'-o',str(exe)],check=True)
r=subprocess.run([str(exe),'18'],capture_output=True,text=True,timeout=30)
assert r.returncode!=0 and 'get(128)==5' in r.stderr and 'error=5122' in r.stderr,(r.returncode,r.stderr)
p=Path('/tmp/rabbit-warm7-slow-baseline.json');p.write_text(json.dumps({'status':'OLD-7S-BASELINE-FAILS-SLOW-COOPERATIVE-NATIVE-SUCCESS','scenario':18,'exit_code':r.returncode,'stderr':r.stderr,'warm_source_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'fixture_sha256':hashlib.sha256((v.ROOT/'init_probe_test.c').read_bytes()).hexdigest(),'physical':False},indent=2)+'\n')
print(p.read_text(),flush=True)
