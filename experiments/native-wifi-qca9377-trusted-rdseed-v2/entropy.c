#include "entropy.h"
#include <string.h>
static void wipe(void*p,size_t n){volatile uint8_t*q=p;while(n--)*q++=0;}
static int overlap(const void*a,size_t n,const void*b,size_t m){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;if((n&&!a)||(m&&!b)||n>UINTPTR_MAX-x||m>UINTPTR_MAX-y)return 1;return n&&m&&x<y+m&&y<x+n;}
static int same(const uint8_t*a,const uint8_t*b,size_t n){unsigned x=0;while(n--)x|=*a++^*b++;return x==0;}
static int outside(const TrustedRng*s,const void*p,size_t n){return p&&n&&!overlap(p,n,s,sizeof(*s))&&(!s->source||(!overlap(p,n,s->source,sizeof(*s->source))&&!overlap(p,n,s->source->services.context,s->source->services.context_bytes)));}
static int source(void*ctx,unsigned char*out,size_t n){TrustedRng*s=ctx;uint8_t code[32];memcpy(code,s->approval.admitted_code_set_sha256,32);int r=trusted_seed_fill(s->source,s->approval.epoch,code,out,n);wipe(code,sizeof code);return r;}
int trusted_rng_open_source(TrustedRng*s,const RngApproval*a,TrustedSeedSource*provider){
 if(!s||!a||!provider||s->attempted||s->initialized||s->busy||s->revoked||overlap(s,sizeof(*s),a,sizeof(*a))||(provider!=&s->local_source&&overlap(s,sizeof(*s),provider,sizeof(*provider)))||overlap(a,sizeof(*a),provider,sizeof(*provider))||overlap(provider->services.context,provider->services.context_bytes,s,sizeof(*s))||overlap(provider->services.context,provider->services.context_bytes,a,sizeof(*a))||!provider->initialized||provider->revoked||provider->busy||a->epoch!=provider->approval.epoch||a->cpu_signature!=provider->approval.cpu_signature||a->cpu_flags!=provider->approval.cpu_flags||a->reviewed!=1||a->trusted_owner_code_only!=1||!same(a->actual_inventory_sha256,provider->approval.actual_inventory_sha256,32)||!same(a->parent_file_sha256,provider->approval.parent_file_sha256,32)||!same(a->admitted_code_set_sha256,provider->approval.admitted_code_set_sha256,32))return -1;
 s->attempted=1;s->approval=*a;s->source=provider;s->busy=1;mbedtls_ctr_drbg_init(&s->drbg);
 mbedtls_ctr_drbg_set_entropy_len(&s->drbg,48);mbedtls_ctr_drbg_set_prediction_resistance(&s->drbg,MBEDTLS_CTR_DRBG_PR_ON);mbedtls_ctr_drbg_set_reseed_interval(&s->drbg,1);
 int r=mbedtls_ctr_drbg_seed(&s->drbg,source,s,a->admitted_code_set_sha256,32);
 s->busy=0;s->source_attempts=provider->source_attempts;s->reseed_count=provider->fill_count;
 if(r){mbedtls_ctr_drbg_free(&s->drbg);s->revoked=1;return -1;}s->initialized=1;return 0;
}
int trusted_rng_open(TrustedRng*s,const RngApproval*a,const RngServices*v){if(!s||s->attempted||s->initialized||s->busy||s->revoked||!a||!v||overlap(s,sizeof(*s),a,sizeof(*a))||overlap(s,sizeof(*s),v,sizeof(*v))||overlap(v->context,v->context_bytes,s,sizeof(*s)))return -1;if(trusted_seed_open(&s->local_source,a,v)){if(s->local_source.attempted){s->attempted=1;s->revoked=1;}return -1;}return trusted_rng_open_source(s,a,&s->local_source);}
int trusted_rng_random(TrustedRng*s,uint64_t epoch,const uint8_t code[32],uint8_t*out,size_t n){
 if(!s||!code||!out||!n||n>RNG_MAX_REQUEST||!outside(s,code,32)||!outside(s,out,n)||overlap(code,32,out,n)||s->busy)return -1;
 if(!s->initialized||s->revoked||epoch!=s->approval.epoch||!same(code,s->approval.admitted_code_set_sha256,32)){wipe(out,n);trusted_rng_revoke(s);return -1;}
 if(s->request_count>=4096){wipe(out,n);trusted_rng_revoke(s);return -1;}s->request_count++;
 s->busy=1;int r=mbedtls_ctr_drbg_random(&s->drbg,out,n);s->busy=0;s->source_attempts=s->source->source_attempts;s->reseed_count=s->source->fill_count;
 if(r){wipe(out,n);mbedtls_ctr_drbg_free(&s->drbg);s->initialized=0;s->revoked=1;return -1;}return 0;
}
int trusted_rng_revoke(TrustedRng*s){if(!s||s->busy)return -1;if(s->initialized)mbedtls_ctr_drbg_free(&s->drbg);s->initialized=0;s->revoked=1;if(s->source){s->source->initialized=0;s->source->revoked=1;}return 0;}
int trusted_rng_close(TrustedRng*s){if(!s||s->busy)return -1;if(s->initialized)mbedtls_ctr_drbg_free(&s->drbg);uint32_t attempted=s->attempted;wipe(s,sizeof(*s));s->attempted=attempted;s->revoked=attempted;return 0;}
