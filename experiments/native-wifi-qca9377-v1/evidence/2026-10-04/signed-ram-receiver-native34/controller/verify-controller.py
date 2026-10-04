import sys,json,copy,subprocess,tempfile
from pathlib import Path
from types import SimpleNamespace
ROOT=Path('/Users/yukakust/rabbit-stack/experiments/native-wifi-qca9377-v1')
sys.path.insert(0,str(ROOT))
import asset_route
source=Path('/tmp/rabbit-fixed-asset-route.py').read_text()
namespace={'__file__':str(ROOT/'asset_route.py'),'__name__':'candidate_controller'}
exec(compile(source,'candidate_controller','exec'),namespace)
original=ROOT.parent/'x86-64-uefi-connected-supervisor-v1/runs/text-world/firmware-ram-y_iygsqw'
report=json.loads((original/'report.json').read_text())
public=Path.home().joinpath('.rabbit-owner/runtime.pub').read_bytes()
state={'engine':{'payload_sha256':report['native_payload_sha256']},'world_sha256':report['world_sha256']}
results=[]
for accepted,timeout in ((4,False),(12,False),(4,True)):
 with tempfile.TemporaryDirectory() as temporary:
  session=Path(temporary);stored=copy.deepcopy(report);stored['completed_chunks']=accepted;stored['sender_steps']=[]
  for packet in report['packets']:(session/packet['file']).write_bytes((original/packet['file']).read_bytes())
  trace=[]
  def save(path,value):
   global stored
   stored=copy.deepcopy(value);trace.append(('save',len(value['sender_steps'])))
  namespace['flow']=SimpleNamespace(read_json=lambda _:copy.deepcopy(stored),save=save,LOCK_FD=None)
  namespace['current']=lambda *_:(report['policy'],public,report['gate'])
  commands=[]
  def run(command,**kwargs):
   commands.append(command)
   if command[:1]==['python3']:
    assert command==['python3',str(ROOT/'send_firmware_chunk.py')];return subprocess.CompletedProcess(command,0)
   assert command[0]==str(ROOT/'runs/mac-control/firmware-sender')
   assert trace[-1]==('save',len(commands)-1), 'write-ahead progress required'
   assert kwargs['env']['RABBIT_ASSET_PEER']==asset_route.PEER and kwargs['timeout']==250
   index=int(Path(command[1]).stem.split('-')[1]);assert index>=accepted or (accepted==12 and index==11)
   if timeout:raise subprocess.TimeoutExpired(command,250)
   receipt={'action':4,'bitmap':(1<<(index+1))-1,'ready':int(index==11),'peripheral':asset_route.PEER}
   kwargs['stdout'].write(json.dumps(receipt)+'\n');return subprocess.CompletedProcess(command,0)
  namespace['subprocess']=SimpleNamespace(run=run,STDOUT=subprocess.STDOUT,TimeoutExpired=subprocess.TimeoutExpired,CompletedProcess=subprocess.CompletedProcess)
  code=namespace['deliver'](SimpleNamespace(session=session,state=Path(temporary)/'state.json'),state)
  assert code==int(timeout)
  if accepted==12:assert len(commands)==2 and commands[-1][-1]=='--query-only'
  if timeout:assert stored['completed_chunks']==4 and stored['status']=='RAM-RECEIPT-NOT-CONFIRMED' and stored['sender_steps'][0]['exit_code']==1
  else:assert stored['completed_chunks']==12 and stored['status']=='EXACT-FULL-FIRMWARE-CONTAINER-IN-RAM'
  results.append({'accepted_before':accepted,'timeout':timeout,'pass':True})
print(json.dumps({'status':'SINGLE-LOCK-RESUME-AND-DURABLE-TIMEOUT-PASS','cases':results,'radio_started':False,'private_key_read':False},indent=2))
