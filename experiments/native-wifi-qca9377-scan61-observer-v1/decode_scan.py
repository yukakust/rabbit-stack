"""Pure native61 QSCN/status/export decoder. Never performs Bluetooth calls."""
import hashlib,importlib.util,pathlib,struct
ROOT=pathlib.Path(__file__).resolve().parent
PROFILE=ROOT.parent/'native-wifi-qca9377-scan-native-profile-v2' # unchanged pinned QEXP reconstruction codec, not61 candidate
PEER='F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF'
EXPORT_SHA='b794cf27f1916719f76b223c3ca03546ebe95e66df25cf84de147f0e2a20441b'  # Confirmed frozen profile-v2 reconstruction.
NAMES=('native_phase native_error stop_requested quiesce_requested actual_owners_released '
'coordinator_phase coordinator_error coordinator_stage coordinator_request tx_phase tx_error tx_request tx_attempted tx_completed '
'pending_phase pending_result pending_started last_event_type last_event_reason last_event_frequency last_event_request_id last_event_scan_id last_rx '
'start_floor live_frequency owned_stop_phase terminal_seen stop_tx_complete terminal_completion ssid_seen has_observation has_orphan dispatcher_count archive_count '
'rx_phase rx_error rx_completed rx_posted_count rx_queue_count backpressure credit_available credit_outstanding credit_reserved credit_total '
'held_buffers dma_users pci_owned wake_owned link_owned irq_owned pin_owned bus_owned access_count adapter_phase cleanup_slots '
'lifecycle_phase lifecycle_error persistent_error startup_ready_seen startup_tx_complete generation policy_count reserved0 reserved1').split()
POLICY=('a5ce1d3e2fdf8aefc2f862c77239cd2fbff1077371763c59c1b7a10d86ae3148',
 '7e236caecd939c8ec98be4870bf30422f28ffef2565a38aaaa2d9ddabd0c2641',
 '0789d74c4b8e2e788bf2e67296190b01673daf42274935a43f14335c47c96027')
POLICY_FREQUENCIES=frozenset(range(2412,2473,5))
OWNERS='held_buffers dma_users pci_owned wake_owned link_owned irq_owned pin_owned bus_owned access_count'.split()
def decode_status(data,require_release=True):
 if not isinstance(data,bytes) or len(data)!=416 or data[:8]!=b'QSCN0001':raise ValueError('exact QSCN1/416 envelope')
 d=dict(zip(NAMES,struct.unpack('<64I',data[8:264])))
 if (d['generation'],d['policy_count'],d['reserved0'],d['reserved1'])!=(61,13,0,0):raise ValueError('native61 generation/policy/reserved')
 for i,h in enumerate(POLICY):
  if data[264+32*i:296+32*i].hex()!=h:raise ValueError('exact reviewed ruleset/location policy binding')
 if any(data[361:364]) or any(data[402:]):raise ValueError('reserved byte suffix')
 for name in ('stop_requested quiesce_requested actual_owners_released pending_started terminal_seen stop_tx_complete ssid_seen has_observation has_orphan backpressure '
              'pci_owned wake_owned link_owned irq_owned pin_owned bus_owned startup_ready_seen startup_tx_complete').split():
  if d[name]>1:raise ValueError('invalid boolean '+name)
 for name,maximum in [('native_phase',5),('coordinator_phase',5),('tx_phase',8),('pending_phase',10),('pending_result',3),('rx_phase',3),
                       ('owned_stop_phase',7),('lifecycle_phase',5),('dispatcher_count',2),('archive_count',16),('rx_queue_count',2),('held_buffers',14),('dma_users',14),('access_count',14),('cleanup_slots',14)]:
  if d[name]>maximum:raise ValueError('bounded enum/owner/queue '+name)
 if any(d[n]>65535 for n in ['credit_available','credit_outstanding','credit_reserved','credit_total']):raise ValueError('credit bounds')
 if d['credit_available']+d['credit_outstanding']+d['credit_reserved']!=d['credit_total']:raise ValueError('credit conservation')
 if d['actual_owners_released'] and any(d[n] for n in OWNERS):raise ValueError('release contradicts actual owners')
 if require_release and (not d['actual_owners_released'] or d['adapter_phase']!=12 or d['cleanup_slots']!=14):raise ValueError('actual complete owner release required before pages')
 length=data[360]
 if length>32 or any(data[364+length:396]):raise ValueError('SSID bounds/padding')
 if not d['has_observation'] and (length or any(data[364:402])):raise ValueError('absent observation contains data')
 if d['ssid_seen'] and not(d['has_observation'] and d['pending_started']):raise ValueError('SSID flag lacks accepted scan/observation')
 d.update(ssid_hex=data[364:364+length].hex(),bssid_hex=data[396:402].hex(),status_sha256=hashlib.sha256(data).hexdigest(),
          wifi_connected=False,device_attestation=False)
 return d

