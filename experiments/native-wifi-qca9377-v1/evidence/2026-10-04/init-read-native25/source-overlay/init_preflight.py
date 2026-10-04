#!/usr/bin/env python3
"""Check observed ROM initialization destinations. Never writes/signs/sends."""
import argparse,copy,hashlib,json
from pathlib import Path
from decode_diagnostic import decode
PERIPHERAL='F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF'
def checked_destinations(d):
 c=d['initial_config_read'];b=d['bmi_probe']
 if not c['read_completed'] or c['read_mask']!=7 or c['fixed_state_address']!='00401ee0':raise ValueError('complete fixed initialization read required')
 if d['reset_probe']['chip_id']!='003821ff' or d['reset_probe']['chip_revision']!=1:raise ValueError('unknown chip')
 if not b['cleanup_completed'] or b['dma_buffers_held'] or b['bus_owned'] or d['pcie_link']['owned']:raise ValueError('cleanup required before preparing next operation')
 words=[int(s,16) for s in c['state_words']];early=int(c['early_alloc'],16);flag2=int(c['option_flag2'],16)
 if len(words)!=9 or any(v==0xffffffff for v in (words[8],early,flag2)):raise ValueError('unusable initialization flags')
 if flag2&0x10:raise ValueError('early configuration already committed; reset/revalidation required')
 if early>>16 not in (0,0x6d8a):raise ValueError('unknown early allocation signature')
 # Conservative finite authorization window, not a claim about total RAM size.
 spans={'pipe_config':(words[0],10*24),'service_map':(words[1],17*12)}
 reserved={'pcie_state':(0x401ee0,36),'host_interest':(0x400800,0x124)}
 for name,(address,size) in spans.items():
  if address&3 or address<0x400000 or address>0x410000-size:raise ValueError('invalid bounded destination: '+name)
 allspans={**spans,**reserved};items=list(allspans.items())
 for i,(name,(address,size)) in enumerate(items):
  for other,(base,n) in items[i+1:]:
   if address<base+n and base<address+size:raise ValueError('overlapping destinations: '+name+'/'+other)
 return {'status':'INITIAL-CONFIG-SPANS-VALIDATED-TARGET-WRITES-DISABLED',
  'target_tables':{n:{'address':f'{a:08x}','bytes':s} for n,(a,s) in spans.items()},
  'config_flags':{'address':'00401f00','observed':f'{words[8]:08x}','candidate':f'{words[8]&~1:08x}'},
  'early_alloc':{'address':'00400900','observed':f'{early:08x}','candidate':f'{early|0x6d8a0009:08x}'},
  'option_flag2':{'address':'004008cc','observed':f'{flag2:08x}','commit_mask':'00000010','commit_enabled':False},
  'table_sizes_reference':'pinned pci.c:10 ce_pipe_config records24bytes;17 ce_service_to_pipe records12bytes',
  'authorization_window':['00400000','00410000'],'configuration_contents_verified':False,
  'target_tables_generated':False,'warm_reset_sequence_verified':False,'target_writes_enabled':False,
  'firmware_compatibility_verified':False,'wifi_association_verified':False,'device_attestation':False}
def rejection_checks(d):
 for value in (0,0xffffffff,0x402001,0x3ffffc,0x40fff0,0x401ee0,0x400800):
  bad=copy.deepcopy(d);bad['initial_config_read']['state_words'][0]=f'{value:08x}'
  try:checked_destinations(bad)
  except ValueError:pass
  else:raise AssertionError('unsafe destination accepted')
 bad=copy.deepcopy(d);bad['initial_config_read']['state_words'][1]=bad['initial_config_read']['state_words'][0]
 try:checked_destinations(bad)
 except ValueError:pass
 else:raise AssertionError('overlapping tables accepted')
 for field,value in (('option_flag2','00000010'),('early_alloc','ffffffff')):
  bad=copy.deepcopy(d);bad['initial_config_read'][field]=value
  try:checked_destinations(bad)
  except ValueError:pass
  else:raise AssertionError('unsafe initialization state accepted')
 return 10
def main():
 p=argparse.ArgumentParser();p.add_argument('--raw',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);p.add_argument('--state',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 if a.raw.stat().st_size>4096 or a.receipt.stat().st_size>65536:raise ValueError('oversized evidence')
 raw=json.loads(a.raw.read_text());receipt=json.loads(a.receipt.read_text());state=json.loads(a.state.read_text())
 if raw.get('format') not in ('QPD12','QPD13') or raw.get('peripheral')!=PERIPHERAL:raise ValueError('known physical QPD12/13 required')
 if (receipt['status']!='EXACT-APPLIED-RECEIPT' or not receipt['receiver_reported_applied']
  or receipt['counter']!=state['engine']['native_counter'] or receipt['payload_sha256']!=state['engine']['payload_sha256']
  or receipt['base_world_sha256']!=state['world_sha256'] or state.get('native_pending') or state.get('recovery_pending') or state.get('pending')):raise ValueError('exact current applied receipt/current world required')
 d=decode(raw);out=checked_destinations(d);out.update(counter=receipt['counter'],payload_sha256=receipt['payload_sha256'],world_sha256=state['world_sha256'],
  raw_sha256=hashlib.sha256(a.raw.read_bytes()).hexdigest(),receipt_sha256=hashlib.sha256(a.receipt.read_bytes()).hexdigest(),negative_cases=rejection_checks(d),
  verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
 a.output.write_text(json.dumps(out,indent=2)+'\n');print(out['status'])
if __name__=='__main__':main()
