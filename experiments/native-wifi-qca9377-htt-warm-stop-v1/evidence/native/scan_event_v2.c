#include "scan_event_v2.h"
static uint32_t word(const uint8_t*p){return p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
 }
static int overlap(const void*a,unsigned n,const void*b,unsigned m){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;
 return x<y?y-x<n:x-y<m;
 }
int qca_scan_event_v2(const uint8_t*p,unsigned n,QcaWmiScanEvent*out){
 if(!p||!out||n<32||n>4096||(uintptr_t)p>UINTPTR_MAX-n||(uintptr_t)out>UINTPTR_MAX-sizeof(*out)||overlap(p,n,out,sizeof(*out))||word(p)!=0x3001)return 0;
 
 QcaWmiTlv t;
 unsigned pos=0,found=0,unhandled=0;
 int rc;
 QcaWmiScanEvent v={0};
 
 while((rc=qca_wmi_tlv(p+4,n-4,&pos,&t))==1){
  if(t.tag==36){
   if(found++||t.bytes<24)return 0;
 
   v.type=word(t.value);
 v.reason=word(t.value+4);
 v.frequency=word(t.value+8);
 
   v.request_id=word(t.value+12);
 v.scan_id=word(t.value+16);
 v.vdev=word(t.value+20);
 
  }else unhandled=1;
 
 }
 if(rc<0||found!=1||!v.type||(v.type&(v.type-1))||(v.type&~0x1ffu)
 ||(v.scan_id&~0xfffu)!=0xa000||(v.request_id&~0xfffu)!=0xa000||!(v.scan_id&0xfff)||!(v.request_id&0xfff))return 0;
 
 *out=v;
 return unhandled?2:1;
 
}
int qca_scan_event_v2_match(const uint8_t*p,unsigned n,unsigned scan,unsigned request,QcaWmiScanEvent*out){
 if(!out||!scan||scan>4095||!request||request>4095)return 0;
 
 QcaWmiScanEvent v;
 if(qca_scan_event_v2(p,n,&v)!=1||v.vdev||v.scan_id!=(0xa000u|scan)||v.request_id!=(0xa000u|request))return 0;
 
 /* Reject alias output even though parsing used a private prefix copy. */
 if(!p||(uintptr_t)out>UINTPTR_MAX-sizeof(*out)||(uintptr_t)p>UINTPTR_MAX-n||overlap(p,n,out,sizeof(*out)))return 0;
 
 *out=v;
 return 1;
 
}
