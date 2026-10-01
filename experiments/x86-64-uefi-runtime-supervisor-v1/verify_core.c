#include "verify_core.h"
#include "sha256.h"
#include "monocypher-ed25519.h"
static const uint8_t domain[]="Rabbit trusted runtime update v1\0";
static const uint8_t world_development_key[32]={3,161,7,191,243,206,16,190,29,112,221,24,231,75,192,153,103,228,214,48,155,165,13,95,29,220,134,100,18,85,49,184};
static uint8_t message[MAX_RUNTIME_BYTES+sizeof(domain)];
static int same(const uint8_t *a,const uint8_t *b,size_t n){uint8_t x=0;for(size_t i=0;i<n;i++)x|=a[i]^b[i];return !x;}
static uint16_t u16(const uint8_t*p){return p[0]|((uint16_t)p[1]<<8);}
static uint32_t u32(const uint8_t*p){return u16(p)|((uint32_t)u16(p+2)<<16);}
static uint64_t u64(const uint8_t*p){return u32(p)|((uint64_t)u32(p+4)<<32);}
int rabbit_update_verify(const uint8_t *p,size_t n,const UpdatePolicy *policy){
 if(same(policy->owner,world_development_key,32))return 2;
 if(n<257||n>MAX_RUNTIME_BYTES||!same(p,(const uint8_t*)"RRT1",4)||u16(p+4)!=1||u16(p+6)!=1||u32(p+8)!=n||u32(p+12)!=n-256||u32(p+16)!=1||u32(p+20)!=1||u64(p+24)<=policy->counter)return 1;
 if(!same(p+32,policy->target,32)||!same(p+64,policy->base,32)||!same(p+128,policy->state,32)||!same(p+160,policy->owner,32))return 2;
 uint8_t hash[32];rabbit_sha256(hash,p+192,n-256);
 if(!same(hash,p+96,32))return 3;
 size_t prefix=sizeof(domain)-1;
 for(size_t i=0;i<prefix;i++)message[i]=domain[i];
 for(size_t i=0;i<n-64;i++)message[prefix+i]=p[i];
 if(crypto_ed25519_check(p+n-64,policy->owner,message,prefix+n-64))return 4;
 return 0;
}
/* Restrictive PE32+ boot-services-driver gate. Loader still performs relocations.
 * This is structural validation, NOT an instruction or side-effect sandbox. */
int rabbit_module_pe(const uint8_t *p,size_t n){
 if(n<128||n>MAX_RUNTIME_BYTES||p[0]!='M'||p[1]!='Z')return 1;
 size_t pe=u32(p+60);
 if(pe>n-24||!same(p+pe,(const uint8_t*)"PE\0\0",4)||u16(p+pe+4)!=0x8664)return 1;
 unsigned count=u16(p+pe+6),optional=u16(p+pe+20);
 size_t opt=pe+24;
 if(!count||count>16||optional!=240||optional>n-opt||u16(p+opt)!=0x20b||u16(p+opt+68)!=11)return 1;
 uint32_t entry=u32(p+opt+16),image=u32(p+opt+56),headers=u32(p+opt+60);
 if(!image||image>4*1024*1024||headers>n||u32(p+opt+108)!=16)return 1;
 /* No OS imports, TLS, CLR, or dynamic import mechanism in this profile. */
 unsigned forbidden[]={9,13,14};
 for(unsigned i=0;i<3;i++)if(u32(p+opt+112+forbidden[i]*8)||u32(p+opt+116+forbidden[i]*8))return 1;
 size_t sections=opt+optional;
 if(count>(n-sections)/40)return 1;
 int executable=0;
 for(unsigned i=0;i<count;i++){
  const uint8_t *s=p+sections+i*40;
  uint32_t virtual_size=u32(s+8),rva=u32(s+12),raw=u32(s+16),offset=u32(s+20),flags=u32(s+36);
  if(rva>image||virtual_size>image-rva||offset>n||raw>n-offset)return 1;
  if((flags&0xa0000000u)==0xa0000000u)return 1; /* No writable executable section. */
  if((flags&0x20000000u)&&entry>=rva&&entry-rva<virtual_size)executable=1;
  for(unsigned j=0;j<i;j++){
   const uint8_t *t=p+sections+j*40;uint32_t tr=u32(t+12),tv=u32(t+8);
   if(virtual_size&&tv&&rva<tr+tv&&tr<rva+virtual_size)return 1;
  }
 }
 /* MinGW emits a 24-byte all-zero import terminator even without imports.
  * Permit only this bounded empty table, never an actual DLL descriptor. */
 uint32_t imports=u32(p+opt+120),import_size=u32(p+opt+124);
 if(imports||import_size){
  if(!imports||import_size<20||import_size>32)return 1;
  const uint8_t *table=0;
  for(unsigned i=0;i<count;i++){
   const uint8_t*s=p+sections+i*40;uint32_t rva=u32(s+12),raw=u32(s+16),offset=u32(s+20);
   if(imports>=rva&&imports-rva<=raw&&import_size<=raw-(imports-rva))table=p+offset+imports-rva;
  }
  if(!table)return 1;
  for(unsigned i=0;i<import_size;i++)if(table[i])return 1;
 }
 return executable?0:1;
}
