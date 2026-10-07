"""Preserve exact physical54 failure/exports; release hardware owner only."""
from pathlib import Path
import sys,json,hashlib,struct,subprocess,shutil
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent.parent
sys.path.insert(0,str(REPO/'experiments/native-wifi-qca9377-scan-observer-v2'));import collect,decode_scan
sys.path.insert(0,str(REPO/'experiments/native-wifi-qca9377-scan-admission-v1'));import scan_route as route
STATE=REPO/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with route.flow.state_lock(STATE):
 if subprocess.run(['ps','-p','52976','-o','pid='],capture_output=True,text=True).stdout.strip():raise ValueError('old controller still live')
 s=route.flow.read_json(STATE)
 if any(s.get(k) for k in ('pending','native_pending','recovery_pending')) or s['engine']['native_counter']!=54 or s['engine']['payload_sha256']!=route.PAYLOAD_SHA:raise ValueError('exact54 state required')
 assets=Path(s['hardware_trial_pending'])
 if assets.name!='firmware-ram-g9g89amj':raise ValueError('exact54 asset session required')
 ar=route.flow.read_json(assets/'report.json');collect.validate_saved_assets(ar,assets)
 cpath=route.PROFILE/'runs/checked-candidate/report.json';receipt=route.flow.read_json(Path(s['engine']['last_release_report']))
 collect.admission(s,receipt,collect.load(cpath),sha(cpath));route.current_assets(s,Path(ar['checked_directory']))
 capture=REPO/'experiments/native-wifi-qca9377-scan-observer-v1/runs/control/scan54-capture.json';raw=collect.load(capture);d=decode_scan.decode_capture(raw)
 boot=route.ROOT/'runs/control/boot54.json';b=json.loads(boot.read_text());payload=bytes.fromhex(b['raw_hex'])
 if b.get('peripheral','').upper()!=route.PEER or b.get('writes')!=0 or len(payload)!=160 or payload[:8]!=b'QWBT0001':raise ValueError('exact known-peer BOOT release required')
 fields=struct.unpack('<30I',payload[8:128])
 if fields!=(5,0,20,0,3114,3114,4202432,3,0,20,2,1792,4,1,0,0,0,0,6,8448,12,14,0,84017153,8,5,0,0,0,1):raise ValueError('exact controlled-stop all14/RAM-release required')
 if not d['actual_owners_released'] or d['lifecycle_phase']!=4 or d['lifecycle_error'] or d['persistent_error'] or d['startup_ready_seen']!=1 or d['startup_tx_complete']!=1:raise ValueError('actual lifecycle/READY release required')
 if (d['native_phase'],d['native_error'],d['coordinator_phase'],d['coordinator_error'],d['coordinator_stage'],d['tx_attempted'],d['tx_completed'],d['pending_started'],d['owned_stop_phase'],d['terminal_seen'],d['stop_tx_complete'])!=(5,6,5,15,5,5,5,0,7,0,1):raise ValueError('exact failed scan/timeout diagnostic required')
 events=[]
 for slot in d['exports']['slots']:
  if not slot['populated'] or slot['event']!=0x3001:continue
  p=bytes.fromhex(slot['payload_hex'])
  if len(p)!=36 or struct.unpack('<HH',p[4:8])!=(28,36):raise ValueError('exact physical event extension required')
  v=struct.unpack('<7I',p[8:36]);events.append({'completion':slot['completion'],'type':v[0],'opaque_reason':v[1],'frequency':v[2],'request':v[3],'scan':v[4],'vdev':v[5],'suffix_hex':p[32:].hex()})
 if [(x['type'],x['opaque_reason'],x['frequency'],x['request'],x['scan'],x['vdev']) for x in events]!=[(1,6,0,0xa008,0xa007,0),(8,6,2412,0xa008,0xa007,0)]:raise ValueError('actual matching STARTED/FOREIGN bytes required')
 e=ROOT/'evidence/2026-10-07';e.mkdir(parents=True,exist_ok=True)
 for p,n in ((capture,'capture54.json'),(capture.with_suffix('.decoded.json'),'capture54-v1.decoded.json'),(capture.with_suffix('.log'),'capture54.log'),(boot,'boot54.json'),(boot.with_suffix('.decoded.json'),'boot54.decoded.json'),(Path(s['engine']['last_release_report']),'native54-receipt.json'),(assets/'report.json','asset54-report.json')):shutil.copy2(p,e/n)
 collect.save(e/'capture54-v2.decoded.json',d)
 result={'status':'PHYSICAL54-SCAN-DISPATCH-FAULT-RAW-PRESERVED-ALL-OWNERS-RELEASED','native_counter':54,'native_payload_sha256':route.PAYLOAD_SHA,'all_raw_pages_saved_twice':True,'all_hardware_owners_released':True,'firmware_matching_started_observed':True,'firmware_matching_channel_observed':2412,'firmware_events':events,'native_started_processed':False,'physical_ssid_discovered':False,'wifi_connected':False,'ip_verified':False,'device_attestation':False,'cause':'two archive slots full of retained boot/debug traffic blocked dispatcher; owned STOP deadline fault. Independent scan codec incompatibility: actual28-byte prefix/nonterminal opaque reason6 versus old exact24/reason checks.','files_sha256':{p.name:sha(p) for p in e.iterdir() if p.is_file()}}
 collect.save(e/'result54.json',result);ar.update(scan_result=str(e/'result54.json'),scan_result_sha256=sha(e/'result54.json'),raw_export_capture_sha256=sha(capture),all_raw_pages_saved_twice=True,all_hardware_owners_released=True);route.flow.save(assets/'report.json',ar);s['hardware_trial_pending']=None;route.flow.save(STATE,s)
 print(json.dumps({k:result[k] for k in ('status','firmware_matching_started_observed','native_started_processed','physical_ssid_discovered','all_hardware_owners_released')}))
