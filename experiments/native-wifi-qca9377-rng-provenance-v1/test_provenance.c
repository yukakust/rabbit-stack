#include "provenance.h"
#include "sha256.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define C(x) do {checks++;if(!(x)){fprintf(stderr,"failure line %d: %s\n",__LINE__,#x);exit(1);}}while(0)
static unsigned checks,mode,free_calls,info_calls,rng_calls;
static PrSession s;
static unsigned char image[4096],path[512];
static void *rh[2],*ih[2];
static PrRng rng;
static PrImage loaded;
static void w16(unsigned char*p,unsigned v){p[0]=v;p[1]=v>>8;}
static void w32(unsigned char*p,unsigned v){w16(p,v);w16(p+2,v>>16);}
static PrStatus PR_API locate(PrGuid*g,void*r,void**out){C(!r);C(!memcmp(g,&pr_rng_guid,16));C(!pr_cleanup(&s));*out=&rng;return mode==1?1:0;}
static PrStatus PR_API handles(uint32_t k,PrGuid*g,void*x,size_t*n,void***out){
 C(k==2&&!x);C(!pr_cleanup(&s));
 if(!memcmp(g,&pr_rng_guid,16)){*out=rh;*n=mode==3?2:1;return mode==2?1:0;}
 C(!memcmp(g,&pr_loaded_guid,16));*out=mode==5?rh:ih;*n=mode==6?2:1;return mode==4?1:0;
}
static PrStatus PR_API protocol(void*h,PrGuid*g,void**out){
 C(!pr_cleanup(&s));
 if(!memcmp(g,&pr_rng_guid,16)){C(h==rh[0]||h==rh[1]);*out=&rng;return 0;}
 C(!memcmp(g,&pr_loaded_guid,16));C(h==ih[0]||h==ih[1]);*out=&loaded;
 if(mode==7)rng.get_rng=image+3000;
 return mode==8?1:0;
}
static PrStatus PR_API release(void*p){C(p==rh||p==ih);C(!pr_cleanup(&s));PrPublic pub;C(!pr_public(&s,&pub));free_calls++;return mode==9?1:0;}
static const PrApi api={locate,handles,protocol,release};
static const unsigned char source_hash[32]={1,2,3};
static void fixture(unsigned m){
 memset(&s,0,sizeof s);memset(image,0,sizeof image);memset(path,0,sizeof path);memset(&loaded,0,sizeof loaded);mode=m;free_calls=0;
 w16(image,0x5a4d);w32(image+60,128);w32(image+128,0x4550);w16(image+132,0x8664);w16(image+134,2);w16(image+148,112);w16(image+152,0x20b);w32(image+208,sizeof image);
 unsigned char*h=image+264;w32(h+8,512);w32(h+12,512);w32(h+36,0x60000020);
 h+=40;w32(h+8,512);w32(h+12,2048);w32(h+36,0xc0000040);
 memset(image+512,0x90,512);memset(image+2048,0x5a,512);
 path[0]=4;path[1]=6;w16(path+2,20);memset(path+4,0x77,16);path[20]=0x7f;path[21]=0xff;w16(path+22,4);
 loaded.revision=0x1000;loaded.base=image;loaded.bytes=sizeof image;loaded.file_path=path;
 rng.get_info=image+512;rng.get_rng=image+600;rh[0]=(void*)1;rh[1]=(void*)2;ih[0]=(void*)3;ih[1]=(void*)4;
 if(m==10)w32(image+300,0xe0000020); /* writable method section */
 if(m==11)path[1]=5;
 if(m==12)rng.get_rng=image+2048;
}
static void code_tests(void){
 fixture(0);PrCode a,b;unsigned char expected[32];C(pr_code(image,sizeof image,(uintptr_t)image+512,&a));rabbit_sha256(expected,image+512,512);C(!memcmp(a.sha256,expected,32));
 memset(image+2048,0xa4,512);C(pr_code(image,sizeof image,(uintptr_t)image+600,&b));C(!memcmp(a.sha256,b.sha256,32));
 unsigned char base[4096];memcpy(base,image,sizeof base);
 const unsigned offsets[]={0,128,132,134,148,152,208,272,276,300};
 for(unsigned j=0;j<sizeof offsets/sizeof *offsets;j++){
  memcpy(image,base,sizeof base);memset(image+offsets[j],0,2);memset(&b,0x3c,sizeof b);PrCode before=b;
  C(!pr_code(image,sizeof image,(uintptr_t)image+512,&b));C(!memcmp(&b,&before,sizeof b));
 }
 memcpy(image,base,sizeof base);C(!pr_code(image,sizeof image,(uintptr_t)image+4096,&b));C(!pr_code(image,sizeof image,(uintptr_t)image+2048,&b));C(!pr_code(image,sizeof image,(uintptr_t)image+512,(PrCode*)image));
 w32(image+316,512);w32(image+312,512);w32(image+340,0x60000020);C(!pr_code(image,sizeof image,(uintptr_t)image+512,&b));
}
int main(void){
 code_tests();
 for(unsigned m=0;m<=12;m++){
  fixture(m);int ok=pr_capture(&s,&api,65,source_hash);C(ok==(m==0));C(s.public.entropy_approved==0&&s.public.random_calls==0&&s.public.msr_calls==0);C(info_calls==0&&rng_calls==0);C(!s.borrowed);
  PrPublic p;C(pr_public(&s,&p));C(p.epoch==65);C(!pr_public(&s,(PrPublic*)&s));
  unsigned previous=free_calls;C(!pr_capture(&s,&api,65,source_hash));int cleanup=pr_cleanup(&s);C(free_calls==previous);C((unsigned)cleanup==s.closed);
  if(m==0){C(s.closed&&s.public.provenance_identified);C(free_calls==2);C(p.owned_pools==0&&p.uncertain_pools==0);C(p.fv_file_guid[0]==0x77);C(p.info_offset==512&&p.rng_offset==600);}
  if(m==2||m==4||m==5||m==9)C(!s.closed&&s.public.uncertain_pools);
 }
 fixture(0);s.public.reserved[0]=1;C(!pr_capture(&s,&api,65,source_hash));fixture(0);C(!pr_capture(&s,&api,0,source_hash));C(!pr_capture(&s,&api,65,(unsigned char*)&s));C(!pr_capture(&s,(PrApi*)&s,65,source_hash));
 printf("PROVENANCE injected firmware boundary: %u assertions; public=%zu; no entropy/native physical proof\n",checks,sizeof(PrPublic));return 0;
}
