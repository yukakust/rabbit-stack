#!/usr/bin/env python3
import setup_build as build
import verify_setup_probe as probe
import verify_init_profile as prior
from decode_diagnostic import combine_qpd18
STATUS='QCA-FULL-CHANNEL-CONFIG-SETUP-BMI-CITY-PROFILE-GATES-PASS'
def fixture(source):
 return prior.fixture(source).replace('"QPD\\17"','"QPD\\22"').replace('diagnostic_reply_size!=209','diagnostic_reply_size!=245').replace('i<172','i<208').replace('12,0,209,0','12,0,245,0').replace('LONG QPD15','LONG QPD17')
def main():
 prior.main(builder=build,probe=probe,profile='setup-profile',version='QPD18',combine=combine_qpd18,
  expected_cases=65,flags=prior.FLAGS+('full_channel_ce7_read','active_dma_guard','completion_before_timeout','full_channel_config_read','config_write_readback','config_done_last','cpu_wake_and_bmi'),
  target_ram_writes=True,status=STATUS,test_transform=fixture,extra_negative=((280,6),(288,11),(292,32),(296,32),(300,6),(304,2),(316,4),(336,13),(340,2),(344,2),(888,4),(904,2),(908,2),(912,4),(900,5)))
if __name__=='__main__':main()
