#include "wmi_scan.h"
#include "upstream-scan.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static void u16(uint8_t*p,unsigned n){p[0]=n;p[1]=n>>8;}
static void store32(uint8_t*p,unsigned n){u16(p,n);u16(p+2,n>>16);}
int main(void){
 uint8_t p[512],expected[512],mut[512];uint16_t freq[]={2412,2437,2462,5180};unsigned n,checks=0;
 assert(WMI_TLV_START_SCAN_CMDID==0x3001&&WMI_TLV_SCAN_EVENTID==0x3001&&WMI_TLV_TAG_STRUCT_START_SCAN_CMD==77&&WMI_TLV_TAG_STRUCT_SCAN_EVENT==36);
 assert(sizeof(struct wmi_tlv_start_scan_cmd)==100&&sizeof(struct wmi_start_scan_common)==60&&sizeof(struct wmi_scan_event)==24);
 memset(expected,0,sizeof(expected));store32(expected,WMI_TLV_START_SCAN_CMDID);
 struct wmi_tlv hdr={.len=sizeof(struct wmi_tlv_start_scan_cmd),.tag=WMI_TLV_TAG_STRUCT_START_SCAN_CMD};memcpy(expected+4,&hdr,4);
 struct wmi_tlv_start_scan_cmd cmd={0};
 cmd.common.scan_id=0xa007;cmd.common.scan_req_id=0xa008;cmd.common.scan_priority=1;cmd.common.notify_scan_events=0x4b;
 cmd.common.dwell_time_active=50;cmd.common.dwell_time_passive=100;cmd.common.min_rest_time=50;cmd.common.max_rest_time=500;
 cmd.common.idle_time=50;cmd.common.max_scan_time=5400;cmd.common.probe_delay=5;cmd.common.scan_ctrl_flags=0x21;
 cmd.num_channels=4;cmd.num_probes=3;memcpy(expected+8,&cmd,100);
 hdr.tag=WMI_TLV_TAG_ARRAY_UINT32;hdr.len=16;memcpy(expected+108,&hdr,4);for(unsigned i=0;i<4;i++)store32(expected+112+4*i,freq[i]);
 hdr.tag=WMI_TLV_TAG_ARRAY_FIXED_STRUCT;hdr.len=0;memcpy(expected+128,&hdr,4);memcpy(expected+132,&hdr,4);
 hdr.tag=WMI_TLV_TAG_ARRAY_BYTE;memcpy(expected+136,&hdr,4);
 n=qca_wmi_passive_scan(p,sizeof(p),7,8,freq,4);assert(n==140&&!memcmp(expected,p,n));checks++;
 unsigned pos=0,records=0;QcaWmiTlv tlv;int ret;
 while((ret=qca_wmi_tlv(p+4,n-4,&pos,&tlv))==1)records++;
 assert(ret==0&&records==5&&pos==n-4);checks++;
 memset(p,0,sizeof(p));store32(p,0x3001);hdr.len=24;hdr.tag=36;memcpy(p+4,&hdr,4);
 struct wmi_scan_event ev={.event_type=8,.reason=0,.channel_freq=5180,.scan_req_id=0xa008,.scan_id=0xa007,.vdev_id=0};memcpy(p+8,&ev,24);n=32;
 QcaWmiScanEvent value,old={0};
 assert(qca_wmi_scan_event(p,n,7,8,&value)&&value.frequency==5180&&value.type==8);checks++;
 for(unsigned i=0;i<n;i++){
  for(unsigned b=0;b<256;b++){
   memcpy(mut,p,n);mut[i]=b;value=old;
   if(!qca_wmi_scan_event(mut,n,7,8,&value))assert(!memcmp(&value,&old,sizeof(value)));
   checks++;
  }
 }
 for(unsigned i=0;i<n;i++){value=old;assert(!qca_wmi_scan_event(p,i,7,8,&value)&&!memcmp(&value,&old,sizeof(value)));checks++;}
 assert(!qca_wmi_scan_event(p,n,8,8,&value));checks++;
 memcpy(p+32,p+4,28);assert(!qca_wmi_scan_event(p,60,7,8,&value));checks++;
 uint16_t wrong[]={2412,2412};memset(p,0xaa,sizeof(p));memcpy(expected,p,sizeof(p));
 assert(!qca_wmi_passive_scan(p,sizeof(p),7,8,wrong,2)&&!memcmp(p,expected,sizeof(p)));checks++;
 wrong[1]=2400;assert(!qca_wmi_passive_scan(p,sizeof(p),7,8,wrong,2));checks++;
 assert(!qca_wmi_passive_scan(p,139,7,8,freq,4));checks++;
 assert(!qca_wmi_passive_scan(p,sizeof(p),0x1000,8,freq,4));checks++;
 pos=1;memset(&tlv,0,sizeof(tlv));QcaWmiTlv prior=tlv;assert(qca_wmi_tlv(p,0,&pos,&tlv)==-1&&pos==1&&!memcmp(&tlv,&prior,sizeof(tlv)));checks++;
 puts("WMI PASSIVE SCAN PINNED-STRUCT DIFFERENTIAL AND REJECTION CHECKS PASS");printf("assertion_groups=%u\n",checks);return 0;
}
