#include "wmi_boot_info.h"
#include "upstream-scan.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static void u16(uint8_t*p,unsigned n){p[0]=n;p[1]=n>>8;}
static void store32(uint8_t*p,unsigned n){u16(p,n);u16(p+2,n>>16);}
static void tag(uint8_t*p,unsigned t,unsigned n){u16(p,n);u16(p+2,t);}
static struct wmi_tlv_abi_version abi(void){return (struct wmi_tlv_abi_version){.abi_ver0=WMI_TLV_ABI_VER0,.abi_ver1=WMI_TLV_ABI_VER1,.abi_ver_ns0=WMI_TLV_ABI_VER_NS0,.abi_ver_ns1=WMI_TLV_ABI_VER_NS1,.abi_ver_ns2=WMI_TLV_ABI_VER_NS2,.abi_ver_ns3=WMI_TLV_ABI_VER_NS3};}
int main(void){
 uint8_t p[512],mut[512];unsigned checks=0;QcaWmiServiceInfo value,old={0};
 assert(sizeof(struct wmi_tlv_svc_rdy_ev)==104&&sizeof(struct wmi_tlv_rdy_ev)==36&&sizeof(struct hal_reg_capabilities)==36&&sizeof(struct wlan_host_mem_req)==16);
 memset(p,0,sizeof(p));store32(p,1);tag(p+4,WMI_TLV_TAG_STRUCT_SERVICE_READY_EVENT,104);
 struct wmi_tlv_svc_rdy_ev ev={.fw_build_vers=1234,.abi=abi(),.num_rf_chains=1,.num_mem_reqs=1};memcpy(p+8,&ev,sizeof(ev));
 tag(p+112,WMI_TLV_TAG_STRUCT_HAL_REG_CAPABILITIES,36);
 struct hal_reg_capabilities reg={.eeprom_rd=0x60,.low_2ghz_chan=2412,.high_2ghz_chan=2472,.low_5ghz_chan=5180,.high_5ghz_chan=5825};memcpy(p+116,&reg,sizeof(reg));
 tag(p+152,WMI_TLV_TAG_ARRAY_UINT32,4);store32(p+156,0xdeadbeef);
 tag(p+160,WMI_TLV_TAG_ARRAY_STRUCT,20);tag(p+164,WMI_TLV_TAG_STRUCT_WLAN_HOST_MEM_REQ,16);
 struct wlan_host_mem_req req={.req_id=0,.unit_size=16,.num_units=256};memcpy(p+168,&req,sizeof(req));
 assert(qca_wmi_service_info(p,184,&value)&&value.build==1234&&value.chains==1&&value.low5==5180&&value.memory_count==1&&value.memory[0].units==256&&value.service_words[0]==0xdeadbeef);checks++;
 for(unsigned i=0;i<184;i++)for(unsigned b=0;b<256;b++){
  memcpy(mut,p,184);mut[i]=b;value=old;
  if(!qca_wmi_service_info(mut,184,&value))assert(!memcmp(&value,&old,sizeof(value)));
  else assert(value.memory_count<=16&&value.service_count<=128);
  checks++;
 }
 for(unsigned i=0;i<184;i++){value=old;assert(!qca_wmi_service_info(p,i,&value)&&!memcmp(&value,&old,sizeof(value)));checks++;}
 memcpy(mut,p,184);store32(mut+80,2);assert(!qca_wmi_service_info(mut,184,&value));checks++;
 memcpy(mut,p,184);store32(mut+176,3);assert(!qca_wmi_service_info(mut,184,&value));checks++;
 memcpy(mut,p,184);tag(mut+160,18,40);memcpy(mut+184,p+164,20);assert(!qca_wmi_service_info(mut,204,&value));checks++;
 memset(p,0,sizeof(p));store32(p,2);tag(p+4,WMI_TLV_TAG_STRUCT_READY_EVENT,36);
 struct wmi_tlv_rdy_ev ready={.abi=abi()};ready.mac_addr.addr[0]=2;ready.mac_addr.addr[5]=1;memcpy(p+8,&ready,sizeof(ready));
 QcaWmiReadyInfo ri,prior={0};assert(qca_wmi_ready_info(p,44,&ri)&&ri.mac[0]==2&&ri.mac[5]==1&&ri.abi_minor==53);checks++;
 memcpy(mut,p,44);mut[32]=3;ri=prior;assert(!qca_wmi_ready_info(mut,44,&ri)&&!memcmp(&ri,&prior,sizeof(ri)));checks++;
 memcpy(mut,p,44);store32(mut+40,1);assert(!qca_wmi_ready_info(mut,44,&ri));checks++;
 memcpy(mut,p,44);memcpy(mut+44,p+4,40);assert(!qca_wmi_ready_info(mut,84,&ri));checks++;
 for(unsigned i=0;i<44;i++){ri=prior;assert(!qca_wmi_ready_info(p,i,&ri)&&!memcmp(&ri,&prior,sizeof(ri)));checks++;}
 puts("WMI BOOT ABI, MEMORY REQUIREMENTS, READY MAC AND MALFORMED-EVENT CHECKS PASS");printf("assertion_groups=%u\n",checks);return 0;
}
