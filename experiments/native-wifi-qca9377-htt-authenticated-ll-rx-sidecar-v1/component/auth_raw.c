#include "auth_raw.h"
static uint32_t word(const uint8_t*p){return p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static int overlaps(const void*a,unsigned n,const void*b,unsigned m){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;return x>UINTPTR_MAX-n||y>UINTPTR_MAX-m||(x<y?y-x<n:x-y<m);}
int qauth_raw_candidate(const QpnLedger*s,const QRxInd*i,const QRxOwner*o,const uint8_t*p,unsigned n,QauthRawCandidate*out){
 if(!s||!i||!o||!p||!out||n!=2048||overlaps(out,sizeof(*out),s,sizeof(*s))||overlaps(out,sizeof(*out),i,sizeof(*i))||overlaps(out,sizeof(*out),o,sizeof(*o))||overlaps(out,sizeof(*out),p,n))return 0;
 /* Descriptor v1 attention, exact primary h_mpdu decryption preconditions.
  * Also reject MIC/peer timeout/required-encryption errors conservatively. */
 uint32_t att=word(p+4),info=word(p+12);
 if((info>>28)!=6||!(info&(1u<<13))||!(att&(1u<<31))||
    (att&((1u<<30)|(1u<<29)|(1u<<28)|(1u<<24)|(1u<<4)|(1u<<3))))return 0;
 unsigned length=word(p+24)&16383u,header=(p[300]&0x80)?26u:24u;
 /* RAW INORD has actual IV8/MIC8/FCS4. Refuse missing crypto bytes;
  * source h_undecap_raw trims these bytes only after HW decrypted status. */
 if(length>1748||length<header+8+8+8+4)return 0;
 const uint8_t*llc=p+300+header+8;
 if(llc[0]!=0xaa||llc[1]!=0xaa||llc[2]!=3||llc[3]||llc[4]||llc[5])return 0;
 unsigned proto=((unsigned)llc[6]<<8)|llc[7];
 /* Bounded first profile: IPv4/ARP or EAPOL. No VLAN/tunnel guessing. */
 if(proto!=0x0800&&proto!=0x0806&&proto!=0x888e)return 0;
 QauthRawCandidate v={0};v.staged=*s;
 if(qpn_counter_owned(&v.staged,i,o,p,n,&v.provenance)!=QPN_COUNTER_ACCEPTED)return 0;
 unsigned body=length-header-8-8-4;
 v.frame_bytes=header+body;
 for(unsigned j=0;j<header;j++)v.frame[j]=p[300+j];
 v.frame[1]&=(uint8_t)~0x40u;
 for(unsigned j=0;j<body;j++)v.frame[header+j]=llc[j];
 v.ethernet_bytes=14+body-8;
 for(unsigned j=0;j<6;j++){v.ethernet[j]=p[304+j];v.ethernet[6+j]=p[316+j];}
 v.ethernet[12]=llc[6];v.ethernet[13]=llc[7];
 for(unsigned j=8;j<body;j++)v.ethernet[14+j-8]=llc[j];
 *out=v;return 1;
}
