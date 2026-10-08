"""Synthetic host fixture; never physical evidence."""
import struct,hashlib
from pathlib import Path
import decode_htt as d
ROOT=Path(__file__).resolve().parent
CONTAINER=ROOT/'runs/public-fixture/firmware-6.bin'
def capture(major=3):
 firmware=CONTAINER.read_bytes();proof=d.firmware(firmware);v={k:0 for k in d.FIELDS};v.update(phase=3,stop_requested=1,profile_attempted=1,actual_released=1,submitted=1,dma_completed=1,version_seen=1,major=major,minor=1,endpoint=2,max_bytes=4096,binding_op=3,watermark=10,consumed=1,firmware_valid=1,htt_op=proof['htt_op'],wmi_op=4,htt_offset=proof['htt_offset'],main_offset=proof['main_offset'],main_bytes=proof['main_bytes'],generation_low=62,rx_phase=1,credit_available=8,credit_total=8,adapter_phase=12,cleanup_slot=14,life_phase=4,init_ready=1,init_dma=1,epoch_low=1,counter=62,stop_latched=1)
 status=b'QHTT0001'+struct.pack('<56I',*(v[k] for k in d.FIELDS))+bytes.fromhex(d.CONTAINER)+bytes.fromhex(proof['main_sha256'])+bytes(24);pages=[]
 for slot in range(6):
  payload=bytes([0,1,major,0]);raw=bytes([2,0,4,0,0,0,0,0])+payload if slot==0 else b'';fields=[slot,int(slot==0),int(slot==0),11 if slot==0 else 0,1,0,2 if slot==0 else 0,1 if slot==0 else 0,4 if slot==0 else 0,len(raw),int.from_bytes(payload,'little') if slot==0 else 0,0];record=b'QHTX0001'+struct.pack('<12I',*fields)+raw+bytes(2048-len(raw));pages.extend(record[i:i+512].hex() for i in range(0,2104,512))
 return {'format':'QHTT1-QHTX1','fixture_kind':'synthetic-host-only','peripheral':d.PEER,'writes':0,'status_hex':[status.hex()]*3,'pages_hex':[pages,pages.copy()]}
