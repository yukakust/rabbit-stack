#include "firmware_port.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
static unsigned scenario,allocs,frees,failed_free;static void*blocks[2];static size_t sizes[2];
static uint32_t u32(const uint8_t*p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static void put(uint8_t*p,uint32_t n){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(n>>(i*8));}
static Status EFIAPI allocate(uint32_t kind,uint64_t n,void**out){
 assert(kind==4&&allocs<2&&n>0&&n<=QCA_FW_MAX);unsigned slot=allocs++;
 if((scenario==1&&!slot)||(scenario==2&&slot))return EFI_ERROR(9);
 if(scenario==5&&!slot)return 0;
 if(scenario==8&&slot){*out=blocks[0];return 0;}
 *out=blocks[slot]=malloc((size_t)n);assert(*out);sizes[slot]=(size_t)n;
 if((scenario==6&&!slot)||(scenario==7&&slot))return EFI_ERROR(9);
 return 0;
}
static Status EFIAPI release(void*p){
 unsigned slot=p==blocks[0]?0:1;assert(p&&p==blocks[slot]);frees++;
 if(!failed_free&&((scenario==3&&!slot)||(scenario==4&&slot))){failed_free=1;return EFI_ERROR(7);}
 if(scenario==10&&!slot)for(size_t i=0;i<sizes[slot];i++)assert(!((uint8_t*)p)[i]);
 free(blocks[slot]);blocks[slot]=0;return 0;
}
static uint8_t*readfile(const char*dir,const char*name,size_t*n){char path[4096];snprintf(path,sizeof(path),"%s/%s",dir,name);FILE*f=fopen(path,"rb");assert(f);assert(!fseek(f,0,SEEK_END));long z=ftell(f);assert(z>0&&z<=QCA_FW_MAX);rewind(f);uint8_t*p=malloc((size_t)z);assert(p&&fread(p,1,(size_t)z,f)==(size_t)z);fclose(f);*n=(size_t)z;return p;}
int main(int argc,char**argv){
 assert(argc==3);scenario=(unsigned)atoi(argv[1]);size_t n;uint8_t*p=readfile(argv[2],"policy.bin",&n);assert(n==120);QcaFirmwarePolicy policy={0};
 memcpy(policy.owner,p,32);memcpy(policy.target,p+32,32);memcpy(policy.digest,p+64,32);policy.total=u32(p+96);policy.type=u32(p+100);policy.version=u32(p+104);policy.kind=u32(p+108);policy.generation=u32(p+112)|((uint64_t)u32(p+116)<<32);free(p);
 uint64_t boot[10]={0};TableHeader*header=(TableHeader*)boot;header->signature=0x56524553544f4f42ull;header->size=80;boot[8]=(uintptr_t)allocate;boot[9]=(uintptr_t)release;
 SystemTable st={0};st.header.signature=0x5453595320494249ull;st.header.size=sizeof(st);st.boot=boot;
 uint8_t d[280]={0};memcpy(d,"QPD\7",4);put(d+4,15);put(d+16,7);put(d+20,1);put(d+64,0x0042168c);put(d+72,0x02800031);put(d+108,0x18101028);put(d+128,5);put(d+132,0x003821ff);put(d+140,1);put(d+200,2);put(d+208,policy.version);put(d+212,policy.type);
 QcaFirmwarePort s={0};unsigned bad_offsets[]={4,8,20,24,64,72,108,128,136,140,164,168,192,196,200,204,208,212,220,228,232,236,244,245,250,251};
 for(unsigned i=0;i<sizeof(bad_offsets)/sizeof(bad_offsets[0]);i++){unsigned off=bad_offsets[i];d[off]^=1;assert(qca_fwp_start(&s,&st,&policy,d,280)<0&&!allocs&&!s.phase);d[off]^=1;}
 assert(qca_fwp_start(&s,&st,&policy,d,279)<0);header->signature^=1;assert(qca_fwp_start(&s,&st,&policy,d,280)<0);header->signature^=1;
 assert(!qca_fwp_start(&s,&st,&policy,d,280));assert(qca_fwp_start(&s,&st,&policy,d,280)<0);
 while(s.phase<4){unsigned before=allocs;int r=qca_fwp_step(&s);assert(allocs-before<=1);if(r<0)break;}
 if(scenario==6||scenario==7||scenario==8){assert(s.uncertain&&qca_fwp_owned(&s)&&qca_fwp_close(&s)<0&&!frees);}
 else{
  if(scenario==10){
   assert(s.phase==4);unsigned count=(policy.total+65535)/65536;
   for(unsigned i=0;i<count;i++){char name[64];snprintf(name,sizeof(name),"chunk-%u.bin",i);p=readfile(argv[2],name,&n);assert(!qca_fw_accept(&s.asset,p,n));free(p);}
   const uint8_t*view;size_t z;assert(!qca_fw_pin(&s.asset,&view,&z));assert(qca_fwp_close(&s)<0&&!frees&&qca_fwp_owned(&s));assert(!qca_fw_unpin(&s.asset));
  }
  if(scenario==9){boot[9]=0;assert(qca_fwp_close(&s)<0&&!frees&&qca_fwp_owned(&s));boot[9]=(uintptr_t)release;}
  int r;unsigned attempts=0;do{unsigned before=frees;r=qca_fwp_close(&s);assert(frees-before<=1&&++attempts<8);}while(r);
  assert(!qca_fwp_owned(&s)&&!s.phase&&!blocks[0]&&!blocks[1]);
 }
 for(unsigned i=0;i<2;i++)if(blocks[i])free(blocks[i]); /* Fixture-only ambiguous allocator reclamation. */
 printf("UEFI RAM PORT SCENARIO %u PASS\n",scenario);return 0;
}
