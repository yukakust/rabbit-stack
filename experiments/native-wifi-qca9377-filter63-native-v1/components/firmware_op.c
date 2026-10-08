#include "firmware_op.h"
#include "sha256.h"
#include "firmware_policy.h"
static uint32_t word(const uint8_t*p){return p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
 }
static int fail(QcaHttFirmwareProof*s,unsigned e){s->error=e;
 return 0;
 }
int qca_htt_firmware_proof(QcaHttFirmwareProof*s,const QcaBootNative*b){
 if(!s||s->valid||s->error||!b||b->phase!=5||b->error||!b->owns_pin||!b->asset)return 0;
 
 const QcaFirmwareChunks*a=b->asset;
 
 if(!a->ready||!a->pinned||a->poisoned||!a->memory||a->capacity<a->policy.total||a->policy.total!=751436
 ||a->policy.type!=8||a->policy.version!=0x05020001||a->policy.kind!=1||!a->policy.generation
 ||(uintptr_t)a->memory>UINTPTR_MAX-a->policy.total)return fail(s,1);
 
 rabbit_sha256(s->digest,a->memory,a->policy.total);
 unsigned d=0;
 
 for(unsigned i=0;i<32;i++)d|=(s->digest[i]^a->policy.digest[i])|(s->digest[i]^qca_htt_container_digest[i]);
 if(d)return fail(s,2);
 
 const uint8_t*p=a->memory;
 const uint8_t magic[11]={'Q','C','A','-','A','T','H','1','0','K',0};
 
 for(unsigned i=0;i<11;i++)if(p[i]!=magic[i])return fail(s,3);
 
 uint32_t seen=0,helper_off=0,helper_bytes=0;
 
 for(uint32_t pos=12;pos<a->policy.total;){
  if(a->policy.total-pos<8)return fail(s,4);
 
  uint32_t tag=word(p+pos),n=word(p+pos+4);
 pos+=8;
 
  if(tag>6||(seen&(1u<<tag))||n>a->policy.total-pos||(((uint64_t)n+3)&~3ull)>a->policy.total-pos)return fail(s,5);
 
  seen|=1u<<tag;
 
  if(tag==3){s->main_offset=pos;
 s->main_bytes=n;
 }
  if(tag==4){helper_off=pos;
 helper_bytes=n;
 }
  if(tag==5||tag==6){if(n!=4)return fail(s,6);
 if(tag==5)s->wmi_op=word(p+pos);
 else {s->htt_op=word(p+pos);
 s->htt_offset=pos;
 }}
  pos+=(n+3)&~3u;
 
 }
 if(!(seen&(1u<<5))||!(seen&(1u<<6))||!(seen&(1u<<3))||!(seen&(1u<<4))||s->wmi_op!=4)return fail(s,7);
 
 if(b->plan.assets.main!=p+s->main_offset||b->plan.assets.main_bytes!=s->main_bytes||s->main_bytes!=727125
 ||b->plan.assets.helper!=p+helper_off||b->plan.assets.helper_bytes!=helper_bytes||helper_bytes!=24193)return fail(s,8);
 
 rabbit_sha256(s->main_digest,p+s->main_offset,s->main_bytes);
 s->generation=a->policy.generation;
 s->valid=1;
 return 1;
 
}
