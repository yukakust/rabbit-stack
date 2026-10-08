/* HOST synthetic interop, mature unedited hostap supplicant + authenticator.
 * Driver callbacks below model actual key storage, not firmware success.
 * Deterministic PUBLIC fixture entropy is intentionally insecure/nonproduction. */
#include "includes.h"
#include "common.h"
#include "eloop.h"
#include "common/wpa_common.h"
#include "rsn_supp/wpa.h"
#include "ap/wpa_auth.h"
#include "crypto/sha1.h"
#include <assert.h>
#define MAX_FRAME 4096
struct frame {int ap_to_sta;size_t n;u8 b[MAX_FRAME];};
struct fixture {
 struct wpa_sm*supp;struct wpa_authenticator*auth;struct wpa_state_machine*station;
 enum wpa_states state;int eapol[8];unsigned ap_ptk,sta_ptk,ap_gtk,sta_gtk,deauth,sent,delivered,protection,install_attempts,backend_installs,quarantined,blocked;
 u8 ap_tk[16],sta_tk[16],ap_gk[4][16],sta_gk[16],pmk[32];unsigned sta_gk_index;
 struct frame queue[32],m3,g1;unsigned head,count;int mode,tampered,group_started;
};
static struct fixture f;
static const u8 ap[6]={2,0,0,0,0,1},sta[6]={2,0,0,0,0,2};
static const u8 ssid[]="RABBIT-SYNTHETIC-ONLY";
static unsigned entropy_calls;
int __wrap_os_get_random(unsigned char*b,size_t n){for(size_t i=0;i<n;i++)b[i]=(u8)((entropy_calls+1)*37+i*13);entropy_calls++;return 0;}
static void pump(void*,void*);
static void enqueue(int direction,const u8*b,size_t n){assert(n<=MAX_FRAME&&f.count<32);struct frame*t=&f.queue[(f.head+f.count)%32];t->ap_to_sta=direction;t->n=n;memcpy(t->b,b,n);f.count++;f.sent++;eloop_register_timeout(0,0,pump,NULL,NULL);}
static void set_state(void*ctx,enum wpa_states s){(void)ctx;f.state=s;}
static enum wpa_states get_state(void*ctx){(void)ctx;return f.state;}
static void deauth(void*ctx,u16 reason){(void)ctx;(void)reason;f.deauth++;f.state=WPA_DISCONNECTED;}
static void reconnect(void*ctx){(void)ctx;assert(!"unexpected reconnect");}
static int get_bssid(void*ctx,u8*b){(void)ctx;memcpy(b,ap,6);return 0;}
static void*network(void*ctx){return ctx;}
static int protect(void*ctx,const u8*addr,int type,int key_type){(void)ctx;(void)key_type;assert(!memcmp(addr,ap,6));if(!f.sta_ptk)return -1;f.protection=(unsigned)type;return 0;}
static int beacon(void*ctx){(void)ctx;size_t n=0;const u8*ie=wpa_auth_get_wpa_ie(f.auth,&n);if(!ie||!n)return -1;return wpa_sm_set_ap_rsn_ie(f.supp,ie,n);}
static void cancel_timeout(void*ctx){(void)ctx;}
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
static void finish(void*e,void*t){(void)e;(void)t;eloop_terminate();}
static void pump(void*e,void*t){(void)e;(void)t;if(!f.count)return;struct frame v=f.queue[f.head];f.head=(f.head+1)%32;f.count--;f.delivered++;
 if(v.ap_to_sta){assert(v.n>=99);unsigned info=WPA_GET_BE16(v.b+5);int pairwise=!!(info&WPA_KEY_INFO_KEY_TYPE),mic=!!(info&WPA_KEY_INFO_MIC);
  if(pairwise&&mic)f.m3=v;else if(!pairwise&&mic)f.g1=v;
  if(f.mode==1&&pairwise&&mic){v.b[81]^=1;f.tampered++;}
  if(f.mode==7&&pairwise&&mic){memset(v.b+9,0,8);f.tampered++;}
  if(f.mode==8&&pairwise&&mic){WPA_PUT_BE16(v.b+97,4095);f.tampered++;}
  if(f.quarantined||f.deauth)f.blocked++;else wpa_sm_rx_eapol(f.supp,ap,v.b,v.n,FRAME_NOT_ENCRYPTED);
 }else{if(f.mode==6){v.b[81]^=1;f.tampered++;}wpa_receive(f.auth,f.station,v.b,v.n);}
 if(f.count)eloop_register_timeout(0,0,pump,NULL,NULL);
}
int main(int argc,char**argv){assert(argc==2);f.mode=atoi(argv[1]);assert(f.mode>=0&&f.mode<=9);assert(eloop_init()==0);f.state=WPA_ASSOCIATED;f.eapol[WPA_EAPOL_portEnabled]=1;
 assert(pbkdf2_sha1("public-hostap-fixture-only",ssid,sizeof(ssid)-1,4096,f.pmk,32)==0);
 struct wpa_auth_config conf={0};conf.wpa=2;conf.wpa_key_mgmt=WPA_KEY_MGMT_PSK;conf.wpa_pairwise=conf.rsn_pairwise=conf.wpa_group=WPA_CIPHER_CCMP;conf.eapol_version=2;conf.wpa_group_update_count=conf.wpa_pairwise_update_count=4;conf.disable_pmksa_caching=1;conf.wpa_group_rekey=f.mode==5?1:0;memcpy(conf.ssid,ssid,sizeof(ssid)-1);conf.ssid_len=sizeof(ssid)-1;
 struct wpa_auth_callbacks cb={0};cb.set_eapol=ap_set_eapol;cb.get_eapol=ap_get_eapol;cb.get_psk=get_psk;cb.set_key=ap_key;cb.get_seqnum=seqnum;cb.send_eapol=ap_send;cb.disconnect=ap_disconnect;cb.get_sta_count=sta_count;cb.for_each_sta=each_sta;cb.for_each_auth=each_auth;
 f.auth=wpa_init(ap,&conf,&cb,NULL);assert(f.auth);assert(wpa_init_keys(f.auth)==0);f.station=wpa_auth_sta_init(f.auth,sta,NULL);assert(f.station);
 struct wpa_sm_ctx*sc=os_zalloc(sizeof(*sc));assert(sc);sc->ctx=&f;sc->set_state=set_state;sc->get_state=get_state;sc->deauthenticate=deauth;sc->reconnect=reconnect;sc->set_key=sta_key;sc->get_network_ctx=network;sc->get_bssid=get_bssid;sc->ether_send=ether_send;sc->get_beacon_ie=beacon;sc->cancel_auth_timeout=cancel_timeout;sc->alloc_eapol=alloc_eapol;sc->mlme_setprotection=protect;
 f.supp=wpa_sm_init(sc);assert(f.supp);struct rsn_supp_config cfg={0};cfg.network_ctx=&f;cfg.ssid=ssid;cfg.ssid_len=sizeof(ssid)-1;cfg.allowed_pairwise_cipher=WPA_CIPHER_CCMP;wpa_sm_set_config(f.supp,&cfg);wpa_sm_set_own_addr(f.supp,sta);u8 client_pmk[32];memcpy(client_pmk,f.pmk,32);if(f.mode==9)client_pmk[0]^=1;wpa_sm_set_pmk(f.supp,client_pmk,32,NULL,ap);forced_memzero(client_pmk,32);
 assert(wpa_sm_set_param(f.supp,WPA_PARAM_PROTO,WPA_PROTO_RSN)==0);assert(wpa_sm_set_param(f.supp,WPA_PARAM_KEY_MGMT,WPA_KEY_MGMT_PSK)==0);assert(wpa_sm_set_param(f.supp,WPA_PARAM_PAIRWISE,WPA_CIPHER_CCMP)==0);assert(wpa_sm_set_param(f.supp,WPA_PARAM_GROUP,WPA_CIPHER_CCMP)==0);assert(wpa_sm_set_param(f.supp,WPA_PARAM_RSN_ENABLED,1)==0);
 size_t ap_ie_len;const u8*ap_ie=wpa_auth_get_wpa_ie(f.auth,&ap_ie_len);assert(ap_ie&&ap_ie_len);assert(wpa_sm_set_ap_rsn_ie(f.supp,ap_ie,ap_ie_len)==0);u8 ie[256];size_t n=sizeof(ie);assert(wpa_sm_set_assoc_wpa_ie_default(f.supp,ie,&n)==0);assert(wpa_validate_wpa_ie(f.auth,f.station,2412,ie,n,NULL,0,NULL,0,NULL,0,NULL)==WPA_IE_OK);
 wpa_sm_notify_assoc(f.supp,ap);assert(wpa_auth_sta_associated(f.auth,f.station)==0);eloop_register_timeout(0,200000,finish,NULL,NULL);eloop_run();
 if(f.mode==0||f.mode==2||f.mode==5){
  assert(f.state==WPA_COMPLETED&&f.eapol[WPA_EAPOL_authorized]&&f.sta_ptk==1&&f.ap_ptk==1&&f.sta_gtk==1&&f.protection);
  assert(!memcmp(f.ap_tk,f.sta_tk,16)&&!memcmp(f.ap_gk[f.sta_gk_index],f.sta_gk,16));
  if(f.mode==2){unsigned before=f.sta_ptk,gtk=f.sta_gtk;assert(f.m3.n);enqueue(1,f.m3.b,f.m3.n);eloop_register_timeout(0,50000,finish,NULL,NULL);eloop_run();assert(f.sta_ptk==before&&f.sta_gtk==gtk&&f.eapol[WPA_EAPOL_authorized]);}
  if(f.mode==5){unsigned ap_before=f.ap_gtk;eloop_register_timeout(0,900000,finish,NULL,NULL);eloop_run();assert(f.ap_gtk==ap_before+1&&f.sta_gtk==2&&f.sta_ptk==1&&f.g1.n&&!memcmp(f.ap_gk[f.sta_gk_index],f.sta_gk,16));unsigned gtk=f.sta_gtk;enqueue(1,f.g1.b,f.g1.n);eloop_register_timeout(0,50000,finish,NULL,NULL);eloop_run();assert(f.sta_gtk==gtk&&f.sta_ptk==1);}
  assert(local_data_allowed());
 }else{
  assert(!local_data_allowed());assert(f.state!=WPA_COMPLETED&&f.sta_ptk==0);if(f.mode!=3&&f.mode!=4)assert(!f.eapol[WPA_EAPOL_authorized]);
  if(f.mode==3){assert(f.quarantined&&f.backend_installs==1&&f.install_attempts==1&&f.deauth);unsigned attempts=f.install_attempts;enqueue(1,f.m3.b,f.m3.n);eloop_register_timeout(0,50000,finish,NULL,NULL);eloop_run();assert(f.blocked&&f.install_attempts==attempts&&f.backend_installs==1);}
  else if(f.mode==4)assert(f.install_attempts&&f.backend_installs==0&&f.deauth);
  else if(f.mode!=9)assert(f.tampered);
 }
 printf("HOST INTEROP mode%d state%d frames%u/%u PTK%u/%u GTK%u/%u authorized%d tampered%d ambiguous%u backend%u blocked%u localdata%d PASS; synthetic only\n",f.mode,f.state,f.sent,f.delivered,f.ap_ptk,f.sta_ptk,f.ap_gtk,f.sta_gtk,f.eapol[WPA_EAPOL_authorized],f.tampered,f.quarantined,f.backend_installs,f.blocked,local_data_allowed());
 wpa_auth_sta_deinit(f.station);f.station=NULL;wpa_sm_deinit(f.supp);f.supp=NULL;wpa_deinit(f.auth);f.auth=NULL;eloop_destroy();forced_memzero(&f,sizeof(f));return 0;
}
