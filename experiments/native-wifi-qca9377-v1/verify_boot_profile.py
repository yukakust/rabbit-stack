#!/usr/bin/env python3
"""Boot trial gates: actual two lifetimes, exact assets, city and GATT QEMU.

No physical signing or radio; full vendor main may execute only in RAM.
"""
import json,shutil
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'native-wifi-qca9377-session-v1'))
import verify_bt_usb
import boot_build as build
import verify_boot_probe,verify_boot_lifetimes,verify_boot_core
import verify_receiver_profile as receiver
import verify_init_profile as prior
from decode_diagnostic import combine_qpd18
from decode_boot import decode,NAMES
STATUS='QCA-EXACT-RAM-MAIN-BOOT-CITY-PROFILE-GATES-PASS'
class Probe:
 @staticmethod
 def main():
  verify_boot_probe.main()
  target=build.ROOT/'runs/full-read-probe-host';target.mkdir(exist_ok=True)
  for n in ('report.json','host.log'):shutil.copyfile(build.ROOT/'runs/boot-probe-host'/n,target/n)
def fixture(source):
 s=receiver.fixture(source)
 # The historical orphan-tail recovery fixture is retained in its own verifier.
 # A stream parser cannot infer a missing header safely. This candidate instead
 # exercises a real connection split16+5, then a matched disconnection, through
 # actual UEFI poll/replacement entrypoints; no guessing or resynchronization.
 old=r""" static unsigned lost_event;
 if(conn_event&&resets>=3&&*n){
  if(!lost_event){uint8_t e[5]={0,0,0x48,0,1};copy(p,e,5);*n=5;lost_event=1;return 0;}
  if(lost_event==1){uint8_t e[6]={5,4,0,3,0,0x13};copy(p,e,6);*n=6;lost_event=2;conn_event=0;advertising=0;return 0;}
 }
"""
 new=r""" static unsigned lost_event;
 if(conn_event&&resets>=3&&*n){
  uint8_t connection[21]={0x3e,19,1,0,0x40,0,1,0,0,0,0,0,0,0,24,0,0,0,200,0,0};
  if(!lost_event){copy(p,connection,16);*n=16;lost_event=1;return 0;}
  if(lost_event==1){copy(p,connection+16,5);*n=5;lost_event=2;connected=1;advertising=0;return 0;}
  if(lost_event==2){uint8_t e[6]={5,4,0,0x40,0,0x13};copy(p,e,6);*n=6;lost_event=3;conn_event=0;connected=advertising=0;return 0;}
 }
"""
 s=build.one(s,old,new)
 s=build.one(s,' static unsigned lost_event;','')
 s=build.one(s,'static unsigned resets,disconnects,violations;','static unsigned resets,disconnects,violations;\nstatic unsigned lost_event;')
 s=build.one(s,'say("EXACT NATIVE RETRY RECEIPT ONLY; NO SECOND APPLY OR DISCONNECT");','if(lost_event!=3)return 1;\n say("FRAGMENTED16+5 CONNECTION AND MATCHED DISCONNECTION VERIFIED THROUGH ACTUAL UEFI USB; NO ORPHAN GUESSING");\n say("EXACT NATIVE RETRY RECEIPT ONLY; NO SECOND APPLY OR DISCONNECT");')
 needle='say("INTEGRATED RAM SERVICE13..19; TARGET ABSENT WRITE REJECTED; CITY RETAINED");'
 extra=r'''
 uint8_t boot_service[7]={0x10,20,0,255,255,0,0x28};
 if(att(boot_service,7,0x11)||diagnostic_reply_size!=22||diagnostic_reply[2]!=20||diagnostic_reply[4]!=22||diagnostic_reply[6]!=0x22)return 1;
 uint8_t boot_status[3]={0x0a,22,0};if(att(boot_status,3,0x0b)||diagnostic_reply_size!=161||!same(diagnostic_reply+1,(const uint8_t*)"QWBT0001",8))return 1;
 uint8_t boot_write[4]={0x12,22,0,0};if(att(boot_write,4,1)||diagnostic_reply_size!=5||diagnostic_reply[4]!=3)return 1;
 say("BOOT SERVICE20..22 READ ONLY; RAM SERVICE PRESERVED; CITY RETAINED");
 '''+needle
 return build.one(s,needle,extra)
