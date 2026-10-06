#include "wmi_boot_info.h"
#include "upstream-layout.h"
#include <assert.h>
#include <stddef.h>
#include <string.h>
#include <stdio.h>
static void put(uint8_t*p,uint32_t n){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(n>>(8*i));}
static unsigned fixture(uint8_t*p,unsigned size,unsigned requests){
 memset(p,0,640);put(p,1);put(p+4,size|(32u<<16));
 struct wmi_tlv_svc_rdy_ev v={0};v.fw_build_vers=21;v.abi.abi_ver0=0x01000000;v.abi.abi_ver1=574;v.abi.abi_ver_ns0=0x5f414351;v.abi.abi_ver_ns1=0x4c4d;v.num_rf_chains=1;v.num_mem_reqs=requests;
 memcpy(p+8,&v,sizeof(v));if(size==128)put(p+8+108,189);
 unsigned pos=8+size;put(p+pos,36|(33u<<16));pos+=4;put(p+pos,108);put(p+pos+20,2312);put(p+pos+24,2732);put(p+pos+28,4920);put(p+pos+32,6100);pos+=36;
 put(p+pos,128|(16u<<16));pos+=4;for(unsigned j=0;j<32;j++)put(p+pos+4*j,j&15);pos+=128;
 put(p+pos,20*requests|(18u<<16));pos+=4;
 for(unsigned j=0;j<requests;j++){put(p+pos,16|(34u<<16));put(p+pos+4,j);put(p+pos+8,32);put(p+pos+12,2);put(p+pos+16,10);pos+=20;}
 return pos;
}
static unsigned checks;
static void reject(const uint8_t*p,unsigned n){QcaWmiServiceInfo v={0},old;memset(&v,0xaa,sizeof(v));old=v;assert(!qca_wmi_service_info(p,n,&v)&&!memcmp(&v,&old,sizeof(v)));checks++;}
int main(void){
 assert(sizeof(struct wmi_tlv_svc_rdy_ev)==104&&offsetof(struct wmi_tlv_svc_rdy_ev,num_mem_reqs)==72&&offsetof(struct wmi_tlv_svc_rdy_ev,num_rf_chains)==36);
 uint8_t p[640],mut[640];QcaWmiServiceInfo info;
 for(unsigned size=104;size<=128;size+=24)for(unsigned requests=0;requests<=16;requests++){
  unsigned n=fixture(p,size,requests);assert(qca_wmi_service_info(p,n,&info)&&info.build==21&&info.abi_minor==574&&info.chains==1&&info.regdomain==108&&info.low2==2312&&info.high2==2732&&info.low5==4920&&info.high5==6100&&info.service_count==32&&info.memory_count==requests);checks++;
  for(unsigned j=0;j<requests;j++){assert(info.memory[j].id==j&&info.memory[j].unit_size==32&&info.memory[j].unit_flags==2&&info.memory[j].units==10);checks++;}
  memcpy(mut,p,n);put(mut+8+72,requests+1);reject(mut,n);
  memcpy(mut,p,n);put(mut+8+36,0);reject(mut,n);
  memcpy(mut,p,n);put(mut+12,0);reject(mut,n);
  for(unsigned cut=0;cut<n;cut++)reject(p,cut);
 }
 unsigned n=fixture(p,128,0);
 for(unsigned size=0;size<200;size+=4)if(size!=104&&size!=128){memcpy(mut,p,n);put(mut+4,size|(32u<<16));reject(mut,n);}
 for(unsigned i=0;i<24;i++)for(unsigned b=0;b<256;b++){memcpy(mut,p,n);mut[8+104+i]=(uint8_t)b;assert(qca_wmi_service_info(mut,n,&info)&&info.memory_count==0&&info.abi_minor==574);checks++;}
 unsigned reg=8+128+4;
 const unsigned positions[]={20,24,28,32};const uint32_t invalid[]={2299,2801,4899,6501};
 for(unsigned j=0;j<4;j++){memcpy(mut,p,n);put(mut+reg+positions[j],invalid[j]);reject(mut,n);}
 printf("PINNED104 CORE / EXTENDED128 / ABI / HARDWARE METADATA / MEMORY ARRAY checks=%u PASS\n",checks);return 0;
}
