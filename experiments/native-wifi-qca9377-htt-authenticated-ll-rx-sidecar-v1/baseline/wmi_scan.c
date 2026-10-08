#include "wmi_scan.h"
#include "scan_event_v2.h"
static unsigned le16(const uint8_t*p){return p[0]|((unsigned)p[1]<<8);}
static void put16(uint8_t*p,unsigned x){p[0]=x;p[1]=x>>8;}
static void put32(uint8_t*p,uint32_t x){put16(p,x);put16(p+2,x>>16);}
static void tag(uint8_t*p,unsigned t,unsigned n){put16(p,n);put16(p+2,t);}
int qca_wmi_tlv(const uint8_t*p,unsigned n,unsigned*offset,QcaWmiTlv*out){
 QcaWmiTlv v;unsigned pos,len;
 if(!p||!offset||!out||n>4096||*offset>n)return -1;
 pos=*offset;if(pos==n)return 0;if(n-pos<4)return -1;
 len=le16(p+pos);if((len&3)||len>n-pos-4)return -1;
 v.tag=le16(p+pos+2);v.value=p+pos+4;v.bytes=len;
 *offset=pos+4+len;*out=v;return 1;
}
int qca_wmi_scan_event(const uint8_t*p,unsigned n,unsigned scan,unsigned request,QcaWmiScanEvent*out){return qca_scan_event_v2_match(p,n,scan,request,out);}
static int frequency(unsigned n){return (n>=2412&&n<=2472&&(n-2412)%5==0)||(n>=5180&&n<=5825&&n%5==0);}
unsigned qca_wmi_passive_scan(uint8_t*p,unsigned cap,unsigned scan,unsigned request,const uint16_t*freq,unsigned count){
 unsigned size,base;
 if(!p||!freq||!count||count>64||!scan||scan>0xfff||!request||request>0xfff)return 0;
 size=124+4*count;if(cap<size)return 0;
 for(unsigned i=0;i<count;i++){if(!frequency(freq[i]))return 0;for(unsigned j=0;j<i;j++)if(freq[j]==freq[i])return 0;}
 for(unsigned i=0;i<size;i++)p[i]=0;
 put32(p,0x3001);tag(p+4,77,100);base=8;
 put32(p+base,0xa000|scan);put32(p+base+4,0xa000|request);
 put32(p+base+12,1);put32(p+base+16,0x4b);put32(p+base+20,50);put32(p+base+24,100);
 put32(p+base+28,50);put32(p+base+32,500);put32(p+base+44,50);
 put32(p+base+48,5000+100*count);put32(p+base+52,5);
 /* WMI-TLV inverts FILTER_PROBE_REQ compared with common WMI flags. */
 put32(p+base+56,0x21);put32(p+base+64,count);put32(p+base+80,3);
 base=108;tag(p+base,16,count*4);base+=4;
 for(unsigned i=0;i<count;i++)put32(p+base+4*i,freq[i]);
 base+=4*count;
 tag(p+base,19,0);tag(p+base+4,19,0);tag(p+base+8,17,0);return size;
}
