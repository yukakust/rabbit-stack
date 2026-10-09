#include "init_wire.h"
static void put(uint8_t*p,uint32_t n){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(n>>(8*i));}
static void tlv(uint8_t*p,unsigned tag,unsigned bytes){put(p,bytes|(tag<<16));}
static int aliases(const uint8_t*out,unsigned n,const void*input,unsigned bytes){
 if(!bytes)return 0;
 uintptr_t a=(uintptr_t)out,b=(uintptr_t)input;
 if(!input||b>UINTPTR_MAX-bytes)return 1;
 return a<b?b-a<n:a-b<bytes;
}
unsigned qca_wmi_init_wire(uint8_t*out,unsigned cap,const uint32_t words[44],
 const QcaWmiServiceInfo*info,const QcaWmiResources*resources,const QcaWmiHostChunk*chunks,unsigned count){
 if(!out||!words||!info||!resources||count>16||(count&&!chunks))return 0;
 unsigned n=220+20*count;QcaWmiMemoryPlan plan;
 if(cap<n||(uintptr_t)out>UINTPTR_MAX-n||aliases(out,n,words,176)||aliases(out,n,info,sizeof(*info))
  ||aliases(out,n,resources,sizeof(*resources))||aliases(out,n,chunks,count*sizeof(*chunks)))return 0;
 if(words[0]!=resources->vdevs||words[1]!=resources->peers||resources->active_peers
  ||qca_wmi_memory_plan(info,resources,&plan)||plan.count!=count)return 0;
 for(unsigned i=0;i<count;i++){
  const QcaWmiHostChunk*c=&chunks[i];
  if(c->id!=plan.item[i].id||c->bytes!=plan.item[i].bytes||!c->bytes||!c->address||(c->address&3)
   ||c->address>UINT32_MAX||c->bytes-1>UINT32_MAX-c->address)return 0;
  for(unsigned j=0;j<i;j++)if(c->address<chunks[j].address+chunks[j].bytes&&chunks[j].address<c->address+c->bytes)return 0;
 }
 put(out,1);tlv(out+4,74,28);
 const uint32_t abi[6]={0x01000000,53,0x5f414351,0x4c4d,0,0};
 for(unsigned i=0;i<6;i++)put(out+8+4*i,abi[i]);
 put(out+32,count);tlv(out+36,75,176);
 for(unsigned i=0;i<44;i++)put(out+40+4*i,words[i]);
 tlv(out+216,18,20*count);
 for(unsigned i=0;i<count;i++){
  uint8_t*p=out+220+20*i;tlv(p,76,16);put(p+4,chunks[i].id);
  put(p+8,(uint32_t)chunks[i].address);put(p+12,chunks[i].bytes);put(p+16,0);
 }
 return n;
}
