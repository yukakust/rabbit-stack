"""Instrument EVERY actual library unit; software fixture only on Yukabox."""
from pathlib import Path
import sys,platform,os,subprocess,json
assert platform.system()=='Linux'
root=Path(__file__).resolve().parent;v=root/'source/mbedtls-3.6.7';out=root/'runs/asan';out.mkdir(parents=True,exist_ok=True);clang=sys.argv[1];logs=[];objects=[]
flags=['-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all','-I'+str(root),'-I'+str(v/'include'),'-I'+str(v/'library'),'-I'+str(v/'tests/include'),'-DMBEDTLS_CONFIG_FILE="tls_config.h"']
def run(cmd):
 r=subprocess.run(cmd,text=True,capture_output=True,env=dict(os.environ,TMPDIR=str(out)));logs.extend([json.dumps(cmd),r.stdout,r.stderr]);(out/'full.log').write_text('\n'.join(logs));assert r.returncode==0,r.stderr;return r.stdout
for p in [*(v/'library').glob('*.c'),v/'tests/src/certs.c',root/'tls_engine.c',root/'tls_heap.c',root/'test_tls.c']:
 obj=out/(p.stem+'.o');run([clang,*flags,'-c',str(p),'-o',str(obj)]);objects.append(obj)
run([clang,'-fsanitize=address,undefined',*[str(p) for p in objects],'-o',str(out/'test')]);print(run([str(out/'test')]).strip())
