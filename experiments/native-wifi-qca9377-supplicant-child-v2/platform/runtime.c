#include "runtime.h"
#include <limits.h>
#include "utils/includes.h"
#include "utils/common.h"
#include "utils/eloop.h"
static RsnRuntime*current;
static int overlap(const void*a,size_t n,const void*b,size_t m){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;return n>UINTPTR_MAX-x||m>UINTPTR_MAX-y||(x<y?y-x<n:x-y<m);}
static void wipe(void*p,size_t n){volatile uint8_t*b=p;while(n--)*b++=0;}
static int healthy(RsnRuntime*r){return r&&r==current&&r->providers.epoch&&!r->revoked;}
int rsn_runtime_healthy(const RsnRuntime*r,uint64_t epoch){return r&&r==current&&!r->revoked&&r->providers.epoch==epoch;}
int rsn_runtime_bind(RsnRuntime*r,uint8_t*arena,size_t bytes,const RsnProviders*p){if(!r||!arena||!p||current||!p->epoch||!p->monotonic_us||!p->revoked||bytes<4096||bytes>1048576||((uintptr_t)arena&15)||overlap(r,sizeof(*r),arena,bytes)||overlap(r,sizeof(*r),p,sizeof(*p))||overlap(arena,bytes,p,sizeof(*p)))return 0;unsigned digest=0;for(unsigned j=0;j<32;j++)digest|=p->source_sha256[j];if(!digest)return 0;os_memset(r,0,sizeof(*r));r->arena=arena;r->bytes=bytes;r->providers=*p;wipe(arena,bytes);current=r;return 1;}
void rsn_runtime_revoke(RsnRuntime*r,unsigned error){if(!r||r!=current||r->revoked)return;r->revoked=1;r->error=error?error:1;r->terminate=1;for(unsigned j=0;j<64;j++)r->timers[j].used=0;if(r->providers.revoked)r->providers.revoked(r->providers.ctx,r->providers.epoch,r->error);}
int rsn_runtime_unbind(RsnRuntime*r){if(!r||r!=current||r->dispatching)return 0;for(unsigned j=0;j<128;j++)if(r->allocation[j].used)return 0;for(unsigned j=0;j<64;j++)if(r->timers[j].used)return 0;rsn_runtime_revoke(r,15);wipe(r->arena,r->bytes);current=0;wipe(r,sizeof(*r));return 1;}
static void span(const void*p,size_t n){if(n>1048576||(n&&!p)||n>UINTPTR_MAX-(uintptr_t)p){rsn_runtime_revoke(current,14);abort();}}
static size_t string_bytes(const char*s){if(!s){rsn_runtime_revoke(current,14);abort();}for(size_t j=0;j<4096;j++)if(!s[j])return j;rsn_runtime_revoke(current,14);abort();}
void*os_memcpy(void*d,const void*s,size_t n){span(d,n);span(s,n);return memcpy(d,s,n);}
void*os_memmove(void*d,const void*s,size_t n){span(d,n);span(s,n);return memmove(d,s,n);}
void*os_memset(void*d,int c,size_t n){span(d,n);return memset(d,c,n);}
int os_memcmp(const void*a,const void*b,size_t n){span(a,n);span(b,n);return memcmp(a,b,n);}
int os_memcmp_const(const void*a,const void*b,size_t n){span(a,n);span(b,n);const volatile uint8_t*x=a,*y=b;unsigned d=0;for(size_t j=0;j<n;j++)d|=x[j]^y[j];return d!=0;}
size_t os_strlen(const char*s){return string_bytes(s);}
int os_strcmp(const char*a,const char*b){string_bytes(a);string_bytes(b);return strcmp(a,b);}
int os_strncmp(const char*a,const char*b,size_t n){if(n>4096)abort();span(a,n);span(b,n);return strncmp(a,b,n);}
char*os_strchr(const char*s,int c){string_bytes(s);return strchr(s,c);}
char*os_strrchr(const char*s,int c){string_bytes(s);return strrchr(s,c);}
char*os_strstr(const char*s,const char*b){string_bytes(s);string_bytes(b);return strstr(s,b);}
int os_snprintf(char*out,size_t n,const char*fmt,...){if(n>8192)abort();span(out,n);string_bytes(fmt);va_list ap;va_start(ap,fmt);int r=vsnprintf(out,n,fmt,ap);va_end(ap);return r;}
static int allocation(void*p){if(!current||!p)return -1;for(unsigned j=0;j<128;j++)if(current->allocation[j].used&&p==current->arena+current->allocation[j].offset)return (int)j;return -1;}
void*os_malloc(size_t bytes){RsnRuntime*r=current;if(!healthy(r)||!bytes||bytes>r->bytes||bytes>SIZE_MAX-15)return 0;size_t capacity=(bytes+15)&~(size_t)15;unsigned slot=128;for(unsigned j=0;j<128;j++)if(!r->allocation[j].used){slot=j;break;}if(slot==128)return 0;size_t at=0;while(at<=r->bytes&&capacity<=r->bytes-at){size_t next=at;for(unsigned j=0;j<128;j++){RsnAllocation*a=&r->allocation[j];if(a->used&&at<a->offset+a->capacity&&a->offset<at+capacity){size_t end=a->offset+a->capacity;if(end>next)next=end;}}if(next==at){r->allocation[slot]=(RsnAllocation){at,bytes,capacity,1};wipe(r->arena+at,capacity);return r->arena+at;}at=next;}return 0;}
void*os_zalloc(size_t n){return os_malloc(n);}
void os_free(void*p){if(!p)return;int id=allocation(p);if(id<0){rsn_runtime_revoke(current,2);return;}RsnAllocation*a=&current->allocation[id];wipe(current->arena+a->offset,a->capacity);os_memset(a,0,sizeof(*a));}
void*os_realloc(void*p,size_t n){if(!p)return os_malloc(n);int id=allocation(p);if(id<0){rsn_runtime_revoke(current,2);return 0;}if(!n){os_free(p);return 0;}if(!healthy(current))return 0;RsnAllocation*a=&current->allocation[id];if(n<=a->capacity){if(n<a->bytes)wipe((uint8_t*)p+n,a->bytes-n);else wipe((uint8_t*)p+a->bytes,n-a->bytes);a->bytes=n;return p;}void*q=os_malloc(n);if(!q)return 0;os_memcpy(q,p,a->bytes);os_free(p);return q;}
void*os_memdup(const void*p,size_t n){if(!p||!n)return 0;void*q=os_malloc(n);if(q)os_memcpy(q,p,n);return q;}
char*os_strdup(const char*p){if(!p)return 0;size_t n=os_strlen(p);if(n==SIZE_MAX)return 0;return os_memdup(p,n+1);}
static int clock_us(uint64_t*out){RsnRuntime*r=current;if(!healthy(r)||!out)return -1;uint64_t t=0;if(r->providers.monotonic_us(r->providers.ctx,&t)||(r->have_time&&t<r->last_us)){rsn_runtime_revoke(r,3);return -1;}r->last_us=t;r->have_time=1;*out=t;return 0;}
int os_get_reltime(struct os_reltime*out){uint64_t t;if(!out||clock_us(&t)||t/1000000>(uint64_t)LONG_MAX)return -1;out->sec=(os_time_t)(t/1000000);out->usec=(os_time_t)(t%1000000);return 0;}
int os_get_time(struct os_time*out){RsnRuntime*r=current;uint64_t t=0;if(!out||!healthy(r)||!r->providers.wall_us||r->providers.wall_us(r->providers.ctx,&t)||t/1000000>(uint64_t)LONG_MAX)return -1;out->sec=(os_time_t)(t/1000000);out->usec=(os_time_t)(t%1000000);return 0;}
int os_get_random(unsigned char*out,size_t n){RsnRuntime*r=current;if(!out||!n||n>256||overlap(out,n,r,r?sizeof(*r):0))return -1;if(!healthy(r)||!r->providers.random){wipe(out,n);rsn_runtime_revoke(r,4);return -1;}uint64_t epoch=r->providers.epoch;if(r->providers.random(r->providers.ctx,out,n)||!healthy(r)||r->providers.epoch!=epoch){wipe(out,n);rsn_runtime_revoke(r,4);return -1;}return 0;}
int eloop_register_timeout(unsigned secs,unsigned usecs,eloop_timeout_handler handler,void*ctx,void*user){RsnRuntime*r=current;uint64_t now;if(!healthy(r)||!handler||clock_us(&now)||r->order==UINT64_MAX)return -1;uint64_t delta=(uint64_t)secs*1000000+usecs;if(delta>UINT64_MAX-now)return -1;for(unsigned j=0;j<64;j++)if(!r->timers[j].used){r->timers[j]=(RsnTimer){now+delta,++r->order,r->providers.epoch,handler,ctx,user,1};return 0;}return -1;}
static int timer_match(const RsnTimer*t,eloop_timeout_handler h,void*c,void*u){return t->used&&t->handler==h&&(c==ELOOP_ALL_CTX||c==t->eloop)&&(u==ELOOP_ALL_CTX||u==t->user);}
int eloop_cancel_timeout(eloop_timeout_handler h,void*c,void*u){if(!current)return 0;int n=0;for(unsigned j=0;j<64;j++)if(timer_match(&current->timers[j],h,c,u)){current->timers[j].used=0;n++;}return n;}
int eloop_is_timeout_registered(eloop_timeout_handler h,void*c,void*u){if(!current)return 0;for(unsigned j=0;j<64;j++)if(timer_match(&current->timers[j],h,c,u))return 1;return 0;}
static int adjust_timeout(unsigned secs,unsigned usecs,eloop_timeout_handler h,void*c,void*u,int deplete){uint64_t now;RsnRuntime*r=current;if(!healthy(r)||clock_us(&now))return -1;uint64_t delta=(uint64_t)secs*1000000+usecs;if(delta>UINT64_MAX-now)return -1;for(unsigned j=0;j<64;j++)if(timer_match(&r->timers[j],h,c,u)){uint64_t target=now+delta;if((deplete&&target<r->timers[j].deadline)||(!deplete&&target>r->timers[j].deadline)){r->timers[j].deadline=target;return 1;}return 0;}return -1;}
int eloop_deplete_timeout(unsigned secs,unsigned usecs,eloop_timeout_handler h,void*c,void*u){return adjust_timeout(secs,usecs,h,c,u,1);}
int eloop_replenish_timeout(unsigned secs,unsigned usecs,eloop_timeout_handler h,void*c,void*u){return adjust_timeout(secs,usecs,h,c,u,0);}
int eloop_cancel_timeout_one(eloop_timeout_handler h,void*c,void*u,struct os_reltime*remaining){uint64_t now;if(!current||!remaining||clock_us(&now))return 0;for(unsigned j=0;j<64;j++)if(timer_match(&current->timers[j],h,c,u)){uint64_t delta=current->timers[j].deadline>now?current->timers[j].deadline-now:0;if(delta/1000000>(uint64_t)LONG_MAX)return 0;remaining->sec=(os_time_t)(delta/1000000);remaining->usec=(os_time_t)(delta%1000000);current->timers[j].used=0;return 1;}return 0;}
int rsn_runtime_poll(RsnRuntime*r,uint64_t now,unsigned budget){if(!healthy(r)||r->dispatching||!budget||budget>64)return -1;if(r->have_time&&now<r->last_us){rsn_runtime_revoke(r,3);return -1;}r->last_us=now;r->have_time=1;r->dispatching=1;unsigned dispatched=0;while(dispatched<budget&&healthy(r)){unsigned best=64;for(unsigned j=0;j<64;j++){RsnTimer*t=&r->timers[j];if(t->used&&t->deadline<=now&&(best==64||t->deadline<r->timers[best].deadline||(t->deadline==r->timers[best].deadline&&t->order<r->timers[best].order)))best=j;}if(best==64)break;RsnTimer t=r->timers[best];r->timers[best].used=0;if(t.epoch!=r->providers.epoch){rsn_runtime_revoke(r,5);break;}t.handler(t.eloop,t.user);dispatched++;}r->dispatching=0;return r->revoked?-1:(int)dispatched;}
int eloop_init(void){return healthy(current)?0:-1;}
void eloop_terminate(void){if(current)current->terminate=1;}
int eloop_terminated(void){return !current||current->terminate;}
void eloop_destroy(void){if(current)for(unsigned j=0;j<64;j++)current->timers[j].used=0;}
void eloop_run(void){RsnRuntime*r=current;if(!healthy(r)||r->dispatching)return;r->terminate=0;for(unsigned polls=0;healthy(r)&&!r->terminate;polls++){if(polls==10000000){rsn_runtime_revoke(r,6);break;}uint64_t now;if(clock_us(&now)||rsn_runtime_poll(r,now,64)<0)break;unsigned pending=0;for(unsigned j=0;j<64;j++)pending|=r->timers[j].used;if(!pending)break;}}
struct eapol_sm;
void eapol_sm_request_reauth(struct eapol_sm*sm){(void)sm;rsn_runtime_revoke(current,7);}
