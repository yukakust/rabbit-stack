"""Owned raw forensic snapshot; no physical verdict, credentials, RF or BLE."""
import struct,hashlib
import scan_decode as scan
from htc_codec import htc
TARGET=b'iPhone (9)';PEER=scan.PEER
FIELDS=('pipeline_phase pipeline_error filter_attempted filter_phase filter_error filter_step filter_tx_count filter_tx_completed echo_seen initial_floor echo_floor filter_last_rx echo_completion echo_raw_bytes echo_pipe echo_endpoint filter_tx_request filter_last_request filter_credit_serial echo_arg tx_phase tx_error tx_serial tx_request tx_attempted tx_completed htt_phase htt_error htt_attempted htt_dma_completed version_seen major minor version_floor version_completion htt_endpoint htt_max_bytes htt_op firmware_valid firmware_error generation_low generation_high epoch_low epoch_high actual_released held_buffers dma_users access_count pci_owned bus_owned wake_owned link_owned irq_owned boot_pin asset_pin adapter_phase cleanup_slots lifecycle_phase lifecycle_error generation service_count rx_error rx_completed persistent_error').split()
assert len(FIELDS)==64
OWNERS=FIELDS[45:55]
def pipeline(data,release=True):
 if len(data)!=448 or data[:8]!=b'QF630001':raise ValueError('QF63 exact448 framing')
 d=dict(zip(FIELDS,struct.unpack_from('<64I',data,8)));d['epoch']=d['epoch_low']+(d['epoch_high']<<32);d['firmware_generation']=d['generation_low']+(d['generation_high']<<32)
 if d['generation']!=63 or data[398]!=10 or data[399] or data[400:410]!=TARGET or any(data[410:432]) or data[440]!=1 or any(data[441:]):raise ValueError('compiled63 target/partial/reserved')
 for key in ('filter_attempted','filter_tx_completed','echo_seen','htt_attempted','htt_dma_completed','version_seen','firmware_valid','actual_released','pci_owned','bus_owned','wake_owned','link_owned','irq_owned','boot_pin','asset_pin'):
  if d[key] not in (0,1):raise ValueError('pipeline boolean '+key)
 if d['pipeline_phase']>5 or d['service_count']>128 or d['held_buffers']>14 or d['dma_users']>14 or d['access_count']>14:raise ValueError('pipeline enum/owners/service bounds')
 if d['actual_released'] and any(d[k] for k in OWNERS):raise ValueError('pipeline release contradicts owners')
 if release and (not d['actual_released'] or any(d[k] for k in OWNERS) or (d['adapter_phase'],d['cleanup_slots'],d['lifecycle_phase'])!=(12,14,4)):raise ValueError('actual all14 CLOSED required')
 words=struct.unpack_from('<32I',data,264)
 if d['service_count']<32 and any(words[d['service_count']:]):raise ValueError('service suffix padding')
 d['service_words_prefix']=words;d['service65_advertised']=bool(d['service_count']>16 and words[16]&2);d['base_mac_hex']=data[392:398].hex();d['echo_slot'],d['version_slot']=struct.unpack_from('<II',data,432);d['partial_startup']=True;d['physical_admission']=False;return d

def exports(pages,epoch):
 if len(pages)!=110:raise ValueError('110 complete pages')
 slots=[]
 for slot in range(22):
  parts=pages[slot*5:slot*5+5]
  if any(len(p)!=(56 if i==4 else 512) for i,p in enumerate(parts)):raise ValueError('QFEX page512/56')
  record=b''.join(parts)
  if record[:8]!=b'QFEX0001':raise ValueError('raw magic')
  idx,present,validated,completion,lo,hi,endpoint,pipe,payload_bytes,raw_bytes,event,error=struct.unpack_from('<12I',record,8);e=lo+(hi<<32)
  if idx!=slot or present not in (0,1) or validated not in (0,1) or payload_bytes>2040 or raw_bytes>2048 or e!=epoch:raise ValueError('raw metadata bounds/epoch')
  raw=record[56:56+raw_bytes]
  if any(record[56+raw_bytes:]):raise ValueError('raw zero padding')
  normalized=b''
  if present:
   if pipe not in (1,2) or not raw_bytes:raise ValueError('actual captured raw/pipe')
   if validated:
    if not completion or endpoint>=9 or error:raise ValueError('validated ownership')
    ep,normalized=htc(raw)
    expected_event=int.from_bytes(normalized[:4],'little') if pipe==2 and normalized else 0
    if ep!=endpoint or len(normalized)!=payload_bytes or (pipe==2 and normalized and len(normalized)<4) or event!=expected_event:raise ValueError('actual raw/body/pipe metadata join')
   elif slot!=17 or not error:raise ValueError('rejected diagnostics only slot17/error')
  elif any((validated,completion,endpoint,pipe,payload_bytes,raw_bytes,event,error)):raise ValueError('empty slot metadata')
  slots.append({'slot':slot,'present':bool(present),'validated':bool(validated),'completion':completion,'epoch':e,'endpoint':endpoint,'pipe':pipe,'payload_bytes':payload_bytes,'raw_bytes':raw_bytes,'event':event,'error':error,'raw_hex':raw.hex(),'payload_hex':normalized.hex(),'raw_sha256':hashlib.sha256(raw).hexdigest()})
 ids=[s['completion'] for s in slots if s['present'] and s['validated']]
 if len(ids)!=len(set(ids)):raise ValueError('duplicate accepted completion owners')
 return {'slots':slots,'record_sha256':hashlib.sha256(b''.join(pages)).hexdigest()}
