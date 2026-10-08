#include "child.h"
/* HOST synthetic interop, official-PMKSA-patched hostap supplicant + mature authenticator.
 * Driver callbacks below model actual key storage, not firmware success.
 * Deterministic PUBLIC fixture entropy is intentionally insecure/nonproduction. */
#include "includes.h"
#include "common.h"
#include "eloop.h"
#include "common/wpa_common.h"
#include "rsn_supp/wpa.h"
#include "rsn_supp/wpa_i.h"
#include "rsn_supp/pmksa_cache.h"
#include "ap/wpa_auth.h"
#include "crypto/sha1.h"
#include "crypto/sha256.h"
#include "crypto/aes_wrap.h"
#include <assert.h>
#include <time.h>
#include "runtime.h"
static _Alignas(16) uint8_t child_arena[131072];
static uint8_t fake_image_bytes[4096];static LoadedImage child_image;static ModRegistration child_registration;static SystemTable child_system;static uint8_t child_boot[352];static uint64_t child_receipt;static unsigned fixture_finished;
struct wpa_sm*rsn_child_model_sm(void);void*rsn_child_model_network(void);
static void begin_child(void);
static int fixture_clock(void*c,uint64_t*out){(void)c;struct timespec t;if(clock_gettime(CLOCK_MONOTONIC,&t))return -1;*out=(uint64_t)t.tv_sec*1000000+t.tv_nsec/1000;return 0;}
static int fixture_wall(void*c,uint64_t*out){(void)c;struct timespec t;if(clock_gettime(CLOCK_REALTIME,&t))return -1;*out=(uint64_t)t.tv_sec*1000000+t.tv_nsec/1000;return 0;}
static int fixture_entropy(void*,unsigned char*,size_t);
static void fixture_revoked(void*,uint64_t,unsigned);
#define MAX_FRAME 4096
struct frame {int ap_to_sta;size_t n;u8 b[MAX_FRAME];};
struct fixture {
 struct wpa_sm*supp;struct wpa_authenticator*auth;struct wpa_state_machine*station;
 enum wpa_states state;int eapol[8];unsigned ap_ptk,sta_ptk,ap_gtk,sta_gtk,deauth,sent,delivered,protection,install_attempts,backend_installs,quarantined,blocked;
 u8 ap_tk[16],sta_tk[16],ap_gk[4][16],sta_gk[16],pmk[32];unsigned sta_gk_index;
 struct frame queue[32],m3,g1;unsigned head,count;int mode,tampered,group_started,pmksa_checked,pmksa_selected;
};
static struct fixture f;
static void fixture_revoked(void*c,uint64_t epoch,unsigned why){(void)c;assert(epoch==99&&why);f.quarantined=1;f.state=WPA_DISCONNECTED;f.deauth++;}
static struct rsn_pmksa_cache_entry *cached;
static int other_network;
/* Enterprise reauthentication is unavailable in this PSK-only fixture: fail closed. */
struct eapol_sm;
/* Unsupported enterprise reauth is supplied by the real fail-closed runtime. */
static const u8 ap[6]={2,0,0,0,0,1},sta[6]={2,0,0,0,0,2};
static const u8 ssid[]="iPhone (9)";
static unsigned entropy_calls;
static int fixture_entropy(void*c,unsigned char*b,size_t n){(void)c;for(size_t i=0;i<n;i++)b[i]=(u8)((entropy_calls+1)*37+i*13);entropy_calls++;return 0;}
static void pump(void*,void*);
static void enqueue(int direction,const u8*b,size_t n){assert(n<=MAX_FRAME&&f.count<32);struct frame*t=&f.queue[(f.head+f.count)%32];t->ap_to_sta=direction;t->n=n;memcpy(t->b,b,n);f.count++;f.sent++;/* Parent owns queued immutable bytes; dispatch outside child timer/provider callback. */ (void)0;}
static void set_state(void*ctx,enum wpa_states s){(void)ctx;f.state=s;}
static enum wpa_states get_state(void*ctx){(void)ctx;return f.state;}
static void deauth(void*ctx,u16 reason){(void)ctx;(void)reason;f.deauth++;f.state=WPA_DISCONNECTED;}
static void reconnect(void*ctx){(void)ctx;assert(!"unexpected reconnect");}
static int get_bssid(void*ctx,u8*b){(void)ctx;memcpy(b,ap,6);return 0;}
static void*network(void*ctx){return ctx;}
static int protect(void*ctx,const u8*addr,int type,int key_type){(void)ctx;(void)key_type;assert(!memcmp(addr,ap,6));if(!f.sta_ptk)return -1;f.protection=(unsigned)type;return 0;}
static int beacon(void*ctx){(void)ctx;size_t n=0;const u8*ie=wpa_auth_get_wpa_ie(f.auth,&n);if(!ie||!n)return -1;return wpa_sm_set_ap_rsn_ie(f.supp,ie,n);}
static void cancel_timeout(void*ctx){(void)ctx;}
/* This fixture has no driver PMKSA offload: report unsupported, never fabricate success. */
static int add_pmkid(void*c,void*network_ctx,const u8*bssid,const u8*pmkid,const u8*cache_id,const u8*pmk,size_t n,u32 life,u8 threshold,int akmp){(void)c;(void)network_ctx;(void)bssid;(void)pmkid;(void)cache_id;(void)pmk;(void)n;(void)life;(void)threshold;(void)akmp;return -1;}
static int remove_pmkid(void*c,void*network_ctx,const u8*bssid,const u8*pmkid,const u8*cache_id){(void)c;(void)network_ctx;(void)bssid;(void)pmkid;(void)cache_id;return -1;}
static int ether_send(void*ctx,const u8*dest,u16 proto,const u8*b,size_t n){(void)ctx;assert(!memcmp(dest,ap,6)&&proto==ETH_P_EAPOL);enqueue(0,b,n);return 0;}
static u8*alloc_eapol(void*ctx,u8 type,const void*data,u16 n,size_t*len,void**pos){(void)ctx;u8*b=os_zalloc(4+n);if(!b)return NULL;b[0]=2;b[1]=type;WPA_PUT_BE16(b+2,n);if(data)memcpy(b+4,data,n);*len=4+n;*pos=b+4;return b;}
static int sta_key(void*ctx,int link,enum wpa_alg alg,const u8*addr,int index,int tx,const u8*seq,size_t seq_len,const u8*key,size_t n,enum key_flag flag){(void)ctx;(void)link;(void)tx;(void)seq;(void)seq_len;(void)flag;if(alg==WPA_ALG_NONE){if(index==0)forced_memzero(f.sta_tk,16);else forced_memzero(f.sta_gk,16);return 0;}assert(alg==WPA_ALG_CCMP&&n==16);if(f.quarantined){f.blocked++;return -1;}if(index==0){assert(!memcmp(addr,ap,6));f.install_attempts++;if(f.mode==4)return -1;if(f.mode==3){memcpy(f.sta_tk,key,16);f.backend_installs++;f.quarantined=1;return -1;}f.backend_installs++;f.sta_ptk++;memcpy(f.sta_tk,key,16);}else{assert(index>0&&index<4);f.sta_gtk++;f.sta_gk_index=(unsigned)index;memcpy(f.sta_gk,key,16);}return 0;}
static void ap_set_eapol(void*ctx,const u8*addr,wpa_eapol_variable var,int value){(void)ctx;assert(!memcmp(addr,sta,6));assert((unsigned)var<8);f.eapol[var]=value;}
static int ap_get_eapol(void*ctx,const u8*addr,wpa_eapol_variable var){(void)ctx;assert(!memcmp(addr,sta,6));return f.eapol[var];}
static const u8*get_psk(void*ctx,const u8*addr,const u8*dev,const u8*prev,size_t*n,int*vlan){(void)ctx;(void)dev;assert(!memcmp(addr,sta,6));if(n)*n=32;if(vlan)*vlan=0;return prev?NULL:f.pmk;}
static int ap_key(void*ctx,int vlan,enum wpa_alg alg,const u8*addr,int index,u8*key,size_t n,enum key_flag flag){(void)ctx;(void)vlan;(void)flag;if(alg==WPA_ALG_NONE){if(index==0)forced_memzero(f.ap_tk,16);else if(index>0&&index<4)forced_memzero(f.ap_gk[index],16);return 0;}assert(alg==WPA_ALG_CCMP&&n==16);if(index==0){assert(addr&&!memcmp(addr,sta,6));f.ap_ptk++;memcpy(f.ap_tk,key,16);}else{assert(index>0&&index<4);f.ap_gtk++;memcpy(f.ap_gk[index],key,16);}return 0;}
static int seqnum(void*ctx,const u8*addr,int idx,u8*seq){(void)ctx;(void)addr;(void)idx;memset(seq,0,8);return 0;}
static int ap_send(void*ctx,const u8*addr,const u8*b,size_t n,int encrypt){(void)ctx;(void)encrypt;assert(!memcmp(addr,sta,6));enqueue(1,b,n);return 0;}
static void ap_disconnect(void*ctx,const u8*addr,u16 reason){(void)ctx;(void)addr;(void)reason;f.deauth++;}
static int sta_count(void*ctx){(void)ctx;return f.station?1:0;}
static int each_sta(void*ctx,int(*cb)(struct wpa_state_machine*,void*),void*arg){(void)ctx;return f.station?cb(f.station,arg):0;}
static int each_auth(void*ctx,int(*cb)(struct wpa_authenticator*,void*),void*arg){(void)ctx;return cb(f.auth,arg);}
static int local_data_allowed(void){return f.state==WPA_COMPLETED&&f.sta_ptk==1&&f.sta_gtk>=1&&f.protection&&!f.quarantined&&!f.deauth;}
static void finish(void*e,void*t){(void)e;(void)t;fixture_finished=1;/* Typed cooperative POLL has no blocking eloop_run to terminate. */}
static void pump(void*e,void*t){(void)e;(void)t;if(!f.count)return;struct frame v=f.queue[f.head];f.head=(f.head+1)%32;f.count--;f.delivered++;
 if(v.ap_to_sta){assert(v.n>=99);unsigned info=WPA_GET_BE16(v.b+5);int pairwise=!!(info&WPA_KEY_INFO_KEY_TYPE),mic=!!(info&WPA_KEY_INFO_MIC);
  if((f.mode>=10&&f.mode<=12)&&pairwise&&!mic){assert(v.n==99);v.b[99]=0xdd;v.b[100]=20;v.b[101]=0;v.b[102]=0x0f;v.b[103]=0xac;v.b[104]=4;memcpy(v.b+105,cached->pmkid,16);v.n=121;WPA_PUT_BE16(v.b+97,22);WPA_PUT_BE16(v.b+2,117);}
  if(pairwise&&mic)f.m3=v;else if(!pairwise&&mic)f.g1=v;
  if(f.mode==1&&pairwise&&mic){v.b[81]^=1;f.tampered++;}
  if(f.mode==7&&pairwise&&mic){memset(v.b+9,0,8);f.tampered++;}
  if(f.mode==8&&pairwise&&mic){WPA_PUT_BE16(v.b+97,4095);f.tampered++;}
  if(f.mode==22)f.blocked++;else if(f.quarantined||f.deauth)f.blocked++;else {RsnChildEapol input={0};input.epoch=99;input.completion=++child_receipt;input.bytes=v.b;input.count=v.n;memcpy(input.peer,ap,6);input.encryption=FRAME_NOT_ENCRYPTED;assert(child_registration.dispatch(RSN_CHILD_EAPOL,&input)==0);if((f.mode>=10&&f.mode<=12)&&pairwise&&!mic){f.pmksa_checked++;f.pmksa_selected=f.supp->cur_pmksa==cached;if(f.mode==12)assert(f.pmksa_selected);else assert(!f.pmksa_selected);}}
 }else{if(f.mode==6){v.b[81]^=1;f.tampered++;}wpa_receive(f.auth,f.station,v.b,v.n);}
 if(f.count)/* Parent owns queued immutable bytes; dispatch outside child timer/provider callback. */ (void)0;
}
/* Public RFC3394 section4.1, RFC2202 case1 and RFC4231 case1. No values logged. */
static void crypto_vectors(void){
 const u8 kek[16]={0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15};
 const u8 plain[16]={0,0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88,0x99,0xaa,0xbb,0xcc,0xdd,0xee,0xff};
 const u8 expected[24]={0x1f,0xa6,0x8b,0x0a,0x81,0x12,0xb4,0x47,0xae,0xf3,0x4b,0xd8,0xfb,0x5a,0x7b,0x82,0x9d,0x3e,0x86,0x23,0x71,0xd2,0xcf,0xe5};
 u8 wrapped[24],unwrapped[16],key[20],mac[32];assert(!aes_wrap(kek,16,2,plain,wrapped)&&!memcmp(wrapped,expected,24));assert(!aes_unwrap(kek,16,2,wrapped,unwrapped)&&!memcmp(unwrapped,plain,16));wrapped[0]^=1;assert(aes_unwrap(kek,16,2,wrapped,unwrapped)==-1);
 memset(key,0x0b,20);const u8 sha1_expected[20]={0xb6,0x17,0x31,0x86,0x55,0x05,0x72,0x64,0xe2,0x8b,0xc0,0xb6,0xfb,0x37,0x8c,0x8e,0xf1,0x46,0xbe,0x00};assert(!hmac_sha1(key,20,(const u8*)"Hi There",8,mac)&&!memcmp(mac,sha1_expected,20));
 const u8 sha256_expected[32]={0xb0,0x34,0x4c,0x61,0xd8,0xdb,0x38,0x53,0x5c,0xa8,0xaf,0xce,0xaf,0x0b,0xf1,0x2b,0x88,0x1d,0xc2,0x00,0xc9,0x83,0x3d,0xa7,0x26,0xe9,0x37,0x6c,0x2e,0x32,0xcf,0xf7};assert(!hmac_sha256(key,20,(const u8*)"Hi There",8,mac)&&!memcmp(mac,sha256_expected,32));forced_memzero(wrapped,sizeof(wrapped));forced_memzero(unwrapped,sizeof(unwrapped));forced_memzero(key,sizeof(key));forced_memzero(mac,sizeof(mac));
}

