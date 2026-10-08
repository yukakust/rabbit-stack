#include "runtime.h"
#include "utils/includes.h"
#include "utils/common.h"
#include "utils/eloop.h"
#include "adapter.h"
#include <assert.h>
static unsigned checks;
#define C(x) do{assert(x);checks++;}while(0)
static _Alignas(16) uint8_t arena[65536];static RsnRuntime runtime;
static uint64_t clock_value=100;static unsigned failure,revoke_calls,timer_calls;
static int clock_provider(void*c,uint64_t*out){(void)c;*out=clock_value;return 0;}
static int random_provider(void*c,uint8_t*out,size_t n){(void)c;for(size_t j=0;j<n;j++)out[j]=(uint8_t)(j+1);if(failure==2)rsn_runtime_revoke(&runtime,88);return failure==1?-1:0;}
static void revoked(void*c,uint64_t epoch,unsigned why){(void)c;assert(epoch==7&&why);revoke_calls++;}
static RsnProviders providers(void){RsnProviders p={0};p.epoch=7;p.monotonic_us=clock_provider;p.random=random_provider;p.revoked=revoked;p.source_sha256[0]=1;return p;}
static void timer(void*c,void*u){assert(c==(void*)1&&u==(void*)2);timer_calls++;}
static void canceler(void*c,void*u){(void)c;(void)u;eloop_cancel_timeout(timer,ELOOP_ALL_CTX,ELOOP_ALL_CTX);timer_calls++;}
static void revoke_timer(void*c,void*u){(void)c;(void)u;rsn_runtime_revoke(&runtime,55);timer_calls++;}
static int compare(const void*a,const void*b){int x=*(const int*)a,y=*(const int*)b;return (x>y)-(x<y);}
int main(void){RsnProviders p=providers();C(rsn_runtime_bind(&runtime,arena,sizeof(arena),&p));C(!rsn_runtime_bind(&runtime,arena,sizeof(arena),&p));void*owned[128];for(unsigned j=0;j<128;j++){owned[j]=os_malloc(j+1);C(owned[j]&&!(15&(uintptr_t)owned[j]));os_memset(owned[j],0xa5,j+1);}C(!os_malloc(1));for(unsigned j=0;j<128;j++){unsigned n=j+1;os_free(owned[j]);for(unsigned k=0;k<n;k++)C(!((uint8_t*)owned[j])[k]);}C(!os_malloc(SIZE_MAX));C(!os_malloc(sizeof(arena)+1));
 uint8_t*a=os_malloc(16);C(a);os_memset(a,7,16);uint8_t*b=os_realloc(a,32);C(b&&b!=a);for(unsigned j=0;j<16;j++)C(b[j]==7&&a[j]==0);b=os_realloc(b,8);C(b);for(unsigned j=8;j<16;j++)C(b[j]==0);os_free(b);C(!os_realloc(0,0));
 struct os_reltime now={0};C(os_get_reltime(&now)==0&&now.usec==100);struct os_time wall={9,9};C(os_get_time(&wall)==-1&&wall.sec==9);
 C(eloop_register_timeout(0,50,timer,(void*)1,(void*)2)==0);C(rsn_runtime_poll(&runtime,149,1)==0);C(rsn_runtime_poll(&runtime,150,1)==1&&timer_calls==1);clock_value=150;C(eloop_register_timeout(0,0,canceler,0,0)==0);C(eloop_register_timeout(0,0,timer,(void*)1,(void*)2)==0);C(rsn_runtime_poll(&runtime,150,64)==1&&timer_calls==2);C(!eloop_is_timeout_registered(timer,(void*)1,(void*)2));
 for(unsigned j=0;j<64;j++)C(!eloop_register_timeout(1,0,timer,(void*)1,(void*)2));C(eloop_register_timeout(1,0,timer,(void*)1,(void*)2)==-1);C(eloop_cancel_timeout(timer,ELOOP_ALL_CTX,ELOOP_ALL_CTX)==64);
 char text[128];C(os_snprintf(text,sizeof(text),"%s %02x %llu %zu %.3s","test",7,1234567890123ull,(size_t)9,"abcdef")==27);C(!os_strcmp(text,"test 07 1234567890123 9 abc"));int values[]={8,-1,3,0};qsort(values,4,sizeof(int),compare);C(values[0]==-1&&values[3]==8);char*end=0;C(strtol(" -0x20x",&end,0)==-32&&*end=='x');C(os_memcmp_const("abc","abc",3)==0&&os_memcmp_const("abc","abd",3)!=0);
 uint8_t entropy[32];C(!os_get_random(entropy,32));for(unsigned j=0;j<32;j++)C(entropy[j]==j+1);C(rsn_runtime_healthy(&runtime,7)&&!rsn_runtime_healthy(&runtime,8));C(rsn_runtime_unbind(&runtime));
 p=providers();C(rsn_runtime_bind(&runtime,arena,sizeof(arena),&p));failure=1;os_memset(entropy,9,32);C(os_get_random(entropy,32)==-1);for(unsigned j=0;j<32;j++)C(!entropy[j]);C(!os_malloc(1)&&revoke_calls==2);C(rsn_runtime_unbind(&runtime));failure=0;
 p=providers();C(rsn_runtime_bind(&runtime,arena,sizeof(arena),&p));failure=2;C(os_get_random(entropy,32)==-1);for(unsigned j=0;j<32;j++)C(!entropy[j]);C(rsn_runtime_unbind(&runtime));failure=0;
 p=providers();C(rsn_runtime_bind(&runtime,arena,sizeof(arena),&p));clock_value=1000;C(!os_get_reltime(&now));clock_value=999;C(os_get_reltime(&now)==-1&&!rsn_runtime_healthy(&runtime,7));C(rsn_runtime_unbind(&runtime));
 p=providers();C(rsn_runtime_bind(&runtime,arena,sizeof(arena),&p));clock_value=2000;C(!eloop_register_timeout(0,0,revoke_timer,0,0));C(!eloop_register_timeout(0,0,timer,(void*)1,(void*)2));C(rsn_runtime_poll(&runtime,2000,64)==-1&&timer_calls==3);C(rsn_runtime_unbind(&runtime));
 printf("checks=%u runtime arena/wipe/RNG/timer/epoch/revoke PASS synthetic-providers\n",checks);return 0;}
