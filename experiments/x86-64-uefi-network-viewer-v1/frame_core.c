#include "frame_core.h"
#include "monocypher-ed25519.h"
static uint16_t u16(const uint8_t *p){return (uint16_t)(p[0]|(uint16_t)p[1]<<8);}
static uint32_t u32(const uint8_t *p){return (uint32_t)u16(p)|(uint32_t)u16(p+2)<<16;}
static uint64_t u64(const uint8_t *p){return (uint64_t)u32(p)|(uint64_t)u32(p+4)<<32;}
static uint32_t rgb(const uint8_t *p){return (uint32_t)p[0]<<16|(uint32_t)p[1]<<8|p[2];}
int rf_accept(const uint8_t *p,size_t n,const uint8_t stream[16],
              const uint8_t key[32],RfFrame *state,uint32_t *pixels,size_t capacity){
  if(!p||!stream||!key||!state||!pixels||n<RF_HEADER+RF_SIGNATURE||n>RF_MAX_WIRE)return 1;
  if(p[0]!='R'||p[1]!='P'||p[2]!='F'||p[3]!='1'||p[4]!=1||
     (p[5]!=1&&p[5]!=2)||u16(p+6)!=RF_HEADER)return 2;
  uint32_t w=u16(p+8),h=u16(p+10),length=u32(p+12);
  uint64_t sequence=u64(p+16);
  if(!w||!h||w>RF_MAX_WIDTH||h>RF_MAX_HEIGHT||w*h>capacity||
     length>RF_MAX_PIXELS*5u||n!=RF_HEADER+(size_t)length+RF_SIGNATURE||
     sequence<=state->sequence)return 3;
  for(unsigned i=0;i<16;i++)if(p[24+i]!=stream[i])return 4;
  for(unsigned i=40;i<RF_HEADER;i++)if(p[i])return 5;
  const uint8_t *body=p+RF_HEADER;
  /* Validate all run boundaries BEFORE touching the previous displayed frame. */
  if(p[5]==1){if(length!=w*h*3u)return 6;}
  else{
    if(length%5)return 6;
    uint32_t count=0;
    for(uint32_t i=0;i<length;i+=5){
      uint32_t run=u16(body+i);
      if(!run||run>w*h-count)return 6;
      count+=run;
    }
    if(count!=w*h)return 6;
  }
  if(crypto_ed25519_check(p+RF_HEADER+length,key,p,RF_HEADER+length))return 7;
  if(p[5]==1)for(uint32_t i=0;i<w*h;i++)pixels[i]=rgb(body+i*3u);
  else{
    uint32_t index=0;
    for(uint32_t i=0;i<length;i+=5){
      uint32_t color=rgb(body+i+2),run=u16(body+i);
      for(uint32_t j=0;j<run;j++)pixels[index++]=color;
    }
  }
  state->width=(uint16_t)w;state->height=(uint16_t)h;state->sequence=sequence;
  return 0;
}
