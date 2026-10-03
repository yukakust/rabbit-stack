/* Synthetic/test keys only. Files supplied by the deterministic host verifier. */
#include "firmware_chunks.h"
#include "sha256.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
static uint32_t u32(const uint8_t*p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static uint8_t*readfile(const char*dir,const char*name,size_t*n){
 char path[4096];assert(snprintf(path,sizeof(path),"%s/%s",dir,name)>0);
 FILE*f=fopen(path,"rb");assert(f);assert(!fseek(f,0,SEEK_END));long len=ftell(f);assert(len>=0&&len<=QCA_FW_MAX);rewind(f);
 uint8_t*p=malloc((size_t)len+1);assert(p);assert(fread(p,1,(size_t)len,f)==(size_t)len);assert(!fclose(f));*n=(size_t)len;return p;
}
int main(int argc,char**argv){
 assert(argc==2);size_t n;uint8_t*raw=readfile(argv[1],"policy.bin",&n);assert(n==120);
 QcaFirmwarePolicy policy={0};memcpy(policy.owner,raw,32);memcpy(policy.target,raw+32,32);memcpy(policy.digest,raw+64,32);
 policy.total=u32(raw+96);policy.type=u32(raw+100);policy.version=u32(raw+104);policy.kind=u32(raw+108);policy.generation=u32(raw+112)|((uint64_t)u32(raw+116)<<32);free(raw);
 uint8_t*memory=malloc(QCA_FW_MAX);assert(memory);memset(memory,0x5a,QCA_FW_MAX);
 QcaFirmwareChunks s={0};QcaFirmwarePolicy bad=policy;
 bad.total=QCA_FW_MAX+1;assert(qca_fw_begin(&s,&bad,memory,QCA_FW_MAX)<0);
 bad=policy;bad.type=0;assert(qca_fw_begin(&s,&bad,memory,QCA_FW_MAX)<0);
 assert(qca_fw_begin(&s,&policy,memory,policy.total-1)<0);
 assert(!qca_fw_begin(&s,&policy,memory,QCA_FW_MAX));assert(qca_fw_begin(&s,&policy,memory,QCA_FW_MAX)<0);
 uint8_t*p=readfile(argv[1],"chunk-0.bin",&n);const uint8_t*out=0;size_t len=0;
 assert(qca_fw_pin(&s,&out,&len)<0);
 for(size_t truncated=0;truncated<QCA_FW_HEADER;truncated++)assert(qca_fw_accept(&s,p,truncated)<0);
 unsigned offsets[]={0,8,40,72,104,108,112,116,120,128,132,136,140,160,224};
 for(unsigned i=0;i<sizeof(offsets)/sizeof(offsets[0]);i++){
  unsigned off=offsets[i];p[off]^=1;assert(qca_fw_accept(&s,p,n)<0);p[off]^=1;
  assert(!s.received&&!s.ready&&memory[0]==0x5a);
 }
 free(p);
 const char*foreign[]={"wrong-key.bin","wrong-generation.bin","wrong-type.bin","wrong-version.bin","wrong-kind.bin","wrong-target.bin"};
 for(unsigned i=0;i<sizeof(foreign)/sizeof(foreign[0]);i++){
  p=readfile(argv[1],foreign[i],&n);assert(qca_fw_accept(&s,p,n)<0);free(p);assert(!s.received&&!s.ready);
 }
 unsigned count=(policy.total+QCA_FW_CHUNK-1)/QCA_FW_CHUNK;
 /* Out-of-order and retry are permitted; ready only after final full hash. */
 for(unsigned i=count;i-->0;){
  char name[64];snprintf(name,sizeof(name),"chunk-%u.bin",i);p=readfile(argv[1],name,&n);
  assert(!qca_fw_accept(&s,p,n));assert(qca_fw_accept(&s,p,n)==1);free(p);
  assert(s.ready==(i==0));
 }
 uint8_t hash[32];rabbit_sha256(hash,memory,policy.total);assert(!memcmp(hash,policy.digest,32));
 assert(!qca_fw_pin(&s,&out,&len)&&out==memory&&len==policy.total);
 assert(qca_fw_cancel(&s)<0);assert(qca_fw_pin(&s,&out,&len)<0);
 p=readfile(argv[1],"chunk-0.bin",&n);assert(qca_fw_accept(&s,p,n)<0);
 assert(!qca_fw_unpin(&s));assert(qca_fw_unpin(&s)<0);
 memory[0]^=1;assert(qca_fw_pin(&s,&out,&len)<0&&s.poisoned&&!s.ready);
 assert(!qca_fw_cancel(&s));for(unsigned i=0;i<policy.total;i++)assert(!memory[i]);if(policy.total<QCA_FW_MAX)assert(memory[policy.total]==0x5a);
 /* Corrupted RAM before final chunk poisons assembly; cannot expose it. */
 if(count>1){
  assert(!qca_fw_begin(&s,&policy,memory,QCA_FW_MAX));assert(!qca_fw_accept(&s,p,n));memory[0]^=1;
  for(unsigned i=1;i<count;i++){
   char name[64];snprintf(name,sizeof(name),"chunk-%u.bin",i);size_t z;uint8_t*q=readfile(argv[1],name,&z);
   int result=qca_fw_accept(&s,q,z);assert(i==count-1?result==-7:result==0);free(q);
  }
  assert(s.poisoned&&!s.ready&&qca_fw_pin(&s,&out,&len)<0);assert(qca_fw_accept(&s,p,n)<0);assert(!qca_fw_cancel(&s));
 }
 free(p);free(memory);printf("RAM SIGNATURE/BOUNDS/RETRY/PIN/CANCEL PASS bytes=%u chunks=%u\n",policy.total,count);return 0;
}
