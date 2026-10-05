#include "init_wire.h"
#include "upstream-init.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static unsigned checks;
#define CHECK(x) do{checks++;assert(x);}while(0)
static unsigned oracle(uint8_t*out,const uint32_t*words,const QcaWmiHostChunk*chunks,unsigned count){
 memset(out,0,600);uint32_t command=WMI_TLV_INIT_CMDID;memcpy(out,&command,4);
 struct wmi_tlv a={.len=sizeof(struct wmi_tlv_init_cmd),.tag=WMI_TLV_TAG_STRUCT_INIT_CMD};memcpy(out+4,&a,4);
 struct wmi_tlv_init_cmd cmd={.abi={.abi_ver0=WMI_TLV_ABI_VER0,.abi_ver1=WMI_TLV_ABI_VER1,.abi_ver_ns0=WMI_TLV_ABI_VER_NS0,.abi_ver_ns1=WMI_TLV_ABI_VER_NS1,.abi_ver_ns2=WMI_TLV_ABI_VER_NS2,.abi_ver_ns3=WMI_TLV_ABI_VER_NS3},.num_host_mem_chunks=count};memcpy(out+8,&cmd,sizeof(cmd));
 unsigned pos=8+sizeof(cmd);a=(struct wmi_tlv){.len=sizeof(struct wmi_tlv_resource_config),.tag=WMI_TLV_TAG_STRUCT_RESOURCE_CONFIG};memcpy(out+pos,&a,4);pos+=4;
 struct wmi_tlv_resource_config cfg;memcpy(&cfg,words,sizeof(cfg));memcpy(out+pos,&cfg,sizeof(cfg));pos+=sizeof(cfg);
 a=(struct wmi_tlv){.len=count*(4+sizeof(struct host_memory_chunk_tlv)),.tag=WMI_TLV_TAG_ARRAY_STRUCT};memcpy(out+pos,&a,4);pos+=4;
 for(unsigned i=0;i<count;i++){
  a=(struct wmi_tlv){.len=sizeof(struct host_memory_chunk_tlv),.tag=WMI_TLV_TAG_STRUCT_WLAN_HOST_MEMORY_CHUNK};memcpy(out+pos,&a,4);pos+=4;
  struct host_memory_chunk_tlv m={.req_id=chunks[i].id,.ptr=(uint32_t)chunks[i].address,.size=chunks[i].bytes};memcpy(out+pos,&m,sizeof(m));pos+=sizeof(m);
 }
 return pos;
}
int main(void){
 CHECK(sizeof(struct wmi_tlv_resource_config)==176&&sizeof(struct wmi_tlv_init_cmd)==28&&sizeof(struct host_memory_chunk_tlv)==16);
 uint32_t words[44];QcaWmiHostChunk chunks[16];uint8_t out[600],expected[600],old[600];QcaWmiResources r={1,2,0,16777216};
 unsigned seed=12345;
 for(unsigned count=0;count<=16;count++)for(unsigned trial=0;trial<128;trial++){
  QcaWmiServiceInfo info={.memory_count=count};
  for(unsigned i=0;i<44;i++){seed=seed*1664525u+1013904223u;words[i]=seed;}
  words[0]=1;words[1]=2;
  for(unsigned i=0;i<count;i++){
   info.memory[i]=(QcaWmiMemoryRequest){i,1+trial,0,1+i};unsigned bytes=(1+i)*((trial+4)&~3u);
   chunks[i]=(QcaWmiHostChunk){i,bytes,0x100000u+0x10000u*i};
  }
  unsigned n=oracle(expected,words,chunks,count);memset(out,0xa5,sizeof(out));memcpy(old,out,sizeof(out));
  for(unsigned cap=0;cap<n;cap++){
   CHECK(!qca_wmi_init_wire(out,cap,words,&info,&r,chunks,count));CHECK(!memcmp(out,old,sizeof(out)));
  }
  CHECK(qca_wmi_init_wire(out,sizeof(out),words,&info,&r,chunks,count)==n);CHECK(!memcmp(out,expected,n));CHECK(!memcmp(out+n,old+n,sizeof(out)-n));
  if(count){
   for(unsigned bad=0;bad<6;bad++){
    QcaWmiHostChunk saved=chunks[0];
    if(bad==0)chunks[0].id=99;
    if(bad==1)chunks[0].bytes++;
    if(bad==2)chunks[0].address=0;
    if(bad==3)chunks[0].address++;
    if(bad==4)chunks[0].address=0x100000000ull;
    if(bad==5)chunks[0].address=0xfffffffcull;
    if(bad==5&&chunks[0].bytes<=4){chunks[0]=saved;continue;}
    memcpy(out,old,sizeof(out));CHECK(!qca_wmi_init_wire(out,sizeof(out),words,&info,&r,chunks,count));CHECK(!memcmp(out,old,sizeof(out)));chunks[0]=saved;
   }
  }
  if(count>1){uint64_t address=chunks[1].address;chunks[1].address=chunks[0].address;CHECK(!qca_wmi_init_wire(out,sizeof(out),words,&info,&r,chunks,count));chunks[1].address=address;}
  words[0]=2;memcpy(out,old,sizeof(out));CHECK(!qca_wmi_init_wire(out,sizeof(out),words,&info,&r,chunks,count));CHECK(!memcmp(out,old,sizeof(out)));words[0]=1;
 }
 QcaWmiServiceInfo info={0};CHECK(!qca_wmi_init_wire(out,sizeof(out),words,&info,&r,chunks,17));
 CHECK(!qca_wmi_init_wire((uint8_t*)words,176,words,&info,&r,chunks,0));CHECK(!qca_wmi_init_wire(0,600,words,&info,&r,chunks,0));
 printf("WMI INIT %u pinned-layout/capacity/address/plan checks PASS\n",checks);return 0;
}
