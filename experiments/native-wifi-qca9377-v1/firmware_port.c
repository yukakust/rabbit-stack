/* Native RAM lifetime adapter. It does not Map RAM for DMA or load firmware. */
#include "firmware_port.h"
typedef Status(EFIAPI *Allocate)(uint32_t,uint64_t,void**);
typedef Status(EFIAPI *Release)(void*);
static uint32_t u32(const uint8_t*p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static int nonzero(const uint8_t*p,size_t n){uint8_t x=0;for(size_t i=0;i<n;i++)x|=p[i];return !!x;}
static int valid(SystemTable*st){
 if(!st||!st->boot||st->header.signature!=0x5453595320494249ull||st->header.size<sizeof(*st))return 0;
 const TableHeader*h=st->boot;
 return h->signature==0x56524553544f4f42ull&&h->size>=80&&service(st,64)&&service(st,72);
}
static int methods(QcaFirmwarePort*s){return valid(s->system)&&service(s->system,64)==s->allocate&&service(s->system,72)==s->release;}
static int fail(QcaFirmwarePort*s,unsigned step,Status rc){s->error=(step<<8)|(uint32_t)(rc&255);s->phase=6;return -1;}
int qca_fwp_owned(const QcaFirmwarePort*s){return s&&(s->memory_owned||s->workspace_owned||s->asset.pinned);}
int qca_fwp_start(QcaFirmwarePort*s,SystemTable*st,const QcaFirmwarePolicy*p,const uint8_t*d,size_t n){
 if(!s||s->phase||qca_fwp_owned(s)||!valid(st)||!p||!d||n!=280
  ||d[0]!='Q'||d[1]!='P'||d[2]!='D'||d[3]!=7||u32(d+4)!=15||nonzero(d+8,8)||nonzero(d+24,16)
  ||u32(d+16)>64||u32(d+20)!=1||u32(d+40)>65535||u32(d+44)>255||u32(d+48)>31||u32(d+52)>7
  ||u32(d+64)!=0x0042168c||u32(d+72)!=0x02800031||u32(d+108)!=0x18101028
  ||u32(d+128)!=5||u32(d+136)||u32(d+140)!=1||!u32(d+132)||u32(d+132)==UINT32_MAX
  ||u32(d+164)||u32(d+168)||u32(d+192)||u32(d+196)||!(u32(d+200)&2)||(u32(d+200)&1)
  ||u32(d+204)||u32(d+208)!=p->version||u32(d+212)!=p->type||u32(d+220)||u32(d+228)||u32(d+232)||u32(d+236)
  ||d[244]||d[245]||d[250]||d[251]
  ||!p->total||p->total>QCA_FW_MAX||!p->generation||!p->type||p->type==UINT32_MAX||!p->version||p->version==UINT32_MAX
  ||(p->kind!=1&&p->kind!=2)||!nonzero(p->owner,32)||!nonzero(p->target,32)||!nonzero(p->digest,32))return -1;
 s->system=st;s->allocate=service(st,64);s->release=service(st,72);s->policy=*p;s->error=0;s->uncertain=0;s->phase=1;return 0;
}
int qca_fwp_step(QcaFirmwarePort*s){
 if(!s||!s->phase||s->phase>4)return -1;
 if(s->phase==4)return 0;
 if(!methods(s))return fail(s,1,0);
 if(s->phase==1||s->phase==2){
  void*pointer=0;unsigned phase=s->phase;
  uint64_t length=phase==1?s->policy.total:QCA_FW_HEADER+QCA_FW_CHUNK;
  Status rc=((Allocate)s->allocate)(4,length,&pointer);
  if(phase==1){s->memory=pointer;s->memory_owned=pointer!=0;}
  else{s->workspace=pointer;s->workspace_owned=pointer!=0;}
  /* A non-NULL output accompanying failure is not safe to dereference/free. */
  if(rc){if(pointer)s->uncertain=1;return fail(s,phase+1,rc);}
  if(!pointer)return fail(s,phase+1,0);
  if((uintptr_t)pointer>UINTPTR_MAX-length){s->uncertain=1;return fail(s,4,0);}
  if(phase==2&&((uintptr_t)s->memory<(uintptr_t)s->workspace+length)
   &&((uintptr_t)s->workspace<(uintptr_t)s->memory+s->policy.total)){s->uncertain=1;return fail(s,4,0);}
  s->phase++;return 1;
 }
 if(qca_fw_begin(&s->asset,&s->policy,s->memory,s->policy.total)
  ||qca_fc_init(&s->channel,&s->asset,s->workspace,QCA_FW_HEADER+QCA_FW_CHUNK))return fail(s,5,0);
 s->phase=4;return 0;
}
int qca_fwp_close(QcaFirmwarePort*s){
 if(!s)return -1;
 if(s->asset.pinned||s->uncertain)return -1;
 if(!qca_fwp_owned(s)){s->phase=0;return 0;}
 if(!methods(s))return fail(s,6,0);
 if(s->channel.workspace&&qca_fc_close(&s->channel))return fail(s,7,0);
 if(s->asset.memory&&qca_fw_cancel(&s->asset))return fail(s,8,0);
 s->phase=5;
 if(s->workspace_owned){
  Status rc=((Release)s->release)(s->workspace);if(rc)return fail(s,9,rc);
  s->workspace_owned=0;s->workspace=0;if(!s->memory_owned)s->phase=0;return s->memory_owned?1:0;
 }
 Status rc=((Release)s->release)(s->memory);if(rc)return fail(s,10,rc);
 s->memory_owned=0;s->memory=0;s->phase=0;return 0;
}
size_t qca_fwp_att(QcaFirmwarePort*s,uint16_t mtu,const uint8_t*p,size_t n,uint8_t*r,size_t capacity){
 return qca_fc_att(s&&s->phase==4?&s->channel:0,mtu,p,n,r,capacity);
}
