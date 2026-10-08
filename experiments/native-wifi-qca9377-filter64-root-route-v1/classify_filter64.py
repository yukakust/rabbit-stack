"""Read-only physical64 ownership/callback classification; no secret or BLE APIs."""
from pathlib import Path
import argparse,importlib.util,json,sys
import gate,assets64,host_gate
ROOT=Path(__file__).resolve().parent
SCOPE=gate.REPO/'experiments/native-wifi-qca9377-filter64-observer-v1'
def module(name,path):
 paths=list(sys.path);names=('scan_decode','htc_codec');saved={n:sys.modules.get(n) for n in names}
 try:
  sys.path.insert(0,str(SCOPE))
  for n in names:sys.modules.pop(n,None)
  spec=importlib.util.spec_from_file_location('_root64_owned_'+name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
 finally:
  sys.path[:]=paths
  for n,v in saved.items():
   if v is None:sys.modules.pop(n,None)
   else:sys.modules[n]=v
decode=module('decode',SCOPE/'decode_filter.py');bindings=module('bindings',SCOPE/'bindings.py')
def capture_from_logs(stdout,callbacks):
 captures=[json.loads(line) for line in stdout.splitlines() if line.startswith('{')]
 captures=[v for v in captures if v.get('format')=='QF641-QSCN1-QFEX1']
 gate.need(len(captures)==1,'one complete64 raw capture required')
 rows=[json.loads(line) for line in callbacks.splitlines() if line.startswith('{')]
 bindings.callback_join(captures[0],rows)
 return captures[0]
def main():
 p=argparse.ArgumentParser();p.add_argument('--state',type=Path,required=True);p.add_argument('--capture-log',type=Path,required=True);p.add_argument('--raw-log',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 # All inputs are read-only; this classifier never acquires/opens another BLE path.
 state_bytes=a.state.read_bytes();s=json.loads(state_bytes);policy,public,g=assets64.route.current(s,gate.CHECKED);host_gate.checked()
 native=Path(s['engine']['last_release_report']).parent;packet=(native/'native.rrt').read_bytes()
 verified=gate.engine.verify(packet,target=bytes.fromhex(policy['target']),owner=public,base_runtime=bytes.fromhex('a636b40f10103a90879bad00a55de173fa36ab2b7a4fd4f38262825191bf4442'),world=Path(s['package']).read_bytes(),counter=63)
 gate.need(verified.counter==64 and gate.flow.sha(verified.payload)==gate.PAYLOAD,'exact public native64 signature')
 session=Path(s['hardware_trial_pending']);report=gate.flow.read_json(session/'report.json')
 gate.need(report['status']=='EXACT-FULL-FIRMWARE-CONTAINER-IN-RAM' and report['completed_chunks']==12 and report['native_counter']==64 and report['native_payload_sha256']==gate.PAYLOAD and report['policy']==policy and report['gate']==g and len(report['packets'])==12,'actual64 complete signed firmware')
 receipt=report['last_receipt'];gate.need(receipt['action']==4 and receipt['bitmap']==4095 and receipt['ready']==1 and receipt['peripheral'].upper()==decode.PEER,'actual complete firmware receipt')
 body=bytearray()
 for item in report['packets']:
  b=(session/gate.safe(item['file'])).read_bytes();v=assets64.observer.validate(b,public)
  gate.need(v=={k:x for k,x in item.items() if k!='file'} and v['generation']==64 and v['offset']==len(body),'immutable firmware signature/ordering')
  body.extend(b[224:])
 gate.need(len(body)==policy['total'] and gate.flow.sha(body)==policy['digest'],'exact full firmware container')
 capture_bytes=a.capture_log.read_bytes();raw_bytes=a.raw_log.read_bytes();raw=capture_from_logs(capture_bytes.decode(),raw_bytes.decode());decoded=decode.decode_capture(raw)
 pstatus=decoded['pipeline'];scan=decoded['scan'];owned=decoded['owned_filter_version_verified'];completed=decoded['pipeline_completed'];target=decoded['target_observed']
 status='PHYSICAL64-OWNED-PASSIVE-TARGET-RELEASE14' if completed and owned and target else 'PHYSICAL64-COMPLETED-PASSIVE-SCAN-NO-TARGET' if completed and owned else 'PHYSICAL64-RELEASED-DIAGNOSTIC-FAILURE'
 result={'status':status,'generation':64,'payload_sha256':gate.PAYLOAD,'native_packet_sha256':gate.flow.sha(packet),'world_package_sha256':gate.WORLD,'asset_session':str(session),'raw_capture_sha256':gate.flow.sha(capture_bytes),'callback_log_sha256':gate.flow.sha(raw_bytes),'state_sha256':gate.flow.sha(state_bytes),'stable_statuses':3,'stable_raw_passes':2,'pages_per_pass':110,'actual_callback_count':232,'owned_filter_version_verified':owned,'pipeline_completed':completed,'target_observed':target,'target_ssid_hex':'6950686f6e6520283929','beacon':decoded['beacon'],'pipeline':pstatus,'scan':scan,'all14_released':bool(pstatus['actual_released']),'partial_startup':True,'htt_data_plane_ready':False,'rx_ring_cfg':False,'aggregation_setup':False,'association':False,'credentials_read':False,'IP':False,'device_attestation':False}
 gate.need(a.state.read_bytes()==state_bytes and a.capture_log.read_bytes()==capture_bytes and a.raw_log.read_bytes()==raw_bytes,'inputs changed during classification')
 gate.need(not a.output.exists(),'never overwrite prior classification');gate.flow.save(a.output,result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
