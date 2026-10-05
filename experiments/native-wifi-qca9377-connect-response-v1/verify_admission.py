#!/usr/bin/env python3
"""Offline admission corruption checks; no secret loading or radio."""
import argparse,json,shutil,tempfile
from pathlib import Path
import operating_route as route
flow=route.flow
def main():
 p=argparse.ArgumentParser();p.add_argument('--checked',type=Path,required=True);p.add_argument('--world',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--operating-observation',type=Path,required=True);a=p.parse_args()
 payload=(a.checked/'payload.efi').read_bytes();world=a.world.read_bytes();route.gates(a.checked,payload,world)
 checks=0
 with tempfile.TemporaryDirectory(prefix='physical-release-admission-') as t:
  d=Path(t);bp=d/'boot.json';op=d/'operating.json'
  boot=flow.read_json(a.baseline);operating=flow.read_json(a.operating_observation)
  flow.save(bp,boot);flow.save(op,operating);route.fresh(bp,op)
  for target,original in ((bp,boot),(op,operating)):
   for key,value in [('writes',1),('peripheral','00000000-0000-0000-0000-000000000000'),('raw_hex','')]:
    changed={**original,key:value};flow.save(target,changed)
    try:route.fresh(bp,op)
    except (ValueError,KeyError):checks+=1
    else:raise AssertionError('invalid physical observation admitted')
    flow.save(target,original)
  # All22 operating words are fixed to the actual failed43 baseline.
  wire=bytes.fromhex(operating['raw_hex'])
  for index in range(27):
   altered=bytearray(wire);altered[8+index*4]^=1
   flow.save(op,{**operating,'raw_hex':altered.hex()})
   try:route.fresh(bp,op)
   except (ValueError,KeyError):checks+=1
   else:raise AssertionError('changed physical control fields admitted')
  flow.save(op,operating)
 def reject(directory,blob=payload,w=world):
  nonlocal checks
  try:route.gates(directory,blob,w)
  except (ValueError,KeyError,FileNotFoundError):checks+=1
  else:raise AssertionError('corrupt admission accepted')
 with tempfile.TemporaryDirectory(prefix='operating-admission-') as t:
  d=Path(t)
  # The baseline is read-only. Each case mutates only its temporary candidate.
  (d/'baseline').symlink_to((a.checked/'baseline').resolve(),target_is_directory=True)
  def reset():
   for n in ('report.json','reproduction.json','operating-report.json','operating-host.log','initial-report.json','initial-host.log','response-report.json','response-host.log'):shutil.copyfile(a.checked/n,d/n)
   for n in ('actors-qemu','actors-empty-boot-qemu'):
    (d/n).mkdir(exist_ok=True)
    for f in ('report.json','observed.log'):shutil.copyfile(a.checked/n/f,d/n/f)
  def edit(file,key,value):
   reset();v=flow.read_json(d/file);v[key]=value;flow.save(d/file,v);reject(d)
  for key,value in [('status','WRONG'),('payload_sha256','0'*64),('payload_bytes',1),('build_host','mac'),('source_sha256',{}),('gates',[]),('receiver_policy',{}),('receiver_policy_sha256','0'*64),('operating_report_sha256','0'*64),('initial_report_sha256','0'*64),('response_report_sha256','0'*64)]:edit('report.json',key,value)
  for key,value in [('status','WRONG'),('payload_sha256','0'*64),('world_package_sha256','0'*64),('inputs',{}),('host_checks',{}),('build_host','mac')]:edit('reproduction.json',key,value)
  for file,cases in [('operating-report.json',27),('initial-report.json',65)]:
   for key,value in [('status','WRONG'),('scenarios',cases-1),('actual_native_entrypoints',False),('build_host','mac'),('host_log_sha256','0'*64)]:
    reset();v=flow.read_json(d/file);v[key]=value;flow.save(d/file,v)
    top=flow.read_json(d/'report.json');top[('operating' if file.startswith('operating') else 'initial')+'_report_sha256']=flow.sha((d/file).read_bytes());flow.save(d/'report.json',top);reject(d)
  for file in ('operating-host.log','initial-host.log','response-host.log','actors-qemu/observed.log','actors-empty-boot-qemu/observed.log'):
   reset();(d/file).write_bytes(b'wrong log');reject(d)
  reset()
  for off in range(0,len(payload),512):
   b=bytearray(payload);b[off]^=1;reject(d,bytes(b))
  reject(d,payload,world[:-1]);reject(d,payload+b'0');reject(d,payload[:-1])
 # Same unmodified positive case after every temporary mutation.
 route.gates(a.checked,payload,world)
 print(json.dumps({'status':'OPERATING-ADMISSION-NEGATIVE-PASS','negative_cases':checks,'secret_loads':0,'radio_writes':0}))
if __name__=='__main__':main()
