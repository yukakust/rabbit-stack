from pathlib import Path
import hashlib,json,os,subprocess,sys,time
repo=Path('/Users/yukakust/rabbit-stack')
sys.path.insert(0,str(repo/'experiments/native-wifi-qca9377-v1'))
import boot_asset_route as route
from send_firmware_chunk import validate
flow=route.flow
state_path=repo/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json'
directory=state_path.parent/'firmware-ram-ytrkhw7x'
diag=Path(__file__).resolve().parent
helper=diag/'cached16-sender'
meta=json.loads((diag/'cached16-report.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(helper)==meta['helper_sha256'] and sha(diag/'cached16_sender.m')==meta['source_sha256']
assert sha(repo/'experiments/native-wifi-qca9377-v1/mac_firmware_sender.m')==meta['parent_source_sha256']
with flow.state_lock(state_path):
 state=flow.read_json(state_path);assert state.get('hardware_trial_pending')==str(directory)
 report=flow.read_json(directory/'report.json')
 policy,public,gate=route.current(state,Path(report['checked_directory']))
 assert report['policy']==policy and report['gate']==gate and report['native_counter']==41
 assert report['native_payload_sha256']==state['engine']['payload_sha256'] and report['world_sha256']==state['world_sha256']
 for item in report['packets']:
  assert validate((directory/item['file']).read_bytes(),public)=={k:v for k,v in item.items() if k!='file'}
 index=report['completed_chunks'];assert 0<=index<len(report['packets'])
 packet=report['packets'][index];path=directory/packet['file'];checkpoint=path.with_suffix(path.suffix+'.checkpoint.json')
 env=os.environ.copy();env['RABBIT_ASSET_PEER']=route.PEER
 if flow.LOCK_FD is not None:env['RABBIT_CONNECTED_LOCK_FD']=str(flow.LOCK_FD)
 first=None;last=None;started=time.monotonic()
 for mode in ('--query-only','--send'):
  log=directory/f'wifi-off-cached16-chunk-{index}-{len(report["sender_steps"])}.log'
  entry={'chunk':index,'mode':mode,'variant':'wifi-off-cached16-window512','helper_sha256':meta['helper_sha256'],'exit_code':None,'log':str(log)}
  report['sender_steps'].append(entry);report['status']='RAM-DIAGNOSTIC-CACHED16';flow.save(directory/'report.json',report)
  with log.open('w') as output:
   try:r=subprocess.run([str(helper),str(path),str(checkpoint),mode],env=env,stdout=output,stderr=subprocess.STDOUT,timeout=(10 if mode=='--query-only' else 25),pass_fds=() if flow.LOCK_FD is None else (flow.LOCK_FD,))
   except subprocess.TimeoutExpired:
    output.write('OUTCOME UNKNOWN: keep exact packet/checkpoint; query before retry\n');r=subprocess.CompletedProcess([],1)
  entry['exit_code']=r.returncode;flow.save(directory/'report.json',report)
  receipt=None
  for line in log.read_text().splitlines():
   try:value=json.loads(line)
   except ValueError:continue
   if value.get('peripheral','').upper()==route.PEER and value.get('packet_sha256')==packet['packet_sha256'] and value.get('error')==0:receipt=value
  if receipt:
   last=receipt['received']
   if first is None:first=last
  print(f'CACHED16 {mode}: exit={r.returncode}, confirmed={last}, elapsed={time.monotonic()-started:.1f}s',flush=True)
  if r.returncode or not receipt or receipt['action'] not in (1,2,3,4):
   report['status']='RAM-CACHED16-RECEIPT-NOT-CONFIRMED';flow.save(directory/'report.json',report);break
  if receipt['action']==4:
   assert receipt['received']==receipt['length'] and receipt['length']==path.stat().st_size and receipt['bitmap']&(1<<index)
   report['completed_chunks']=index+1;report['last_receipt']=receipt;report['status']='RAM-STAGING';flow.save(directory/'report.json',report);break
  if mode=='--send':
   report['status']='RAM-CACHED16-RECEIPT-NOT-CONFIRMED';flow.save(directory/'report.json',report)
 result={'status':'CACHED16-PHYSICAL-ATTEMPT-OBSERVED','chunk_index':index,'initial_confirmed':first,'last_confirmed':last,'elapsed_seconds':time.monotonic()-started,'helper':meta,'fully_accepted':report['completed_chunks']>index,'wifi_connected':False,'private_key_read':False}
 (diag/f'physical-wifi-off-cached16-{len(report["sender_steps"])}.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result),flush=True)
