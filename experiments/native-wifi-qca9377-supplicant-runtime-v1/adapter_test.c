#include "adapter.h"
#include "utils/eloop.h"
#include <assert.h>
#include <stdio.h>
static unsigned checks,send_calls,key_calls,protect_calls,close_calls,state_calls,failure;
#define C(x) do{assert(x);checks++;}while(0)
static RsnRuntime runtime;static _Alignas(16) uint8_t arena[65536];static uint64_t time_us=100;
static void runtime_close(void*c,uint64_t epoch,unsigned why){(void)c;assert(epoch==7&&why);}
static int clock_provider(void*c,uint64_t*t){(void)c;*t=time_us;return 0;}
static int sender(void*c,uint64_t epoch,const uint8_t dest[6],uint16_t proto,const uint8_t*p,size_t n){(void)c;C(epoch==7&&dest[0]==2&&proto==0x888e&&p&&n==99);send_calls++;return failure==1?-1:0;}
static int installer(void*c,uint64_t epoch,int alg,const uint8_t*peer,int index,int tx,const uint8_t*seq,size_t sn,const uint8_t*key,size_t n,unsigned flags){(void)c;(void)tx;(void)seq;(void)sn;(void)flags;C(epoch==7&&alg==WPA_ALG_CCMP&&peer[0]==2&&index==0&&key&&n==16);key_calls++;return failure==2?-1:0;}
static int protecter(void*c,uint64_t epoch,const uint8_t peer[6],int type,int cls){(void)c;C(epoch==7&&peer[0]==2&&type==3&&cls==1);protect_calls++;return failure==3?-1:0;}
static void closer(void*c,uint64_t epoch,unsigned why){(void)c;C(epoch==7&&why);close_calls++;}
static void core(void*c,uint64_t epoch,unsigned state){(void)c;C(epoch==7&&state<=9);state_calls++;}
static RsnNativeIo setup(void){RsnProviders p={0};p.epoch=7;p.revoked=runtime_close;p.monotonic_us=clock_provider;p.source_sha256[0]=1;C(rsn_runtime_bind(&runtime,arena,sizeof(arena),&p));RsnNativeIo i={0};i.runtime=&runtime;i.epoch=7;i.network=&runtime;i.peer[0]=2;i.peer[5]=1;i.own[0]=2;i.own[5]=2;i.rsn[0]=48;i.rsn[1]=20;i.rsn_bytes=22;i.auth_timeout_us=1000;i.send_owned=sender;i.install_confirmed=installer;i.protect_confirmed=protecter;i.close=closer;i.core_state=core;return i;}
int main(void){for(unsigned mode=0;mode<6;mode++){failure=mode;time_us=100;RsnNativeIo i=setup();struct wpa_sm_ctx*ctx=os_zalloc(sizeof(*ctx));C(ctx);C(rsn_native_ctx(&i,ctx));C(eloop_is_timeout_registered(0,0,0)==0);ctx->set_state(ctx->ctx,WPA_ASSOCIATED);C(ctx->get_state(ctx->ctx)==WPA_ASSOCIATED);uint8_t frame[99]={2,3,0,95},key[16]={0};if(mode==0){C(!ctx->ether_send(ctx->ctx,i.peer,0x888e,frame,99));C(!ctx->set_key(ctx->ctx,-1,WPA_ALG_CCMP,i.peer,0,1,0,0,key,16,0));C(!ctx->mlme_setprotection(ctx->ctx,i.peer,3,1));ctx->cancel_auth_timeout(ctx->ctx);C(rsn_runtime_poll(&runtime,1100,64)==0);}
 else if(mode==1)C(ctx->ether_send(ctx->ctx,i.peer,0x888e,frame,99)==-1&&i.closed);
 else if(mode==2)C(ctx->set_key(ctx->ctx,-1,WPA_ALG_CCMP,i.peer,0,1,0,0,key,16,0)==-1&&i.closed);
 else if(mode==3)C(ctx->mlme_setprotection(ctx->ctx,i.peer,3,1)==-1&&i.closed);
 else if(mode==4){C(rsn_runtime_poll(&runtime,1100,64)==-1&&i.closed);C(ctx->ether_send(ctx->ctx,i.peer,0x888e,frame,99)==-1);}
 else {frame[3]=94;unsigned before=send_calls;C(ctx->ether_send(ctx->ctx,i.peer,0x888e,frame,99)==-1&&i.closed&&send_calls==before);}
 if(mode)C(!rsn_runtime_healthy(&runtime,7)&&ctx->get_state(ctx->ctx)==WPA_DISCONNECTED);os_free(ctx);eloop_destroy();C(rsn_runtime_unbind(&runtime));}
 RsnNativeIo missing=setup();missing.send_owned=0;struct wpa_sm_ctx*ctx=os_zalloc(sizeof(*ctx));C(!rsn_native_ctx(&missing,ctx));os_free(ctx);eloop_destroy();C(rsn_runtime_unbind(&runtime));C(send_calls==2&&key_calls==2&&protect_calls==2&&state_calls==6&&close_calls>=5);printf("checks=%u actual-mature-callback adapter failures/timeouts/revoke PASS synthetic providers only\n",checks);return 0;}
