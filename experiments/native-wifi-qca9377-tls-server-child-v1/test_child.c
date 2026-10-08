/* Real TLS server through actual child-entry ABI; public upstream fixtures;
 * synthetic firmware+entropy ONLY, no physical calls or key output. */
#include "child.h"
#include "mbedtls/sha256.h"
#include "test/certs.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static unsigned calls,fail_rng;static uint64_t dummy_state=9;static _Alignas(16) uint8_t pool[65536];static TlsBleEndpoint client;static LoadedImage image;static SystemTable st;static uint8_t boot[232];static int parent,handle;
static int EFIAPI rng(void*c,uint8_t*p,size_t n){(void)c;calls++;if(fail_rng)return -1;while(n--){dummy_state^=dummy_state<<13;dummy_state^=dummy_state>>7;dummy_state^=dummy_state<<17;*p++=(uint8_t)dummy_state;}return 0;}
static int client_rng(void*c,uint8_t*p,size_t n){return rng(c,p,n);}
static Status EFIAPI get(void*h,const Guid*g,void**p){assert(h==&handle&&g->a==loaded_image_guid.a);*p=&image;return 0;}
static void pin(const uint8_t*p,size_t n,uint8_t hash[32]){mbedtls_x509_crt c;uint8_t der[128];mbedtls_x509_crt_init(&c);assert(!mbedtls_x509_crt_parse_der(&c,p,n));int bytes=mbedtls_pk_write_pubkey_der(&c.pk,der,sizeof der);assert(bytes>0);assert(!mbedtls_sha256(der+sizeof der-(size_t)bytes,(size_t)bytes,hash,0));mbedtls_x509_crt_free(&c);}
static ChildStatus state(ModDispatch f){ChildStatus s={.epoch=7};assert(!f(CHILD_STATUS,&s));return s;}
int main(void){unsigned cases=0;for(unsigned mode=0;mode<7;mode++){
 memset(&client,0,sizeof(client));ModRegistration r={.magic=MOD_REG_MAGIC,.abi=1,.size=sizeof(r),.role=1,.epoch=7,.counter=1};memset(r.digest,1,32);memset(r.parent_hash,2,32);st.boot=boot;TableHeader bh={.signature=UINT64_C(0x56524553544f4f42),.size=sizeof(boot)};memcpy(boot,&bh,sizeof(bh));HandleProtocol fn=get;memcpy(boot+152,&fn,sizeof(fn));image=(LoadedImage){.parent=&parent,.system=&st,.options_size=sizeof(r),.options=&r,.base=(void*)0x10000,.size=131072};
 assert(!tls_child_entry(&handle,&st)&&r.dispatch&&image.unload);assert(tls_child_entry(&handle,&st));ModDispatch f=r.dispatch;
 uint8_t sp[32],cp[32];/* Pin helper requires heap, so public SPKI hashes below computed outside child in prior fixture. */
 static const uint8_t spki_server[32]={0};(void)spki_server;
 /* Bind/open with provisional peer hash then pin both fixtures in same child-owned heap. */
 memset(cp,1,32);ChildOpen open={7,1,50000000,pool,sizeof(pool),mbedtls_test_srv_crt_ec_der,mbedtls_test_srv_crt_ec_der_len,mbedtls_test_srv_key_ec_der,mbedtls_test_srv_key_ec_der_len,cp,rng,0};
 ChildOpen stale=open;stale.epoch=8;assert(f(CHILD_OPEN,&stale));stale=open;stale.entropy=0;assert(f(CHILD_OPEN,&stale));assert(!state(f).initialized);unsigned before=calls;assert(!f(CHILD_OPEN,&open));assert(f(CHILD_OPEN,&open)&&calls==before);assert(image.unload(&handle));
 pin(mbedtls_test_srv_crt_ec_der,mbedtls_test_srv_crt_ec_der_len,sp);pin(mbedtls_test_cli_crt_ec_der,mbedtls_test_cli_crt_ec_der_len,cp);
 /* Reconfigure with correct independently full SPKI: close/reopen before client. */
 assert(!f(0,0));assert(!f(CHILD_OPEN,&open));if(mode==1)sp[31]^=1;
 assert(tls_ble_open(&client,0,mbedtls_test_cli_crt_ec_der,mbedtls_test_cli_crt_ec_der_len,mbedtls_test_cli_key_ec_der,mbedtls_test_cli_key_ec_der_len,sp,"localhost",client_rng,0,7,1,50000000)==1);
 uint8_t bytes[240],plain[32]={0},message[]={1,2,3,4};ChildIo io={.epoch=7,.bytes=message,.count=sizeof(message)};assert(!f(CHILD_WRITE,&io)&&io.result<0);io.epoch=8;assert(f(CHILD_WRITE,&io));io.epoch=7;io.bytes=pool;io.count=1;assert(f(CHILD_FEED,&io));
 if(mode==2)fail_rng=1;if(mode==3){io=(ChildIo){.epoch=7,.sequence=1,.bytes=bytes,.count=1};assert(!f(CHILD_FEED,&io)&&io.result<0);}if(mode==4){io=(ChildIo){.epoch=7,.now=50000001};assert(!f(CHILD_POLL,&io)&&io.result<0);}
 uint32_t seq=0;unsigned fragment=mode==5?1:240;
 for(unsigned tick=0;tick<20000;tick++){ChildStatus s=state(f);if(client.fault||s.fault||(client.ready&&s.ready))break;if(tls_ble_poll(&client,7,2+tick*1000)<0)break;io=(ChildIo){.epoch=7,.now=2+tick*1000};assert(!f(CHILD_POLL,&io));size_t n=tls_ble_drain(&client,7,bytes,fragment);if(n){io=(ChildIo){.epoch=7,.sequence=seq++,.bytes=bytes,.count=n};assert(!f(CHILD_FEED,&io));}io=(ChildIo){.epoch=7,.bytes=bytes,.count=fragment};assert(!f(CHILD_DRAIN,&io));if(io.result>0)assert(tls_ble_feed(&client,7,client.feed_sequence,bytes,(size_t)io.result)==1);}
 if(mode==0||mode==5||mode==6){assert(client.ready&&state(f).ready);assert(tls_ble_write(&client,7,message,sizeof(message))==sizeof(message));for(unsigned tick=0;tick<1000&&!plain[0]&&!state(f).fault;tick++){size_t n=tls_ble_drain(&client,7,bytes,240);if(n){if(mode==6)bytes[n-1]^=1;io=(ChildIo){.epoch=7,.sequence=seq++,.bytes=bytes,.count=n};assert(!f(CHILD_FEED,&io));}io=(ChildIo){.epoch=7,.bytes=plain,.count=sizeof(plain)};assert(!f(CHILD_READ,&io));}if(mode==6)assert(state(f).fault&&!plain[0]);else assert(!memcmp(plain,message,sizeof(message)));}else assert(client.fault||state(f).fault);
 fail_rng=0;tls_ble_close(&client);assert(!f(0,0));assert(!state(f).initialized&&!state(f).heap_live);for(unsigned i=0;i<sizeof(pool);i++)assert(!pool[i]);assert(!image.unload(&handle));cases++;
 }printf("PASS %u actual child-entry TLS13 synthetic interoperability/lifetime scenarios; no physical RNG/BLE/key output\n",cases);return 0;}
