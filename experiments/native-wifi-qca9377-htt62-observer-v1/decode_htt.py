"""Read-only bounded bytes decoding; no signature/device-attestation claim."""
import struct,hashlib
FIELDS='phase error stop_requested profile_attempted actual_released submitted dma_completed version_seen major minor endpoint max_bytes binding_op watermark consumed archive_count firmware_valid firmware_error htt_op wmi_op htt_offset main_offset main_bytes generation_low generation_high rx_phase rx_error rx_completed rx_posts rx_count backpressure credit_available credit_outstanding credit_reserved credit_total mappings dma_users pci wake link irq pin bus access_count adapter_phase cleanup_slot life_phase life_error persistent_error polls init_ready init_dma epoch_low epoch_high counter stop_latched'.split()
assert len(FIELDS)==56
CONTAINER='8f8b002fccfe81d42238f27dd1f56d189604f180bd4772c7c8e75ae1fef16f01'
MAIN='57cbd474bda6a5e34e5e9e75ec5aba79f426f4a0b35719421c75f941ec693915'
def status(data):
 if len(data)!=320 or data[:8]!=b'QHTT0001' or any(data[296:]):raise ValueError('status framing/padding')
 d=dict(zip(FIELDS,struct.unpack_from('<56I',data,8)))
 if d['counter']!=62 or d['archive_count']>2 or d['rx_count']>2 or d['mappings']>14 or d['dma_users']>14:raise ValueError('status bounds')
 for k in 'stop_requested profile_attempted actual_released submitted dma_completed version_seen firmware_valid backpressure pci wake link irq pin bus init_ready init_dma stop_latched'.split():
  if d[k] not in (0,1):raise ValueError('boolean:'+k)
 d['generation']=d['generation_low']+(d['generation_high']<<32);d['epoch']=d['epoch_low']+(d['epoch_high']<<32)
 d['container_sha256']=data[232:264].hex();d['main_sha256']=data[264:296].hex()
 d['bounded_version_trial_pass']=all((d['phase']==3,not d['error'],d['stop_requested']==1,d['profile_attempted']==1,d['actual_released']==1,d['submitted']==1,d['dma_completed']==1,d['version_seen']==1,d['major'] in (2,3),d['minor']<=255,0<d['endpoint']<9,4<=d['max_bytes']<=4096,d['binding_op']==3,d['firmware_valid']==1,not d['firmware_error'],d['htt_op']==3,d['wmi_op']==4,12<=d['htt_offset']<=751432,12<=d['main_offset']<=751436-727125,d['main_bytes']==727125,d['generation']==62,d['container_sha256']==CONTAINER,d['main_sha256']==MAIN,d['rx_phase']==1,not d['rx_error'],d['credit_available']==d['credit_total'],not d['credit_outstanding'],not d['credit_reserved'],d['credit_total']>0,all(not d[k] for k in 'mappings dma_users pci wake link irq pin bus access_count'.split()),d['adapter_phase']==12,d['cleanup_slot']==14,d['life_phase']==4,not d['life_error'],not d['persistent_error'],d['init_ready']==1,d['init_dma']==1,d['epoch']>0,d['stop_latched']==1))
 d['device_attestation']=False;d['htt_dataplane_ready']=False;d['wifi_connected']=False
 return d
def exports(pages,epoch=None):
 if len(pages)!=30:raise ValueError('all30 exact pages required')
 for i,p in enumerate(pages):
  if len(p)!=(56 if i%5==4 else 512):raise ValueError('page length')
 out=[]
 for slot in range(6):
  record=b''.join(pages[slot*5:slot*5+5])
  if record[:8]!=b'QHTX0001':raise ValueError('raw magic')
  v=struct.unpack_from('<12I',record,8);i,present,validated,completion,lo,hi,endpoint,pipe,payload,n,event,error=v;e=lo+(hi<<32)
  if i!=slot or present not in (0,1) or validated not in (0,1) or payload>2040 or n>2048:raise ValueError('record bounds')
  if epoch is not None and e!=epoch:raise ValueError('epoch mismatch')
  if present:
   if not completion or not e or n<8 or pipe not in (1,2) or validated!=(slot!=5):raise ValueError('owned raw metadata')
   if validated and endpoint>=9:raise ValueError('validated endpoint')
   if record[56]!=endpoint:raise ValueError('raw endpoint differs')
  elif any((validated,completion,endpoint,pipe,payload,n,event)):raise ValueError('absent slot metadata')
  if any(record[56+n:]):raise ValueError('raw padding')
  raw=record[56:56+n]
  out.append({'slot':slot,'present':bool(present),'htc_validated':bool(validated),'completion':completion,'epoch':e,'endpoint':endpoint,'pipe':pipe,'payload_bytes':payload,'raw_bytes':n,'event':event,'rx_error':error,'record_sha256':hashlib.sha256(record).hexdigest(),'raw_sha256':hashlib.sha256(raw).hexdigest(),'raw_hex':raw.hex()})
 return {'slots':out,'all_records_sha256':hashlib.sha256(b''.join(pages)).hexdigest(),'device_attestation':False,'wifi_connected':False}
