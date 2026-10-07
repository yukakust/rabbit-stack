#include <stdint.h>
#include <stddef.h>
void qca_htt_status(uint8_t[320]);
unsigned qca_htt_profile_export(unsigned,uint8_t*,unsigned);
static unsigned half(const uint8_t*p){return p[0]|((unsigned)p[1]<<8);}
static void put(uint8_t*p,unsigned v){p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);}
static void uuid(uint8_t*p,unsigned id){const uint8_t base[16]={0,0,0,0,0,0,0,0x80,0x49,0x46,0x54,0x49,0x42,0x42,0x41,0x52};for(unsigned j=0;j<16;j++)p[j]=base[j];p[0]=(uint8_t)id;}
static size_t error(uint8_t*out,unsigned op,unsigned h,unsigned e){out[0]=1;out[1]=(uint8_t)op;put(out+2,h);out[4]=(uint8_t)e;return 5;}
size_t qca_htt_profile_att(uint16_t mtu,const uint8_t*p,size_t n,uint8_t*out,size_t cap){
 if(!p||!n||!out||cap<247||mtu<23||mtu>247||n>mtu)return 0;
 unsigned op=p[0],h=n>=3?half(p+1):0;
 if(op==2)return SIZE_MAX;
 if(op==6){
  if(n!=23)return SIZE_MAX;uint8_t u[16];unsigned kind=0;
  for(unsigned k=0;k<2;k++){uuid(u,k?0x30:0x2e);unsigned diff=0;for(unsigned j=0;j<16;j++)diff|=u[j]^p[7+j];if(!diff)kind=k+1;}
  if(!kind)return SIZE_MAX;unsigned first=kind==1?29:32,last=kind==1?31:92;
  if(!h||h>half(p+3))return error(out,op,h,1);
  if(half(p+5)!=0x2800||h>first||half(p+3)<first)return error(out,op,h,10);
  out[0]=7;put(out+1,first);put(out+3,last);return 5;
 }
 if(h<29||h>92)return SIZE_MAX;
 if(op==0x10||op==8||op==4){
  if(n!=(op==4?5u:7u))return error(out,op,h,4);
  unsigned end=half(p+3);if(h>end)return error(out,op,h,1);
  if(op==0x10){unsigned start=h<=29?29:h<=32?32:0;
   if(half(p+5)!=0x2800||!start||end<start)return error(out,op,h,10);
   out[0]=0x11;out[1]=20;put(out+2,start);put(out+4,start==29?31:92);uuid(out+6,start==29?0x2e:0x30);return 22;
  }
  if(op==8){unsigned decl=h<=30?30:h<=33?33:(h|1);
   if(half(p+5)!=0x2803||decl>91||end<decl)return error(out,op,h,10);
   out[0]=9;out[1]=21;put(out+2,decl);out[4]=2;put(out+5,decl+1);uuid(out+7,decl==30?0x2f:0x80+(decl-33)/2);return 23;
  }
  if(h==29||h==30||h==32||(h>=33&&(h&1))){out[0]=5;out[1]=1;put(out+2,h);put(out+4,h==29||h==32?0x2800:0x2803);return 6;}
  out[0]=5;out[1]=2;put(out+2,h);uuid(out+4,h==31?0x2f:0x80+(h-34)/2);return 20;
 }
 if(op==10||op==12){
  if(n!=(op==10?3u:5u))return error(out,op,h,4);
  uint8_t value[512];unsigned bytes=0,offset=op==10?0:half(p+3);
  if(h==29||h==32){uuid(value,h==29?0x2e:0x30);bytes=16;}
  else if(h==31){qca_htt_status(value);bytes=320;}
  else if(h>=34&&!(h&1))bytes=qca_htt_profile_export((h-34)/2,value,sizeof(value));
  else return error(out,op,h,2);
  if(!bytes||offset>bytes)return error(out,op,h,7);
  unsigned take=bytes-offset;if(take>mtu-1u)take=mtu-1u;
  out[0]=(uint8_t)(op==10?11:13);for(unsigned j=0;j<take;j++)out[j+1]=value[offset+j];return take+1;
 }
 if(op==0x12)return error(out,op,h,3);
 if(op&0x40)return 0;
 return error(out,op,h,6);
}
