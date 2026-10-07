"""Actual saved PUBLIC55 signature/source regression, no hardware or live state."""
import json,tempfile,shutil
from pathlib import Path
import gate
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent.parent
A=ROOT/'runs/public55';C=ROOT/'runs/checked55'
def run():
 proof=gate.public_bundle(REPO,A/'pci-native-ehv85hvp',A/'firmware-ram-g4w7ruqs',C,A/'world.rup');count=0
 with tempfile.TemporaryDirectory(prefix='public-negative-',dir=ROOT/'runs') as tmp:
  base=Path(tmp);n=base/'native';a=base/'assets';c=base/'checked'
  shutil.copytree(A/'pci-native-ehv85hvp',n);shutil.copytree(A/'firmware-ram-g4w7ruqs',a);shutil.copytree(C,c)
  def reject(path,data):
   nonlocal count
   original=path.read_bytes();path.write_bytes(data)
   try:
    try:gate.public_bundle(REPO,n,a,c,A/'world.rup')
    except Exception:count+=1
    else:raise AssertionError('corruption accepted: '+str(path))
   finally:path.write_bytes(original)
  for f,pos in [('native.rrt',-1),('native.rrt',192),('native.rrt',24),('payload.efi',0)]:
   p=n/f;v=bytearray(p.read_bytes());v[pos]^=1;reject(p,bytes(v))
  for i in (0,11):
   for pos in (160,224,104,128):
    p=a/f'chunk-{i}.bin';v=bytearray(p.read_bytes());v[pos]^=1;reject(p,bytes(v))
  for p,k,v in [(a/'report.json','completed_chunks',11),(n/'report.json','status','MODEL'),(c/'report.json','payload_sha256','0'*64)]:
   d=json.loads(p.read_bytes());d[k]=v;reject(p,json.dumps(d).encode())
  p=a/'chunk-11.bin.checkpoint.json';d=json.loads(p.read_bytes());d['floor']-=1;reject(p,json.dumps(d).encode())
  p=a/'report.json';d=json.loads(p.read_bytes());d['last_receipt']['bitmap']=2047;reject(p,json.dumps(d).encode())
  p=c/'report.json';d=json.loads(p.read_bytes());d['source_sha256'][next(iter(d['source_sha256']))]='0'*64;reject(p,json.dumps(d).encode())
 result={'status':'PUBLIC55-SIGNATURES-ALL12-CHECKPOINTS-642-SOURCE-NEGATIVE-PASS','negative_cases':count,'source_count':642,'native_counter':55,'public_bundle':proof,'device_writes':0,'private_key_loads':0,'production_state_read':False}
 (ROOT/'runs/public-host-report.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],count)
if __name__=='__main__':run()
