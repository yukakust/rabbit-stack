/* Public deterministic protocol fixtures only. No live RNG/key/credential/signature. */
#include <noise/protocol.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
static int fail_after=-1;static unsigned checks,rng_calls,allocations;static size_t live,peak;static void*slots[64];static size_t sizes[64];
void *__real_malloc(size_t);void *__real_calloc(size_t,size_t);void __real_free(void*);
void *__wrap_calloc(size_t count,size_t size){if(fail_after==0)return 0;if(fail_after>0)fail_after--;void*p=__real_calloc(count,size);if(p){unsigned i=0;while(i<64&&slots[i])i++;assert(i<64);slots[i]=p;sizes[i]=count*size;live+=sizes[i];if(live>peak)peak=live;allocations++;}return p;}
void *__wrap_malloc(size_t n){if(fail_after==0)return 0;if(fail_after>0)fail_after--;void*p=__real_malloc(n);if(p){unsigned i=0;while(i<64&&slots[i])i++;assert(i<64);slots[i]=p;sizes[i]=n;live+=n;if(live>peak)peak=live;allocations++;}return p;}
void __wrap_free(void*p){if(p){unsigned i=0;while(i<64&&slots[i]!=p)i++;assert(i<64);for(size_t j=0;j<sizes[i];j++)assert(!((unsigned char*)p)[j]);live-=sizes[i];slots[i]=0;sizes[i]=0;}__real_free(p);}
/* Disabled algorithm factories are unavailable, never insecure substitutes. */
NoiseCipherState*noise_aesgcm_new_ref(void){return 0;}
NoiseDHState*noise_curve448_new(void){return 0;}NoiseDHState*noise_newhope_new(void){return 0;}
NoiseHashState*noise_blake2s_new(void){return 0;}NoiseHashState*noise_blake2b_new(void){return 0;}NoiseHashState*noise_sha512_new(void){return 0;}
void noise_rand_bytes(void*p,size_t n){(void)p;(void)n;rng_calls++;abort();}
static unsigned entropy_attempts;
int qca_noise_entropy(uint8_t*p,size_t n){memset(p,0xa5,n);entropy_attempts++;return -1;}
#define CHECK(x) do{assert(x);checks++;}while(0)
static void create(NoiseHandshakeState**mac,NoiseHandshakeState**dell,unsigned mismatch){
 CHECK(noise_handshakestate_new_by_name(mac,"Noise_NK_25519_ChaChaPoly_SHA256",NOISE_ROLE_INITIATOR)==0);
 CHECK(noise_handshakestate_new_by_name(dell,"Noise_NK_25519_ChaChaPoly_SHA256",NOISE_ROLE_RESPONDER)==0);
 uint8_t ds[32],me[32],de[32],pub[32],prologue[128];for(unsigned j=0;j<32;j++){ds[j]=(uint8_t)(j+1);me[j]=(uint8_t)(j+41);de[j]=(uint8_t)(j+81);}
 CHECK(noise_dhstate_set_keypair_private(noise_handshakestate_get_local_keypair_dh(*dell),ds,32)==0);
 CHECK(noise_dhstate_get_public_key(noise_handshakestate_get_local_keypair_dh(*dell),pub,32)==0);if(mismatch==1)pub[0]^=1;
 CHECK(noise_dhstate_set_public_key(noise_handshakestate_get_remote_public_key_dh(*mac),pub,32)==0);
 CHECK(noise_dhstate_set_keypair_private(noise_handshakestate_get_fixed_ephemeral_dh(*mac),me,32)==0);
 CHECK(noise_dhstate_set_keypair_private(noise_handshakestate_get_fixed_ephemeral_dh(*dell),de,32)==0);
 for(unsigned j=0;j<sizeof(prologue);j++)prologue[j]=(uint8_t)j;
 CHECK(noise_handshakestate_set_prologue(*mac,prologue,sizeof(prologue))==0);if(mismatch==2)prologue[100]^=1;
 CHECK(noise_handshakestate_set_prologue(*dell,prologue,sizeof(prologue))==0);
 CHECK(noise_handshakestate_start(*mac)==0);CHECK(noise_handshakestate_start(*dell)==0);
}
static int handshake(NoiseHandshakeState*mac,NoiseHandshakeState*dell,unsigned tamper,unsigned cut){
 uint8_t msg[512],empty[1],digest1[32],digest2[32];NoiseBuffer wire,payload;
 CHECK(noise_handshakestate_get_action(mac)==NOISE_ACTION_WRITE_MESSAGE);
 noise_buffer_set_output(wire,msg,sizeof(msg));noise_buffer_set_input(payload,empty,0);
 CHECK(noise_handshakestate_write_message(mac,&wire,&payload)==0);CHECK(wire.size==48);
 if(tamper<48)msg[tamper]^=1;if(cut<48)wire.size=cut;
 noise_buffer_set_output(payload,empty,sizeof(empty));int rc=noise_handshakestate_read_message(dell,&wire,&payload);if(rc)return rc;
 CHECK(noise_handshakestate_get_action(dell)==NOISE_ACTION_WRITE_MESSAGE);
 noise_buffer_set_output(wire,msg,sizeof(msg));noise_buffer_set_input(payload,empty,0);
 CHECK(noise_handshakestate_write_message(dell,&wire,&payload)==0);CHECK(wire.size==48);
 noise_buffer_set_output(payload,empty,sizeof(empty));rc=noise_handshakestate_read_message(mac,&wire,&payload);if(rc)return rc;
 CHECK(noise_handshakestate_get_action(mac)==NOISE_ACTION_SPLIT&&noise_handshakestate_get_action(dell)==NOISE_ACTION_SPLIT);
 CHECK(noise_handshakestate_get_handshake_hash(mac,digest1,sizeof(digest1))==0);CHECK(noise_handshakestate_get_handshake_hash(dell,digest2,sizeof(digest2))==0);CHECK(!memcmp(digest1,digest2,32));return 0;
}
static void destroy(NoiseHandshakeState*mac,NoiseHandshakeState*dell){CHECK(noise_handshakestate_free(mac)==0);CHECK(noise_handshakestate_free(dell)==0);CHECK(!live);}
#include "noise_vector.h"
static void vector_test(void){
 NoiseHandshakeState*mac,*dell;NoiseCipherState*ms,*mr,*ds,*dr;uint8_t p[512],got[512];NoiseBuffer wire,payload;
 CHECK(noise_handshakestate_new_by_name(&mac,"Noise_NK_25519_ChaChaPoly_SHA256",NOISE_ROLE_INITIATOR)==0);
 CHECK(noise_handshakestate_new_by_name(&dell,"Noise_NK_25519_ChaChaPoly_SHA256",NOISE_ROLE_RESPONDER)==0);
 CHECK(noise_dhstate_set_public_key(noise_handshakestate_get_remote_public_key_dh(mac),vec_init_remote_static,32)==0);
 CHECK(noise_dhstate_set_keypair_private(noise_handshakestate_get_local_keypair_dh(dell),vec_resp_static,32)==0);
 CHECK(noise_dhstate_set_keypair_private(noise_handshakestate_get_fixed_ephemeral_dh(mac),vec_init_ephemeral,32)==0);
 CHECK(noise_dhstate_set_keypair_private(noise_handshakestate_get_fixed_ephemeral_dh(dell),vec_resp_ephemeral,32)==0);
 CHECK(noise_handshakestate_set_prologue(mac,vec_init_prologue,sizeof(vec_init_prologue))==0);
 CHECK(noise_handshakestate_set_prologue(dell,vec_init_prologue,sizeof(vec_init_prologue))==0);
 CHECK(noise_handshakestate_start(mac)==0);CHECK(noise_handshakestate_start(dell)==0);
 for(unsigned i=0;i<2;i++){
  noise_buffer_set_input(payload,(uint8_t*)vec_payload[i],vec_payload_len[i]);noise_buffer_set_output(wire,p,sizeof(p));
  CHECK(noise_handshakestate_write_message(i?dell:mac,&wire,&payload)==0);
  CHECK(wire.size==vec_ciphertext_len[i]&&!memcmp(p,vec_ciphertext[i],wire.size));
  noise_buffer_set_output(payload,got,sizeof(got));CHECK(noise_handshakestate_read_message(i?mac:dell,&wire,&payload)==0);
  CHECK(payload.size==vec_payload_len[i]&&!memcmp(got,vec_payload[i],payload.size));
 }
 CHECK(noise_handshakestate_split(mac,&ms,&mr)==0);CHECK(noise_handshakestate_split(dell,&ds,&dr)==0);
 for(unsigned i=2;i<6;i++){
  memcpy(p,vec_payload[i],vec_payload_len[i]);noise_buffer_set_inout(wire,p,vec_payload_len[i],sizeof(p));
  CHECK(noise_cipherstate_encrypt(i%2?ds:ms,&wire)==0);CHECK(wire.size==vec_ciphertext_len[i]&&!memcmp(p,vec_ciphertext[i],wire.size));
  CHECK(noise_cipherstate_decrypt(i%2?mr:dr,&wire)==0);CHECK(wire.size==vec_payload_len[i]&&!memcmp(p,vec_payload[i],wire.size));
 }
 CHECK(noise_cipherstate_free(ms)==0);CHECK(noise_cipherstate_free(mr)==0);CHECK(noise_cipherstate_free(ds)==0);CHECK(noise_cipherstate_free(dr)==0);destroy(mac,dell);
}

