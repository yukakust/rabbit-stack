"""Initial real library object-size assessment; Yukabox only."""
from pathlib import Path
import sys,platform,subprocess,os,json,hashlib
assert platform.system()=='Linux','native builds only Yukabox'
root=Path(__file__).resolve().parent;vendor=root/'source/mbedtls-3.6.7';out=root/'runs/size';out.mkdir(parents=True,exist_ok=True)
clang=sys.argv[1];logs=[];objects=[]
inputs={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [root/'tls_config.h',*[p for p in (vendor/'library').glob('*.c')]]}
for p in (vendor/'library').glob('*.c'):
 cmd=[clang,'-Os','-ffunction-sections','-fdata-sections','-I'+str(root),'-I'+str(vendor/'include'),'-DMBEDTLS_CONFIG_FILE="tls_config.h"','-c',str(p),'-o',str(out/(p.stem+'.o'))]
 r=subprocess.run(cmd,env=dict(os.environ,TMPDIR=str(out)),text=True,capture_output=True);logs.extend([json.dumps(cmd),r.stdout,r.stderr]);
 if r.returncode:(out/'build.log').write_text('\n'.join(logs));raise RuntimeError(r.stderr)
 objects.append(out/(p.stem+'.o'))
size=subprocess.run(['size',*[str(p) for p in objects]],text=True,capture_output=True,check=True).stdout;(out/'size.log').write_text(size);(out/'build.log').write_text('\n'.join(logs));total=[0,0,0]
for line in size.splitlines()[1:]:
 cols=line.split()
 if len(cols)>=3:
  for i in range(3):total[i]+=int(cols[i])
(out/'initial.json').write_text(json.dumps({'status':'ACTUAL-MBEDTLS367-MINIMAL-TLS13-OBJECT-ASSESSMENT','source_sha256':inputs,'all_object_text':total[0],'all_object_data':total[1],'all_object_bss':total[2],'final_link_not_yet_proven':True,'physical':False},indent=2)+'\n');print('Actual raw library totals text/data/bss',total)
