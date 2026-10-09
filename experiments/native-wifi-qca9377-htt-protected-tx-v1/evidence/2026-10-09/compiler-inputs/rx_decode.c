#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wmisleading-indentation"
#pragma GCC diagnostic ignored "-Warray-parameter"
#include "rx_decode.h"
static uint32_t w(const uint8_t*p){return p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static unsigned h(const uint8_t*p){return p[0]|((unsigned)p[1]<<8);}
static int bounds(const void*p,unsigned n){return p&&(uintptr_t)p<=UINTPTR_MAX-n;}
static int overlap(const void*a,unsigned n,const void*b,unsigned m){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;return x<y?y-x<n:x-y<m;}
int qrx_indication(unsigned op,unsigned major,unsigned minor,uint64_t epoch,uint64_t completion,uint64_t floor,const uint8_t*p,unsigned n,QRxInd*out){
 if(op!=3||major!=3||minor!=56||!epoch||completion<=floor||!bounds(p,n)||!bounds(out,sizeof(*out))||!n||n>QRX_RAW||overlap(p,n,out,sizeof(*out)))return 0;
 QRxInd v={0};v.epoch=epoch;v.completion=completion;v.raw_bytes=n;for(unsigned i=0;i<n;i++)v.raw[i]=p[i];v.kind=p[0];v.usable=1;
 if(v.kind==0x12){
  if(n<8)return 0;v.tid=p[1]&31;v.offload=(p[1]>>5)&1;v.frag=(p[1]>>6)&1;v.peer=h(p+2);v.vdev=p[4];v.count=h(p+6);
  if(v.count>QRX_MAX||n!=8+8*v.count)return 0;
  if((p[1]&128)||p[5]||v.offload||v.frag||!v.count){v.usable=0;v.reason=1;}
  for(unsigned i=0;i<v.count;i++){const uint8_t*d=p+8+i*8;v.paddr[i]=w(d);v.length[i]=(uint16_t)h(d+4);v.fw_desc[i]=d[6];if(d[7]){v.usable=0;v.reason=1;}}
 }else if(v.kind==1){
  /* 1byte resp +7byte hdr +36byte PPDU +4byte prefix. */
  if(n<48)return 0;v.tid=p[1]&31;v.flush=(p[1]>>5)&1;v.release=(p[1]>>6)&1;v.peer=h(p+2);uint32_t info=w(p+4);v.ranges=info>>24;v.fw_bytes=h(p+44);
  unsigned at=48+((v.fw_bytes+3)&~3u);if(v.ranges>QRX_MAX||at>n||n-at!=v.ranges*4)return 0;
  if(v.flush||v.release||(p[1]&128)){v.usable=0;v.reason=2;}
  for(unsigned i=0;i<v.ranges;i++){const uint8_t*d=p+at+i*4;v.range_count[i]=d[0];v.range_status[i]=d[1];v.mpdu_count+=d[0];if(d[1]!=1){v.usable=0;v.reason=3;}}
 }else{v.usable=0;v.reason=4;*out=v;return 2;}
 *out=v;return 1;
}
int qrx_claim(QRxRing*r,const QRxInd*i){
 if(!bounds(r,sizeof(*r))||!bounds(i,sizeof(*i))||overlap(r,sizeof(*r),i,sizeof(*i))||r->count>QRX_OWNER_MAX||r->op!=3||r->major!=3||r->minor!=56||r->full_reorder!=1||!r->epoch||i->kind!=0x12||!i->usable||i->count>QRX_MAX||!i->count||i->epoch!=r->epoch||i->completion<=r->floor||i->completion<=r->last)return 0;
 if(!bounds(r->owners,r->count*sizeof(*r->owners))||overlap(r,sizeof(*r),r->owners,r->count*sizeof(*r->owners))||overlap(i,sizeof(*i),r->owners,r->count*sizeof(*r->owners))||i->offload||i->frag)return 0;
 unsigned matched[QRX_MAX];
 for(unsigned a=0;a<r->count;a++){const QRxOwner*e=&r->owners[a];if(!e->paddr||(e->paddr&7)||e->bytes!=2048||e->paddr>UINT32_MAX-2047||e->epoch!=r->epoch||!e->map_identity||e->state<1||e->state>3)return 0;for(unsigned b=0;b<a;b++)if(e->paddr>r->owners[b].paddr?e->paddr-r->owners[b].paddr<2048:r->owners[b].paddr-e->paddr<2048)return 0;}
 for(unsigned a=0;a<i->count;a++){if(!i->paddr[a]||!i->length[a]||i->length[a]>1748)return 0;for(unsigned b=0;b<a;b++)if(i->paddr[a]==i->paddr[b])return 0;unsigned found=QRX_OWNER_MAX;for(unsigned b=0;b<r->count;b++)if(r->owners[b].paddr==i->paddr[a])found=b;if(found==QRX_OWNER_MAX||r->owners[found].state!=1)return 0;matched[a]=found;}
 for(unsigned a=0;a<i->count;a++){r->owners[matched[a]].state=2;r->owners[matched[a]].completion=i->completion;}r->last=i->completion;return 1;
}
int qrx_retire(QRxRing*r,uint32_t paddr,uint64_t epoch,uint64_t completion){if(!bounds(r,sizeof(*r))||r->count>QRX_OWNER_MAX||!bounds(r->owners,r->count*sizeof(*r->owners))||epoch!=r->epoch)return 0;for(unsigned a=0;a<r->count;a++){QRxOwner*e=&r->owners[a];if(e->paddr==paddr&&e->state==2&&e->epoch==epoch&&e->completion==completion){e->state=3;return 1;}}return 0;}
int qrx_frame(const uint8_t*p,unsigned n,unsigned expected,QRxFrame*out){
 if(!bounds(p,n)||!bounds(out,sizeof(*out))||n<300||n>2048||overlap(p,n,out,sizeof(*out)))return 0;
 QRxFrame v={0};v.attention=w(p+4);v.bytes=w(p+24)&16383;v.decap=(w(p+32)>>8)&3;uint32_t end=w(p+56);v.first=(end>>14)&1;v.last=(end>>15)&1;v.seq=(w(p+12)>>16)&4095;
 if(!(v.attention&0x80000000u)||(v.attention&0x7c032000u)||p[10]||v.decap||!v.first||!v.last||v.bytes<24||v.bytes>1748||v.bytes>n-300||(expected&&v.bytes!=expected))return 0;
 v.encrypted=(w(p+12)>>13)&1;if((h(p+300)&0x0400)|| (h(p+322)&15))return 0;
 for(unsigned a=0;a<v.bytes;a++)v.payload[a]=p[300+a];*out=v;return 1;
}

#pragma GCC diagnostic pop
