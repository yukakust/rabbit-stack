#include "provenance.h"
#include "sha256.h"
const PrGuid pr_rng_guid={0x3152bca5,0xeade,0x433d,{0x86,0x2e,0xc0,0x1c,0xdc,0x29,0x1f,0x44}};
const PrGuid pr_loaded_guid={0x5b1b31a1,0x9562,0x11d2,{0x8e,0x3f,0,0xa0,0xc9,0x69,0x72,0x3b}};
static uint16_t u16(const uint8_t*p){return p[0]|(uint16_t)p[1]<<8;}
static uint32_t u32(const uint8_t*p){return u16(p)|(uint32_t)u16(p+2)<<16;}
static void copy(void*d,const void*s,size_t n){uint8_t*a=d;const uint8_t*b=s;while(n--)*a++=*b++;}
static int span(const void*p,size_t n){return p&&n&&n<=UINTPTR_MAX-(uintptr_t)p;}
static int apart(const void*a,size_t n,const void*b,size_t m){return span(a,n)&&span(b,m)&&((uintptr_t)a+n<=(uintptr_t)b||(uintptr_t)b+m<=(uintptr_t)a);}
static int same(const void*a,const void*b,size_t n){const uint8_t*x=a,*y=b;unsigned d=0;while(n--)d|=*x++^*y++;return !d;}
static int contains(const void*p,size_t n,uintptr_t q){return span(p,n)&&q>=(uintptr_t)p&&q-(uintptr_t)p<n;}
static int failed(PrSession*s,unsigned error){s->public.phase=3;s->public.error=error;return 0;}
int pr_code(const uint8_t*p,size_t bytes,uintptr_t method,PrCode*out){
 if(bytes<256||bytes>16777216||!apart(p,bytes,out,sizeof *out)||!contains(p,bytes,method)||u16(p)!=0x5a4d)return 0;
 uint32_t pe=u32(p+60);if(pe>bytes-24||u32(p+pe)!=0x4550||u16(p+pe+4)!=0x8664)return 0;
 unsigned sections=u16(p+pe+6),optional=u16(p+pe+20);
 if(!sections||sections>32||optional<112||optional>512||optional>bytes-pe-24)return 0;
 size_t opt=pe+24,table=opt+optional;
 if(u16(p+opt)!=0x20b||u32(p+opt+56)!=bytes||sections>(bytes-table)/40)return 0;
 PrCode selected={0};unsigned found=0;size_t offset=method-(uintptr_t)p;
 for(unsigned j=0;j<sections;j++){
  const uint8_t*h=p+table+j*40;uint32_t size=u32(h+8),rva=u32(h+12),flags=u32(h+36);
  if(!size||rva>=bytes||size>bytes-rva)return 0;
  if(offset<rva||offset-rva>=size)continue;
  /* Never visit or hash writable data/DRBG state/seed bytes. */
  if((flags&0x60000020u)!=0x60000020u||(flags&0x80000000u)||size>131072||found++)return 0;
  selected.rva=rva;selected.bytes=size;selected.characteristics=flags;
 }
 if(found!=1)return 0;
 rabbit_sha256(selected.sha256,p+selected.rva,selected.bytes);*out=selected;return 1;
}
static int filepath(const uint8_t*p,uint8_t file[16],uint8_t volume[16]){
 if(!span(p,512))return 0;size_t off=0;unsigned file_seen=0,volume_seen=0;
 for(unsigned j=0;j<32&&off<512;j++){
  if(!span(p+off,4))return 0;unsigned n=u16(p+off+2);if(n<4||n>512-off||!span(p+off,n))return 0;
  if(p[off]==0x7f){if(p[off+1]!=0xff||n!=4)return 0;return file_seen==1;}
  if(p[off]==4&&(p[off+1]==6||p[off+1]==7)){
   if(n!=20)return 0;if(p[off+1]==6){if(file_seen++)return 0;copy(file,p+off+4,16);}else{if(volume_seen++)return 0;copy(volume,p+off+4,16);}
  }
  off+=n;
 }
 return 0;
}
int pr_cleanup(PrSession*s){
 if(!s||s->borrowed||!s->attempted)return 0;
 if(s->rng_uncertain||s->image_uncertain)return 0;
 s->borrowed=1;
 if(s->rng_handles){s->public.status=s->api.free_pool(s->rng_handles);if(s->public.status){s->rng_uncertain=1;goto done;}s->rng_handles=0;}
 if(s->image_handles){s->public.status=s->api.free_pool(s->image_handles);if(s->public.status){s->image_uncertain=1;goto done;}s->image_handles=0;}
 s->closed=1;
 done:s->borrowed=0;s->public.owned_pools=!!s->rng_handles+!!s->image_handles;s->public.uncertain_pools=s->rng_uncertain+s->image_uncertain;return s->closed;
}
int pr_capture(PrSession*s,const PrApi*a,uint64_t epoch,const uint8_t code[32]){
 if(!apart(s,sizeof *s,a,sizeof *a)||!apart(s,sizeof *s,code,32)||!epoch||!a->locate||!a->handles||!a->protocol||!a->free_pool||s->attempted||s->rng_handles||s->image_handles||s->provider)return 0;
 for(size_t j=0;j<sizeof *s;j++)if(((const uint8_t*)s)[j])return 0;
 unsigned nz=0;for(unsigned i=0;i<32;i++)nz|=code[i];if(!nz)return 0;
 s->attempted=1;s->borrowed=1;s->api=*a;PrPublic*p=&s->public;copy(p->magic,"QPRV0001",8);p->version=1;p->bytes=sizeof *p;p->epoch=epoch;copy(p->adapter_sha256,code,32);p->phase=1;
 PrGuid guid=pr_rng_guid;void*provider=0;p->status=a->locate(&guid,0,&provider);
 if(p->status||!provider){failed(s,1);goto done;}s->provider=provider;
 if(!span(provider,sizeof(PrRng))||!apart(s,sizeof *s,provider,sizeof(PrRng))){failed(s,2);goto done;}
 PrRng methods=*s->provider;if(!methods.get_info||!methods.get_rng){failed(s,3);goto done;}
 guid=pr_rng_guid;p->status=a->handles(2,&guid,0,&s->rng_count,&s->rng_handles);
 if(p->status){if(s->rng_handles)s->rng_uncertain=1;failed(s,4);goto done;}
 if(!s->rng_handles||!s->rng_count||s->rng_count>16||!apart(s,sizeof *s,s->rng_handles,s->rng_count*sizeof(void*))){if(s->rng_handles)s->rng_uncertain=1;failed(s,5);goto done;}
 p->provider_count=(uint32_t)s->rng_count;unsigned matches=0;
 for(size_t j=0;j<s->rng_count;j++){
  void*value=0;guid=pr_rng_guid;p->status=a->protocol(s->rng_handles[j],&guid,&value);if(p->status||!value){failed(s,6);goto done;}if(value==provider)matches++;
 }
 if(s->rng_count!=1||matches!=1){failed(s,7);goto done;}
 guid=pr_loaded_guid;p->status=a->handles(2,&guid,0,&s->image_count,&s->image_handles);
 if(p->status){if(s->image_handles)s->image_uncertain=1;failed(s,8);goto done;}
 if(!s->image_handles||!s->image_count||s->image_count>256||!apart(s,sizeof *s,s->image_handles,s->image_count*sizeof(void*))||!apart(s->rng_handles,s->rng_count*sizeof(void*),s->image_handles,s->image_count*sizeof(void*))){if(s->image_handles)s->image_uncertain=1;failed(s,9);goto done;}
 p->image_count=(uint32_t)s->image_count;
 for(size_t j=0;j<s->image_count;j++){
  void*value=0;guid=pr_loaded_guid;p->status=a->protocol(s->image_handles[j],&guid,&value);if(p->status||!value){failed(s,10);goto done;}
  if(!apart(s,sizeof *s,value,sizeof(PrImage))){failed(s,11);goto done;}PrImage*i=value;
  if(i->revision!=0x1000||i->bytes<256||i->bytes>16777216||!span(i->base,(size_t)i->bytes))continue;
  if(!contains(i->base,(size_t)i->bytes,(uintptr_t)methods.get_info)||!contains(i->base,(size_t)i->bytes,(uintptr_t)methods.get_rng))continue;
  p->matching_images++;if(p->matching_images!=1||!apart(s,sizeof *s,i->base,(size_t)i->bytes)){failed(s,12);goto done;}
  PrCode info={0},rng={0};uint8_t file[16]={0},volume[16]={0};
  if(!pr_code(i->base,(size_t)i->bytes,(uintptr_t)methods.get_info,&info)||!pr_code(i->base,(size_t)i->bytes,(uintptr_t)methods.get_rng,&rng)||!filepath(i->file_path,file,volume)){failed(s,13);goto done;}
  p->image_bytes=i->bytes;p->info_offset=(uint32_t)((uintptr_t)methods.get_info-(uintptr_t)i->base);p->rng_offset=(uint32_t)((uintptr_t)methods.get_rng-(uintptr_t)i->base);p->info_code=info;p->rng_code=rng;p->code_sections=info.rva==rng.rva?1:2;copy(p->fv_file_guid,file,16);copy(p->fv_volume_guid,volume,16);
 }
 if(!p->matching_images||!same(s->provider,&methods,sizeof methods)){failed(s,14);goto done;}
 p->phase=2;p->provenance_identified=1; /* implementation identity only, NOT entropy approval */
 done:s->borrowed=0;if(!pr_cleanup(s))failed(s,15);p->owned_pools=!!s->rng_handles+!!s->image_handles;p->uncertain_pools=s->rng_uncertain+s->image_uncertain;return p->phase==2&&s->closed;
}
int pr_public(const PrSession*s,PrPublic*out){if(!apart(s,sizeof *s,out,sizeof *out)||s->borrowed)return 0;*out=s->public;return 1;}
