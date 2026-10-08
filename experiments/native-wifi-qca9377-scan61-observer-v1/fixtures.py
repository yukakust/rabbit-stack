#!/usr/bin/env python3
"""Static fixtures/corruptions and Mac compile/preflight; NEVER --read."""
import copy,hashlib,json,pathlib,struct
import decode_scan as d

ROOT=d.ROOT
checks=0
def reject(fn,*args):
 global checks
 try:fn(*args)
 except (ValueError,TypeError,KeyError):checks+=1;return
 raise AssertionError('invalid observation accepted')
def status(released=True,observation=False):
 f=[0]*64
 if released:
  for name,value in dict(native_phase=4,quiesce_requested=1,actual_owners_released=1,coordinator_phase=4,
                        tx_phase=8,pending_phase=8,pending_result=2,pending_started=1,start_floor=20,
                        live_frequency=2437,owned_stop_phase=6,terminal_seen=1,terminal_completion=40,
                        credit_available=2,credit_total=2,adapter_phase=12,cleanup_slots=14,
                        lifecycle_phase=4,startup_ready_seen=1,startup_tx_complete=1).items():f[d.NAMES.index(name)]=value
 f[60]=61;f[61]=13
 if observation:f[29]=f[30]=1
 b=bytearray(b'QSCN0001'+struct.pack('<64I',*f)+b''.join(bytes.fromhex(x) for x in d.POLICY)+bytes(56))
 if observation:b[360]=16;b[364:380]=b'SILK_56E35E_Plus';b[396:402]=bytes([2,4,6,8,10,12])
 assert len(b)==416;return bytes(b)
def beacon():
 f=bytearray(36);struct.pack_into('<H',f,0,0x80);f[4:10]=b'\xff'*6;f[10:16]=f[16:22]=bytes([2,4,6,8,10,12]);struct.pack_into('<HH',f,32,100,17)
 f+=bytes([0,16])+b'SILK_56E35E_Plus'+bytes([3,1,6])
 return struct.pack('<IHH10IHH',0x7001,40,44,6,31,54000,7,len(f),0,19,20,21,22,len(f),17)+f
def pages(observation=False):
 out=[]
 for i in range(22):
  payload=beacon() if observation and i==16 else b''
  fields=(i,int(bool(payload)),25 if payload else 0,42,0,1 if payload else 0,2 if payload else 0,len(payload),0x7001 if payload else 0)
  b=b'QEXP0001'+struct.pack('<9I',*fields)+payload+bytes(2040-len(payload))
  out.extend(b[j:j+512].hex() for j in range(0,2084,512))
 return out
def capture(observation=False):
 s=status(observation=observation).hex();p=pages(observation)
 return dict(peripheral=d.PEER,writes=0,status_hex=[s]*3,pages_hex=[p,p.copy()],fixture_kind='SYNTHETIC-HOST-NOT-PHYSICAL')
