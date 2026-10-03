#!/usr/bin/env python3
"""Interpret a bounded read-only PCI report; never infers BMI/firmware support."""
import argparse,json,struct
from pathlib import Path
def decode(value):
 version=1 if value.get('format')=='QPD1' else 2 if value.get('format')=='QPD2' else 0
 length=128 if version==1 else 160
 if not version or not isinstance(value.get('raw_hex'),str) or len(value['raw_hex'])!=length*2:
  raise ValueError('bounded QPD1 envelope required')
 raw=bytes.fromhex(value['raw_hex'])
 if len(raw)!=length or raw[:4]!=b'QPD'+bytes([version]):raise ValueError('invalid QPD bytes')
 flags,count,targets=struct.unpack_from('<I',raw,4)[0],struct.unpack_from('<I',raw,16)[0],struct.unpack_from('<I',raw,20)[0]
 enum_status,read_status,location_status=struct.unpack_from('<Q',raw,8)[0],struct.unpack_from('<Q',raw,24)[0],struct.unpack_from('<Q',raw,32)[0]
 if flags&~63 or any(raw[60:64]):raise ValueError('unknown flags/reserved bytes')
 config=list(struct.unpack_from('<16I',raw,64));bdf=list(struct.unpack_from('<4I',raw,40))
 result={'format':'QPD'+str(version),'device_attestation':False,'flags':flags,'enum_status':f'{enum_status:016x}',
  'handle_count':count,'target_count':targets,'read_status':f'{read_status:016x}',
  'location_status':f'{location_status:016x}','bdf':bdf,'config_words':[f'{n:08x}' for n in config],
  'physical_identity_usable':False,'wifi_association_verified':False,'bmi_target_version':None}
 if flags&2:
  result.update(vendor=f'{config[0]&65535:04x}',device=f'{config[0]>>16:04x}',
   subsystem_vendor=f'{config[11]&65535:04x}',subsystem_device=f'{config[11]>>16:04x}',
   pci_revision=config[2]&255,command=f'{config[1]&65535:04x}',bar0_raw=f'{config[4]:08x}')
  usable=(flags==15 and not enum_status and targets==1 and count<=64 and config[0]==0x0042168c
   and config[2]>>16==0x0280 and (config[3]>>16)&127==0 and not location_status
   and bdf[0]<=65535 and bdf[1]<=255 and bdf[2]<=31 and bdf[3]<=7)
  result['physical_identity_usable']=usable
  if usable:
   result['board_catalog_candidate']=f'bus=pci,vendor=168c,device=0042,subsystem-vendor={config[11]&65535:04x},subsystem-device={config[11]>>16:04x}'
   result['bar0']=f'{((config[5]<<32) if config[4]&6==4 else 0)|(config[4]&0xfffffff0):016x}'
 if version==2:
  stage,chip,error,cleanup,extent,attributes=struct.unpack_from('<IIIIQQ',raw,128)
  if stage>4 or cleanup not in (1,2):raise ValueError('invalid bringup state')
  result['wake_probe']={'stage':stage,'chip_id':f'{chip:08x}','error':error,'cleanup_completed':cleanup==1,
   'bar_extent':extent,'original_attributes':f'{attributes:016x}',
   'chip_revision':(chip>>8)&15 if stage==2 else None,
   'probe_succeeded':stage==2 and not error and cleanup==1,'dma_enabled':False,'firmware_uploaded':False}
 return result
def main():
 p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
 if a.input.stat().st_size>4096:raise ValueError('oversized report')
 result=decode(json.loads(a.input.read_text()));text=json.dumps(result,indent=2)+'\n'
 if a.output:a.output.write_text(text)
 print(text,end='')
if __name__=='__main__':main()
