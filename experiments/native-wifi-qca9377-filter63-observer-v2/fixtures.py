"""Explicit synthetic component bytes; never physical or source admission."""
import struct
import decode_filter as d
scan=d.scan
def frame(endpoint,payload,trailer=False):
 tail=bytes([1,4,0,0,1,1,0,0]) if trailer else b'';return bytes([endpoint,2 if tail else 0])+struct.pack('<H',len(payload)+len(tail))+bytes([len(tail),0,0,0])+payload+tail
def beacon():
 f=bytearray(36);struct.pack_into('<H',f,0,0x80);f[4:10]=b'\xff'*6;f[10:16]=f[16:22]=bytes([2,4,6,8,10,12]);struct.pack_into('<HH',f,32,100,17);f+=bytes([0,10])+d.TARGET+bytes([3,1,6]);return struct.pack('<IHH10IHH',0x7001,40,44,6,31,54000,7,len(f),0,19,20,21,22,len(f),17)+f
def capture(observation=True):
 s={k:0 for k in scan.NAMES};s.update(native_phase=4,quiesce_requested=1,actual_owners_released=1,coordinator_phase=4,tx_phase=8,tx_attempted=7,tx_completed=7,pending_phase=8,pending_result=2,pending_started=1,start_floor=20,owned_stop_phase=6,terminal_seen=1,terminal_completion=40,credit_available=8,credit_total=8,adapter_phase=12,cleanup_slots=14,lifecycle_phase=4,startup_ready_seen=1,startup_tx_complete=1,generation=63,policy_count=13,archive_count=3,rx_completed=40,ssid_seen=int(observation),has_observation=int(observation));status=bytearray(b'QSCN0001'+struct.pack('<64I',*(s[k] for k in scan.NAMES))+b''.join(bytes.fromhex(x) for x in scan.POLICY)+bytes(56))
 if observation:status[360]=10;status[364:374]=d.TARGET;status[396:402]=bytes([2,4,6,8,10,12])
 p={k:0 for k in d.FIELDS};p.update(pipeline_phase=4,filter_attempted=1,filter_phase=7,filter_step=2,filter_tx_count=3,filter_tx_completed=1,echo_seen=1,initial_floor=1,echo_floor=10,filter_last_rx=11,echo_completion=11,echo_pipe=2,echo_endpoint=1,echo_arg=0x63000001,tx_phase=8,tx_attempted=7,tx_completed=7,htt_phase=5,htt_attempted=1,htt_dma_completed=1,version_seen=1,major=3,minor=56,version_floor=11,version_completion=12,htt_endpoint=2,htt_max_bytes=4096,htt_op=3,firmware_valid=1,generation_low=63,epoch_low=42,actual_released=1,adapter_phase=12,cleanup_slots=14,lifecycle_phase=4,generation=63,service_count=32,rx_completed=40)
 owned={0:(11,2,frame(1,struct.pack('<III',0x1d001,4|(54<<16),p['echo_arg']),True)),1:(12,1,frame(2,bytes([0,56,3,0]),True)),2:(13,1,frame(0,b'',True))}
 if observation:owned[16]=(25,2,frame(1,beacon(),True))
 p['echo_raw_bytes']=len(owned[0][2]);pipeline=bytearray(b'QF630001'+struct.pack('<64I',*(p[k] for k in d.FIELDS))+bytes(184));struct.pack_into('<I',pipeline,264+16*4,2);pipeline[392:398]=bytes([2,4,6,8,10,12]);pipeline[398]=10;pipeline[400:410]=d.TARGET;struct.pack_into('<II',pipeline,432,0,1);pipeline[440]=1;pages=[]
 for slot in range(22):
  present=slot in owned;completion,pipe,raw=owned[slot] if present else (0,0,b'');ep,payload=d.htc(raw) if present else (0,b'');event=int.from_bytes(payload[:4],'little') if pipe==2 and payload else 0;fields=(slot,int(present),int(present),completion,42,0,ep,pipe,len(payload),len(raw),event,0);record=b'QFEX0001'+struct.pack('<12I',*fields)+raw+bytes(2048-len(raw));pages.extend(record[i:i+512].hex() for i in range(0,2104,512))
 return {'format':'QF631-QSCN1-QFEX1','peripheral':d.PEER,'writes':0,'pipeline_hex':[pipeline.hex()]*3,'status_hex':[status.hex()]*3,'pages_hex':[pages,pages.copy()],'fixture_kind':'SYNTHETIC NOT PHYSICAL'}