def main():
 prior.main(builder=build,probe=Probe,profile='boot-profile',version='QPD18',combine=combine_qpd18,expected_cases=65,
  flags=prior.FLAGS+('full_channel_ce7_read','active_dma_guard','completion_before_timeout','full_channel_config_read','config_write_readback','config_done_last','cpu_wake_and_bmi','signed_ram_receiver_integrated'),
  target_ram_writes=True,status=STATUS,test_transform=fixture,extra_negative=((280,6),(288,11),(292,32),(296,32),(300,6),(304,2),(316,4),(336,13),(340,2),(344,2),(888,4),(904,2),(908,2),(912,4),(900,5)))
 out=build.ROOT/'runs/boot-profile'
 verify_boot_lifetimes.main();verify_boot_core.main()
 report=json.loads((out/'report.json').read_text())
 for name,run in (('asset-core','firmware-chunks'),('asset-channel','firmware-channel'),('asset-port','firmware-port'),('boot-core','boot-core'),('boot-lifetimes','boot-two-lifetime-host')):
  for src,dst in (('report.json',name+'-report.json'),('host.log',name+'-host.log')):shutil.copyfile(build.ROOT/'runs'/run/src,out/dst)
  report[name+'_report_sha256']=prior.sha((out/(name+'-report.json')).read_bytes())
 observations=[];rejected=0
 for line in (out/'boot-lifetimes-host.log').read_text().splitlines():
  if not line.startswith('QWBT_MOCK='):continue
  raw=bytes.fromhex(line.split('=',1)[1]);d=decode({'format':'QWBT1','raw_hex':raw.hex()});observations.append(d)
  for off,value in ((8,7),(16,23),(24,4001),(28,4001),(40,727126),(44,257),(56,10),(60,2),(72,21),(88,15),(120,4096)):
   b=bytearray(raw);b[off:off+4]=value.to_bytes(4,'little')
   try:decode({'format':'QWBT1','raw_hex':b.hex()})
   except ValueError:rejected+=1
   else:raise AssertionError(f'boot bounds accepted {off}')
  if d['phase']==5:
   for key,value in (('error',1),('plan_phase',19),('calibration_result',1),('calibration_result',2),('calibration_result',4),('ready_bytes',0),('bmi_type',7),('board_error',1),('asset_ready',0),('asset_bitmap',0)):
    b=bytearray(raw);off=8+4*NAMES.index(key);b[off:off+4]=value.to_bytes(4,'little')
    try:decode({'format':'QWBT1','raw_hex':b.hex()})
    except ValueError:rejected+=1
    else:raise AssertionError('false main ready accepted')
  if d['phase']==5:
   b=bytearray(raw);off=8+4*NAMES.index('calibration_result');b[off:off+4]=(3).to_bytes(4,'little');assert decode({'format':'QWBT1','raw_hex':b.hex()})['physical_trial_complete']
 assert len(observations)==8 and observations[0]['physical_trial_complete'] and all(o['all_loader_resources_released'] for o in observations) and all(not o['htc_ready_observed'] for o in observations[1:])
 verify_bt_usb.main()
 usb=build.ROOT.parent/'native-wifi-qca9377-session-v1'/'runs/bt-usb'
 for src,dst in (('report.json','bt-usb-report.json'),('asan.log','bt-usb-asan.log'),('regression.log','bt-usb-regression.log')):shutil.copyfile(usb/src,out/dst)
 ur=json.loads((out/'bt-usb-report.json').read_text())
 assert prior.sha((out/'usb_port.c').read_bytes())==ur['derived_usb_sha256']
 assert prior.sha((out/'usb_port.h').read_bytes())==ur['derived_header_sha256']
 report.update(bt_orphan_resynchronization=False,bt_usb_integrated=True,bt_usb_report_sha256=prior.sha((out/'bt-usb-report.json').read_bytes()))
 report.update(receiver_policy=build.policy(),receiver_policy_sha256=prior.sha(build.POLICY.read_bytes()),firmware_upload=True,firmware_staging_only=False,firmware_execution=True,two_lifetimes_verified=True,boot_decode_rejections=rejected,permanent_otp_programming=False,wifi_connected=False,
  physical_operation='Fresh setup then closed RAM receiver, full signed exact container, second fresh PCI/SMBIOS/helper query, exact board write/readback, calibration execute0, exact main LZ load, UART disabled, BMI DONE, bounded HTC READY receive, full cleanup; RAM-only; no scan/association')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
