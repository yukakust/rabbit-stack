#include "wmi_boot_info.h"
static uint32_t word(const uint8_t*p){return p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static int abi(const uint8_t*p){return word(p)==0x01000000&&word(p+8)==0x5f414351&&word(p+12)==0x4c4d&&!word(p+16)&&!word(p+20);}
static int band(uint32_t low,uint32_t high,unsigned min,unsigned max){return (!low&&!high)||(low>=min&&low<=high&&high<=max);}
int qca_wmi_service_info(const uint8_t*p,unsigned n,QcaWmiServiceInfo*out){
 QcaWmiServiceInfo v={0};QcaWmiTlv t,m;unsigned pos=0,seen=0,arrays=0,declared=0;int rc;
 if(!p||!out||n<4||n>4096||word(p)!=1)return 0;
 while((rc=qca_wmi_tlv(p+4,n-4,&pos,&t))==1){
  if(t.tag==32){
   if((seen&1)||(t.bytes!=104&&t.bytes!=128)||!abi(t.value+4))return 0;
   seen|=1;v.build=word(t.value);v.abi_minor=word(t.value+8);v.chains=word(t.value+36);declared=word(t.value+72);
   if(!v.chains||v.chains>4||declared>16)return 0;
  }else if(t.tag==33){
   if((seen&2)||t.bytes!=36)return 0;
   seen|=2;v.regdomain=word(t.value);v.low2=word(t.value+20);v.high2=word(t.value+24);v.low5=word(t.value+28);v.high5=word(t.value+32);
   if(!band(v.low2,v.high2,2300,2800)||!band(v.low5,v.high5,4900,6500))return 0;
  }else if(t.tag==16){
   if(!arrays++){
    if(!t.bytes||t.bytes>512)return 0;
    seen|=4;v.service_count=t.bytes/4;for(unsigned i=0;i<v.service_count;i++)v.service_words[i]=word(t.value+4*i);
   }
  }else if(t.tag==18){
   unsigned off=0;int nested;
   if(seen&8)return 0;
   seen|=8;
   while((nested=qca_wmi_tlv(t.value,t.bytes,&off,&m))==1){
    if(m.tag!=34||m.bytes!=16||v.memory_count>=16)return 0;
    QcaWmiMemoryRequest req={word(m.value),word(m.value+4),word(m.value+8),word(m.value+12)};
    if(!req.unit_size||req.unit_size>65536||req.unit_flags>4||(req.unit_flags&&(req.unit_flags&(req.unit_flags-1)))||req.units>1048576)return 0;
    for(unsigned i=0;i<v.memory_count;i++)if(v.memory[i].id==req.id)return 0;
    v.memory[v.memory_count++]=req;
   }
   if(nested<0)return 0;
  }
 }
 if(rc<0||seen!=15||declared!=v.memory_count)return 0;
 *out=v;return 1;
}
int qca_wmi_ready_info(const uint8_t*p,unsigned n,QcaWmiReadyInfo*out){
 QcaWmiReadyInfo v={0};QcaWmiTlv t;unsigned pos=0,seen=0,any=0;int rc;
 if(!p||!out||n<4||n>4096||word(p)!=2)return 0;
 while((rc=qca_wmi_tlv(p+4,n-4,&pos,&t))==1){
  if(t.tag==35){
   if(seen++||t.bytes!=36||!abi(t.value)||word(t.value+32))return 0;
   v.abi_minor=word(t.value+4);for(unsigned i=0;i<6;i++){v.mac[i]=t.value[24+i];any|=v.mac[i];}
   if(!any||(v.mac[0]&1))return 0;
  }
 }
 if(rc<0||seen!=1)return 0;
 *out=v;return 1;
}
