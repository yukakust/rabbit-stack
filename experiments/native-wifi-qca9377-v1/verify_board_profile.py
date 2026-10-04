#!/usr/bin/env python3
"""Board helper native entrypoints, city/ATT QEMU and current-source gates."""
import json,shutil
from decode_board import decode
import board_build as build
import verify_board_probe as probe
import verify_board_core as core
import verify_setup_profile as setup
import verify_init_profile as prior
from decode_diagnostic import combine_qpd18
STATUS='QCA-FRESH-BOARD-HELPER-QUERY-CITY-PROFILE-GATES-PASS'
def fixture(source):
 s=setup.fixture(source)
 needle='say("ACTUAL UEFI PCI ENUMERATION READ THROUGH MOCK USB ATT; QCA ABSENT; NO WRITES");'
 extra=r'''
 uint8_t board_service[7]={0x10,13,0,255,255,0,0x28};
 if(att(board_service,7,0x11)||diagnostic_reply_size!=22||diagnostic_reply[2]!=13||diagnostic_reply[4]!=15||diagnostic_reply[6]!=0x20)return 1;
 uint8_t board_status_request[3]={0x0a,15,0};if(att(board_status_request,3,0x0b)||diagnostic_reply_size!=161||!same(diagnostic_reply+1,(const uint8_t*)"QBDI0001",8))return 1;
 uint8_t board_write_request[4]={0x12,15,0,0};if(att(board_write_request,4,1)||diagnostic_reply[4]!=3)return 1;
 say("READ-ONLY BOARD SERVICE13..15; WRITE REJECTED; CITY RETAINED");
 '''+needle
 return build.one(s,needle,extra)
def main():
 core.main()
 prior.main(builder=build,probe=probe,profile='board-profile',version='QPD18',combine=combine_qpd18,expected_cases=len(probe.CASES),flags=prior.FLAGS+('full_channel_ce7_read','active_dma_guard','completion_before_timeout','full_channel_config_read','config_write_readback','config_done_last','cpu_wake_and_bmi','board_query_integrated'),target_ram_writes=True,status=STATUS,test_transform=fixture,extra_negative=((280,6),(288,11),(292,32),(296,32),(300,6),(304,2),(316,4),(336,13),(340,2),(344,2),(888,4),(904,2),(908,2),(912,4),(900,5)))
 out=build.ROOT/'runs/board-profile'
 observations=0;negative=0
 for line in (out/'probe-host.log').read_text().splitlines():
  if line.startswith('QBDI_MOCK='):
   raw=bytearray.fromhex(line.split('=',1)[1]);decode({'format':'QBDI1','raw_hex':raw.hex()});observations+=1
   for off,value in ((8,7),(16,102),(20,24197),(36,32),(40,4),(44,2),(48,2),(52,5),(60,4097),(64,1048577),(116,14),(120,15),(124,15)):
    bad=raw.copy();bad[off:off+4]=value.to_bytes(4,'little')
    try:decode({'format':'QBDI1','raw_hex':bad.hex()})
    except ValueError:negative+=1
    else:raise AssertionError('invalid board telemetry accepted')
   bad=raw.copy();bad[128]^=1
   try:decode({'format':'QBDI1','raw_hex':bad.hex()})
   except ValueError:negative+=1
   else:raise AssertionError('foreign helper hash accepted')
 assert observations==len(probe.CASES)
 report=json.loads((out/'report.json').read_text())
 for src,dst in (('report.json','board-core-report.json'),('host.log','board-core-host.log')):shutil.copyfile(build.ROOT/'runs/board-core'/src,out/dst)
 report.update(board_decode_rejections=negative,board_core_report_sha256=prior.sha((out/'board-core-report.json').read_bytes()),board_policy=build.policy(),board_policy_sha256=prior.sha(build.POLICY.read_bytes()),helper_ram_upload=True,helper_execute_parameter=0x10,main_firmware_execution=False,permanent_otp_programming=False,physical_operation='Fresh active native setup/BMI type8/version05020001 + exact RAM helper via bounded LZ + GET_EEPROM_BOARD_ID only; SMBIOS BDF variant read; all host DMA/PCI/IRQ/link/wake resources closed or retained')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
