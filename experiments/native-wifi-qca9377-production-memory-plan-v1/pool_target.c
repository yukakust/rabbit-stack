#include "pool_target.h"
#include <string.h>
static int range(const void*p,size_t n){return p&&(uintptr_t)p<=UINTPTR_MAX-n;}
static int overlap(const void*a,size_t an,const void*b,size_t bn){return (uintptr_t)a<(uintptr_t)b+bn&&(uintptr_t)b<(uintptr_t)a+an;}
/* Official EDK2 x64 offsets, independently checked in host/COFF oracle.
 * Caller proves platform-supplied mapped SystemTable/BootServices lifetimes.
 * Header signatures/nonnull functions are consistency checks, not authenticity. */
int qca_pool_api_from_system(const void*st,QcaPoolBoot*out){
 if(!range(st,120)||!range(out,sizeof(*out))||(uintptr_t)st%8||(uintptr_t)out%_Alignof(QcaPoolBoot)||overlap(st,120,out,sizeof(*out)))return 0;
 uint64_t sig;uint32_t bytes;memcpy(&sig,st,8);memcpy(&bytes,(const uint8_t*)st+12,4);
 if(sig!=UINT64_C(0x5453595320494249)||bytes<120||bytes>4096)return 0;
 const void*bs;memcpy(&bs,(const uint8_t*)st+96,sizeof(bs));
 if(!range(bs,80)||(uintptr_t)bs%8||overlap(bs,80,out,sizeof(*out)))return 0;
 memcpy(&sig,bs,8);memcpy(&bytes,(const uint8_t*)bs+12,4);
 if(sig!=UINT64_C(0x56524553544f4f42)||bytes<80||bytes>4096)return 0;
 QcaPoolBoot tmp;memcpy(&tmp.allocate,(const uint8_t*)bs+64,8);memcpy(&tmp.release,(const uint8_t*)bs+72,8);
 if(!tmp.allocate||!tmp.release)return 0;*out=tmp;return 1;
}