static int EFIAPI parent_clock(void*c,uint64_t*out){return fixture_clock(c,out);}
static int EFIAPI parent_wall(void*c,uint64_t*out){return fixture_wall(c,out);}
static int EFIAPI parent_entropy(void*c,uint8_t*out,size_t n){RsnChildStatus status={0};status.epoch=99;assert(!child_registration.dispatch(RSN_CHILD_STATUS,&status));if(f.mode==21&&status.busy){assert(status.borrowed&&child_registration.dispatch(0,NULL)!=0&&child_image.unload(&child_image)!=0);}if(f.mode==20&&status.busy){for(size_t j=0;j<n/2;j++)out[j]=0x5a;return -1;}return fixture_entropy(c,out,n);}
static void EFIAPI parent_revoked(void*c,uint64_t epoch,unsigned reason){fixture_revoked(c,epoch,reason);}
static void EFIAPI parent_state(void*c,uint64_t epoch,unsigned state){assert(epoch==99);set_state(c,(enum wpa_states)state);}
static int EFIAPI parent_send(void*c,uint64_t epoch,const uint8_t*peer,uint16_t protocol,const uint8_t*p,size_t n){assert(epoch==99);return ether_send(c,peer,protocol,p,n);}
static int EFIAPI parent_key(void*c,uint64_t epoch,int alg,const uint8_t*peer,int index,int tx,const uint8_t*seq,size_t seq_bytes,const uint8_t*key,size_t bytes,unsigned flags){assert(epoch==99);return sta_key(c,-1,(enum wpa_alg)alg,peer,index,tx,seq,seq_bytes,key,bytes,(enum key_flag)flags);}
static int EFIAPI parent_protect(void*c,uint64_t epoch,const uint8_t*peer,int type,int key_type){assert(epoch==99);return protect(c,peer,type,key_type);}
static Status EFIAPI fake_get(void*handle,const Guid*guid,void**out){assert(handle==&child_image&&!memcmp(guid,&loaded_image_guid,sizeof(*guid)));*out=&child_image;return 0;}
static void begin_child(void){TableHeader*h=(TableHeader*)child_boot;h->signature=UINT64_C(0x56524553544f4f42);h->size=sizeof child_boot;void*get=(void*)fake_get;memcpy(child_boot+152,&get,sizeof get);child_system.boot=child_boot;child_image.system=&child_system;child_image.parent=&f;child_image.base=fake_image_bytes;child_image.size=sizeof fake_image_bytes;child_registration.magic=MOD_REG_MAGIC;child_registration.abi=1;child_registration.size=sizeof child_registration;child_registration.role=2;child_registration.epoch=99;child_registration.counter=1;child_registration.digest[0]=1;child_registration.parent_hash[0]=2;child_image.options=&child_registration;child_image.options_size=sizeof child_registration;assert(rsn_child_entry(&child_image,&child_system)==0&&child_registration.dispatch);static const uint8_t rsn[]={48,20,1,0,0,15,172,4,1,0,0,15,172,4,1,0,0,15,172,2,0,0};uint8_t pmk[32];memcpy(pmk,f.pmk,32);if(f.mode==9)pmk[0]^=1;RsnChildOpen open={0};open.epoch=99;open.rx_floor=1;child_receipt=1;open.arena=child_arena;open.arena_bytes=sizeof child_arena;open.providers.context=&f;open.providers.context_bytes=sizeof f;open.providers.source_sha256[0]=1;open.providers.monotonic_us=parent_clock;open.providers.wall_us=parent_wall;open.providers.random=parent_entropy;open.providers.send_owned=parent_send;open.providers.install_confirmed=parent_key;open.providers.protect_confirmed=parent_protect;open.providers.state=parent_state;open.providers.revoked=parent_revoked;memcpy(open.peer,ap,6);memcpy(open.own,sta,6);open.ssid=ssid;open.ssid_bytes=sizeof(ssid)-1;open.rsn=rsn;open.rsn_bytes=sizeof rsn;open.pmk=pmk;open.pmk_bytes=32;open.auth_timeout_us=f.mode==22?1000:5000000;RsnChildOpen bad=open;bad.providers.context=&bad;bad.providers.context_bytes=sizeof bad;assert(child_registration.dispatch(RSN_CHILD_OPEN,&bad)!=0);bad=open;bad.pmk=open.arena;assert(child_registration.dispatch(RSN_CHILD_OPEN,&bad)!=0);bad=open;bad.epoch=100;assert(child_registration.dispatch(RSN_CHILD_OPEN,&bad)!=0);bad=open;bad.auth_timeout_us=30000001;assert(child_registration.dispatch(RSN_CHILD_OPEN,&bad)!=0);bad=open;bad.providers.random=NULL;assert(child_registration.dispatch(RSN_CHILD_OPEN,&bad)!=0);RsnChildStatus unopened={0};unopened.epoch=99;assert(!child_registration.dispatch(RSN_CHILD_STATUS,&unopened)&&!unopened.opened&&!unopened.allocations&&!unopened.timers);assert(child_registration.dispatch(RSN_CHILD_OPEN,&open)==0);RsnChildStatus alias={0};alias.epoch=99;memcpy(child_arena+120000,&alias,sizeof alias);assert(child_registration.dispatch(RSN_CHILD_STATUS,child_arena+120000)!=0);memset(child_arena+120000,0,sizeof alias);RsnChildPoll malformed={99,1,65,0,0};assert(child_registration.dispatch(RSN_CHILD_POLL,&malformed)!=0);RsnChildEapol stale={0};stale.epoch=99;stale.completion=open.rx_floor;stale.bytes=pmk;stale.count=32;memcpy(stale.peer,ap,6);assert(child_registration.dispatch(RSN_CHILD_EAPOL,&stale)!=0);assert(child_registration.dispatch(99,NULL)!=0);forced_memzero(pmk,sizeof pmk);assert(child_image.unload(&child_image)!=0);}
static void fixture_loop(void){fixture_finished=0;for(unsigned loops=0;loops<10000000&&!fixture_finished;loops++){if(f.count&&!f.quarantined&&!f.deauth)pump(NULL,NULL);else{uint64_t now;assert(!fixture_clock(NULL,&now));RsnChildPoll poll={99,f.mode==23?1:now,64,0,0};Status status=child_registration.dispatch(RSN_CHILD_POLL,&poll);if(status){RsnChildStatus stopped={0};stopped.epoch=99;assert(!child_registration.dispatch(RSN_CHILD_STATUS,&stopped)&&stopped.fault);break;}if(poll.result<0)break;struct timespec pause={0,100000};nanosleep(&pause,NULL);}}}

