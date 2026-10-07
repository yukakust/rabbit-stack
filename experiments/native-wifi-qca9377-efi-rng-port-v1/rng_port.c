#include "rng_port.h"
#define ERR(n) (UINT64_C(0x8000000000000000)|(n))
const RngGuid rng_protocol_guid={0x3152bca5,0xeade,0x433d,{0x86,0x2e,0xc0,0x1c,0xdc,0x29,0x1f,0x44}};
const RngGuid rng_hash_guid={0xa7af67cb,0x603b,0x4d42,{0xba,0x21,0x70,0xbf,0xb6,0x29,0x3f,0x96}};
const RngGuid rng_hmac_guid={0xc5149b43,0xae85,0x4f53,{0x99,0x82,0xb9,0x43,0x35,0xd3,0xa9,0xe7}};
const RngGuid rng_ctr_guid={0x44f0de6e,0x4d8c,0x4045,{0xa8,0xc7,0x4d,0xd1,0x68,0x85,0x6b,0x9e}};
static void wipe(void *p,size_t n){volatile uint8_t*q=p;while(n--)*q++=0;}
static void copy(void*d,const void*s,size_t n){uint8_t*a=d;const uint8_t*b=s;while(n--)*a++=*b++;}
static int same(const void*a,const void*b,size_t n){const uint8_t*x=a,*y=b;unsigned diff=0;while(n--)diff|=*x++^*y++;return !diff;}
static int fail(RngSession*s,unsigned e){s->phase=3;s->error=e;return 0;}
void rng_diagnostic(const RngSession*s,const uint8_t code[32],RngPublicDiagnostic*out){
 if(!s||!code||!out)return;
 RngPublicDiagnostic d;wipe(&d,sizeof d);
 d.phase=s->phase;d.error=s->error;d.status=s->last_status;
 d.owned_pool_count=!!s->pool;d.uncertain_pool_count=!!s->pool_uncertain;
 d.protocol=rng_protocol_guid;d.selected=s->selected;d.algorithm_count=s->count<=16?s->count:0;
 copy(d.algorithms,s->algorithms,d.algorithm_count*16);copy(d.adapter_code_sha256,code,32);copy(out,&d,sizeof d);
}
int rng_cleanup(RngSession*s){
 if(!s||s->pool_uncertain)return 0;
 if(!s->pool)return 1;
 wipe(s->pool,s->pool_bytes);s->last_status=s->boot.free_pool(s->pool);
 if(s->last_status)return fail(s,9);
 s->pool=0;s->pool_bytes=0;return 1;
}
static int allocate(RngSession*s,size_t n){
 if(s->pool||s->pool_uncertain||!n||n>256)return fail(s,4);
 void*p=0;s->last_status=s->boot.allocate(2,n,&p); /* EfiLoaderData */
 if(s->last_status){if(p){s->pool=p;s->pool_uncertain=1;}return fail(s,4);}
 if(!p)return fail(s,4);s->pool=p;s->pool_bytes=n;wipe(p,n);return 1;
}
int rng_discover(RngSession*s,const RngBootApi*b,uint64_t epoch){
 if(!s||s->phase||s->pool||s->pool_uncertain||s->provider||s->epoch||s->count||!b||!b->locate||!b->allocate||!b->free_pool||!epoch)return 0;
 s->boot=*b;s->epoch=epoch;s->phase=1;
 RngGuid g=rng_protocol_guid;void*p=0;
 s->last_status=b->locate(&g,0,&p);
 if(s->last_status||!p)return fail(s,1);
 s->provider=p;if(!s->provider->get_info||!s->provider->get_rng)return fail(s,2);
 s->bound_methods=*s->provider;
 size_t needed=0;s->last_status=s->provider->get_info(s->provider,&needed,0);
 if(s->last_status!=ERR(5)||!needed||needed>256||needed%16)return fail(s,3);
 if(!allocate(s,needed))return 0;
 size_t bytes=needed;s->last_status=s->provider->get_info(s->provider,&bytes,s->pool);
 unsigned error=s->last_status||!bytes||bytes>needed||bytes%16;
 if(!error){
  s->count=(uint32_t)(bytes/16);copy(s->algorithms,s->pool,bytes);
  for(unsigned i=0;i<s->count;i++)for(unsigned j=0;j<i;j++)if(same(&s->algorithms[i],&s->algorithms[j],16))error=1;
 }
 RngStatus result=s->last_status;if(!rng_cleanup(s))return 0;
 s->last_status=result;if(error)return fail(s,5);s->phase=2;return 1;
}
int rng_fill(RngSession*s,const RngReview*r,uint8_t*out,size_t n){
 uint8_t pending[256]={0};unsigned any=0,found=0;
 if(!s||!r||!out||!n||n>256||s->phase!=2||s->pool||s->pool_uncertain)return 0;
 for(unsigned i=0;i<32;i++)any|=r->provider_provenance_sha256[i];
 if(!any||r->provider!=s->provider||r->epoch!=s->epoch||s->provider->get_info!=s->bound_methods.get_info||s->provider->get_rng!=s->bound_methods.get_rng)return fail(s,6);
 if(!same(&r->algorithm,&rng_hash_guid,16)&&!same(&r->algorithm,&rng_hmac_guid,16)&&!same(&r->algorithm,&rng_ctr_guid,16))return fail(s,7);
 for(unsigned i=0;i<s->count;i++)found|=same(&r->algorithm,&s->algorithms[i],16);
 if(!found)return fail(s,7);
 s->selected=r->algorithm;if(!allocate(s,n))return 0;
 RngGuid requested=s->selected;
 s->last_status=s->provider->get_rng(s->provider,&requested,n,s->pool);
 RngStatus result=s->last_status;
 int algorithm_unchanged=same(&requested,&r->algorithm,16);wipe(&requested,sizeof requested);
 if(!result&&algorithm_unchanged)copy(pending,s->pool,n);
 int closed=rng_cleanup(s);
 if(!closed||result||!algorithm_unchanged){wipe(pending,sizeof pending);s->last_status=result?result:s->last_status;return fail(s,8);}
 copy(out,pending,n);wipe(pending,sizeof pending);s->last_status=0;return 1;
}
