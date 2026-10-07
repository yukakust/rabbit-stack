/* Read-only WMI INIT observation, UUID26/30, handles26..31. */
#include <stddef.h>
#include <stdint.h>
void qca_profile_status(uint8_t[192]);
static uint16_t u16(const uint8_t*p){return (uint16_t)p[0]|((uint16_t)p[1]<<8);}
static void put(uint8_t*p,uint16_t n){p[0]=(uint8_t)n;p[1]=(uint8_t)(n>>8);}
static void uuid(uint8_t*p,uint8_t id){const uint8_t base[16]={0,0,0,0,0,0,0,0x80,0x49,0x46,0x54,0x49,0x42,0x42,0x41,0x52};for(unsigned i=0;i<16;i++)p[i]=base[i];p[0]=id;}
static size_t error(uint8_t*r,uint8_t op,uint16_t h,uint8_t code){r[0]=1;r[1]=op;put(r+2,h);r[4]=code;return 5;}
size_t qca_profile_att(uint16_t mtu,const uint8_t*p,size_t n,uint8_t*r,size_t capacity){
 if(!p||!n||!r||capacity<247||mtu<23||mtu>247||n>mtu)return 0;
 uint8_t op=p[0];uint16_t h=n>=3?u16(p+1):0;
 if(op==2)return SIZE_MAX;
 if(op==6){
  if(n!=23)return SIZE_MAX;
  uint8_t expected[16];uuid(expected,0x28);unsigned mismatch=0;for(unsigned i=0;i<16;i++)mismatch|=p[i+7]^expected[i];
  if(mismatch)return SIZE_MAX;
  if(!h||h>u16(p+3))return error(r,op,h,1);
  if(u16(p+5)!=0x2800||h>29||u16(p+3)<29)return error(r,op,h,0x0a);
  r[0]=7;put(r+1,29);put(r+3,31);return 5;
 }
 if(h<29)return SIZE_MAX;
 if(op==0x10||op==8||op==4){
  if(n!=(op==4?5u:7u))return error(r,op,h,4);
  uint16_t end=u16(p+3);if(h>end)return error(r,op,h,1);
  if(op==0x10){
   if(u16(p+5)!=0x2800)return error(r,op,h,0x10);
   if(h>29||end<29)return error(r,op,h,0x0a);
   r[0]=0x11;r[1]=20;put(r+2,29);put(r+4,31);uuid(r+6,0x28);return 22;
  }
  if(op==8){
   if(u16(p+5)!=0x2803||h>30||end<30)return error(r,op,h,0x0a);
   r[0]=9;r[1]=21;put(r+2,30);r[4]=2;put(r+5,31);uuid(r+7,0x29);return 23;
  }
  if(h>31)return error(r,op,h,0x0a);
  r[0]=5;if(h==29||h==30){r[1]=1;put(r+2,h);put(r+4,h==29?0x2800:0x2803);return 6;}
  r[1]=2;put(r+2,h);uuid(r+4,0x29);return 20;
 }
 if(op==0x0a||op==0x0c){
  if(n!=(op==0x0a?3u:5u))return error(r,op,h,4);
  uint16_t offset=op==0x0a?0:u16(p+3);uint8_t value[192];size_t length;
  if(h==29){uuid(value,0x28);length=16;}
  else if(h==31){qca_profile_status(value);length=192;}
  else return error(r,op,h,h<=31?2:1);
  if(offset>length)return error(r,op,h,7);
  size_t count=length-offset;if(count>mtu-1u)count=mtu-1u;
  r[0]=op==0x0a?0x0b:0x0d;for(size_t i=0;i<count;i++)r[i+1]=value[offset+i];return count+1;
 }
 if(op==0x12)return error(r,op,h,h<=31?3:1);
 if(op&0x40)return 0;
 return error(r,op,h,6);
}
