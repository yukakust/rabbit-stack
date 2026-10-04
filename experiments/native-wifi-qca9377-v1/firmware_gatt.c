/* Native-owned asset service, UUID suffix7, seven consecutive handles.
 * Legacy base11; full split diagnostic profile requires base13 (13..19).
 * UUIDs stay fixed so saved senders discover values independently of handles. */
#include "firmware_channel.h"
#ifndef QCA_FC_BASE
#define QCA_FC_BASE 11
#endif
#define H(n) (QCA_FC_BASE+((n)-11))
static uint16_t u16(const uint8_t*p){return (uint16_t)p[0]|((uint16_t)p[1]<<8);}
static void put(uint8_t*p,uint16_t n){p[0]=(uint8_t)n;p[1]=(uint8_t)(n>>8);}
static void uuid(uint8_t*p,uint8_t last){const uint8_t base[16]={7,0,0,0,0,0,0,0x80,0x49,0x46,0x54,0x49,0x42,0x42,0x41,0x52};for(unsigned i=0;i<16;i++)p[i]=base[i];p[0]=last;}
static size_t error(uint8_t*r,uint8_t op,uint16_t handle,uint8_t code){r[0]=1;r[1]=op;put(r+2,handle);r[4]=code;return 5;}
size_t qca_fc_att(QcaFirmwareChannel*s,uint16_t mtu,const uint8_t*p,size_t n,uint8_t*r,size_t capacity){
 if(!p||!n||!r||capacity<247||mtu<23||mtu>247||n>mtu)return 0;
 uint8_t op=p[0];uint16_t handle=n>=3?u16(p+1):0;
 if(op==2)return SIZE_MAX; /* Legacy server owns MTU negotiation. */
 if(op==6){
  if(n!=23)return SIZE_MAX;
  uint8_t expected[16];uuid(expected,7);unsigned mismatch=0;for(unsigned i=0;i<16;i++)mismatch|=p[i+7]^expected[i];
  if(mismatch)return SIZE_MAX;
  if(!handle||handle>u16(p+3))return error(r,op,handle,1);
  if(u16(p+5)!=0x2800||handle>H(11)||u16(p+3)<H(11))return error(r,op,handle,0x0a);
  r[0]=7;put(r+1,H(11));put(r+3,H(17));return 5;
 }
 if(handle<H(11))return SIZE_MAX;
 if(op==0x10||op==8||op==4){
  if(n!=(op==4?5u:7u))return error(r,op,handle,4);
  uint16_t end=u16(p+3);if(handle>end)return error(r,op,handle,1);
  if(op==0x10){
   if(u16(p+5)!=0x2800)return error(r,op,handle,0x10);
   if(handle>H(11)||end<H(11))return error(r,op,handle,0x0a);
   r[0]=0x11;r[1]=20;put(r+2,H(11));put(r+4,H(17));uuid(r+6,7);return 22;
  }
  if(op==8){
   if(u16(p+5)!=0x2803)return error(r,op,handle,0x0a);
   uint16_t declaration=handle<=H(12)?H(12):handle<=H(14)?H(14):handle<=H(16)?H(16):0;
   if(!declaration||declaration>end)return error(r,op,handle,0x0a);
   r[0]=9;r[1]=21;put(r+2,declaration);r[4]=declaration==H(16)?2:8;put(r+5,declaration+1);uuid(r+7,(uint8_t)((declaration-QCA_FC_BASE+11)/2+2));return 23;
  }
  if(handle>H(17))return error(r,op,handle,0x0a);
  r[0]=5;
  if(handle==H(11)||handle==H(12)||handle==H(14)||handle==H(16)){r[1]=1;put(r+2,handle);put(r+4,handle==H(11)?0x2800:0x2803);return 6;}
  r[1]=2;put(r+2,handle);uuid(r+4,(uint8_t)((handle-QCA_FC_BASE+10)/2+2));return 20;
 }
 if(op==0x0a||op==0x0c){
  if(n!=(op==0x0a?3u:5u))return error(r,op,handle,4);
  uint16_t offset=op==0x0a?0:u16(p+3);uint8_t value[64];size_t length;
  if(handle==H(11)){uuid(value,7);length=16;}
  else if(handle==H(17)){qca_fc_status(s,value);length=64;}
  else return error(r,op,handle,handle<=H(17)?2:1);
  if(offset>length)return error(r,op,handle,7);
  size_t count=length-offset;if(count>mtu-1u)count=mtu-1u;
  r[0]=op==0x0a?0x0b:0x0d;for(size_t i=0;i<count;i++)r[i+1]=value[offset+i];return count+1;
 }
 if(op==0x12){
  if(n<4)return error(r,op,handle,4);
  int failed=handle==H(13)?qca_fc_control(s,p+3,n-3):handle==H(15)?qca_fc_data(s,p+3,n-3):-1;
  if(failed)return error(r,op,handle,handle==H(13)||handle==H(15)?0x80:handle<=H(17)?3:1);
  r[0]=0x13;return 1;
 }
 if(op&0x40)return 0;
 return error(r,op,handle,6);
}