int main(int argc,char**argv){assert(argc==2);f.mode=atoi(argv[1]);for(unsigned j=0;j<32;j++)f.pmk[j]=(u8)(j+1);begin_child();assert((f.mode>=0&&f.mode<=12)||(f.mode>=20&&f.mode<=23));if(f.mode==0)crypto_vectors();assert(eloop_init()==0);f.state=WPA_ASSOCIATED;f.eapol[WPA_EAPOL_portEnabled]=1;
 /* Explicit public fixture PMK, not credentials or a production provider. */
 struct wpa_auth_config conf={0};conf.wpa=2;conf.wpa_key_mgmt=WPA_KEY_MGMT_PSK;conf.wpa_pairwise=conf.rsn_pairwise=conf.wpa_group=WPA_CIPHER_CCMP;conf.eapol_version=2;conf.wpa_group_update_count=conf.wpa_pairwise_update_count=4;conf.disable_pmksa_caching=1;conf.wpa_group_rekey=f.mode==5?1:0;memcpy(conf.ssid,ssid,sizeof(ssid)-1);conf.ssid_len=sizeof(ssid)-1;
 struct wpa_auth_callbacks cb={0};cb.set_eapol=ap_set_eapol;cb.get_eapol=ap_get_eapol;cb.get_psk=get_psk;cb.set_key=ap_key;cb.get_seqnum=seqnum;cb.send_eapol=ap_send;cb.disconnect=ap_disconnect;cb.get_sta_count=sta_count;cb.for_each_sta=each_sta;cb.for_each_auth=each_auth;
 f.auth=wpa_init(ap,&conf,&cb,NULL);assert(f.auth);assert(wpa_init_keys(f.auth)==0);f.station=wpa_auth_sta_init(f.auth,sta,NULL);assert(f.station);
 f.supp=rsn_child_model_sm();assert(f.supp);size_t ap_ie_len;const u8*ap_ie=wpa_auth_get_wpa_ie(f.auth,&ap_ie_len);assert(ap_ie&&ap_ie_len);assert(wpa_validate_wpa_ie(f.auth,f.station,2412,ap_ie,ap_ie_len,NULL,0,NULL,0,NULL,0,NULL)==WPA_IE_OK);
 if((f.mode>=10&&f.mode<=12)){cached=pmksa_cache_add(f.supp->pmksa,f.pmk,32,NULL,NULL,0,ap,sta,f.mode==10?(void*)&other_network:rsn_child_model_network(),f.mode==11?WPA_KEY_MGMT_IEEE8021X:WPA_KEY_MGMT_PSK,NULL);assert(cached);assert(!f.supp->cur_pmksa);}
 assert(wpa_auth_sta_associated(f.auth,f.station)==0);eloop_register_timeout(0,200000,finish,NULL,NULL);fixture_loop();
 if(f.mode==0||f.mode==2||f.mode==5||f.mode==12||f.mode==21){
  assert(f.state==WPA_COMPLETED&&f.eapol[WPA_EAPOL_authorized]&&f.sta_ptk==1&&f.ap_ptk==1&&f.sta_gtk==1&&f.protection);
  assert(!memcmp(f.ap_tk,f.sta_tk,16)&&!memcmp(f.ap_gk[f.sta_gk_index],f.sta_gk,16));
  if(f.mode==2){unsigned before=f.sta_ptk,gtk=f.sta_gtk;assert(f.m3.n);enqueue(1,f.m3.b,f.m3.n);eloop_register_timeout(0,50000,finish,NULL,NULL);fixture_loop();assert(f.sta_ptk==before&&f.sta_gtk==gtk&&f.eapol[WPA_EAPOL_authorized]);}
  if(f.mode==5){unsigned ap_before=f.ap_gtk;eloop_register_timeout(0,900000,finish,NULL,NULL);fixture_loop();RsnChildStatus group_status={0};group_status.epoch=99;assert(!child_registration.dispatch(RSN_CHILD_STATUS,&group_status));fprintf(stderr,"GROUP ap=%u before=%u sta=%u ptk=%u state=%u fault=%u queue=%u timers=%u\n",f.ap_gtk,ap_before,f.sta_gtk,f.sta_ptk,(unsigned)f.state,group_status.fault,f.count,group_status.timers);assert(f.ap_gtk==ap_before+1&&f.sta_gtk==2&&f.sta_ptk==1&&f.g1.n&&!memcmp(f.ap_gk[f.sta_gk_index],f.sta_gk,16));unsigned gtk=f.sta_gtk;enqueue(1,f.g1.b,f.g1.n);eloop_register_timeout(0,50000,finish,NULL,NULL);fixture_loop();assert(f.sta_gtk==gtk&&f.sta_ptk==1);}
  assert(local_data_allowed());
 }else if(f.mode==20||f.mode==22||f.mode==23){RsnChildStatus failed={0};failed.epoch=99;assert(!child_registration.dispatch(RSN_CHILD_STATUS,&failed)&&failed.fault&&!local_data_allowed());if(f.mode!=23)assert(!f.sta_ptk&&!f.sta_gtk);if(f.mode==23)assert(f.state==WPA_DISCONNECTED&&f.quarantined);if(f.mode==22)assert(failed.fault==13);if(f.mode==23)assert(failed.fault==3);
 }else if(f.mode==10||f.mode==11){assert(f.pmksa_checked&&!f.pmksa_selected);
 }else{
  assert(!local_data_allowed());assert(f.state!=WPA_COMPLETED&&f.sta_ptk==0);if(f.mode!=3&&f.mode!=4)assert(!f.eapol[WPA_EAPOL_authorized]);
  if(f.mode==3){assert(f.quarantined&&f.backend_installs==1&&f.install_attempts==1&&f.deauth);unsigned attempts=f.install_attempts;RsnChildEapol blocked={0};blocked.epoch=99;blocked.completion=++child_receipt;blocked.bytes=f.m3.b;blocked.count=f.m3.n;memcpy(blocked.peer,ap,6);blocked.encryption=FRAME_NOT_ENCRYPTED;assert(child_registration.dispatch(RSN_CHILD_EAPOL,&blocked)!=0);f.blocked++;assert(f.install_attempts==attempts&&f.backend_installs==1);}
  else if(f.mode==4)assert(f.install_attempts&&f.backend_installs==0&&f.deauth);
  else if(f.mode!=9)assert(f.tampered);
 }
 printf("HOST INTEROP mode%d state%d frames%u/%u PTK%u/%u GTK%u/%u authorized%d tampered%d ambiguous%u backend%u blocked%u localdata%d PASS; synthetic only\n",f.mode,f.state,f.sent,f.delivered,f.ap_ptk,f.sta_ptk,f.ap_gtk,f.sta_gtk,f.eapol[WPA_EAPOL_authorized],f.tampered,f.quarantined,f.backend_installs,f.blocked,local_data_allowed());
 wpa_auth_sta_deinit(f.station);f.station=NULL;wpa_deinit(f.auth);f.auth=NULL;eloop_cancel_timeout(finish,NULL,NULL);eloop_cancel_timeout(pump,NULL,NULL);assert(child_registration.dispatch(0,NULL)==0);f.supp=NULL;RsnChildStatus status={0};status.epoch=99;assert(child_registration.dispatch(RSN_CHILD_STATUS,&status)==0&&!status.opened&&!status.borrowed&&!status.allocations&&!status.timers);for(unsigned j=0;j<sizeof child_arena;j++)assert(!child_arena[j]);assert(child_image.unload(&child_image)==0);forced_memzero(&f,sizeof(f));return 0;
}
