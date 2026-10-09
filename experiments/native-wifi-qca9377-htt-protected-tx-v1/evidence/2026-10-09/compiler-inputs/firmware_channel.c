#include "firmware_channel.h"
#include "sha256.h"
static uint32_t u32(const uint8_t*p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static void put(uint8_t*p,uint32_t n){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(n>>(8*i));}
static int same(const uint8_t*a,const uint8_t*b,size_t n){uint8_t x=0;for(size_t i=0;i<n;i++)x|=a[i]^b[i];return !x;}
int qca_fc_init(QcaFirmwareChannel*s,QcaFirmwareChunks*a,uint8_t*w,size_t capacity){
 if(!s||s->workspace||!a||!a->memory||a->pinned||a->poisoned||!w||capacity<QCA_FW_HEADER+QCA_FW_CHUNK)return -1;
 s->asset=a;s->workspace=w;s->capacity=capacity;s->state=s->error=0;s->length=s->received=0;
 for(unsigned i=0;i<32;i++)s->digest[i]=0;
 return 0;
}
int qca_fc_control(QcaFirmwareChannel*s,const uint8_t*p,size_t n){
 if(!s||!s->workspace||!s->asset||!s->asset->memory||s->asset->pinned||!p||n!=QCA_FC_CONTROL
  ||!same(p,(const uint8_t*)"RFC1",4)||p[5]||p[6]||p[7])return -1;
 uint32_t length=u32(p+8);uint8_t op=p[4];
 if(length<=QCA_FW_HEADER||length>QCA_FW_HEADER+QCA_FW_CHUNK||length>s->capacity)return -1;
 int match=length==s->length&&same(p+12,s->digest,32);
 if(op==1){
  if(match&&s->state!=QCA_FC_IDLE&&s->state!=QCA_FC_ABORTED)return 0; /* Includes final receipt. */
  if(s->state==QCA_FC_STAGING||s->asset->poisoned)return -1;
  s->length=length;s->received=0;s->state=QCA_FC_STAGING;s->error=0;
  for(unsigned i=0;i<32;i++)s->digest[i]=p[12+i];
  return 0;
 }
 if(!match)return -1;
 if(op==3){
  if(s->state!=QCA_FC_STAGING&&s->state!=QCA_FC_ABORTED)return -1;
  for(uint32_t i=0;i<s->received;i++)s->workspace[i]=0;
  s->state=QCA_FC_ABORTED;return 0; /* Preserve exact aborted-session receipt. */
 }
 if(op!=2)return -1;
 if(s->state==QCA_FC_ACCEPTED||s->state==QCA_FC_REJECTED)return 0;
 if(s->state!=QCA_FC_STAGING||s->received!=s->length)return -1;
 uint8_t hash[32];rabbit_sha256(hash,s->workspace,s->length);
 int result=same(hash,s->digest,32)?qca_fw_accept(s->asset,s->workspace,s->length):-20;
 s->error=result<0?(uint8_t)(-result):0;
 s->state=result<0?QCA_FC_REJECTED:QCA_FC_ACCEPTED;return 0;
}
int qca_fc_data(QcaFirmwareChannel*s,const uint8_t*p,size_t n){
 if(!s||!s->workspace||!s->asset||!s->asset->memory||s->asset->pinned||s->asset->poisoned||s->state!=QCA_FC_STAGING||!p||n<=4||n>244)return -1;
 uint32_t offset=u32(p);size_t length=n-4;
 if(offset>s->length||length>s->length-offset)return -1;
 if(offset<s->received)return length<=s->received-offset&&same(s->workspace+offset,p+4,length)?0:-1;
 if(offset!=s->received)return -1;
 for(size_t i=0;i<length;i++)s->workspace[offset+i]=p[4+i];
 s->received+=(uint32_t)length;return 0;
}
void qca_fc_status(const QcaFirmwareChannel*s,uint8_t out[QCA_FC_STATUS]){
 for(unsigned i=0;i<QCA_FC_STATUS;i++)out[i]=0;
 for(unsigned i=0;i<8;i++)out[i]=(const uint8_t[]){'R','F','C','S','0','0','0','1'}[i];
 if(!s)return;
 put(out+8,s->state);put(out+12,s->error);put(out+16,s->length);put(out+20,s->received);
 for(unsigned i=0;i<32;i++)out[24+i]=s->digest[i];
 if(s->asset){put(out+56,s->asset->received);out[60]=s->asset->ready;out[61]=s->asset->pinned;out[62]=s->asset->poisoned;}
}
int qca_fc_close(QcaFirmwareChannel*s){
 if(!s||!s->workspace||!s->asset||s->asset->pinned)return -1;
 for(uint32_t i=0;i<s->received;i++)s->workspace[i]=0;
 s->workspace=0;s->capacity=0;s->asset=0;s->length=s->received=0;s->state=s->error=0;
 for(unsigned i=0;i<32;i++)s->digest[i]=0;
 return 0;
}
