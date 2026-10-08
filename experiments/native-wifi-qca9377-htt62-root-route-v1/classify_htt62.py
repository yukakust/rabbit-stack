"""Read-only physical62 raw classification. No radio, signing or credential APIs."""
from pathlib import Path
import argparse,importlib.util,json
import gate,assets62,host_gate
ROOT=Path(__file__).resolve().parent
DECODER=gate.REPO/'experiments/native-wifi-qca9377-htt62-observer-v2/decode_htt.py'
spec=importlib.util.spec_from_file_location('_root62_owned_htt_decode',DECODER)
decode=importlib.util.module_from_spec(spec);spec.loader.exec_module(decode)
def no_fixture(value):
 gate.need(not any(k in value for k in ('fixture_kind','synthetic_only','test_clock','model_capture')),'synthetic/fixture evidence is not physical')
def capture_from_logs(stdout,callbacks):
 parsed=[]
 for line in stdout.splitlines():
  if not line.startswith('{'):continue
  row=json.loads(line)
  if row.get('format','').startswith('QHTT1-QHTX1'):parsed.append(row)
 gate.need(len(parsed)==1 and parsed[0]['format']=='QHTT1-QHTX1','one complete raw capture, no partial substitute')
 raw=parsed[0];no_fixture(raw)
 gate.need(type(raw.get('status_hex')) is list and len(raw['status_hex'])==3 and type(raw.get('pages_hex')) is list and len(raw['pages_hex'])==2,'three statuses and two raw passes required')
 rows=[json.loads(line) for line in callbacks.splitlines() if line.startswith('{')]
 gate.need(rows,'actual callback log required')
 for row in rows:
  no_fixture(row);gate.need(row.get('peripheral','').upper()==decode.PEER and type(row.get('writes')) is int and row['writes']==0 and row.get('NSError_code')==0 and not row.get('NSError_domain') and not row.get('cached_value_possible'),'wrong-peer/error/cached/write callback')
 gate.need(len(rows)==67 and [r['stage'] for r in rows[:4]]==['services','characteristics','services','characteristics'] and all(r['stage']=='read' for r in rows[4:]),'exact two-service discovery then63 sequential callbacks')
 reads=[r for r in rows if r['stage']=='read']
 expected=[(0,0,0x2f,raw['status_hex'][0])]
 for stage,passnum in ((1,0),(3,1)):
  gate.need(len(raw['pages_hex'][passnum])==30,'complete page pass required')
  if stage==3:expected.append((2,0,0x2f,raw['status_hex'][1]))
  expected.extend((stage,page,0x80+page,h) for page,h in enumerate(raw['pages_hex'][passnum]))
 expected.append((4,0,0x2f,raw['status_hex'][2]));gate.need(len(reads)==len(expected)==63,'exact63 callbacks required')
 for row,(stage,page,uuid,h) in zip(reads,expected):
  gate.need(row['capture_stage']==stage and (stage in (0,2,4) or row['page']==page) and row['expected'].upper()==f'52414242-4954-4649-8000-{uuid:012X}' and row['raw_hex']==h and row['raw_bytes']==len(bytes.fromhex(h)),'raw callback/result sequence mismatch')
 return raw
def main():
 p=argparse.ArgumentParser();p.add_argument('--state',type=Path,required=True);p.add_argument('--capture-log',type=Path,required=True);p.add_argument('--raw-log',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 # All inputs are read-only; this classifier never acquires/opens another BLE path.
 state_bytes=a.state.read_bytes();s=json.loads(state_bytes);policy,public,g=assets62.route.current(s,gate.CHECKED);host_gate.checked()
 native=Path(s['engine']['last_release_report']).parent;packet=(native/'native.rrt').read_bytes()
 verified=gate.engine.verify(packet,target=bytes.fromhex(policy['target']),owner=public,base_runtime=bytes.fromhex('305d0171c3c2e296fdf00f82a01cc838d67c0a1f3ffa836a847f4f12770ce074'),world=Path(s['package']).read_bytes(),counter=61)
 gate.need(verified.counter==62 and gate.flow.sha(verified.payload)==gate.PAYLOAD,'exact public native62 signature')
 session=Path(s['hardware_trial_pending']);report=gate.flow.read_json(session/'report.json')
 gate.need(report['status']=='EXACT-FULL-FIRMWARE-CONTAINER-IN-RAM' and report['completed_chunks']==12 and report['native_counter']==62 and report['native_payload_sha256']==gate.PAYLOAD and report['policy']==policy and report['gate']==g and len(report['packets'])==12,'actual62 complete signed firmware')
 receipt=report['last_receipt'];gate.need(receipt['action']==4 and receipt['bitmap']==4095 and receipt['ready']==1 and receipt['peripheral'].upper()==decode.PEER,'actual complete firmware receipt')
 body=bytearray()
 for item in report['packets']:
  b=(session/gate.safe(item['file'])).read_bytes();v=assets62.observer.validate(b,public)
  gate.need(v=={k:x for k,x in item.items() if k!='file'} and v['generation']==62 and v['offset']==len(body),'immutable firmware signature/ordering')
  body.extend(b[224:])
 gate.need(len(body)==policy['total'] and gate.flow.sha(body)==policy['digest'],'exact full firmware container')
 capture_bytes=a.capture_log.read_bytes();raw_bytes=a.raw_log.read_bytes();raw=capture_from_logs(capture_bytes.decode(),raw_bytes.decode());decoded=decode.decode_capture(raw,container=bytes(body))
 found=bool(decoded['version_only_pass'])
 result={'status':'PHYSICAL62-OWNED-HTT-VERSION-CONF-RELEASE14' if found else 'PHYSICAL62-COMPLETE-HTT-CAPTURE-NO-VERSION-PASS','generation':62,'payload_sha256':gate.PAYLOAD,'native_packet_sha256':gate.flow.sha(packet),'world_package_sha256':gate.WORLD,'asset_session':str(session),'raw_capture_sha256':gate.flow.sha(capture_bytes),'callback_log_sha256':gate.flow.sha(raw_bytes),'state_sha256':gate.flow.sha(state_bytes),'stable_statuses':3,'stable_raw_passes':2,'pages_per_pass':30,'version_confirmed':found,'major':decoded['major'],'minor':decoded['minor'],'native_error':decoded['error'],'all14_released':True,'htt_data_plane_ready':False,'association':False,'credentials_read':False,'IP':False,'device_attestation':False}
 gate.need(a.state.read_bytes()==state_bytes and a.capture_log.read_bytes()==capture_bytes and a.raw_log.read_bytes()==raw_bytes,'inputs changed during classification')
 gate.need(not a.output.exists(),'never overwrite prior classification');gate.flow.save(a.output,result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
