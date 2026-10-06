#include "completion.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
unsigned reference_bundle(uint8_t*,unsigned,unsigned);
unsigned reference_single(uint8_t*,uint32_t);
static unsigned checks;
static void put(uint8_t*p,uint32_t n){for(unsigned j=0;j<4;j++)p[j]=(uint8_t)(n>>(8*j));}
static void reject(const uint8_t*p,unsigned n,unsigned ack){
 QcaMgmtCompletion c,old;memset(&c,0xa5,sizeof(c));old=c;
 assert(!qca_mgmt_completion(p,n,ack,&c)&&!memcmp(&old,&c,sizeof(c)));checks++;
}
int main(void){
 uint8_t p[2048],mut[2048];uint32_t ids[32];QcaMgmtCompletion c;
 for(unsigned count=0;count<=32;count++)for(unsigned arrays=2;arrays<=4;arrays++)for(unsigned ack=0;ack<=1;ack++){
  unsigned n=reference_bundle(p,count,arrays);
  if(ack&&arrays!=4){reject(p,n,ack);continue;}
  assert(qca_mgmt_completion(p,n,ack,&c)&&c.count==count&&c.has_ppdu==(arrays>=3)&&c.has_rssi==ack);checks++;
  for(unsigned j=0;j<count;j++){
   assert(c.report[j].id==100+j&&c.report[j].status==j%5&&!c.report[j].pdev);
   assert(c.report[j].ppdu==(arrays>=3?1000+j:0)&&c.report[j].rssi==(ack?0xffffff80+j:0));ids[j]=100+j;
  }
  uint32_t mask=0xfeed;
  assert(qca_mgmt_completion_plan(&c,ids,count,&mask)&&mask==(count==32?UINT32_MAX:((1u<<count)-1)));checks++;
  if(count){ids[count-1]=9000;mask=0xfeed;assert(!qca_mgmt_completion_plan(&c,ids,count,&mask)&&mask==0xfeed);checks++;}
  for(unsigned cut=0;cut<n;cut++){
   /* A complete optional array boundary is also a valid narrower envelope. */
   if(!ack&&(cut==20+8*count||cut==24+12*count))continue;
   reject(p,cut,ack);
  }
  memcpy(mut,p,n);put(mut+8,33);reject(mut,n,ack);
  if(count>1){memcpy(mut,p,n);put(mut+20,100);reject(mut,n,ack);}
  memcpy(mut,p,n);put(mut+12,(4*count+4)|(16u<<16));reject(mut,n,ack);
 }
 for(unsigned ack=0;ack<2;ack++)for(unsigned id=0;id<32;id++){
  unsigned n=reference_single(p,id);assert(qca_mgmt_completion(p,n,ack,&c)&&c.count==1&&c.report[0].id==id&&c.report[0].status==3&&c.report[0].pdev==0&&c.report[0].ppdu==77&&c.has_rssi==ack&&c.report[0].rssi==(ack?UINT32_MAX:0));checks++;
  for(unsigned cut=0;cut<n;cut++)reject(p,cut,ack);
  memcpy(mut,p,n);put(mut+4,16|(423u<<16));reject(mut,n,ack);
  memcpy(mut,p,n);memcpy(mut+n,p+4,n-4);reject(mut,2*n-4,ack);
 }
 unsigned n=reference_bundle(p,32,5);reject(p,n,0);
 n=reference_single(p,0);memcpy(mut,p,n);put(mut+4,20|(424u<<16));reject(mut,n,0);
 memcpy(mut,p,n);put(mut,0xdead);reject(mut,n,0);
 memcpy(mut,p,n);put(mut+4,19|(423u<<16));reject(mut,n,0);
 memcpy(mut,p,n);put(mut+4,2044|(423u<<16));reject(mut,n,0);
 put(p+12,UINT32_MAX);assert(qca_mgmt_completion(p,n,0,&c)&&c.report[0].status==UINT32_MAX);checks++;
 uint32_t unknown_mask=0xfeed;ids[0]=0;
 assert(!qca_mgmt_completion_plan(&c,ids,33,&unknown_mask)&&unknown_mask==0xfeed);checks++;
 assert(!qca_mgmt_completion_plan(&c,ids,1,ids));checks++;
 c.count=33;assert(!qca_mgmt_completion_plan(&c,ids,1,&unknown_mask)&&unknown_mask==0xfeed);checks++;
 reject(p,2049,0);
 reference_bundle(p,2,3);assert(qca_mgmt_completion(p,48,0,&c));
 c.report[1].id=c.report[0].id;ids[0]=100;ids[1]=101;uint32_t mask=0xfeed;
 assert(!qca_mgmt_completion_plan(&c,ids,2,&mask)&&mask==0xfeed);checks++;
 ids[1]=100;assert(!qca_mgmt_completion_plan(&c,ids,2,&mask)&&mask==0xfeed);checks++;
 reject(p,48,2);assert(!qca_mgmt_completion(0,48,0,&c)&&!qca_mgmt_completion(p,48,0,0));checks++;
 assert(!qca_mgmt_completion(p,48,0,(QcaMgmtCompletion*)p));checks++;
 printf("WMI management single/bundle completion bounds and atomic owner plan checks=%u PASS\n",checks);
}
