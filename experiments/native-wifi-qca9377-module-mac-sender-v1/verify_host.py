"""Mac Objective-C host proof. Never creates a real Bluetooth manager."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
assert sys.platform=='darwin'
r=Path(__file__).resolve().parent;o=r/'runs';o.mkdir(exist_ok=True)
e=r/'evidence';e.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs={p.name:sha(p) for p in r.iterdir() if p.is_file()}
logs=[]
env=os.environ.copy()
for n in ['CPATH','C_INCLUDE_PATH','CPLUS_INCLUDE_PATH','SDKROOT']:env.pop(n,None)
plist=r.parent/'x86-64-uefi-connected-supervisor-v1/FileSender-Info.plist'
inputs['../x86-64-uefi-connected-supervisor-v1/FileSender-Info.plist']=sha(plist)
def run(cmd):
 p=subprocess.run(cmd,cwd=r,text=True,capture_output=True,env=env,timeout=60)
 logs.append(json.dumps(cmd)+'\n'+p.stdout+p.stderr)
 (e/'full.log').write_text('\n'.join(logs))
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 return p.stdout
for source,out in [('sender.m','sender'),('host_test.m','host-test')]:
 run(['xcrun','--sdk','macosx','clang','-x','objective-c','-fobjc-arc','-Wall','-Wextra','-Werror',source,'-framework','Foundation','-framework','CoreBluetooth','-Wl,-sectcreate,__TEXT,__info_plist,'+str(plist),'-o',str(o/out)])
preflight=run([str(o/'sender'),'--preflight'])
callbacks=run([str(o/'host-test'),str(o/'host-cases')])
run(['python3','-m','unittest','discover','-s',str(r),'-p','test_*.py'])
for name,h in inputs.items():assert sha(r/name)==h,name
d={'status':'PUBLIC-MODULE-MAC-167-CALLBACK-COMPILE-PREFLIGHT-PASS',
   'source_sha256':inputs,'log_sha256':sha(e/'full.log'),
   'callback_result':callbacks.splitlines()[-1],'preflight':preflight.strip(),
   'real_Bluetooth_manager_started':False,'real_writes':0,'keys_read':0,
   'physical_delivery':False,'whole_candidate_admission':False}
(e/'report.json').write_text(json.dumps(d,indent=2)+'\n');print(d['callback_result'])
