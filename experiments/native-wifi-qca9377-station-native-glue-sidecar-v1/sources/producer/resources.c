#include "resources.h"
int qca_tlv_resources(const QcaWmiServiceInfo*i,QcaTlvResources*out){
 if(!i||!out||i->service_count!=32||!i->chains||i->chains>4)return 0;
 uintptr_t a=(uintptr_t)i,b=(uintptr_t)out;
 if(a>UINTPTR_MAX-sizeof(*i)||b>UINTPTR_MAX-sizeof(*out)
  ||(a<b?b-a<sizeof(*i):a-b<sizeof(*out)))return 0;
 /* Pinned ath10k QCA9377 PCI defaults, not a minimized guessed vector.
  * RX_FULL_REORDER service65 uses four low bits per u32, not 32. */
 uint32_t offload=(i->service_words[65/4]>>(65%4))&1;
 QcaTlvResources v={.words={
  4,33,0,0,2,66,16,7,7,100,100,100,40,1,4,4,4,8,
  0,0,0,1024,32,0,0,0,0,2,1056,2,1,32,2,5,22,6,0,1,1,0,0,0,0,512
 },.memory={4,33,0,16777216}};
 v.words[2]=v.words[3]=offload?4:0;
 /* Linux advertises management completion bundles (bit9). The future native
  * dispatcher must implement that contract before this vector is admitted.
  * TX_ACK_RSSI bit18 is omitted: extended service174 is not validated here. */
 *out=v;return 1;
}
