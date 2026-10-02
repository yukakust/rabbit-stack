/* Bounded fixed-channel ATT/GATT server. No HCI/USB ownership is claimed here.
 * The adapter must supply complete reassembled PDUs from ONE connected bearer. */
#include "gatt_core.h"
static uint16_t u16(const uint8_t*p){return (uint16_t)(p[0]|((unsigned)p[1]<<8));}
static void w16(uint8_t*p,uint16_t v){p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);}
/* 52414242-4954-4649-8000-000000000001, Bluetooth little-endian UUID. */
static const uint8_t service_uuid[16]={1,0,0,0,0,0,0,0x80,0x49,0x46,0x54,0x49,0x42,0x42,0x41,0x52};
static void uuid(uint8_t*p,uint8_t last){for(unsigned i=0;i<16;i++)p[i]=service_uuid[i];p[0]=last;}
static size_t error(uint8_t*r,uint8_t op,uint16_t handle,uint8_t code){r[0]=1;r[1]=op;w16(r+2,handle);r[4]=code;return 5;}
static RfFile *file(RgServer*s){return s->shared?s->shared:&s->file;}
void rg_init(RgServer*s,RfApply apply){rf_init(&s->file,apply);s->shared=0;s->mtu=23;}
void rg_init_shared(RgServer*s,RfFile*f){s->shared=f;s->mtu=23;}
void rg_disconnected(RgServer*s){s->mtu=23;}
size_t rg_att(RgServer*s,const uint8_t*p,size_t n,uint8_t*r,size_t capacity){
 if(!s||!p||!r||!n||capacity<RG_MTU_MAX||n>s->mtu)return 0;
 uint8_t op=p[0];uint16_t handle=n>=3?u16(p+1):0;
 if(op==2){
  if(n!=3||u16(p+1)<23)return error(r,op,0,4);
  uint16_t requested=u16(p+1);s->mtu=requested<RG_MTU_MAX?requested:RG_MTU_MAX;
  r[0]=3;w16(r+1,RG_MTU_MAX);return 3;
 }
 /* Targeted primary-service discovery for clients that know the UUID. */
 if(op==6){
  if(n!=23)return error(r,op,handle,4);
  uint16_t end=u16(p+3);
  if(!handle||handle>end)return error(r,op,handle,1);
  uint8_t mismatch=0;for(unsigned i=0;i<16;i++)mismatch|=p[7+i]^service_uuid[i];
  if(u16(p+5)!=0x2800||handle>1||end<1||mismatch)return error(r,op,handle,0x0a);
  r[0]=7;w16(r+1,1);w16(r+3,7);return 5;
 }
 if(op==0x10||op==8||op==4){
  if((op==4&&n!=5)||(op!=4&&n!=7))return error(r,op,handle,4);
  uint16_t end=u16(p+3);if(!handle||handle>end)return error(r,op,handle,1);
  if(op==0x10){
   if(u16(p+5)!=0x2800)return error(r,op,handle,0x10);
   if(handle>1||end<1)return error(r,op,handle,0x0a);
   r[0]=0x11;r[1]=20;w16(r+2,1);w16(r+4,7);uuid(r+6,1);return 22;
  }
  if(op==8){
   if(u16(p+5)!=0x2803)return error(r,op,handle,0x0a);
   uint16_t declaration=handle<=2?2:handle<=4?4:handle<=6?6:0;
   if(!declaration||declaration>end)return error(r,op,handle,0x0a);
   r[0]=9;r[1]=21;w16(r+2,declaration);r[4]=declaration==6?2:8;
   w16(r+5,declaration+1);uuid(r+7,(uint8_t)(declaration/2+1));return 23;
  }
  if(handle>7)return error(r,op,handle,0x0a);
  r[0]=5;
  if(handle==1||handle==2||handle==4||handle==6){r[1]=1;w16(r+2,handle);w16(r+4,handle==1?0x2800:0x2803);return 6;}
  r[1]=2;w16(r+2,handle);uuid(r+4,(uint8_t)((handle-1)/2+1));return 20;
 }
 if(op==0x0a||op==0x0c){
  if(n!=(op==0x0a?3u:5u))return error(r,op,handle,4);
  uint16_t offset=op==0x0c?u16(p+3):0;
  uint8_t value[RF_STATUS_SIZE];size_t length=0;
  if(handle==7){rf_status(file(s),value);length=RF_STATUS_SIZE;}
  else if(handle==1){uuid(value,1);length=16;}
  else return error(r,op,handle,handle<=7?2:1);
  if(offset>length)return error(r,op,handle,7);
  size_t count=length-offset;if(count>(size_t)s->mtu-1)count=s->mtu-1;
  r[0]=op==0x0a?0x0b:0x0d;for(size_t i=0;i<count;i++)r[i+1]=value[offset+i];return count+1;
 }
 if(op==0x12){
  if(n<4)return error(r,op,handle,4);
  int failed=handle==3?rf_control(file(s),p+3,n-3):handle==5?rf_data(file(s),p+3,n-3):1;
  if(failed)return error(r,op,handle,handle==3||handle==5?0x80:handle<=7?3:1);
  r[0]=0x13;return 1;
 }
 /* Write commands have no ATT response. Unsupported commands are ignored. */
 if(op&0x40)return 0;
 return error(r,op,handle,6);
}
