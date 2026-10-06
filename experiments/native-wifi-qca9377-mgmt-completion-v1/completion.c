#include "completion.h"
static uint32_t word(const uint8_t*p){return p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static int overlap(const void*a,unsigned na,const void*b,unsigned nb){
 uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;
 if(x>UINTPTR_MAX-na||y>UINTPTR_MAX-nb)return 1;
 return x<y?y-x<na:x-y<nb;
}
int qca_mgmt_completion(const uint8_t*p,unsigned n,unsigned ack,QcaMgmtCompletion*out){
 if(!p||!out||n<8||n>2048||ack>1||overlap(p,n,out,sizeof(*out)))return 0;
 QcaMgmtCompletion v={0};uint32_t event=word(p);unsigned pos=4,seen=0,arrays=0;
 const uint8_t*data[4]={0};unsigned bytes[4]={0};
 if(event!=28678&&event!=28679)return 0;
 while(pos<n){
  if(n-pos<4)return 0;
  uint32_t head=word(p+pos);unsigned tag=head>>16,len=head&65535;pos+=4;
  if((len&3)||len>n-pos)return 0;
  if(event==28678&&tag==423){
   if(seen++||len!=20)return 0;
   v.count=1;v.has_ppdu=1;v.has_rssi=(uint8_t)ack;
   QcaMgmtReport*r=&v.report[0];r->id=word(p+pos);r->status=word(p+pos+4);
   r->pdev=word(p+pos+8);r->ppdu=word(p+pos+12);if(ack)r->rssi=word(p+pos+16);
  }else if(event==28679&&tag==552){
   if(seen++||len!=4)return 0;
   v.count=word(p+pos);if(v.count>QCA_MGMT_REPORTS)return 0;
  }else if(event==28679&&tag==16){
   if(arrays==4)return 0;
   data[arrays]=p+pos;bytes[arrays++]=len;
  }else return 0; /* Narrow admitted envelope, no guessed extension. */
  pos+=len;
 }
 if(seen!=1)return 0;
 if(event==28679){
  if(arrays<2||(ack&&arrays!=4))return 0;
  for(unsigned j=0;j<arrays;j++)if(bytes[j]!=4*v.count)return 0;
  v.has_ppdu=arrays>=3;v.has_rssi=(uint8_t)ack;
  for(unsigned j=0;j<v.count;j++){
   QcaMgmtReport*r=&v.report[j];r->id=word(data[0]+4*j);r->status=word(data[1]+4*j);
   if(v.has_ppdu)r->ppdu=word(data[2]+4*j);
   if(ack)r->rssi=word(data[3]+4*j);
   for(unsigned k=0;k<j;k++)if(r->id==v.report[k].id)return 0;
  }
 }
 *out=v;return 1;
}
int qca_mgmt_completion_plan(const QcaMgmtCompletion*c,const uint32_t*ids,unsigned n,uint32_t*out){
 if(!c||!out||n>32||(n&&!ids)||c->count>32||c->has_ppdu>1||c->has_rssi>1
  ||overlap(c,sizeof(*c),out,sizeof(*out))||(n&&overlap(ids,n*4,out,sizeof(*out))))return 0;
 uint32_t mask=0;
 for(unsigned j=0;j<n;j++)for(unsigned k=0;k<j;k++)if(ids[j]==ids[k])return 0;
 for(unsigned j=0;j<c->count;j++){
  unsigned k=0;for(;k<n;k++)if(ids[k]==c->report[j].id)break;
  if(k==n||(mask&(1u<<k)))return 0;
  mask|=1u<<k;
 }
 *out=mask;return 1;
}
