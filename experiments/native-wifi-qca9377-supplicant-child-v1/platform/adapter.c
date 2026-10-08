#include "adapter.h"
#include "utils/eloop.h"
static int alive(RsnNativeIo*i){return i&&!i->closed&&rsn_runtime_healthy(i->runtime,i->epoch);}
static int same(const uint8_t*a,const uint8_t*b){for(unsigned j=0;j<6;j++)if(a[j]!=b[j])return 0;return 1;}
static void close_io(RsnNativeIo*i,unsigned reason){if(!i||i->closed)return;i->closed=1;i->state=WPA_DISCONNECTED;if(i->close)i->close(i->owner,i->epoch,reason);rsn_runtime_revoke(i->runtime,reason);}
static void set_state(void*c,enum wpa_states s){RsnNativeIo*i=c;if(!alive(i))return;i->state=s;if(i->core_state)i->core_state(i->owner,i->epoch,(unsigned)s);}
static enum wpa_states get_state(void*c){RsnNativeIo*i=c;return alive(i)?i->state:WPA_DISCONNECTED;}
static void deauth(void*c,u16 reason){close_io(c,reason?reason:8);}
static void reconnect(void*c){close_io(c,9);}
static void*network(void*c){RsnNativeIo*i=c;return alive(i)?i->network:0;}
static int bssid(void*c,u8*p){RsnNativeIo*i=c;if(!alive(i)||!p)return -1;os_memcpy(p,i->peer,6);return 0;}
static int key(void*c,int link,enum wpa_alg alg,const u8*addr,int index,int tx,const u8*seq,size_t seq_bytes,const u8*k,size_t bytes,enum key_flag flags){RsnNativeIo*i=c;if(!alive(i)||link!=-1||alg!=WPA_ALG_CCMP||!k||bytes!=16||index<0||index>3||seq_bytes>8||(seq_bytes&&!seq)||!addr||(!same(addr,i->peer)&&!(index&&is_broadcast_ether_addr(addr)))||!i->install_confirmed){close_io(i,10);return -1;}int rc=i->install_confirmed(i->owner,i->epoch,(int)alg,addr,index,tx,seq,seq_bytes,k,bytes,(unsigned)flags);if(rc||!alive(i)){close_io(i,10);return -1;}return 0;}
static int ether(void*c,const u8*dest,u16 protocol,const u8*p,size_t n){RsnNativeIo*i=c;if(!alive(i)||!dest||!same(dest,i->peer)||protocol!=0x888e||!p||n<99||n>4096||p[0]<1||p[0]>3||p[1]!=3||(((size_t)p[2]<<8)|p[3])!=n-4||!i->send_owned){close_io(i,11);return -1;}int rc=i->send_owned(i->owner,i->epoch,dest,protocol,p,n);if(rc||!alive(i)){close_io(i,11);return -1;}return 0;}
static int beacon(void*c){RsnNativeIo*i=c;return alive(i)&&i->sm&&i->rsn_bytes>=2&&i->rsn_bytes<=257?wpa_sm_set_ap_rsn_ie(i->sm,i->rsn,i->rsn_bytes):-1;}
static void auth_timeout(void*c,void*u){(void)u;close_io(c,13);}
static void cancel_timeout(void*c){eloop_cancel_timeout(auth_timeout,c,0);}
static u8*alloc_eapol(void*c,u8 type,const void*body,u16 n,size_t*bytes,void**at){RsnNativeIo*i=c;if(!alive(i)||!bytes||!at||n>4092)return 0;u8*p=os_zalloc(4+n);if(!p)return 0;p[0]=2;p[1]=type;p[2]=(u8)(n>>8);p[3]=(u8)n;if(body)os_memcpy(p+4,body,n);*bytes=4+n;*at=p+4;return p;}
static int pmkid_add(void*c,void*network_ctx,const u8*bssid,const u8*pmkid,const u8*cache_id,const u8*pmk,size_t n,u32 lifetime,u8 threshold,int akmp){(void)c;(void)network_ctx;(void)bssid;(void)pmkid;(void)cache_id;(void)pmk;(void)n;(void)lifetime;(void)threshold;(void)akmp;return -1;}
static int pmkid_remove(void*c,void*network_ctx,const u8*bssid,const u8*pmkid,const u8*cache_id){(void)c;(void)network_ctx;(void)bssid;(void)pmkid;(void)cache_id;return -1;}
static int protect(void*c,const u8*peer,int type,int class){RsnNativeIo*i=c;if(!alive(i)||!peer||!same(peer,i->peer)||type<0||type>3||class!=1||!i->protect_confirmed){close_io(i,12);return -1;}int rc=i->protect_confirmed(i->owner,i->epoch,peer,type,class);if(rc||!alive(i)){close_io(i,12);return -1;}return 0;}
int rsn_native_ctx(RsnNativeIo*i,struct wpa_sm_ctx*out){if(!i||!out||!alive(i)||!i->network||!i->auth_timeout_us||i->auth_timeout_us>30000000||i->rsn_bytes<2||i->rsn_bytes>257||i->rsn[0]!=48||(size_t)i->rsn[1]+2!=i->rsn_bytes||!i->send_owned||!i->install_confirmed||!i->protect_confirmed||!i->close||!i->core_state)return 0;os_memset(out,0,sizeof(*out));out->ctx=i;out->set_state=set_state;out->get_state=get_state;out->deauthenticate=deauth;out->reconnect=reconnect;out->set_key=key;out->get_network_ctx=network;out->get_bssid=bssid;out->ether_send=ether;out->get_beacon_ie=beacon;out->cancel_auth_timeout=cancel_timeout;out->alloc_eapol=alloc_eapol;out->add_pmkid=pmkid_add;out->remove_pmkid=pmkid_remove;out->mlme_setprotection=protect;if(eloop_register_timeout(i->auth_timeout_us/1000000,i->auth_timeout_us%1000000,auth_timeout,i,0))return 0;return 1;}

const uint32_t rsn_runtime_sizes[2]={sizeof(RsnRuntime),sizeof(RsnNativeIo)};
