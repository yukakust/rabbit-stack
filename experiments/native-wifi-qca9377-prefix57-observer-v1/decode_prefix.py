"""Prefix57 bounded snapshot parser. No BLE, state, secrets or device attestation."""
import hashlib,json,struct,re
PEER='F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF'
sha=lambda b:hashlib.sha256(b).hexdigest()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def pairs(items):
 out={}
 for k,v in items:need(k not in out,'duplicate JSON key');out[k]=v
 return out
def loads(raw):
 need(len(raw)<=100000,'capture JSON bound')
 return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('nonfinite JSON')))
def blob(s,n):
 need(isinstance(s,str) and len(s)==2*n and re.fullmatch('[0-9a-f]+',s),'exact bounded hex');return bytes.fromhex(s)
def critical(e):
 return e[0] in (5,16) or (e[0]==62 and len(e)>=3 and e[2]==1) or (e[0]==14 and len(e)>=6 and e[5]!=0) or (e[0]==15 and len(e)>=6 and e[2]!=0)
def status(data):
 need(len(data)==240 and data[:8]==b'QPFX0001','status magic/size');w=struct.unpack_from('<58I',data,8)
 need(w[0]==57 and w[1]==3 and w[4]==1 and w[20]==12 and w[21]==14,'actual57 all14 released')
 need(all(w[i]==0 for i in range(22,33)),'retained owner')
 need(w[2]<=6 and w[3]>0,'bounded stop reason/actual cleanup attempts')
 need(w[48]<=16 and w[50]==0,'status bounds/USB fault')
 need(w[2]==2 or (w[57]<<32|w[56]) >= (w[55]<<32|w[54]),'unreported status time rollback')
 return w

def decode_capture(c):
 need(isinstance(c,dict) and c.get('format')=='QPFX1-QPHCI1','complete capture format')
 need(c.get('peripheral')==PEER and type(c.get('writes')) is int and c['writes']==0 and c.get('device_attestation') is False,'known peer zero writes/not attestation')
 ss=c.get('status_hex');pp=c.get('pages_hex')
 need(isinstance(ss,list) and len(ss)==3,'three status reads')
 words=[status(blob(s,240)) for s in ss];w=words[0]
 frozen=tuple(range(33))+(48,49,54,55,56,57)
 need(all(tuple(v[i] for i in frozen)==tuple(w[i] for i in frozen) for v in words),'status frozen invariants changed')
 need(isinstance(pp,list) and len(pp)==2 and all(isinstance(p,list) and len(p)==10 for p in pp) and pp[0]==pp[1],'two identical ten-page passes')
 raw=b''.join(blob(p,512 if i<9 else 64) for i,p in enumerate(pp[0]));need(len(raw)==4672 and raw[:8]==b'QPHCI001','raw magic/size')
 h=struct.unpack_from('<14I',raw,8)
 need(h[0]==57 and h[1]==w[48] and h[2]==w[49] and h[3]==1 and h[4]==3 and h[5]==4672,'raw/status frozen identity')
 cc,rc,head,over=h[6:10];need(cc<=4 and rc<=12 and h[1]==cc+rc and head<12,'ring bounds')
 need((rc==12 or (head==rc and over==0)) and (over==0 or rc==12),'ring overwrite/head bounds')
 need((h[2]==0 or cc==4) and tuple(h[10:])==tuple(w[54:58]),'overflow/time correlation')
 start=h[11]<<32|h[10];last=h[13]<<32|h[12];events=[];previous=[None,None]
 for i in range(16):
  r=raw[64+i*288:64+(i+1)*288];valid=i<cc if i<4 else i-4<rc
  if not valid:need(r==bytes(288),'unused record nonzero');continue
  at,n,state,pending,crit=struct.unpack_from('<Q4I',r)
  need(2<=n<=257 and (w[2]==2 or at>=start),'event length/time bounds');e=r[24:24+n]
  need(n==2+e[1] and r[24+n:]==bytes(288-24-n),'HCI length/zero tail')
  need(crit==int(i<4) and bool(crit)==critical(e),'critical predicate/partition')
  partition=int(i>=4);need(w[2]==2 or previous[partition] is None or at>=previous[partition],'partition chronological order');previous[partition]=at
  events.append({'slot':i,'at_us':at,'length':n,'pre_dispatch_ble_state':state,'pending':pending,'critical':bool(crit),'event_hex':e.hex()})
 return {'capture_origin':'HOST-FIXTURE-NEVER-PHYSICAL' if 'fixture_kind' in c else 'UNAUTHENTICATED-CAPTURE-INPUT','status':'STABLE-PREFIX57-FROZEN-ALL14-RELEASED-SNAPSHOT','native_counter':57,'all14_release_exported':True,'device_attestation':False,'bounded_history_only':True,'raw_sha256':sha(raw),'stop_reason':w[2],'stop_offset':w[5],'critical_overflow':h[2],'routine_overwritten':over,'events':events,'wifi_connected_claimed':False,'context_verified':False,'status_live_telemetry_preserved':[list(v[33:48])+list(v[50:54]) for v in words]}
