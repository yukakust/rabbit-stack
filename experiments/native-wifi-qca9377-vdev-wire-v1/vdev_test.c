#include "vdev_wire.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
unsigned reference(uint8_t*,unsigned,unsigned,const uint8_t[6]);
static unsigned checks;
int main(void){
 uint8_t out[64],expected[64],mac[6]={2,0,0,0,0,1},old[64];uint32_t seed=9377;
 for(unsigned n=0;n<1024;n++)for(unsigned id=0;id<4;id++){
  for(unsigned j=0;j<6;j++){seed=1664525*seed+1013904223;mac[j]=(uint8_t)(seed>>24);}mac[0]&=254;mac[5]|=1;
  for(unsigned cmd=0;cmd<3;cmd++){
   memset(out,0xa5,sizeof(out));memset(expected,0xa5,sizeof(expected));unsigned size=reference(expected,cmd,id,mac);
   unsigned actual=cmd==0?qca_station_create_wire(out,64,id,mac):cmd==1?qca_station_stop_wire(out,64,id):qca_station_delete_wire(out,64,id);
   assert(actual==size&&!memcmp(out,expected,sizeof(out)));checks++;
  }
 }
 for(unsigned cmd=0;cmd<3;cmd++)for(unsigned cap=0;cap<(cmd?12u:28u);cap++){
  memset(out,0xa5,sizeof(out));memcpy(old,out,sizeof(out));
  unsigned n=cmd==0?qca_station_create_wire(out,cap,0,mac):cmd==1?qca_station_stop_wire(out,cap,0):qca_station_delete_wire(out,cap,0);
  assert(!n&&!memcmp(out,old,sizeof(out)));checks++;
 }
 for(unsigned id=4;id<256;id++){memset(out,0xa5,sizeof(out));memcpy(old,out,sizeof(out));assert(!qca_station_create_wire(out,64,id,mac)&&!qca_station_stop_wire(out,64,id)&&!qca_station_delete_wire(out,64,id)&&!memcmp(out,old,sizeof(out)));checks++;}
 memset(out,0xa5,sizeof(out));memcpy(old,out,sizeof(out));memset(mac,0,6);assert(!qca_station_create_wire(out,64,0,mac)&&!memcmp(out,old,64));checks++;
 for(unsigned first=1;first<256;first+=2){mac[0]=(uint8_t)first;mac[5]=1;assert(!qca_station_create_wire(out,64,0,mac)&&!memcmp(out,old,64));checks++;}
 assert(!qca_station_create_wire(out,64,0,out)&&!memcmp(out,old,64));checks++;
 assert(!qca_station_create_wire(out,64,0,0)&&!qca_station_create_wire(0,64,0,mac)&&!qca_station_stop_wire(0,64,0)&&!qca_station_delete_wire(0,64,0));checks++;
 printf("QCA TLV STA CREATE/STOP/DELETE pinned wire / bounds / MAC checks=%u PASS\n",checks);
}