def decode_capture(raw):
 if raw.get('format')!='QF631-QSCN1-QFEX1' or raw.get('peripheral','').upper()!=PEER or type(raw.get('writes')) is not int or raw['writes']!=0:raise ValueError('format/known-peer/zero writes')
 def stable(name):
  v=[bytes.fromhex(x) for x in raw[name]]
  if len(v)!=3 or any(x!=v[0] for x in v):raise ValueError('three stable '+name)
  return v[0]
 p=pipeline(stable('pipeline_hex'));s=scan.decode_status(stable('status_hex'));passes=raw['pages_hex']
 if len(passes)!=2 or passes[0]!=passes[1]:raise ValueError('two stable raw passes')
 if s['lifecycle_phase']!=4 or p['epoch']==0:raise ValueError('scan CLOSED/actual epoch')
 x=exports([bytes.fromhex(h) for h in passes[0]],p['epoch']);slots=x['slots'];expected=[i<s['archive_count'] for i in range(16)]+[bool(s['has_observation']),bool(s['has_orphan'])]+[i<s['dispatcher_count'] for i in range(2)]+[i<s['rx_queue_count'] for i in range(2)]
 if [z['present'] for z in slots]!=expected:raise ValueError('actual owner graph/status counts')
 if p['rx_completed']!=s['rx_completed'] or p['rx_error']!=s['rx_error']:raise ValueError('pipeline/scan sameRX owner snapshot')
 for z in slots:
  if z['present'] and z['validated'] and z['completion']>p['rx_completed']:raise ValueError('accepted completion beyond actualRX')
  if z['present'] and not z['validated']:
   if z['completion']!=p['rx_completed']+1 or z['error']!=p['rx_error'] or z['payload_bytes'] or z['event'] or z['raw_bytes']<8 or z['endpoint']!=bytes.fromhex(z['raw_hex'])[0]:raise ValueError('rejected actualRX metadata')

 p['owned_echo_verified']=False;p['owned_version_verified']=False
 if p['echo_seen']:
  if p['echo_slot']>=s['archive_count']:raise ValueError('echo archive slot')
  z=slots[p['echo_slot']];payload=bytes.fromhex(z['payload_hex'])
  if not z['validated'] or z['pipe']!=2 or z['endpoint']!=p['echo_endpoint'] or z['completion']!=p['echo_completion'] or z['completion']<=p['echo_floor'] or z['raw_bytes']!=p['echo_raw_bytes'] or p['echo_pipe']!=2 or len(payload)!=12 or struct.unpack('<III',payload)!=(0x1d001,4|(54<<16),p['echo_arg']):raise ValueError('owned exact ECHO reply/floor/argument')
  p['owned_echo_verified']=True
 if p['version_seen']:
  if p['version_slot']>=s['archive_count'] or p['version_slot']==p['echo_slot']:raise ValueError('version distinct archive slot')
  z=slots[p['version_slot']];payload=bytes.fromhex(z['payload_hex'])
  if not z['validated'] or z['pipe']!=1 or z['endpoint']!=p['htt_endpoint'] or z['completion']!=p['version_completion'] or z['completion']<=p['version_floor'] or len(payload)!=4 or payload[0] or payload[3] or (payload[2],payload[1])!=(p['major'],p['minor']) or payload[2] not in (2,3):raise ValueError('owned real VERSION3.56')
  p['owned_version_verified']=True
 beacon=None;s['raw_beacon_matches_status']=False
 if s['has_observation']:
  z=slots[16]
  if not z['validated'] or z['pipe']!=2 or z['endpoint']!=p['echo_endpoint'] or z['completion']<=s['start_floor']:raise ValueError('accepted observation provenance/floor')
  beacon=scan.parse_raw_beacon(bytes.fromhex(z['payload_hex']))
  if not s['pending_started'] or (beacon['ssid_hex'],beacon['bssid_hex'])!=(s['ssid_hex'],s['bssid_hex']) or beacon['frequency_mhz'] not in scan.POLICY_FREQUENCIES or (s['live_frequency'] and s['live_frequency']!=beacon['frequency_mhz']):raise ValueError('MGMT/status/frequency join')
  s['raw_beacon_matches_status']=True
 if s['ssid_seen'] and (beacon is None or beacon['hidden'] or beacon['ssid_hex']!=TARGET.hex()):raise ValueError('false requestedtarget flag')
 return {'pipeline':p,'scan':s,'exports':x,'beacon':beacon,'owned_filter_version_verified':bool(p['owned_echo_verified'] and p['owned_version_verified'] and p['filter_tx_count']==3 and p['filter_tx_completed']==1 and p['firmware_valid'] and not p['firmware_error'] and p['firmware_generation']==63 and p['htt_op']==3 and (p['major'],p['minor'])==(3,56)),'target_observed':bool(s['ssid_seen'] and s['raw_beacon_matches_status']),'pipeline_completed':bool(p['pipeline_phase']==4 and not any(p[k] for k in ('pipeline_error','filter_error','htt_error','firmware_error','lifecycle_error','rx_error','persistent_error')) and p['filter_phase']==7 and p['filter_step']==2 and p['htt_phase']==5 and p['htt_attempted']==p['htt_dma_completed']==1),'partial_startup':True,'association':False,'IP':False,'physical_admission':False}
