#include "artifact.h"
#include "reference/sha256.h"
#include "reference/monocypher-ed25519.h"
static uint32_t rd32(const uint8_t*p){return p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static uint16_t rd16(const uint8_t*p){return p[0]|((uint16_t)p[1]<<8);}
static uint64_t rd64(const uint8_t*p){return rd32(p)|((uint64_t)rd32(p+4)<<32);}
static int eq(const uint8_t*a,const uint8_t*b,size_t n){uint8_t x=0;for(size_t i=0;i<n;i++)x|=a[i]^b[i];return !x;}
static int nz(const uint8_t*p,size_t n){uint8_t x=0;for(size_t i=0;i<n;i++)x|=p[i];return !!x;}
void mod_wipe(void*p,size_t n){volatile uint8_t*q=p;while(n--)*q++=0;}
int mod_overlap(const void*a,size_t n,const void*b,size_t m){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;if((n&&!a)||(m&&!b)||n>UINTPTR_MAX-x||m>UINTPTR_MAX-y)return 1;return n&&m&&x<y+m&&y<x+n;}
int mod_begin(ModArtifact*s,const ModPolicy*p,uint8_t*m,size_t capacity){
 if(!s||!p||!m||mod_overlap(s,sizeof(*s),p,sizeof(*p))||mod_overlap(s,sizeof(*s),m,capacity)||mod_overlap(p,sizeof(*p),m,capacity)||s->memory||s->pinned||!p->epoch||p->counter<=p->last_counter||!p->total||p->total>MOD_FILE_MAX||capacity<p->total||capacity>MOD_FILE_MAX||!p->mapped||p->mapped>MOD_AGGREGATE_MAX||(p->role!=1&&p->role!=2)||p->abi!=MOD_ABI||!nz(p->owner,32)||!nz(p->target,32)||!nz(p->parent_hash,32)||!nz(p->digest,32))return -1;
 s->policy=*p;s->memory=m;s->capacity=capacity;s->received=s->ready=s->poisoned=s->pinned=0;return 0;
}
int mod_accept(ModArtifact*s,const uint8_t*p,size_t n){
 if(!s||!s->memory||s->pinned||s->poisoned||!p||n<MOD_HEADER||n>MOD_HEADER+MOD_CHUNK||mod_overlap(s,sizeof(*s),p,n)||mod_overlap(s->memory,s->capacity,p,n))return -1;
 ModPolicy*q=&s->policy;
 if(!eq(p,(const uint8_t*)(q->role==1?"RABMOD01":"RABRSN01"),8)||!eq(p+8,q->owner,32)||!eq(p+40,q->target,32)||!eq(p+72,q->parent_hash,32)||!eq(p+104,q->digest,32)||rd64(p+168)!=q->epoch||rd64(p+176)!=q->counter||rd32(p+184)!=q->total||rd32(p+196)!=q->role||rd32(p+200)!=q->abi||rd32(p+204)!=q->mapped||rd32(p+208)!=MOD_CHUNK||nz(p+212,12))return -2;
 uint32_t off=rd32(p+188),len=rd32(p+192);if(off>=q->total||off%MOD_CHUNK||len!=n-MOD_HEADER||len!=((q->total-off>MOD_CHUNK)?MOD_CHUNK:q->total-off))return -3;
 if(crypto_ed25519_check(p+224,q->owner,p,224))return -4;
 uint8_t hash[32];rabbit_sha256(hash,p+MOD_HEADER,len);if(!eq(hash,p+136,32))return -5;
 uint32_t bit=1u<<(off/MOD_CHUNK);if(s->received&bit){if(eq(s->memory+off,p+MOD_HEADER,len))return 1;s->poisoned=1;s->ready=0;return -6;}
 for(size_t i=0;i<len;i++)s->memory[off+i]=p[MOD_HEADER+i];s->received|=bit;
 if(s->received==((1u<<((q->total+MOD_CHUNK-1)/MOD_CHUNK))-1)){rabbit_sha256(hash,s->memory,q->total);if(!eq(hash,q->digest,32)){s->poisoned=1;return -7;}s->ready=1;}return 0;
}
int mod_pin(ModArtifact*s){if(!s||!s->memory||!s->ready||s->poisoned||s->pinned)return -1;uint8_t h[32];rabbit_sha256(h,s->memory,s->policy.total);if(!eq(h,s->policy.digest,32)){s->poisoned=1;s->ready=0;return -1;}s->pinned=1;return 0;}
int mod_cancel(ModArtifact*s){if(!s||s->pinned)return -1;if(s->memory)mod_wipe(s->memory,s->policy.total);mod_wipe(s,sizeof(*s));return 0;}
int mod_pe(const uint8_t*p,size_t n,uint32_t*mapped,uint32_t*entry){
 if(!p||!mapped||!entry||mod_overlap(p,n,mapped,4)||mod_overlap(p,n,entry,4)||mod_overlap(mapped,4,entry,4)||n<128||n>MOD_FILE_MAX||p[0]!='M'||p[1]!='Z')return -1;
 size_t pe=rd32(p+60);if(pe>n-24||!eq(p+pe,(const uint8_t*)"PE\0\0",4)||rd16(p+pe+4)!=0x8664)return -1;
 unsigned count=rd16(p+pe+6);size_t opt=pe+24;if(!count||count>16||rd16(p+pe+20)!=240||240>n-opt||rd16(p+opt)!=0x20b||rd16(p+opt+68)!=11||rd32(p+opt+108)!=16)return -1;
 uint32_t img=rd32(p+opt+56),ent=rd32(p+opt+16),head=rd32(p+opt+60),align=rd32(p+opt+32);size_t sections=opt+240;
 if(!img||img>MOD_AGGREGATE_MAX||align!=4096||img%4096||!head||head>n||count>(n-sections)/40||sections+count*40>head)return -1;
 unsigned forbidden[]={9,13,14};for(unsigned i=0;i<3;i++)if(rd32(p+opt+112+8*forbidden[i])||rd32(p+opt+116+8*forbidden[i]))return -1;
 int exec=0;for(unsigned i=0;i<count;i++){const uint8_t*s=p+sections+i*40;uint32_t sz=rd32(s+8),rva=rd32(s+12),raw=rd32(s+16),off=rd32(s+20),fl=rd32(s+36);uint32_t extent=sz>raw?sz:raw;
 if(rva<head||rva%4096||rva>img||extent>img-rva||off>n||raw>n-off||(raw&&off<head)||(fl&0xa0000000u)==0xa0000000u)return -1;
 if((fl&0x20000000u)&&ent>=rva&&ent-rva<sz)exec=1;
 for(unsigned j=0;j<i;j++){const uint8_t*t=p+sections+j*40;uint32_t tr=rd32(t+12),ts=rd32(t+8),tw=rd32(t+16);if(tw>ts)ts=tw;if(extent&&ts&&rva<tr+ts&&tr<rva+extent)return -1;}}
 uint32_t imp=rd32(p+opt+120),is=rd32(p+opt+124);if(imp||is){if(!imp||is<20||is>32)return -1;const uint8_t*t=0;for(unsigned i=0;i<count;i++){const uint8_t*s=p+sections+i*40;uint32_t r=rd32(s+12),raw=rd32(s+16),off=rd32(s+20);if(imp>=r&&imp-r<=raw&&is<=raw-(imp-r))t=p+off+imp-r;}if(!t||nz(t,is))return -1;}
 if(!exec)return -1;*mapped=img;*entry=ent;return 0;
}
int mod_exec_address(const uint8_t*p,size_t n,uintptr_t base,size_t size,uintptr_t a){uint32_t m,e;if(mod_pe(p,n,&m,&e)||size!=m||size>UINTPTR_MAX-base||a<base||a-base>=size)return 0;size_t pe=rd32(p+60),sections=pe+264;unsigned count=rd16(p+pe+6);for(unsigned i=0;i<count;i++){const uint8_t*s=p+sections+40*i;uint32_t r=rd32(s+12),z=rd32(s+8);if((rd32(s+36)&0x20000000u)&&a-base>=r&&a-base-r<z)return 1;}return 0;}
