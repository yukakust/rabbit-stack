#include "seed_source.h"
#include <string.h>
static void wipe(void*p,size_t n){volatile uint8_t*q=p;while(n--)*q++=0;}
static int overlap(const void*a,size_t n,const void*b,size_t m){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;if((n&&!a)||(m&&!b)||n>UINTPTR_MAX-x||m>UINTPTR_MAX-y)return 1;return n&&m&&x<y+m&&y<x+n;}
static int nz(const uint8_t*p,size_t n){unsigned x=0;while(n--)x|=*p++;return x!=0;}
static int same(const uint8_t*a,const uint8_t*b,size_t n){unsigned x=0;while(n--)x|=*a++^*b++;return x==0;}
static int outside(const TrustedSeedSource*s,const void*p,size_t n){return p&&n&&!overlap(p,n,s,sizeof(*s))&&!overlap(p,n,s->services.context,s->services.context_bytes);}
static int clock_read(TrustedSeedSource*s,uint64_t*out){if(s->services.clock_us(s->services.context,out)||*out<s->last_time)return -1;s->last_time=*out;return 0;}
int trusted_seed_fill(TrustedSeedSource*s,uint64_t epoch,const uint8_t code[32],uint8_t*out,size_t n){uint8_t scratch[64];uint64_t begin,now;unsigned used=0,attempts=0;int result=-1;
 if(!s||!code||!out||!n||n>sizeof scratch||n%8||!outside(s,code,32)||!outside(s,out,n)||overlap(code,32,out,n)||s->busy)return -1;
 if(!s->initialized||s->revoked||epoch!=s->approval.epoch||!same(code,s->approval.admitted_code_set_sha256,32)||s->fill_count>=4097){wipe(out,n);s->initialized=0;s->revoked=1;return -1;}
 s->busy=1;if(clock_read(s,&begin)||begin>UINT64_MAX-RNG_SOURCE_DEADLINE_US)goto done;
 while(used<n&&attempts<RNG_MAX_ATTEMPTS){
  if(clock_read(s,&now)||now>=begin+RNG_SOURCE_DEADLINE_US)goto done;
  uint64_t value=0;if(s->source_attempts==UINT32_MAX)goto done;int ok=trusted_rdseed64_native(&value);attempts++;s->source_attempts++;
  if(ok<0||ok>1){wipe(&value,sizeof value);goto done;}
  if(ok){for(unsigned i=0;i<8;i++)scratch[used++]=(uint8_t)(value>>(8*i));}
  wipe(&value,sizeof value);
 }
 if(used==n){memcpy(out,scratch,n);s->fill_count++;result=0;}
 done:if(result){wipe(out,n);s->initialized=0;s->revoked=1;}wipe(scratch,sizeof scratch);s->busy=0;return result;
}
int trusted_seed_open(TrustedSeedSource*s,const RngApproval*a,const RngServices*v){
 if(!s||!a||!v||s->attempted||s->initialized||s->busy||s->revoked||overlap(s,sizeof(*s),a,sizeof(*a))||overlap(s,sizeof(*s),v,sizeof(*v))||!a->epoch||a->reviewed!=1||a->trusted_owner_code_only!=1||a->cpu_signature!=0x906ea||a->cpu_flags!=3||!nz(a->actual_inventory_sha256,32)||!nz(a->parent_file_sha256,32)||!nz(a->admitted_code_set_sha256,32)||!v->clock_us||(v->context&&!v->context_bytes)||(!v->context&&v->context_bytes)||v->context_bytes>1048576||overlap(v->context,v->context_bytes,s,sizeof(*s))||overlap(v->context,v->context_bytes,a,sizeof(*a))||overlap(v->context,v->context_bytes,v,sizeof(*v)))return -1;
 RngCpu cpu={0};if(trusted_cpu_native(&cpu)||cpu.signature!=a->cpu_signature||cpu.flags!=a->cpu_flags||!same(cpu.vendor,(const uint8_t*)"GenuineIntel",12))return -1;
 s->attempted=1;s->approval=*a;s->services=*v;s->initialized=1;return 0;
}
int trusted_seed_close(TrustedSeedSource*s){if(!s||s->busy)return -1;uint32_t attempted=s->attempted;wipe(s,sizeof(*s));s->attempted=attempted;s->revoked=attempted;return 0;}
