/* Actual retained low diagnostic route, supplied actual production probe fixture. */
#include "gatt_core.h"
#include "pci_collect.h"
#include "sha256.h"
#include <stdio.h>
#include <assert.h>
#include <string.h>
uint8_t qca_diagnostic[QCA_DIAGNOSTIC_SIZE];
static uint8_t reply[RG_MTU_MAX];
int main(int argc,char**argv){assert(argc==2);FILE*f=fopen(argv[1],"rb");assert(f&&fread(qca_diagnostic,1,sizeof(qca_diagnostic),f)==sizeof(qca_diagnostic)&&!fclose(f));RgServer s;rg_init(&s,0);s.mtu=RG_MTU_MAX;unsigned checks=0;
 for(unsigned handle=10;handle<=12;handle+=2){unsigned size=handle==10?512:448;uint8_t expected[512]={0};if(handle==10)memcpy(expected,qca_diagnostic,512);else{memcpy(expected,"QIC\2",4);rabbit_sha256(expected+4,qca_diagnostic,512);memcpy(expected+36,qca_diagnostic+512,412);}for(unsigned off=0;off<=size+1;off++){uint8_t request[5]={0x0c,(uint8_t)handle,0,(uint8_t)off,(uint8_t)(off>>8)};size_t n=rg_att(&s,request,sizeof(request),reply,sizeof(reply));if(off>size)assert(n==5&&reply[0]==1&&reply[4]==7);else{unsigned take=size-off;if(take>RG_MTU_MAX-1)take=RG_MTU_MAX-1;assert(n==take+1&&reply[0]==0x0d&&!memcmp(reply+1,expected+off,take));}checks++;}uint8_t write[4]={0x12,(uint8_t)handle,0,7};assert(rg_att(&s,write,4,reply,sizeof(reply))==5&&reply[4]==3);checks++;}
 uint8_t high[7]={0x10,13,0,255,0,0,0x28};assert(rg_att(&s,high,7,reply,sizeof(reply))==5&&reply[4]==0x0a);checks++;printf("PASS %u actual diagnostic65 ATT offset/integrity/readonly/nohighWLAN-service checks\n",checks);return 0;}
