import struct
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
