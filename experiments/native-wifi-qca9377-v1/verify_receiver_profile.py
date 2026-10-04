#!/usr/bin/env python3
"""Integrated native signed RAM staging, normal/EMPTY city and ATT gates."""
import json,shutil
import receiver_build as build
import verify_receiver_probe as probe
import verify_setup_profile as setup
import verify_init_profile as prior
from decode_diagnostic import combine_qpd18
STATUS='QCA-SETUP-SIGNED-RAM-RECEIVER-CITY-PROFILE-GATES-PASS'
def fixture(source):
 s=setup.fixture(source)
 needle='say("ACTUAL UEFI PCI ENUMERATION READ THROUGH MOCK USB ATT; QCA ABSENT; NO WRITES");'
 extra=r'''
 uint8_t ram_service[7]={0x10,13,0,255,255,0,0x28};
 if(att(ram_service,7,0x11)||diagnostic_reply_size!=22||diagnostic_reply[2]!=13||diagnostic_reply[4]!=19||diagnostic_reply[6]!=7)return 1;
 uint8_t ram_status[3]={0x0a,19,0};if(att(ram_status,3,0x0b)||diagnostic_reply_size!=65||!same(diagnostic_reply+1,(const uint8_t*)"RFCS0001",8))return 1;
 for(unsigned i=9;i<65;i++)if(diagnostic_reply[i])return 1;
 uint8_t no_ram_write[47]={0x12,15,0,'R','F','C','1',1};if(att(no_ram_write,47,1))return 1;
 say("INTEGRATED RAM SERVICE13..19; TARGET ABSENT WRITE REJECTED; CITY RETAINED");
 '''+needle
 return build.one(s,needle,extra)
def main():
 prior.main(builder=build,probe=probe,profile='receiver-profile',version='QPD18',combine=combine_qpd18,
  expected_cases=65,flags=prior.FLAGS+('full_channel_ce7_read','active_dma_guard','completion_before_timeout','full_channel_config_read','config_write_readback','config_done_last','cpu_wake_and_bmi','signed_ram_receiver_integrated'),target_ram_writes=True,status=STATUS,test_transform=fixture,extra_negative=((280,6),(288,11),(292,32),(296,32),(300,6),(304,2),(316,4),(336,13),(340,2),(344,2),(888,4),(904,2),(908,2),(912,4),(900,5)))
 out=build.ROOT/'runs/receiver-profile';report=json.loads((out/'report.json').read_text())
 for name,run in (('asset-core','firmware-chunks'),('asset-channel','firmware-channel'),('asset-port','firmware-port')):
  for source,destination in (('report.json',name+'-report.json'),('host.log',name+'-host.log')):shutil.copyfile(build.ROOT/'runs'/run/source,out/destination)
  report[name+'_report_sha256']=prior.sha((out/(name+'-report.json')).read_bytes())
 report.update(receiver_policy=build.policy(),receiver_policy_sha256=prior.sha(build.POLICY.read_bytes()),firmware_staging_only=True,firmware_execution=False,physical_operation='Fresh native33 setup/BMI + complete DMA/PCI teardown + owner/target-bound signed container RAM staging through handles13..19; no firmware write/execute/done to chip')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
