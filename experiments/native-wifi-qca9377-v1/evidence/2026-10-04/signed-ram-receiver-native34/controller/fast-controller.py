# Controller composition only: already gated/signature-verified immutable packets.
# Keep one lock; launch the already compiled Cocoa helper directly under it.
import sys,subprocess,os
from pathlib import Path
from types import SimpleNamespace
sys.path.insert(0,'/Users/yukakust/rabbit-stack/experiments/native-wifi-qca9377-v1')
import asset_route as route
import inspect
resume=inspect.getsource(route.deliver).replace("if i<report['completed_chunks']-1:continue", "if i<report['completed_chunks'] and not (report['completed_chunks']==len(report['packets']) and i==len(report['packets'])-1):continue")
exec(resume,route.__dict__)
original=subprocess.run
exe=Path('/tmp/rabbit-windowed-fast-sender')
state=Path('/Users/yukakust/rabbit-stack/experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json')
session=state.parent/'firmware-ram-y_iygsqw'
def single_controller(command,**kwargs):
 if len(command)==8 and command[:2]==['python3',str(route.ROOT/'send_firmware_chunk.py')]:
  packet=Path(command[2]);mode=command[3]
  assert mode in ('--send','--query-only') and command[4:]==['--state',str(state),'--peer',route.PEER]
  checkpoint=packet.with_suffix(packet.suffix+'.checkpoint.json')
  env=dict(kwargs.get('env',os.environ));env['RABBIT_ASSET_PEER']=route.PEER;kwargs['env']=env
  return original([str(exe),str(packet),str(checkpoint),mode],timeout=250,**kwargs)
 return original(command,**kwargs)
# Physical native code/compiled sender unchanged; only avoid nested flock.
route.subprocess.run=single_controller
with route.flow.state_lock(state):
 raise SystemExit(route.deliver(SimpleNamespace(session=session,state=state),route.flow.read_json(state)))
