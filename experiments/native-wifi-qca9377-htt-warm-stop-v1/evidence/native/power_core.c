/* Bounded PCI conventional-capability decoding. No hardware operations. */
#include "power_core.h"
static uint16_t word(const uint8_t*p){return (uint16_t)p[0]|((uint16_t)p[1]<<8);}
static void put(uint8_t*p,uint32_t v,unsigned n){for(unsigned i=0;i<n;i++)p[i]=(uint8_t)(v>>(8*i));}
void qca_power_decode(const uint8_t c[256],uint8_t out[16]){
 for(unsigned i=0;i<16;i++)out[i]=0;
 uint8_t seen[64]={0};unsigned offset=c[0x34],pm=0,pcie=0,status=2;
 if(!(word(c+6)&16)){if(offset)status=3;goto done;}
 for(unsigned step=0;offset;step++){
  if(step>=48||offset<0x40||offset>0xfc||(offset&3)||seen[offset/4]){status=3;goto done;}
  seen[offset/4]=1;
  if(c[offset]==1){if(pm||offset>0xf8){status=3;goto done;}pm=offset;}
  if(c[offset]==0x10){if(pcie||offset>0xec){status=3;goto done;}pcie=offset;}
  offset=c[offset+1];
 }
 if(pm){status=1;put(out,pm,2);put(out+2,word(c+pm+4),2);}
 if(pcie){put(out+4,pcie,2);put(out+6,word(c+pcie+0x10),2);}
 done:put(out+8,status,4);
}
