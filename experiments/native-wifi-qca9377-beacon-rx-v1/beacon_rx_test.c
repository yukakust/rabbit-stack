#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <stddef.h>
#include <stdlib.h>
#include "beacon_rx.h"
#include "upstream-mgmt.h"
static uint8_t p[4097];static unsigned checks,total,frame_len,array_len;
static void p16(uint8_t *q,unsigned x){q[0]=x;q[1]=x>>8;}
static void p32(uint8_t *q,uint32_t x){p16(q,x);p16(q+2,x>>16);}
static void tlv(uint8_t *q,unsigned tag,unsigned bytes){p16(q,bytes);p16(q+2,tag);}
static unsigned fixture(int pad){
 const char ssid[]="SILK_56E35E_Plus";uint8_t *frame=p+52;
 memset(p,0,sizeof p);p32(p,WMI_TLV_MGMT_RX_EVENTID);
 tlv(p+4,WMI_TLV_TAG_STRUCT_MGMT_RX_HDR,sizeof(struct wmi_tlv_mgmt_rx_ev));
 p32(p+8,6);p32(p+12,31);p32(p+16,54000);p32(p+20,7);
 for(unsigned i=0;i<4;i++)p32(p+32+4*i,19+i);
 p16(frame,0x80);memset(frame+4,0xff,6);
 for(unsigned i=0;i<6;i++)frame[10+i]=frame[16+i]=(uint8_t)(2+2*i);
 p16(frame+32,100);p16(frame+34,0x11);
 frame[36]=0;frame[37]=sizeof ssid-1;memcpy(frame+38,ssid,sizeof ssid-1);
 frame_len=38+sizeof ssid-1;frame[frame_len++]=3;frame[frame_len++]=1;frame[frame_len++]=6;
 array_len=pad?((frame_len+3)&~3u):frame_len;
 p32(p+24,frame_len);tlv(p+48,WMI_TLV_TAG_ARRAY_BYTE,array_len);
 total=52+array_len;return total;
}
static void test(unsigned n,int accepted){
 QcaWmiBeaconRx out,old;memset(&out,0x5a,sizeof out);memcpy(&old,&out,sizeof out);
 int result=qca_wmi_beacon_rx(p,n,&out);
 assert((result==QCA_BEACON_RX_ACCEPTED)==accepted);
 if(!accepted)assert(memcmp(&out,&old,sizeof out)==0);
 else {
  assert(out.buf_len==frame_len&&out.status==0&&out.bss.ssid_bytes==16);
  assert(!memcmp(out.bss.ssid,"SILK_56E35E_Plus",16));
  assert(out.frequency_mhz==2407+5*out.channel);
  assert(qca_beacon_ssid_matches(&out.bss,(const uint8_t *)"SILK_56E35E_Plus",16));
 }
 ++checks;
}
int main(void){
 unsigned x,n;QcaWmiBeaconRx out;
 assert(WMI_TLV_MGMT_RX_EVENTID==0x7001);
 assert(WMI_TLV_TAG_ARRAY_BYTE==17&&WMI_TLV_TAG_STRUCT_MGMT_RX_HDR==44);
 assert(WMI_RX_STATUS_OK==0&&WMI_RX_STATUS_ERR_CRC==1&&WMI_RX_STATUS_ERR_DECRYPT==8);
 assert(WMI_RX_STATUS_ERR_MIC==16&&WMI_RX_STATUS_ERR_KEY_CACHE_MISS==32&&WMI_RX_STATUS_EXT_INFO==64);
 assert(sizeof(struct wmi_tlv_mgmt_rx_ev)==40);
 assert(offsetof(struct wmi_tlv_mgmt_rx_ev,channel)==0);
 assert(offsetof(struct wmi_tlv_mgmt_rx_ev,snr)==4);
 assert(offsetof(struct wmi_tlv_mgmt_rx_ev,rate)==8);
 assert(offsetof(struct wmi_tlv_mgmt_rx_ev,phy_mode)==12);
 assert(offsetof(struct wmi_tlv_mgmt_rx_ev,buf_len)==16);
 assert(offsetof(struct wmi_tlv_mgmt_rx_ev,status)==20);
 assert(offsetof(struct wmi_tlv_mgmt_rx_ev,rssi)==24);
 fixture(0);n=total;for(x=0;x<n;++x)test(x,0);test(n,1);
 for(x=0;x<n;++x){
  uint8_t *short_input=malloc(x?x:1);assert(short_input);
  memcpy(short_input,p,x);memset(&out,0x5a,sizeof out);QcaWmiBeaconRx old=out;
  assert(qca_wmi_beacon_rx(short_input,x,&out)!=QCA_BEACON_RX_ACCEPTED);
  assert(!memcmp(&out,&old,sizeof out));free(short_input);++checks;
 }
 fixture(1);test(total,1);
 for(x=0;x<=65535;++x){
  fixture(0);p16(p+4,x);test(total,x==40);
  fixture(0);p16(p+48,x);test(total,x==frame_len);
  fixture(1);p32(p+24,x);test(total,x==frame_len);
  fixture(0);p32(p+28,x);test(total,x==0);
  fixture(0);p32(p+8,x);test(total,x==6);
  fixture(0);p32(p,x);test(total,x==WMI_TLV_MGMT_RX_EVENTID);
  fixture(0);p16(p+52,x);test(total,!(x&0xc707)&&((x&0xfc)==0x80||(x&0xfc)==0x50));
 }
 for(x=0;x<256;++x){fixture(0);p[3]=(uint8_t)x;test(total,1);assert(qca_wmi_beacon_rx(p,total,&out)==1&&out.platform_private==x);}
 /* ARRAY_BYTE may precede header and have an unaligned byte length. */
 fixture(0);uint8_t header[44],array[128];
 memcpy(header,p+4,44);memcpy(array,p+48,total-48);
 memcpy(p+4,array,total-48);memcpy(p+4+total-48,header,44);test(total,1);
 /* Duplicate header/array, unknown extensions, nonzero padding. */
 fixture(0);memcpy(p+total,p+4,44);test(total+44,0);
 fixture(0);memcpy(p+total,p+48,4+frame_len);test(total+4+frame_len,0);
 fixture(0);tlv(p+total,999,0);test(total+4,0);
 fixture(1);for(x=frame_len;x<array_len;++x){p[52+x]=1;test(total,0);p[52+x]=0;}
 fixture(0);p32(p+24,UINT32_MAX);test(total,0);
 fixture(0);p32(p+28,WMI_RX_STATUS_EXT_INFO);test(total,0);
 fixture(0);p[52+frame_len-1]=11;test(total,0); /* DS/RX channel conflict */
 fixture(0);p16(p+52,0xb0);test(total,0); /* authentication frame belongs to caller */
 fixture(0);p16(p+4,44);test(total,0); /* unreviewed header extension */
 const uint32_t values[]={0,1,100,1000,54000,UINT32_MAX};
 for(x=0;x<sizeof values/sizeof *values;++x){
  fixture(0);p32(p+12,values[x]);p32(p+16,values[x]);p32(p+20,values[x]);
  p32(p+32,values[x]);test(total,1);
  assert(qca_wmi_beacon_rx(p,total,&out)==1&&out.snr==values[x]&&out.rate==values[x]&&out.phy_mode==values[x]&&out.rssi[0]==values[x]);
 }
 fixture(0);memset(p+52+38,0,16);
 assert(qca_wmi_beacon_rx(p,total,&out)==1&&out.bss.hidden);
 assert(!qca_beacon_ssid_matches(&out.bss,(const uint8_t *)"SILK_56E35E_Plus",16));++checks;
 fixture(0);p[total++]=48;p[total++]=2;p[total++]=1;p[total++]=0;
 frame_len+=4;p32(p+24,frame_len);tlv(p+48,WMI_TLV_TAG_ARRAY_BYTE,frame_len);
 test(total,1);assert(qca_wmi_beacon_rx(p,total,&out)==1&&out.bss.rsn_bytes==2);
 fixture(0);frame_len-=3;total-=3;p32(p+24,frame_len);tlv(p+48,WMI_TLV_TAG_ARRAY_BYTE,frame_len);
 test(total,1);assert(qca_wmi_beacon_rx(p,total,&out)==1&&out.bss.channel==0);
 assert(qca_wmi_beacon_rx(NULL,4,&out)==-1);++checks;
 assert(qca_wmi_beacon_rx(p,total,NULL)==-1);++checks;
 test(4097,0);
 printf("PASS %u pinned-layout WMI beacon RX checks\n",checks);return 0;
}
