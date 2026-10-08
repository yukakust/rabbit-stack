"""Three genuine unsigned parent builds on Yukabox only."""
from pathlib import Path
import sys,subprocess,hashlib,json,os
assert sys.platform.startswith('linux')
sys.dont_write_bytecode=True
r=Path(__file__).resolve().parent;p=r/'parent-projection';out=p/'runs/native-projection';digests=[]
for i in range(3):
 result=subprocess.run([sys.executable,str(p/'native_build.py')],text=True,capture_output=True)
 (out/('rebuild-'+str(i)+'.log')).write_text(result.stdout+result.stderr)
 assert not result.returncode,result.stderr
 digests.append(hashlib.sha256((out/'payload.efi').read_bytes()).hexdigest())
assert len(set(digests))==1
(out/'reproduction.json').write_text(json.dumps({'status':'ROLE2-PARENT-THREE-IDENTICAL-UNSIGNED-BUILDS','payload_sha256':digests,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'physical_admission':False},indent=2)+'\n')
print(digests[0])
