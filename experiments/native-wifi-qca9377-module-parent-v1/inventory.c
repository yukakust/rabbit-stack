#include "inventory.h"
static int overlap(const void*a,size_t n,const void*b,size_t m){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;if((n&&!a)||(m&&!b)||n>UINTPTR_MAX-x||m>UINTPTR_MAX-y)return 1;return n&&m&&x<y+m&&y<x+n;}
static void wipe(void*p,size_t n){volatile uint8_t*q=p;while(n--)*q++=0;}
static void word(uint8_t*p,uint32_t n){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(n>>(i*8));}
int INV_API inv_cpuid_native(void*unused,uint32_t leaf,uint32_t sub,InvLeaf*out){(void)unused;if(!out)return -1;uint32_t a,b,c,d;__asm__ volatile("cpuid":"=a"(a),"=b"(b),"=c"(c),"=d"(d):"a"(leaf),"c"(sub):"memory");*out=(InvLeaf){a,b,c,d};return 0;}
int inv_capture(InvRecord*out,InvCpuid read,void*ctx,uint64_t epoch,const uint8_t hash[32]){
 if(!out||!read||!epoch||!hash||overlap(out,sizeof(*out),hash,32)||(ctx&&overlap(out,sizeof(*out),ctx,1)))return -1;
 uint8_t nz=0;for(unsigned i=0;i<32;i++)nz|=hash[i];if(!nz)return -1;
 InvRecord r={0};const uint8_t magic[8]={'Q','R','N','G','0','0','0','1'};for(unsigned i=0;i<8;i++)r.magic[i]=magic[i];r.version=1;r.size=sizeof(r);r.epoch=epoch;for(unsigned i=0;i<32;i++)r.source_sha256[i]=hash[i];
 if(read(ctx,0,0,&r.leaf[0]))goto fail;r.leaf_count=1;uint32_t max=r.leaf[0].a;word(r.vendor,r.leaf[0].b);word(r.vendor+4,r.leaf[0].d);word(r.vendor+8,r.leaf[0].c);
 const uint8_t intel[12]={'G','e','n','u','i','n','e','I','n','t','e','l'};unsigned same=1;for(unsigned i=0;i<12;i++)if(r.vendor[i]!=intel[i])same=0;if(same)r.flags|=1;
 if(max>=1){if(read(ctx,1,0,&r.leaf[1]))goto fail;r.leaf_count++;if(r.leaf[1].c&(1u<<31))r.flags|=4;}
 if(max>=7){if(read(ctx,7,0,&r.leaf[2]))goto fail;r.leaf_count++;if(r.leaf[2].b&(1u<<18))r.flags|=2;if(r.leaf[2].d&(1u<<9))r.flags|=8;}
 if(read(ctx,0x80000000u,0,&r.leaf[3]))goto fail;r.leaf_count++;
 if(r.leaf[3].a>=0x80000004u&&r.leaf[3].a<=0x8000ffffu){for(unsigned i=0;i<3;i++){if(read(ctx,0x80000002u+i,0,&r.leaf[4+i]))goto fail;r.leaf_count++;word(r.brand+16*i,r.leaf[4+i].a);word(r.brand+16*i+4,r.leaf[4+i].b);word(r.brand+16*i+8,r.leaf[4+i].c);word(r.brand+16*i+12,r.leaf[4+i].d);}}
 *out=r;wipe(&r,sizeof(r));return 0;
 fail:wipe(&r,sizeof(r));return -1; /* caller output unchanged, never partial success */
}
