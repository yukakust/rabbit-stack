"""Read-only physical61 raw classification. No radio, signing or credential APIs."""
from pathlib import Path
import argparse,importlib.util,json
import gate,assets61,host_gate
ROOT=Path(__file__).resolve().parent
DECODER=gate.REPO/'experiments/native-wifi-qca9377-scan61-observer-v1/decode_scan.py'
spec=importlib.util.spec_from_file_location('_root61_owned_scan_decode',DECODER)
decode=importlib.util.module_from_spec(spec);spec.loader.exec_module(decode)
def no_fixture(value):
 gate.need(not any(k in value for k in ('fixture_kind','synthetic_only','test_clock','model_capture')),'synthetic/fixture evidence is not physical')
def capture_from_logs(stdout,callbacks):
 parsed=[]
 for line in stdout.splitlines():
  if not line.startswith('{'):continue
  row=json.loads(line)
  if row.get('format','').startswith('QSCN1-QEXP1'):parsed.append(row)
 gate.need(len(parsed)==1 and parsed[0]['format']=='QSCN1-QEXP1','one complete raw capture, no partial substitute')
 raw=parsed[0];no_fixture(raw)
 gate.need(type(raw.get('status_hex')) is list and len(raw['status_hex'])==3 and type(raw.get('pages_hex')) is list and len(raw['pages_hex'])==2,'three statuses and two raw passes required')
 rows=[json.loads(line) for line in callbacks.splitlines() if line.startswith('{')]
 gate.need(rows,'actual callback log required')
 for row in rows:
  no_fixture(row);gate.need(row.get('peripheral','').upper()==decode.PEER and type(row.get('writes')) is int and row['writes']==0 and row.get('NSError_code')==0 and not row.get('NSError_domain') and not row.get('cached_value_possible'),'wrong-peer/error/cached/write callback')
 gate.need(len(rows)==227 and [r['stage'] for r in rows[:4]]==['services','characteristics','services','characteristics'] and all(r['stage']=='read' for r in rows[4:]),'exact two-service discovery then223 sequential callbacks')
 reads=[r for r in rows if r['stage']=='read']
 expected=[(0,0,0x2b,raw['status_hex'][0])]
 for stage,passnum in ((1,0),(3,1)):
  gate.need(len(raw['pages_hex'][passnum])==110,'complete page pass required')
  if stage==3:expected.append((2,0,0x2b,raw['status_hex'][1]))
  expected.extend((stage,page,0x80+page,h) for page,h in enumerate(raw['pages_hex'][passnum]))
 expected.append((4,0,0x2b,raw['status_hex'][2]));gate.need(len(reads)==len(expected)==223,'exact223 callbacks required')
 for row,(stage,page,uuid,h) in zip(reads,expected):
  gate.need(row['capture_stage']==stage and (stage in (0,2,4) or row['page']==page) and row['expected'].upper()==f'52414242-4954-4649-8000-{uuid:012X}' and row['raw_hex']==h and row['raw_bytes']==len(bytes.fromhex(h)),'raw callback/result sequence mismatch')
 return raw
def main():
 p=argparse.ArgumentParser();p.add_argument('--state',type=Path,required=True);p.add_argument('--capture-log',type=Path,required=True);p.add_argument('--raw-log',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 # All inputs are read-only; this classifier never acquires/opens another BLE path.
 state_bytes=a.state.read_bytes();s=json.loads(state_bytes);policy,public,g=assets61.route.current(s,gate.CHECKED);host_gate.checked()
 native=Path(s['engine']['last_release_report']).parent;packet=(native/'native.rrt').read_bytes()
 verified=gate.engine.verify(packet,target=bytes.fromhex(policy['target']),owner=public,base_runtime=bytes.fromhex('3984d3f5d1c9a3c3540bf2ef00972bea52406a6f78edc56bd215507110668fd6'),world=Path(s['package']).read_bytes(),counter=60)
 gate.need(verified.counter==61 and gate.flow.sha(verified.payload)==gate.PAYLOAD and gate.flow.sha(packet)=='ecd2703c73c1bc92e266542cf08241ef03c613ad4cfba75dcf6942ad0812d71c','exact public native61 signature')
 session=Path(s['hardware_trial_pending']);report=gate.flow.read_json(session/'report.json')
 gate.need(report['status']=='EXACT-FULL-FIRMWARE-CONTAINER-IN-RAM' and report['completed_chunks']==12 and report['native_counter']==61 and report['native_payload_sha256']==gate.PAYLOAD and report['policy']==policy and report['gate']==g and len(report['packets'])==12,'actual61 complete signed firmware')
 receipt=report['last_receipt'];gate.need(receipt['action']==4 and receipt['bitmap']==4095 and receipt['ready']==1 and receipt['peripheral'].upper()==decode.PEER,'actual complete firmware receipt')
 body=bytearray()
 for item in report['packets']:
  b=(session/gate.safe(item['file'])).read_bytes();v=assets61.observer.validate(b,public)
  gate.need(v=={k:x for k,x in item.items() if k!='file'} and v['generation']==61 and v['offset']==len(body),'immutable firmware signature/ordering')
  body.extend(b[224:])
 gate.need(len(body)==policy['total'] and gate.flow.sha(body)==policy['digest'],'exact full firmware container')
 capture_bytes=a.capture_log.read_bytes();raw_bytes=a.raw_log.read_bytes();raw=capture_from_logs(capture_bytes.decode(),raw_bytes.decode());decoded=decode.decode_capture(raw)
 found=bool(decoded['ssid_seen'] and decoded['pending_started'] and decoded['startup_ready_seen'] and decoded['startup_tx_complete'] and decoded['raw_beacon_matches_status'] and decoded['beacon']['ssid_hex']==b'SILK_56E35E_Plus'.hex())
 result={'status':'PHYSICAL61-OWNED-SSID-OBSERVED-RELEASE14' if found else 'PHYSICAL61-COMPLETE-SCAN-CAPTURE-NO-ACCEPTED-TARGET','generation':61,'payload_sha256':gate.PAYLOAD,'native_packet_sha256':gate.flow.sha(packet),'world_package_sha256':gate.WORLD,'asset_session':str(session),'raw_capture_sha256':gate.flow.sha(capture_bytes),'callback_log_sha256':gate.flow.sha(raw_bytes),'state_sha256':gate.flow.sha(state_bytes),'stable_statuses':3,'stable_raw_passes':2,'pages_per_pass':110,'target_SSID_observed':found,'scan_native_error':decoded['native_error'],'all14_released':True,'beacon':decoded.get('beacon'),'epoch':decoded['epoch'],'observation_completion':decoded['exports']['slots'][16]['completion'],'historical_scan_frequency':decoded['live_frequency'],'security_validated':False,'association':False,'credentials_read':False,'IP':False,'device_attestation':False,'physical_zero_TX_verified':False}
 gate.need(a.state.read_bytes()==state_bytes and a.capture_log.read_bytes()==capture_bytes and a.raw_log.read_bytes()==raw_bytes,'inputs changed during classification')
 gate.need(not a.output.exists(),'never overwrite prior classification');gate.flow.save(a.output,result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
