#include "scan_event_v2.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
unsigned physical_regression(void);
unsigned reference(const uint8_t*,unsigned,QcaWmiScanEvent*);
static unsigned checks;
#define CK(x) do{checks++;if(!(x)){fprintf(stderr,"line%u\n",__LINE__);abort();}}while(0)
static void put(uint8_t*p,unsigned n){for(unsigned j=0;j<4;j++)p[j]=(uint8_t)(n>>(8*j));}
int main(void){
 uint8_t p[240];QcaWmiScanEvent a,b;
 for(unsigned extra=0;extra<=128;extra+=4)for(unsigned i=0;i<5;i++)for(unsigned bit=0;bit<9;bit++){
  unsigned reasons[]={0,1,4,6,0xffffffff};unsigned n=32+extra;memset(p,0xff,sizeof p);put(p,0x3001);put(p+4,(24+extra)|(36u<<16));
  put(p+8,1u<<bit);put(p+12,reasons[i]);put(p+16,bit==3?2412:0);put(p+20,0xa008);put(p+24,0xa007);put(p+28,0);
  CK(qca_scan_event_v2(p,n,&a)==1);CK(reference(p,n,&b));CK(!memcmp(&a,&b,sizeof a));CK(qca_scan_event_v2_match(p,n,7,8,&a));
  QcaWmiScanEvent old=a;CK(!qca_scan_event_v2_match(p,n,8,8,&a));CK(!memcmp(&a,&old,sizeof a));
 }
 memset(p,0,64);put(p,0x3001);put(p+4,28|(36u<<16));put(p+8,1);put(p+12,6);put(p+20,0xa008);put(p+24,0xa007);
 CK(qca_scan_event_v2(p,36,&a)==1&&a.reason==6&&a.type==1);CK(!qca_wmi_scan_event(p,36,7,8,&b));
 for(unsigned n=0;n<36;n++)CK(!qca_scan_event_v2(p,n,&a));
 put(p+36,4|(999u<<16));put(p+40,0x11223344);CK(qca_scan_event_v2(p,44,&a)==2);CK(!qca_scan_event_v2_match(p,44,7,8,&b));
 put(p+36,24|(36u<<16));CK(!qca_scan_event_v2(p,64,&a));
 CK(!qca_scan_event_v2(p,36,(QcaWmiScanEvent*)p));CK(!qca_scan_event_v2_match(p,36,7,8,(QcaWmiScanEvent*)p));
 CK(!qca_scan_event_v2(0,36,&a));CK(!qca_scan_event_v2(p,36,0));CK(!qca_scan_event_v2(p,4097,&a));
 CK(!qca_scan_event_v2(p,36,(QcaWmiScanEvent*)(UINTPTR_MAX-3)));
 checks+=physical_regression();printf("checks=%u\n",checks);return 0;
}
