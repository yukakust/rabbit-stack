#include "available.h"
#include "upstream-available.h"
#include <assert.h>
#include <string.h>
#include <stdio.h>
int main(void){
 assert(WMI_TLV_SERVICE_AVAILABLE_EVENTID==3&&WMI_TLV_TAG_STRUCT_SERVICE_AVAILABLE_EVENT==559);
 const uint8_t captured[28]={3,0,0,0,20,0,0x2f,2,128,0,0,0,0,0,0,8,0,0,0,0,0,0,0,0,0,0,0,0};
 unsigned checks=0;QcaWmiAvailable value={0};assert(qca_wmi_available(captured,28,&value)&&value.advertised_length==128&&value.words[0]==0x08000000);checks++;
 uint8_t p[28];
 for(unsigned i=0;i<28;i++)for(unsigned b=0;b<256;b++){
  memcpy(p,captured,28);p[i]=(uint8_t)b;QcaWmiAvailable before=value;
  int valid=qca_wmi_available(p,28,&value);
  assert(valid==(i>=12||p[i]==captured[i]));if(!valid)assert(!memcmp(&before,&value,sizeof(value)));checks++;
 }
 for(unsigned n=0;n<28;n++){QcaWmiAvailable before=value;assert(!qca_wmi_available(captured,n,&value)&&!memcmp(&before,&value,sizeof(value)));checks++;}
 assert(!qca_wmi_available(0,28,&value)&&!qca_wmi_available(captured,29,&value)&&!qca_wmi_available(captured,28,0));checks++;
 printf("ACTUAL SERVICE_AVAILABLE strict layout/bitmap/rejection checks=%u PASS\n",checks);return 0;
}
