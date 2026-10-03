#include "firmware_sender_core.h"
static uint32_t u32(const uint8_t*p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static int same(const uint8_t*a,const uint8_t*b,size_t n){uint8_t x=0;for(size_t i=0;i<n;i++)x|=a[i]^b[i];return !x;}
int qfs_parse(QfsStatus*s,const uint8_t*p,size_t n){
 if(!s||!p||n!=64||!same(p,(const uint8_t*)"RFCS0001",8)||p[60]>1||p[61]>1||p[62]>1||p[63])return -1;
 QfsStatus v={0};v.state=u32(p+8);v.error=u32(p+12);v.length=u32(p+16);v.received=u32(p+20);v.bitmap=u32(p+56);v.ready=p[60];v.pinned=p[61];v.poisoned=p[62];
 for(unsigned i=0;i<32;i++)v.digest[i]=p[i+24];
 if(v.state>4||v.received>v.length||v.length>65760||v.error>20||(v.error>7&&v.error!=20)
  ||(v.ready&&v.poisoned)||(v.pinned&&!v.ready)||(v.state!=3&&v.error))return -1;
 if(v.state==0){uint8_t x=0;for(unsigned i=0;i<32;i++)x|=v.digest[i];if(v.length||v.received||x)return -1;}
 else if(v.length<=224)return -1;
 if((v.state==2||v.state==3)&&v.received!=v.length)return -1;
 if(v.state==3&&!v.error)return -1;
 *s=v;return 0;
}
int qfs_next(const QfsStatus*s,const QfsExpected*e,QfsProgress*p){
 if(!s||!e||!p||e->length<=224||e->length>65760||!e->bit||(e->bit&(e->bit-1))
  ||(e->bit&e->all)!=e->bit||!e->all||p->floor>e->length||p->attempted>1)return QFS_INVALID;
 int match=s->length==e->length&&same(s->digest,e->digest,32);
 if(match&&s->state==3)return QFS_REJECTED;
 if(s->poisoned)return QFS_BUSY;
 if(match&&s->state==2){
  if(!(s->bitmap&e->bit)||(s->bitmap&~e->all)||s->ready!=(s->bitmap==e->all))return QFS_INVALID;
  p->floor=e->length;return QFS_DONE;
 }
 if(s->pinned)return QFS_BUSY;
 if(match&&s->state==1){
  if(s->received<p->floor)return QFS_LOSS;
  p->floor=s->received;return s->received==e->length?QFS_COMMIT:QFS_DATA;
 }
 if(s->state==1||s->state==4)return QFS_BUSY;
 if(p->attempted||p->floor)return QFS_LOSS;
 return QFS_BEGIN;
}
