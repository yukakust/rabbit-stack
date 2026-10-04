#!/usr/bin/env python3
"""Exact native warm/channel trial: host faults, real PE and city/ATT QEMU."""
import hashlib,json,os,shutil,subprocess
import init_build as build
import verify_init_core,verify_init_probe,verify_port,verify_reset
import verify_bmi_profile as prior
from decode_diagnostic import decode,combine_qpd14
ROOT=build.ROOT
sha=lambda b:hashlib.sha256(b).hexdigest()
STATUS='QCA-WARM-FULL-CHANNEL-CITY-PROFILE-GATES-PASS'
FLAGS=('native_init_entrypoints','mapped_irq_scope','warm_and_cold_recovery',
       'full_channel_ownership','hash_bound_split_diagnostic','ble_untracked_disconnect_recovery','post_cold_ce_stop')
def fixture(source):
 return prior.fixture(source).replace('"QPD\\15"','"QPD\\16"').replace('diagnostic_reply_size!=121','diagnostic_reply_size!=185').replace('i<84','i<148').replace('12,0,121,0','12,0,185,0').replace('LONG QPD13','LONG QPD14')
def main():
 if not __debug__:raise SystemExit('optimized Python forbidden')
 out=ROOT/'runs/init-profile';out.mkdir(parents=True,exist_ok=False)
 # Conservative closure includes generated-source builders, all native headers,
 # policies, validators and fixtures. remote_check additionally binds the city,
 # supervisor, crypto provenance and live world package before signing.
 paths=sorted(p for p in ROOT.iterdir() if p.suffix in ('.c','.h','.py','.json'))
 paths += [build.CITY/n for n in ('actors_build.py','city_core.c','city_core.h','city_display.c','actor_clock.c','actors_gate.py')]
 inputs={str(p.relative_to(ROOT.parent.parent)):sha(p.read_bytes()) for p in paths}
 for component,module,run in [('port',verify_port,'port'),('reset',verify_reset,'reset-core'),('init',verify_init_core,'init-core'),('probe',verify_init_probe,'init-probe-host')]:
  module.main()
  for src,dst in [('report.json',component+'-report.json'),('host.log',component+'-host.log')]:shutil.copyfile(ROOT/'runs'/run/src,out/dst)
 shutil.copyfile(ROOT/'runs/init-core/pack-report.json',out/'pack-report.json')
 public=bytes.fromhex('29acbae141bccaf0b22e1a94d34d0bc7361e526d0bfe12c89794bc9322966dd7')
 _,_,crypto=build.actors.engine.prepare(out,public)
 payload=build.compile_driver(out,crypto)
 assert payload==build.compile_driver(out,crypto)
 (out/'payload.efi').write_bytes(payload)
 log=(out/'probe-host.log').read_text();cases=0;negative=0
 for line in log.splitlines():
  if not line.startswith('QPD14_MOCK='):continue
  raw=bytearray.fromhex(line.split('=',1)[1]);decoded=decode({'format':'QPD14','raw_hex':raw.hex()})
  prefix=bytes(raw[:716]);extension=b'QIC'+bytes([1])+hashlib.sha256(prefix).digest()+bytes(raw[716:])
  assert decode(combine_qpd14(prefix,extension))==decoded;cases+=1
  active=bytearray(prefix);active[128:132]=(18).to_bytes(4,'little');active_ext=b'QIC'+bytes([1])+hashlib.sha256(active).digest()+bytes(raw[716:])
  for a,b in ((bytes(active),active_ext),(prefix[:-1],extension),(prefix,extension[:-1]),(prefix,extension[:4]+bytes(32)+extension[36:]),(prefix,b'BAD!'+extension[4:])):
   try:combine_qpd14(a,b)
   except ValueError:negative+=1
   else:raise AssertionError('invalid QPD14 split accepted')
  for offset,value in ((800,14),(808,14),(816,2),(820,2),(824,3),(828,3),(832,8),(836,15),(840,15),(844,2),(848,5),(852,2),(220,15),(224,2),(236,0x4000),(716,1),(280,1)):
   bad=raw.copy();bad[offset:offset+4]=value.to_bytes(4,'little')
   try:decode({'format':'QPD14','raw_hex':bad.hex()})
   except ValueError:negative+=1
   else:raise AssertionError('invalid QPD14 bounds accepted')
  if decoded['native_init']['warm_and_channels_verified']:
   for offset,value in ((136,1),(824,1),(828,1),(836,13),(840,13),(816,1),(844,1),(860,1),(244,1),(250,1)):
    bad=raw.copy();bad[offset:offset+4]=value.to_bytes(4,'little')
    try:decode({'format':'QPD14','raw_hex':bad.hex()})
    except ValueError:negative+=1
    else:raise AssertionError('false warm success accepted')
 assert cases==18
 for name,source,defs in [('ble-baseline',build.actors.LINK/'hci_link.c',['-DBASELINE']),('ble-fixed',out/'ble_recovery_link.c',[])]:
  test=out/name
  subprocess.run(['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all',
   '-I'+str(build.actors.LINK),'-I'+str(build.actors.NATIVE),str(ROOT/'test_ble_recovery.c'),str(source),*defs,'-o',str(test)],check=True)
  run=subprocess.run([str(test)],capture_output=True,text=True,check=True,timeout=30)
  log+=name+': PASS\n'+run.stdout+run.stderr
 log+=f'QPD14 exact18 snapshots + {negative} corrupt bounds/split/success rejections PASS\n'
 (out/'host.log').write_text(log)
 gates=[prior.actors_gate.qemu_gate(out,payload,test_transform=fixture),prior.actors_gate.qemu_gate(out,payload,True,test_transform=fixture)]
 assert inputs=={str(p.relative_to(ROOT.parent.parent)):sha(p.read_bytes()) for p in paths},'source changed during profile gate'
 report={'status':STATUS,'payload_sha256':sha(payload),'source_sha256':inputs,'host_log_sha256':sha(log.encode()),
  **{n:True for n in FLAGS},'gates':gates,'physical_dell_verified':False,'target_ram_writes':False,'firmware_upload':False,
  'physical_operation':'cold/wake/ROM + mapped warm reset + fourteen coherent pages/full channel configuration with bus mastering off + teardown; verified cold recovery or retain ownership on fault',
  **{n+'_report_sha256':sha((out/(n+'-report.json')).read_bytes()) for n in ('port','reset','init','probe')},
  'pack_report_sha256':sha((out/'pack-report.json').read_bytes()),'build_host':'yukabox'}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(STATUS+' payload='+sha(payload))
if __name__=='__main__':main()
