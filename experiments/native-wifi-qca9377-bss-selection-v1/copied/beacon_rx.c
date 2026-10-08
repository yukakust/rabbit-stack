#include "beacon_rx.h"
static unsigned u16(const uint8_t *p){return p[0]|((unsigned)p[1]<<8);}
static uint32_t u32(const uint8_t *p){return u16(p)|((uint32_t)u16(p+2)<<16);}
int qca_wmi_beacon_rx(const uint8_t *p,unsigned n,QcaWmiBeaconRx *out){
 const uint8_t *hdr=0,*frame=0; unsigned at=4,frame_bytes=0;
 QcaWmiBeaconRx v={0};
 if(!p||!out||n<4||n>4096)return QCA_BEACON_RX_MALFORMED;
 if((u32(p)&0xffffffu)!=0x7001u)return QCA_BEACON_RX_OTHER_EVENT;
 v.platform_private=p[3];
 while(at<n){
  unsigned bytes,tag;
  if(n-at<4)return QCA_BEACON_RX_MALFORMED;
  bytes=u16(p+at);tag=u16(p+at+2);at+=4;
  if(bytes>n-at)return QCA_BEACON_RX_MALFORMED;
  if(tag==44){
   if(hdr)return QCA_BEACON_RX_MALFORMED;
   if(bytes<40)return QCA_BEACON_RX_MALFORMED;
   if(bytes!=40)return QCA_BEACON_RX_UNSUPPORTED;
   hdr=p+at;
  }else if(tag==17){
   if(frame)return QCA_BEACON_RX_MALFORMED;
   frame=p+at;frame_bytes=bytes;
  }else return QCA_BEACON_RX_UNSUPPORTED;
  at+=bytes;
 }
 if(!hdr||!frame)return QCA_BEACON_RX_MALFORMED;
 v.channel=u32(hdr);v.snr=u32(hdr+4);v.rate=u32(hdr+8);
 v.phy_mode=u32(hdr+12);v.buf_len=u32(hdr+16);v.status=u32(hdr+20);
 for(unsigned i=0;i<4;i++)v.rssi[i]=u32(hdr+24+4*i);
 if(v.status)return QCA_BEACON_RX_UNSUPPORTED;
 if(v.channel<1||v.channel>13)return QCA_BEACON_RX_UNSUPPORTED;
 /* Never let the frame borrow bytes from a following TLV. Both exact and
  * 4-byte-padded ARRAY_BYTE representations are accepted; padding is zero. */
 if(v.buf_len<36||v.buf_len>4096||v.buf_len>frame_bytes)return QCA_BEACON_RX_MALFORMED;
 if(frame_bytes!=v.buf_len&&frame_bytes!=((v.buf_len+3u)&~3u))return QCA_BEACON_RX_MALFORMED;
 for(unsigned i=v.buf_len;i<frame_bytes;i++)if(frame[i])return QCA_BEACON_RX_MALFORMED;
 if((u16(frame)&0xfcu)!=0x80u&&(u16(frame)&0xfcu)!=0x50u)return QCA_BEACON_RX_UNSUPPORTED;
 if(qca_beacon_info(frame,v.buf_len,&v.bss))return QCA_BEACON_RX_MALFORMED;
 /* A conflicting advertised DS/HT channel is not an accepted first-profile
  * BSS observation. Missing channel IE stays missing, never fabricated. */
 if(v.bss.channel&&v.bss.channel!=v.channel)return QCA_BEACON_RX_UNSUPPORTED;
 v.frequency_mhz=2407+5*v.channel;*out=v;return QCA_BEACON_RX_ACCEPTED;
}
