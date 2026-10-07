#include "prefix.h"
void qca_prefix_arm(QcaPrefix*s,uint64_t now){if(s&&!s->phase){s->started=s->last=now;s->phase=1;}}
void qca_prefix_request(QcaPrefix*s,uint32_t why,uint32_t offset,uint32_t submitted,uint32_t completed,uint32_t plan,uint32_t io){
 if(!s||s->phase!=1)return;
 s->reason=why;s->phase=2;s->stop_offset=offset;s->stop_submitted=submitted;s->stop_completed=completed;s->stop_plan=plan;s->stop_io=io;
}
int qca_prefix_tick(QcaPrefix*s,uint64_t now,uint32_t boot_phase,uint32_t plan,uint32_t offset,uint32_t submitted,uint32_t completed,uint32_t pending,uint32_t io,uint32_t actual_released){
 if(!s||!s->phase)return 0;
 if(s->polls!=UINT32_MAX)s->polls++;
 if(s->phase==3)return 0;
 if(s->phase==2){s->last=now;if(actual_released==1){s->phase=3;s->raw_frozen=1;return 0;}return 1;}
 if(now<s->last)qca_prefix_request(s,2,offset,submitted,completed,plan,io);
 else if(now-s->started>=QCA_PREFIX_DEADLINE_US)qca_prefix_request(s,1,offset,submitted,completed,plan,io);
 else if(boot_phase!=1)qca_prefix_request(s,4,offset,submitted,completed,plan,io);
 else if(s->raw_overflow)qca_prefix_request(s,5,offset,submitted,completed,plan,io);
 else if(s->usb_fault)qca_prefix_request(s,6,offset,submitted,completed,plan,io);
 else if(plan==17&&offset>=QCA_PREFIX_LIMIT&&!pending&&submitted==completed)qca_prefix_request(s,0,offset,submitted,completed,plan,io);
 s->last=now;
 return s->phase==2;
}
void qca_prefix_event(QcaPrefix*s,const uint8_t*p,unsigned n,uint64_t now,uint32_t state,uint32_t pending){
 if(!s||(s->phase!=1&&s->phase!=2)||s->raw_frozen||!p||n<2||n>QCA_PREFIX_HCI_BYTES||n!=2u+p[1])return;
 unsigned critical=p[0]==5||p[0]==0x10||(p[0]==0x3e&&n>=3&&p[2]==1)
  ||(p[0]==0x0e&&n>=6&&p[5])||(p[0]==0x0f&&n>=6&&p[2]);
 unsigned i;
 if(critical){
  if(s->critical_count==4){if(s->raw_overflow!=UINT32_MAX)s->raw_overflow++;return;}
  i=s->critical_count++;
 }else{
  i=4+s->routine_head;s->routine_head=(s->routine_head+1)%12;
  if(s->routine_count<12)s->routine_count++;
  else if(s->routine_overwritten!=UINT32_MAX)s->routine_overwritten++;
 }
 s->raw_count=s->critical_count+s->routine_count;
 s->raw[i].at=now;s->raw[i].length=n;s->raw[i].state=state;s->raw[i].pending=pending;
 for(unsigned j=0;j<n;j++)s->raw[i].bytes[j]=p[j];
}
/* Stable after actual owner release: protected4 critical events + chronological
 * last12 routine events, explicit overwritten/critical-overflow counts.
 * This is bounded diagnostic history, never a complete controller history. */
unsigned qca_prefix_raw(const QcaPrefix*s,uint8_t*out,unsigned cap,unsigned offset){
 enum{TOTAL=64+QCA_PREFIX_HCI_SLOTS*288};if(!s||!out||offset>TOTAL)return UINT32_MAX;
 unsigned n=TOTAL-offset;if(n>cap)n=cap;
 for(unsigned i=0;i<n;i++){
  unsigned at=offset+i;uint8_t value=0;
  if(at<8){static const uint8_t m[8]={'Q','P','H','C','I','0','0','1'};value=m[at];}
  else if(at<64){const uint32_t v[14]={57,s->raw_count,s->raw_overflow,s->raw_frozen,s->phase,TOTAL,s->critical_count,s->routine_count,s->routine_head,s->routine_overwritten,(uint32_t)s->started,(uint32_t)(s->started>>32),(uint32_t)s->last,(uint32_t)(s->last>>32)};unsigned j=(at-8)/4;value=(uint8_t)(v[j]>>(8*((at-8)%4)));}
  else if(s->raw_frozen){unsigned logical=(at-64)/288,pos=(at-64)%288;
   unsigned valid=logical<4?logical<s->critical_count:logical-4<s->routine_count;
   unsigned slot=logical<4?logical:4+((logical-4+(s->routine_count==12?s->routine_head:0))%12);
   if(valid){const uint32_t h[4]={s->raw[slot].length,s->raw[slot].state,s->raw[slot].pending,logical<4};
    if(pos<8)value=(uint8_t)(s->raw[slot].at>>(8*pos));
    else if(pos<24)value=(uint8_t)(h[(pos-8)/4]>>(8*((pos-8)%4)));
    else if(pos<24+s->raw[slot].length)value=s->raw[slot].bytes[pos-24];
   }
  }
  out[i]=value;
 }
 return n;
}
