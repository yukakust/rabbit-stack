"""Exact cached physical tuple corruption tests; no key/radio calls."""
from pathlib import Path
import json,struct,copy
from decode_release import decode,route
c=route.ROOT/'runs/control';raw=json.loads((c/'boot53.json').read_text());w=json.loads((c/'startup53.json').read_text());p=json.loads((c/'profile53.json').read_text())
s=json.loads((route.REPO/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json').read_text());a=json.loads((Path(s.get('hardware_trial_pending') or str(route.REPO/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/firmware-ram-8sztj97t'))/'report.json').read_text());decode(raw,w,p,a);count=0
def rejected(x,y,z,b):
 global count
 try:decode(x,y,z,b)
 except (ValueError,KeyError):count+=1;return
 raise AssertionError('corruption accepted')
for i in range(30):
 x=copy.deepcopy(raw);v=bytearray.fromhex(x['raw_hex']);struct.pack_into('<I',v,8+4*i,struct.unpack_from('<I',v,8+4*i)[0]^1);x['raw_hex']=v.hex();rejected(x,w,p,a)
for field in ('phase','error','ready_seen','tx_complete'):
 x=copy.deepcopy(w);offset={'phase':8,'error':12,'ready_seen':32,'tx_complete':36}[field];v=bytearray.fromhex(x['raw_hex']);struct.pack_into('<I',v,offset,struct.unpack_from('<I',v,offset)[0]^1);x['raw_hex']=v.hex();rejected(raw,x,p,a)
from decode_profile import NAMES
for field in ('trial_phase','trial_error','expired','stop_requested','actual_owners_released','lifecycle_phase','lifecycle_error','bridge_error','rx_error','held_buffers','dma_users','pci_owned','pin_owned','ready_seen','tx_complete','credit_outstanding'):
 x=copy.deepcopy(p);v=bytearray.fromhex(x['raw_hex']);off=8+4*NAMES.index(field);struct.pack_into('<I',v,off,struct.unpack_from('<I',v,off)[0]^1);x['raw_hex']=v.hex();rejected(raw,w,x,a)
for obj in (raw,w,p):
 x=copy.deepcopy(raw);y=copy.deepcopy(w);z=copy.deepcopy(p)
 target=x if obj is raw else y if obj is w else z;target['writes']=1;rejected(x,y,z,a)
for field in ('native_counter','completed_chunks'):
 b=copy.deepcopy(a);b[field]-=1;rejected(raw,w,p,b)
b=copy.deepcopy(a);b['last_receipt']['packet_sha256']='0'*64;rejected(raw,w,p,b)
print(json.dumps({'status':'EXACT53-CONTROLLED-STOP-COMBINED-DECODER-NEGATIVE-PASS','rejections':count,'key_access':False,'radio_access':False}))
