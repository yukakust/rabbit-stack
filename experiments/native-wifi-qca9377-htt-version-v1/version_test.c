#include "version.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
unsigned ref_req(uint8_t*);void ref_conf(uint8_t*,unsigned,unsigned);
static unsigned checks;
#define CHECK(x) do{checks++;if(!(x)){fprintf(stderr,"line%u\n",__LINE__);abort();}}while(0)
int main(void){
 QcaHtcSession s={0};s.phase=QCA_HTC_RUNNING;s.ready.endpoints=3;s.wmi=(QcaHtcConnection){QCA_HTC_WMI,1784,1};s.htt=(QcaHtcConnection){QCA_HTC_HTT,256,2};
 QcaHttBinding b={0};CHECK(qca_htt_version_bind(&s,3,&b));CHECK(b.endpoint==2&&b.max_bytes==256&&b.op_version==3);
 uint8_t req[6]={99,99,99,99,99,99},expected[4];CHECK(ref_req(expected)==4);CHECK(qca_htt_version_request(&b,req+1,4)==4);CHECK(!memcmp(req+1,expected,4)&&req[0]==99&&req[5]==99);
 for(unsigned major=0;major<256;major++)for(unsigned minor=0;minor<256;minor++){
  uint8_t frame[4];ref_conf(frame,major,minor);QcaHttVersion v={99,99};int yes=qca_htt_version_conf(&b,frame,4,&v);
  CHECK(yes==(major==2||major==3));CHECK(yes?(v.major==major&&v.minor==minor):(v.major==99&&v.minor==99));
 }
 uint8_t frame[4]={0,4,3,0};QcaHttVersion v={99,99};
 for(unsigned n=0;n<12;n++)if(n!=4)CHECK(!qca_htt_version_conf(&b,frame,n,&v));
 for(unsigned i=1;i<256;i++){frame[0]=(uint8_t)i;CHECK(!qca_htt_version_conf(&b,frame,4,&v));frame[0]=0;frame[3]=(uint8_t)i;CHECK(!qca_htt_version_conf(&b,frame,4,&v));frame[3]=0;}
 for(unsigned op=0;op<32;op++)if(op!=3){QcaHttBinding old=b;CHECK(!qca_htt_version_bind(&s,op,&b));CHECK(!memcmp(&b,&old,sizeof b));}
 QcaHtcSession bad=s;bad.htt.endpoint=1;CHECK(!qca_htt_version_bind(&bad,3,&b));bad=s;bad.htt.service=256;CHECK(!qca_htt_version_bind(&bad,3,&b));bad=s;bad.htt.max_bytes=3;CHECK(!qca_htt_version_bind(&bad,3,&b));bad=s;bad.htt.max_bytes=4097;CHECK(!qca_htt_version_bind(&bad,3,&b));bad=s;bad.phase=6;CHECK(!qca_htt_version_bind(&bad,3,&b));bad=s;bad.prepared=1;CHECK(!qca_htt_version_bind(&bad,3,&b));
 CHECK(!qca_htt_version_bind(&s,3,(QcaHttBinding*)&s));CHECK(!qca_htt_version_conf(&b,frame,4,(QcaHttVersion*)frame));CHECK(!qca_htt_version_request(&b,(uint8_t*)&b,4));
 CHECK(!qca_htt_version_conf(&b,frame,4,0));CHECK(!qca_htt_version_conf(0,frame,4,&v));CHECK(!qca_htt_version_conf(&b,0,4,&v));
 CHECK(!qca_htt_version_request(&b,(uint8_t*)(UINTPTR_MAX-2),4));
 for(unsigned cap=0;cap<4;cap++)CHECK(!qca_htt_version_request(&b,req,cap));
 printf("checks=%u\n",checks);return 0;
}
