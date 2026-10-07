#include "firmware_chunks.h"
#include "sha256.h"
#include "monocypher-ed25519.h"
static int same(const uint8_t*a,const uint8_t*b,size_t n){uint8_t x=0;for(size_t i=0;i<n;i++)x|=a[i]^b[i];return !x;}
static int nonzero(const uint8_t*a,size_t n){uint8_t x=0;for(size_t i=0;i<n;i++)x|=a[i];return x!=0;}
static uint32_t u32(const uint8_t*p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static uint64_t u64(const uint8_t*p){return u32(p)|((uint64_t)u32(p+4)<<32);}
int qca_fw_begin(QcaFirmwareChunks*s,const QcaFirmwarePolicy*p,uint8_t*m,size_t capacity){
 if(!s||!p||!m||s->memory||s->pinned||!p->total||p->total>QCA_FW_MAX||capacity<p->total
  ||!p->type||p->type==UINT32_MAX||!p->version||p->version==UINT32_MAX||!p->generation
  ||(p->kind!=1&&p->kind!=2)||!nonzero(p->owner,32)||!nonzero(p->target,32)||!nonzero(p->digest,32))return -1;
 s->policy=*p;s->memory=m;s->capacity=capacity;s->received=0;s->ready=s->poisoned=s->pinned=0;
 return 0;
}
int qca_fw_accept(QcaFirmwareChunks*s,const uint8_t*p,size_t n){
 if(!s||!s->memory||s->pinned||s->poisoned||!p||n<QCA_FW_HEADER||n>QCA_FW_HEADER+QCA_FW_CHUNK)return -1;
 if(!same(p,(const uint8_t*)"RABFW001",8)||!same(p+8,s->policy.target,32)||!same(p+40,s->policy.digest,32)
  ||u32(p+104)!=s->policy.total||u32(p+116)!=QCA_FW_CHUNK||u64(p+120)!=s->policy.generation
  ||u32(p+128)!=s->policy.type||u32(p+132)!=s->policy.version||u32(p+136)!=s->policy.kind
  ||nonzero(p+140,20))return -2;
 uint32_t offset=u32(p+108),length=u32(p+112),total=s->policy.total;
 if(offset>=total||offset%QCA_FW_CHUNK||!length||length>total-offset||length!=n-QCA_FW_HEADER
  ||length!=((total-offset>QCA_FW_CHUNK)?QCA_FW_CHUNK:total-offset))return -3;
 /* Signature covers the domain, immutable manifest and this chunk's hash. */
 if(crypto_ed25519_check(p+160,s->policy.owner,p,160))return -4;
 uint8_t hash[32];rabbit_sha256(hash,p+QCA_FW_HEADER,length);
 if(!same(hash,p+72,32))return -5;
 uint32_t bit=1u<<(offset/QCA_FW_CHUNK);
 if(s->received&bit)return same(s->memory+offset,p+QCA_FW_HEADER,length)?1:-6;
 for(uint32_t i=0;i<length;i++)s->memory[offset+i]=p[QCA_FW_HEADER+i];
 s->received|=bit;
 unsigned count=(total+QCA_FW_CHUNK-1)/QCA_FW_CHUNK;
 uint32_t all=count==32?UINT32_MAX:(1u<<count)-1;
 if(s->received==all){
  rabbit_sha256(hash,s->memory,total);
  if(!same(hash,s->policy.digest,32)){s->poisoned=1;return -7;}
  s->ready=1;
 }
 return 0;
}
int qca_fw_pin(QcaFirmwareChunks*s,const uint8_t**data,size_t*length){
 if(!s||!data||!length||!s->memory||!s->ready||s->poisoned||s->pinned)return -1;
 uint8_t hash[32];rabbit_sha256(hash,s->memory,s->policy.total);
 if(!same(hash,s->policy.digest,32)){s->poisoned=1;s->ready=0;return -1;}
 s->pinned=1;*data=s->memory;*length=s->policy.total;return 0;
}
int qca_fw_unpin(QcaFirmwareChunks*s){if(!s||!s->pinned)return -1;s->pinned=0;return 0;}
int qca_fw_cancel(QcaFirmwareChunks*s){
 if(!s||s->pinned)return -1;
 if(s->memory)for(uint32_t i=0;i<s->policy.total;i++)s->memory[i]=0;
 s->memory=0;s->capacity=0;s->received=0;s->ready=s->poisoned=0;return 0;
}
