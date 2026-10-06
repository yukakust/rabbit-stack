#include "wmi_boot_info.h"
#include "oracle.h"
#include <assert.h>
#include <stddef.h>
#include <string.h>
#include <stdio.h>
static unsigned checks;
static void put(uint8_t*p,uint32_t x){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(x>>(i*8));}
int main(void){
 _Static_assert(sizeof(struct wmi_tlv_rdy_ev)==36,"actual Linux prefix");
 _Static_assert(offsetof(struct wmi_tlv_rdy_ev,mac_addr)==24,"actual MAC offset");
 _Static_assert(offsetof(struct wmi_tlv_rdy_ev,status)==32,"actual status offset");
 uint8_t p[520]={0};QcaWmiReadyInfo v,old;memset(&old,0xa5,sizeof(old));
 for(unsigned size=0;size<=512;size+=4){
  memset(p,0,sizeof(p));put(p,2);put(p+4,size|(35u<<16));
  if(size>=36){struct wmi_tlv_rdy_ev q={0};q.abi.abi_ver0=0x01000000;q.abi.abi_ver1=574;q.abi.abi_ver_ns0=0x5f414351;q.abi.abi_ver_ns1=0x4c4d;q.mac_addr.addr[0]=0xc0;q.mac_addr.addr[5]=0xfb;memcpy(p+8,&q,sizeof(q));memset(p+44,0x5a,size-36);}
  v=old;assert(qca_wmi_ready_info(p,size+8,&v)==(size>=36));checks++;
  if(size<36)assert(!memcmp(&v,&old,sizeof(v)));
 }
 /* Exact observed60-byte WMI payload, no fabricated target acceptance. */
 const uint8_t actual[]={2,0,0,0,52,0,35,0,0,0,0,1,62,2,0,0,81,67,65,95,77,76,0,0,0,0,0,0,0,0,0,0,192,181,215,120,195,251,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
 assert(qca_wmi_ready_info(actual,sizeof(actual),&v)&&v.abi_minor==574&&v.mac[0]==192&&v.mac[5]==251);checks++;
 for(unsigned n=0;n<sizeof(actual);n++){v=old;assert(!qca_wmi_ready_info(actual,n,&v)&&!memcmp(&v,&old,sizeof(v)));checks++;}
 for(unsigned offset=8;offset<32;offset+=4){memcpy(p,actual,sizeof(actual));p[offset]^=1;v=old;if(offset!=12){assert(!qca_wmi_ready_info(p,sizeof(actual),&v)&&!memcmp(&v,&old,sizeof(v)));checks++;}}
 memcpy(p,actual,sizeof(actual));p[40]=1;assert(!qca_wmi_ready_info(p,sizeof(actual),&v));checks++;
 memcpy(p,actual,sizeof(actual));p[32]|=1;assert(!qca_wmi_ready_info(p,sizeof(actual),&v));checks++;
 memcpy(p,actual,sizeof(actual));memset(p+32,0,6);assert(!qca_wmi_ready_info(p,sizeof(actual),&v));checks++;
 for(unsigned i=44;i<60;i++)for(unsigned x=0;x<256;x++){memcpy(p,actual,sizeof(actual));p[i]=(uint8_t)x;assert(qca_wmi_ready_info(p,sizeof(actual),&v)&&v.mac[5]==251&&v.abi_minor==574);checks++;}
 puts("Linux prefix/physical52-byte value/extensions/rejections PASS");printf("checks=%u\n",checks);return 0;
}
