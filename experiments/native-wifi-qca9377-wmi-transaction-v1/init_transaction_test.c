#include "init_transaction.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static unsigned checks;
static void put(uint8_t*p,uint32_t n){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(n>>(8*i));}
static unsigned ready(uint8_t*p,unsigned credits){
 memset(p,0,64);p[0]=1;p[2]=44;put(p+8,2);put(p+12,36|(35u<<16));
 put(p+16,0x01000000);put(p+20,53);put(p+24,0x5f414351);put(p+28,0x4c4d);p[40]=2;p[45]=1;
 if(credits){p[1]=2;p[2]=52;p[4]=8;p[52]=1;p[53]=4;p[56]=1;p[57]=(uint8_t)credits;return 60;}
 return 52;
}
static unsigned report(uint8_t*p,unsigned ep,unsigned credits){
 memset(p,0,64);p[1]=2;p[2]=8;p[4]=8;p[8]=1;p[9]=4;p[12]=(uint8_t)ep;p[13]=(uint8_t)credits;return 16;
}
static QcaHtcSession session(void){
 QcaHtcSession h={0};h.phase=QCA_HTC_RUNNING;h.ready=(QcaHtcReady){.credits=2,.credit_size=1792,.endpoints=4};
 h.wmi=(QcaHtcConnection){.service=QCA_HTC_WMI,.max_bytes=1784,.endpoint=1};h.htt=(QcaHtcConnection){.service=QCA_HTC_HTT,.max_bytes=1784,.endpoint=2};return h;
}
static void reject_rx(QcaWmiInitTransaction*s,const uint8_t*p,unsigned n,uint32_t id){
 QcaWmiInitTransaction old=*s;QcaHtcCredit c=*s->credit;
 assert(!qca_wmi_init_receive(s,p,n,id)&&!memcmp(s,&old,sizeof(old))&&!memcmp(s->credit,&c,sizeof(c)));checks++;
}
int main(void){
 QcaWmiServiceInfo info={0};QcaWmiResources resources={1,2,0,1048576};uint32_t words[44]={1,2};QcaWmiHostChunk chunks[16];uint8_t p[64],mut[64];
 for(unsigned count=0;count<=16;count++)for(unsigned early=0;early<2;early++)for(unsigned returned=0;returned<2;returned++){
  info.memory_count=count;for(unsigned i=0;i<count;i++){info.memory[i]=(QcaWmiMemoryRequest){i,8,0,4};chunks[i]=(QcaWmiHostChunk){i,32,0x200000+4096*i};}
  QcaHtcSession h=session();QcaHtcCredit c={0};QcaWmiInitTransaction s={0};assert(qca_htc_credit_begin(&c,&h.ready,&h.wmi));
  assert(qca_wmi_init_begin(&s,&c,&h,&info,&resources,words,chunks,count)&&c.reserved==1&&s.phase==QCA_INIT_RESERVED&&s.frame_bytes==228+20*count);checks++;
  unsigned n=ready(p,returned);reject_rx(&s,p,n,1);
  assert(qca_wmi_init_post(&s)&&c.outstanding==1&&!c.reserved&&!qca_wmi_init_cancel(&s));checks++;
  assert(!qca_wmi_init_complete(&s,s.frame_bytes-1));checks++;
  if(!early)assert(qca_wmi_init_complete(&s,s.frame_bytes)&&s.phase==QCA_INIT_WAIT_READY);
  memcpy(mut,p,n);mut[48]=1;reject_rx(&s,mut,n,1); /* Firmware READY reports failure. */
  memcpy(mut,p,n);mut[0]=2;reject_rx(&s,mut,n,1);
  memcpy(mut,p,n);mut[20]=54;reject_rx(&s,mut,n,1);
  reject_rx(&s,p,n,0);reject_rx(&s,p,n,2);
  assert(qca_wmi_init_receive(&s,p,n,1)&&s.ready_seen&&s.ready.mac[0]==2&&s.ready.mac[5]==1&&c.available==1+returned&&c.outstanding==1-returned);checks++;
  if(early){assert(s.phase==QCA_INIT_POSTED);reject_rx(&s,p,n,1);reject_rx(&s,p,n,2);assert(qca_wmi_init_complete(&s,s.frame_bytes));checks++;}
  assert(s.phase==QCA_INIT_RUNNING&&!qca_wmi_init_complete(&s,s.frame_bytes));checks++;reject_rx(&s,p,n,2);
 }
 info.memory_count=0;
 for(unsigned mode=0;mode<11;mode++){
  QcaHtcSession h=session();QcaHtcCredit c={0};QcaWmiInitTransaction s={0};assert(qca_htc_credit_begin(&c,&h.ready,&h.wmi));
  if(mode==0){c.size=h.ready.credit_size=64;} /* Insufficient credits. */
  if(mode==1)h.phase=QCA_HTC_SEND_SETUP;
  if(mode==2)h.prepared=1;
  if(mode==3)h.wmi.endpoint=2;
  if(mode==4)h.wmi.max_bytes=100;
  if(mode==5)c.outstanding=1;
  if(mode==6)c.reserved=1;
  if(mode==7)c.ticket=9;
  if(mode==8)h.wmi.service=QCA_HTC_HTT;
  if(mode==9)h.ready.endpoints=1;
  if(mode==10)h.htt.endpoint=1;
  QcaHtcCredit old=c;QcaWmiInitTransaction old_s=s;
  assert(!qca_wmi_init_begin(&s,&c,&h,&info,&resources,words,0,0)&&!memcmp(&old,&c,sizeof(c))&&!memcmp(&old_s,&s,sizeof(s)));checks++;
 }
 for(unsigned mode=0;mode<4;mode++){
  QcaHtcSession h=session();QcaHtcCredit c={0};QcaWmiInitTransaction s={0};assert(qca_htc_credit_begin(&c,&h.ready,&h.wmi));
  assert(qca_wmi_init_begin(&s,&c,&h,&info,&resources,words,0,0));
  if(mode==0){qca_wmi_init_fault(&s);assert(s.phase==QCA_INIT_RESERVED&&c.reserved==1);assert(qca_wmi_init_cancel(&s)&&c.available==2&&!c.reserved&&!qca_wmi_init_cancel(&s));checks++;continue;}
  assert(qca_wmi_init_post(&s));
  if(mode==1){qca_wmi_init_fault(&s);assert(s.phase==QCA_INIT_FAULT&&c.outstanding==1&&!qca_wmi_init_cancel(&s));checks++;continue;}
  unsigned n=ready(p,0);assert(qca_wmi_init_receive(&s,p,n,1)&&s.phase==QCA_INIT_POSTED);
  n=report(p,1,1);reject_rx(&s,p,n,1);reject_rx(&s,p,n,3);
  memcpy(mut,p,n);mut[13]=2;reject_rx(&s,mut,n,2);
  memcpy(mut,p,n);mut[12]=2;reject_rx(&s,mut,n,2);
  assert(qca_wmi_init_receive(&s,p,n,2)&&c.available==2&&!c.outstanding);checks++;reject_rx(&s,p,n,2);
  if(mode==2){assert(qca_wmi_init_complete(&s,s.frame_bytes)&&s.phase==QCA_INIT_RUNNING);checks++;}
  else{qca_wmi_init_fault(&s);assert(s.phase==QCA_INIT_FAULT&&c.available==2);checks++;}
 }
 printf("WMI INIT RESERVE/PUBLISH/DMA/READY ORDER, CREDIT REPORTS AND REJECTION checks=%u PASS\n",checks);return 0;
}