PEER='F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF'
def firmware(container):
 if len(container)!=751436 or hashlib.sha256(container).hexdigest()!=CONTAINER or container[:11]!=b'QCA-ATH10K\0':raise ValueError('exact public firmware container')
 pos=12;ies={}
 while pos<len(container):
  if len(container)-pos<8:raise ValueError('IE header')
  tag,n=struct.unpack_from('<II',container,pos);pos+=8
  if tag>6 or tag in ies or pos+((n+3)&~3)>len(container):raise ValueError('IE bounds/duplicates')
  ies[tag]=(pos,container[pos:pos+n]);pos+=(n+3)&~3
 if not all(i in ies for i in (3,4,5,6)) or len(ies[5][1])!=4 or len(ies[6][1])!=4 or struct.unpack('<I',ies[5][1])[0]!=4 or len(ies[3][1])!=727125 or len(ies[4][1])!=24193:raise ValueError('firmware IE profile')
 return {'htt_op':struct.unpack('<I',ies[6][1])[0],'htt_offset':ies[6][0],'main_offset':ies[3][0],'main_bytes':len(ies[3][1]),'main_sha256':hashlib.sha256(ies[3][1]).hexdigest()}
def htc(raw):
 if not 8<=len(raw)<=4096 or raw[0]>=9 or raw[1]&~3 or struct.unpack_from('<H',raw,2)[0]!=len(raw)-8:raise ValueError('HTC envelope')
 trailer=raw[4] if raw[1]&2 else 0
 if (not raw[1]&2 and raw[4]) or (raw[1]&2 and trailer<4) or trailer>len(raw)-8:raise ValueError('HTC trailer')
 at=len(raw)-trailer
 while at<len(raw):
  if len(raw)-at<4:raise ValueError('trailer header')
  tag,n=raw[at:at+2];at+=4
  if n>len(raw)-at or tag not in (0,1,2,3):raise ValueError('trailer bounds/tag')
  if tag==1 and (not n or n%4 or any(raw[at+i]>=9 for i in range(0,n,4))):raise ValueError('credit trailer')
  if tag==2 and n!=12 or tag==3 and (not n or n%4 or n>128):raise ValueError('trailer profile')
  at+=n
 return raw[0],raw[8:len(raw)-trailer if trailer else len(raw)]
def decode_capture(raw,container=None):
 if raw.get('peripheral','').upper()!=PEER or type(raw.get('writes')) is not int or raw['writes']!=0:raise ValueError('known peer/zero writes')
 statuses=[bytes.fromhex(x) for x in raw['status_hex']]
 if len(statuses)!=3 or any(x!=statuses[0] for x in statuses):raise ValueError('three stable statuses')
 d=status(statuses[0]);owners='mappings dma_users pci wake link irq pin bus access_count'.split()
 if not d['actual_released'] or any(d[k] for k in owners) or d['adapter_phase']!=12 or d['cleanup_slot']!=14 or d['life_phase']!=4:raise ValueError('all14 actual release required')
 if d['credit_available']+d['credit_outstanding']+d['credit_reserved']!=d['credit_total'] or any(d[k]>65535 for k in ('credit_available','credit_outstanding','credit_reserved','credit_total')):raise ValueError('credit conservation')
 passes=raw['pages_hex']
 if len(passes)!=2 or passes[0]!=passes[1]:raise ValueError('two stable raw passes')
 x=exports([bytes.fromhex(p) for p in passes[0]],d['epoch']);slots=x['slots'];ids=[s['completion'] for s in slots if s['present']]
 if len(ids)!=len(set(ids)) or sum(s['present'] for s in slots[1:3])!=d['archive_count'] or sum(s['present'] for s in slots[3:5])!=d['rx_count']:raise ValueError('owned graph counts/duplicate completion')
 for s in slots[:5]:
  if s['present']:
   ep,p=htc(bytes.fromhex(s['raw_hex']))
   if ep!=s['endpoint'] or len(p)!=s['payload_bytes'] or int.from_bytes(p[:4],'little')!=s['event']:raise ValueError('HTC raw metadata join')
 d['raw_version_verified']=False;d['authenticated_IE6_verified']=False
 if d['version_seen']:
  s=slots[0]
  if not s['present'] or s['pipe']!=1 or s['endpoint']!=d['endpoint'] or s['completion']<=d['watermark']:raise ValueError('VERSION ownership/floor')
  ep,p=htc(bytes.fromhex(s['raw_hex']))
  if len(p)!=4 or p[0] or p[3] or p[2] not in (2,3) or (p[2],p[1])!=(d['major'],d['minor']):raise ValueError('actual VERSION_CONF bytes')
  d['raw_version_verified']=True
 if container is not None:
  f=firmware(container)
  if any(d[k]!=v for k,v in f.items()):raise ValueError('actual firmware IE6/status mismatch')
  d['authenticated_IE6_verified']=True
 d['version_only_pass']=bool(d['bounded_version_trial_pass'] and d['raw_version_verified'] and d['authenticated_IE6_verified']);d['exports']=x;d['physical_admission']=False;return d
