"""Read-only bounded bytes decoding; no signature/device-attestation claim."""
import struct,hashlib
FIELDS='phase error stop_requested profile_attempted actual_released submitted dma_completed version_seen major minor endpoint max_bytes binding_op watermark consumed archive_count firmware_valid firmware_error htt_op wmi_op htt_offset main_offset main_bytes generation_low generation_high rx_phase rx_error rx_completed rx_posts rx_count backpressure credit_available credit_outstanding credit_reserved credit_total mappings dma_users pci wake link irq pin bus access_count adapter_phase cleanup_slot life_phase life_error persistent_error polls init_ready init_dma epoch_low epoch_high counter stop_latched'.split()
assert len(FIELDS)==56
CONTAINER='8f8b002fccfe81d42238f27dd1f56d189604f180bd4772c7c8e75ae1fef16f01'
MAIN='57cbd474bda6a5e34e5e9e75ec5aba79f426f4a0b35719421c75f941ec693915'
def status(data):
 if len(data)!=320 or data[:8]!=b'QHTT0001' or any(data[296:]):raise ValueError('status framing/padding')
 d=dict(zip(FIELDS,struct.unpack_from('<56I',data,8)))
 if d['counter']!=55 or d['archive_count']>2 or d['rx_count']>2 or d['mappings']>14 or d['dma_users']>14:raise ValueError('status bounds')
 for k in 'stop_requested profile_attempted actual_released submitted dma_completed version_seen firmware_valid backpressure pci wake link irq pin bus init_ready init_dma stop_latched'.split():
  if d[k] not in (0,1):raise ValueError('boolean:'+k)
 d['generation']=d['generation_low']+(d['generation_high']<<32);d['epoch']=d['epoch_low']+(d['epoch_high']<<32)
 d['container_sha256']=data[232:264].hex();d['main_sha256']=data[264:296].hex()
 d['bounded_version_trial_pass']=all((d['phase']==3,not d['error'],d['stop_requested']==1,d['profile_attempted']==1,d['actual_released']==1,d['submitted']==1,d['dma_completed']==1,d['version_seen']==1,d['major'] in (2,3),d['minor']<=255,0<d['endpoint']<9,4<=d['max_bytes']<=4096,d['binding_op']==3,d['firmware_valid']==1,not d['firmware_error'],d['htt_op']==3,d['wmi_op']==4,12<=d['htt_offset']<=751432,12<=d['main_offset']<=751436-727125,d['main_bytes']==727125,d['generation']==55,d['container_sha256']==CONTAINER,d['main_sha256']==MAIN,d['rx_phase']==1,not d['rx_error'],d['credit_available']==d['credit_total'],not d['credit_outstanding'],not d['credit_reserved'],d['credit_total']>0,all(not d[k] for k in 'mappings dma_users pci wake link irq pin bus access_count'.split()),d['adapter_phase']==12,d['cleanup_slot']==14,d['life_phase']==4,not d['life_error'],not d['persistent_error'],d['init_ready']==1,d['init_dma']==1,d['epoch']>0,d['stop_latched']==1))
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