def parse_raw_beacon(payload):
 """Independent secret-free check matching the frozen beacon adapter profile."""
 if len(payload)<4 or len(payload)>2040 or struct.unpack_from('<I',payload)[0]&0xffffff!=0x7001:raise ValueError('not supported raw MGMT')
 at=4;hdr=frame=None
 while at<len(payload):
  if len(payload)-at<4:raise ValueError('truncated TLV')
  n,tag=struct.unpack_from('<HH',payload,at);at+=4
  if n>len(payload)-at:raise ValueError('TLV overrun')
  v=payload[at:at+n];at+=n
  if tag==44:
   if hdr is not None or n!=40:raise ValueError('mgmt header profile')
   hdr=v
  elif tag==17:
   if frame is not None:raise ValueError('duplicate frame')
   frame=v
  else:raise ValueError('unsupported mgmt extension')
 if hdr is None or frame is None:raise ValueError('missing mgmt fields')
 channel,snr,rate,phy,n,status,*rssi=struct.unpack('<10I',hdr)
 if status or not 1<=channel<=13 or n<36 or n>len(frame) or len(frame) not in (n,(n+3)&~3) or any(frame[n:]):raise ValueError('mgmt status/channel/length')
 frame=frame[:n];fc,=struct.unpack_from('<H',frame)
 if fc&0xc707 or fc&0xfc not in (0x80,0x50) or struct.unpack_from('<H',frame,22)[0]&15:raise ValueError('not ordinary beacon/probe')
 sa,bssid=frame[10:16],frame[16:22]
 if sa!=bssid or not any(sa) or sa[0]&1:raise ValueError('BSSID/source')
 interval,caps=struct.unpack_from('<HH',frame,32)
 if not interval or not caps&1 or caps&2:raise ValueError('infrastructure capability')
 at=36;ssid=None;ds=ht=None;rsn=None
 while at<len(frame):
  if len(frame)-at<2:raise ValueError('IE header')
  tag,n=frame[at:at+2];at+=2
  if n>len(frame)-at:raise ValueError('IE overrun')
  v=frame[at:at+n];at+=n
  if tag==0:
   if ssid is not None or n>32:raise ValueError('SSID IE')
   ssid=v
  elif tag==3:
   if ds is not None or n!=1 or not v[0]:raise ValueError('DS IE')
   ds=v[0]
  elif tag==61:
   if ht is not None or n!=22 or not v[0]:raise ValueError('HT IE')
   ht=v[0]
  elif tag==48:
   if rsn is not None or not caps&16 or n<2 or v[:2]!=b'\1\0':raise ValueError('opaque RSN IE')
   rsn=v
 if ssid is None or (ds and ht and ds!=ht) or (ds or ht) not in (None,channel):raise ValueError('SSID/channel conflict')
 return dict(ssid_hex=ssid.hex(),bssid_hex=bssid.hex(),frequency_mhz=2407+5*channel,hidden=not any(ssid),
             raw_channel=channel,raw_snr=snr,raw_rate=rate,raw_phy_mode=phy,raw_rssi=rssi,security_validated=False)

def decode_capture(raw):
 if raw.get('peripheral','').upper()!=PEER or type(raw.get('writes')) is not int or raw['writes']!=0:raise ValueError('known peer/zero writes')
 statuses=[bytes.fromhex(x) for x in raw['status_hex']]
 if len(statuses)!=3 or any(x!=statuses[0] for x in statuses):raise ValueError('before/mid/after status not stable')
 d=decode_status(statuses[0]);passes=raw['pages_hex']
 if len(passes)!=2 or any(len(p)!=110 for p in passes) or passes[0]!=passes[1]:raise ValueError('two exact immutable110-page passes')
 pages=[bytes.fromhex(p) for p in passes[0]]
 if len(pages[0])<28:raise ValueError('first export page')
 lo,hi=struct.unpack_from('<2I',pages[0],20);epoch=lo+(hi<<32)
 path=PROFILE/'decode_exports.py'
 if hashlib.sha256(path.read_bytes()).hexdigest()!=EXPORT_SHA:raise ValueError('frozen export decoder changed')
 spec=importlib.util.spec_from_file_location('frozen_scan_exports',path)
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 exports=mod.reconstruct(pages,epoch)
 expected=[i<d['archive_count'] for i in range(16)]+[bool(d['has_observation']),bool(d['has_orphan'])]+[i<d['dispatcher_count'] for i in range(2)]+[i<d['rx_queue_count'] for i in range(2)]
 if [s['populated'] for s in exports['slots']]!=expected:raise ValueError('export owner graph/status counts differ')
 ids=[s['completion'] for s in exports['slots'] if s['populated']]
 if len(ids)!=len(set(ids)):raise ValueError('completion has duplicate retained owners')
 # Raw slot16 corresponds to the coordinator's retained accepted observation.
 d['raw_beacon_matches_status']=False;d['physical_ssid_discovered']=False
 if d['has_observation']:
  s=exports['slots'][16]
  if not s['populated'] or s['pipe']!=2 or s['endpoint']!=1 or s['completion']<=d['start_floor']:raise ValueError('observation missing owned WMI provenance/floor')
  b=parse_raw_beacon(bytes.fromhex(s['payload_hex']))
  if not d['pending_started'] or not epoch:raise ValueError('retained observation lacks STARTED/acquisition epoch')
  if (b['ssid_hex'],b['bssid_hex'])!=(d['ssid_hex'],d['bssid_hex']):raise ValueError('raw beacon/status identity mismatch')
  if b['frequency_mhz'] not in POLICY_FREQUENCIES:raise ValueError('retained observation outside exact13-channel policy')
  if d['live_frequency']:
   if b['frequency_mhz']!=d['live_frequency']:raise ValueError('active frequency/retained observation mismatch')
  elif not (d['quiesce_requested'] and d['actual_owners_released']):raise ValueError('zero live frequency without quiesced snapshot')
  # Terminal events clear live_frequency without erasing the owned observation.
  # Keep that zero in status; the beacon's own frequency is a separate field.
  d['raw_beacon_matches_status']=True;d['beacon']=b
  if d['ssid_seen'] and (b['hidden'] or b['ssid_hex']!=b'SILK_56E35E_Plus'.hex() or not d['pending_started']):raise ValueError('false requestedSSID flag')
 d['exports']=exports;d['epoch']=epoch;d['stable_capture']=True
 # The pure decoder does not turn a cached JSON fixture into physical evidence.
 return d
