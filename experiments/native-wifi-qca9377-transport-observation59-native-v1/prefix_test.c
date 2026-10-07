#include "prefix.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static unsigned cases;
static uint32_t u32(const uint8_t*p){return p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
int main(void){
 QcaPrefix p={0};qca_prefix_arm(&p,1000);assert(p.phase==1);
 assert(!qca_prefix_tick(&p,2000,1,17,32736,311,311,0,0,0));
 assert(!qca_prefix_tick(&p,3000,1,17,32984,312,311,1,1,0));
 assert(qca_prefix_tick(&p,4000,1,17,32984,312,312,0,0,0));assert(p.phase==2&&!p.reason&&p.stop_offset==32984);cases++;
 assert(qca_prefix_tick(&p,5000,1,17,32984,312,312,0,0,0));assert(p.phase==2);
 assert(!qca_prefix_tick(&p,6000,1,17,32984,312,312,0,0,1)&&p.phase==3&&p.raw_frozen);cases++;
 for(unsigned mode=1;mode<=4;mode++){
  p=(QcaPrefix){0};qca_prefix_arm(&p,1000);
  if(mode==3)p.usb_fault=3;
  unsigned rc=qca_prefix_tick(&p,mode==1?1000+QCA_PREFIX_DEADLINE_US:mode==2?999:2000,mode==4?5:1,17,248,1,1,0,0,0);
  assert(rc&&p.phase==2&&p.reason==(mode==1?1:mode==2?2:mode==3?6:4));cases++;
 }
 p=(QcaPrefix){0};qca_prefix_arm(&p,1000);
 uint8_t ordinary[7]={0x13,5,1,1,0,0,0};
 for(unsigned i=0;i<2000;i++)qca_prefix_event(&p,ordinary,7,1000+i,3,0);
 assert(p.routine_count==12&&p.raw_count==12&&p.routine_overwritten==1988&&!p.raw_overflow);
 assert(!qca_prefix_tick(&p,4000,1,17,19592,259,258,1,1,0));cases++;
 uint8_t critical[6]={5,4,0,1,0,0x13};qca_prefix_event(&p,critical,6,4500,3,0);
 for(unsigned i=0;i<100;i++)qca_prefix_event(&p,ordinary,7,4501+i,3,0);
 assert(p.critical_count==1&&p.routine_overwritten==2088&&!memcmp(p.raw[0].bytes,critical,6));cases++;
 for(unsigned i=0;i<4;i++)qca_prefix_event(&p,critical,6,5000+i,3,0);
 assert(p.critical_count==4&&p.raw_overflow==1);
 assert(qca_prefix_tick(&p,6000,1,17,19592,259,258,1,1,0)&&p.reason==5);cases++;
 assert(!qca_prefix_tick(&p,7000,1,17,19592,259,258,1,1,1));
 struct {uint8_t before[16],data[4672],after[16];} blob;memset(&blob,0xa5,sizeof(blob));
 assert(qca_prefix_raw(&p,blob.data,4672,0)==4672&&!memcmp(blob.data,"QPHCI001",8));
 for(unsigned i=0;i<16;i++)assert(blob.before[i]==0xa5&&blob.after[i]==0xa5);
 assert(u32(blob.data+8)==59&&u32(blob.data+28)==4672&&u32(blob.data+44)==2088);
 assert(u32(blob.data+64+8)==6&&!memcmp(blob.data+64+24,critical,6));
 assert(u32(blob.data+64+4*288+8)==7);cases++;
 uint8_t unchanged[4672];memcpy(unchanged,blob.data,sizeof(unchanged));qca_prefix_event(&p,ordinary,7,9000,3,0);
 assert(qca_prefix_raw(&p,blob.data,4672,0)==4672&&!memcmp(unchanged,blob.data,4672));cases++;
 assert(qca_prefix_raw(&p,blob.data,4672,4672)==0&&qca_prefix_raw(&p,blob.data,4672,4673)==UINT32_MAX);cases++;
 printf("BOUNDED PREFIX CORE %u cases; routine2000 reachable, criticalprotected, release/rollback/deadline/bounds PASS\n",cases);return 0;
}