#ifndef QCA_COMPACT_ONLY
#include "differential.h"
#endif
int main(void){
#ifndef QCA_COMPACT_ONLY
differential();
#endif
vector_test();NoiseHandshakeState*mac,*dell;NoiseCipherState*ms,*mr,*ds,*dr;uint8_t p[512],cached[512],ad[64];NoiseBuffer b;memset(ad,0x91,sizeof(ad));
 create(&mac,&dell,0);CHECK(handshake(mac,dell,48,48)==0);CHECK(noise_handshakestate_split(mac,&ms,&mr)==0);CHECK(noise_handshakestate_split(dell,&ds,&dr)==0);
 for(unsigned n=0;n<=128;n++){for(unsigned j=0;j<n;j++)p[j]=(uint8_t)j;noise_buffer_set_inout(b,p,n,sizeof(p));CHECK(noise_cipherstate_encrypt_with_ad(ms,ad,sizeof(ad),&b)==0);CHECK(b.size==n+16);memcpy(cached,p,b.size);
  CHECK(noise_cipherstate_decrypt_with_ad(dr,ad,sizeof(ad),&b)==0);CHECK(b.size==n);for(unsigned j=0;j<n;j++)CHECK(p[j]==(uint8_t)j);
  noise_buffer_set_inout(b,cached,n+16,sizeof(cached));CHECK(noise_cipherstate_decrypt_with_ad(dr,ad,sizeof(ad),&b)!=0); /* same ciphertext cannot apply twice */
 }
 memcpy(p,"dummy-record-not-authorization",30);noise_buffer_set_inout(b,p,30,sizeof(p));CHECK(noise_cipherstate_encrypt_with_ad(ds,ad,sizeof(ad),&b)==0);CHECK(noise_cipherstate_decrypt_with_ad(mr,ad,sizeof(ad),&b)==0);CHECK(!memcmp(p,"dummy-record-not-authorization",30));
 CHECK(noise_cipherstate_free(ms)==0);CHECK(noise_cipherstate_free(mr)==0);CHECK(noise_cipherstate_free(ds)==0);CHECK(noise_cipherstate_free(dr)==0);destroy(mac,dell);
 for(unsigned kind=1;kind<=2;kind++){create(&mac,&dell,kind);CHECK(handshake(mac,dell,48,48)!=0);destroy(mac,dell);}
 for(unsigned at=0;at<48;at++){create(&mac,&dell,0);CHECK(handshake(mac,dell,at,48)!=0);destroy(mac,dell);}
 for(unsigned n=0;n<48;n++){create(&mac,&dell,0);CHECK(handshake(mac,dell,48,n)!=0);destroy(mac,dell);}
 CHECK(!rng_calls);printf("checks=%u Noise-NK-library dummy handshake/transport/replay/mismatch PASS peak_heap=%zu allocations=%u rng_calls=%u\n",checks,peak,allocations,rng_calls);return 0;}
