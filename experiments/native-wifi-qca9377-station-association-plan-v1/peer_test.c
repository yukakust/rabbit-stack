#include "peer_wire.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
unsigned reference(uint8_t*,unsigned,const uint8_t*);
static unsigned checks;
#define CHECK(x) do{checks++;if(!(x)){fprintf(stderr,"line %u\n",__LINE__);abort();}}while(0)
int main(void){
 uint8_t out[48],oracle[24],mac[6]={2,0,0,0,0,1};
 for(unsigned i=0;i<1000;i++){
  mac[1]=(uint8_t)i;mac[2]=(uint8_t)(i>>8);memset(out,0xa5,sizeof(out));
  CHECK(qca_sta_peer_create_wire(out+8,24,i%4,mac)==24);
  CHECK(reference(oracle,i%4,mac)==24);CHECK(!memcmp(out+8,oracle,24));
  for(unsigned j=0;j<8;j++)CHECK(out[j]==0xa5);
  for(unsigned j=32;j<48;j++)CHECK(out[j]==0xa5);
 }
 for(unsigned cap=0;cap<24;cap++){memset(out,0xa5,48);CHECK(!qca_sta_peer_create_wire(out,cap,0,mac));for(unsigned j=0;j<48;j++)CHECK(out[j]==0xa5);}
 for(unsigned id=4;id<100;id++){memset(out,0xa5,48);CHECK(!qca_sta_peer_create_wire(out,48,id,mac));CHECK(out[0]==0xa5);}
 memset(mac,0,6);CHECK(!qca_sta_peer_create_wire(out,48,0,mac));mac[0]=1;CHECK(!qca_sta_peer_create_wire(out,48,0,mac));
 CHECK(!qca_sta_peer_create_wire(0,48,0,mac));CHECK(!qca_sta_peer_create_wire(out,48,0,0));
 memset(out,2,48);for(unsigned at=0;at<24;at++){CHECK(!qca_sta_peer_create_wire(out,48,0,out+at));CHECK(out[0]==2);}
 CHECK(!qca_sta_peer_create_wire((uint8_t*)(UINTPTR_MAX-12),48,0,mac));
 CHECK(!qca_sta_peer_create_wire(out,48,0,(uint8_t*)(UINTPTR_MAX-3)));
 printf("checks=%u\n",checks);return 0;
}
