"""Pure exact-byte export reconstruction; no radio/state or ACK operations."""
import struct,hashlib
def reconstruct(pages,expected_epoch):
 if len(pages)!=110:raise ValueError('all110 immutable pages required')
 slots=[]
 for slot in range(22):
  part=pages[slot*5:slot*5+5]
  if any(len(p)!=512 for p in part[:4]) or len(part[4])!=36:raise ValueError('fixed page bounds')
  raw=b''.join(part)
  if len(raw)!=2084 or raw[:8]!=b'QEXP0001':raise ValueError('export envelope')
  index,populated,completion,lo,hi,endpoint,pipe,n,event=struct.unpack('<9I',raw[8:44])
  if index!=slot or populated>1 or lo+(hi<<32)!=expected_epoch:raise ValueError('slot/epoch binding')
  payload=raw[44:]
  if populated:
   if not completion or not n or n>2040 or endpoint>8 or pipe not in (1,2) or any(payload[n:]):raise ValueError('owned payload bounds')
   if pipe==2 and (n<4 or struct.unpack('<I',payload[:4])[0]!=event):raise ValueError('event word differs')
  elif any((completion,endpoint,pipe,n,event)) or any(payload):raise ValueError('empty slot contains data')
  slots.append({'slot':slot,'populated':bool(populated),'completion':completion,'epoch':expected_epoch,'endpoint':endpoint,
                'pipe':pipe,'payload_bytes':n,'event':event,'payload_hex':payload[:n].hex(),'export_sha256':hashlib.sha256(raw).hexdigest()})
 return {'format':'QEXP1','slots':slots,'all_pages_sha256':hashlib.sha256(b''.join(pages)).hexdigest(),'device_attestation':False}
