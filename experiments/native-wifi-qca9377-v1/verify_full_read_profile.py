#!/usr/bin/env python3
import full_read_build as build
import verify_full_read_probe as probe
import verify_init_profile as prior
from decode_diagnostic import combine_qpd16
STATUS='QCA-FULL-CHANNEL-CE7-READ-CITY-PROFILE-GATES-PASS'
def fixture(source):
 return prior.fixture(source).replace('"QPD\\17"','"QPD\\20"').replace('diagnostic_reply_size!=209','diagnostic_reply_size!=245').replace('i<172','i<208').replace('12,0,209,0','12,0,245,0').replace('LONG QPD15','LONG QPD16')
def main():
 prior.main(builder=build,probe=probe,profile='full-read-profile',version='QPD16',combine=combine_qpd16,
  expected_cases=25,flags=prior.FLAGS+('full_channel_ce7_read','active_dma_guard','completion_before_timeout'),
  status=STATUS,test_transform=fixture,extra_negative=((888,4),(904,2),(908,2),(912,4),(900,5)))
if __name__=='__main__':main()
