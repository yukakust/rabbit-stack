#include "power_core.h"
#include <assert.h>
#include <string.h>
#include <stdio.h>
static unsigned status(const uint8_t*out){return out[8];}
int main(void){
 uint8_t c[256]={0},out[16];qca_power_decode(c,out);assert(status(out)==2);
 c[6]=16;c[0x34]=0x40;c[0x40]=1;c[0x44]=3;
 qca_power_decode(c,out);assert(status(out)==1&&out[0]==0x40&&out[2]==3);
 for(unsigned i=1;i<256;i++){
  memset(c,0,sizeof(c));c[6]=16;c[0x34]=(uint8_t)i;
  qca_power_decode(c,out);
  if(i<0x40||i>0xfc||(i&3))assert(status(out)==3);
  else assert(status(out)==2);
 }
 memset(c,0,sizeof(c));c[6]=16;c[0x34]=0x40;c[0x40]=1;c[0x41]=0x40;
 qca_power_decode(c,out);assert(status(out)==3);
 c[0x41]=0x48;c[0x48]=1;qca_power_decode(c,out);assert(status(out)==3);
 c[0x48]=0x10;c[0x49]=0x50;c[0x50]=0x10;qca_power_decode(c,out);assert(status(out)==3);
 memset(c,0,sizeof(c));c[0x34]=0x40;qca_power_decode(c,out);assert(status(out)==3);
 memset(c,0,sizeof(c));c[6]=16;c[0x34]=0xfc;c[0xfc]=1;qca_power_decode(c,out);assert(status(out)==3);
 c[0xfc]=0x10;qca_power_decode(c,out);assert(status(out)==3);
 puts("PCI PM capability parser: D3, all255 pointers, loops, duplicate, missing, truncated PM/PCIe PASS");return 0;
}
