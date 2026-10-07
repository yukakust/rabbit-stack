/* HOST ONLY. Published public Cacophony dummy fixture keys, never device keys. */
#include "auth_frame.h"
#include "noise_vector.h"
#include <assert.h>
#include <string.h>
typedef struct {NoiseHandshakeState *mac,*dell;NoiseCipherState *ms,*mr,*ds,*dr;OaContext context;} Fx;
static void fx_new(Fx*f){
 memset(f,0,sizeof *f);
 assert(!noise_handshakestate_new_by_name(&f->mac,"Noise_NK_25519_ChaChaPoly_SHA256",NOISE_ROLE_INITIATOR));
 assert(!noise_handshakestate_new_by_name(&f->dell,"Noise_NK_25519_ChaChaPoly_SHA256",NOISE_ROLE_RESPONDER));
 assert(!noise_dhstate_set_public_key(noise_handshakestate_get_remote_public_key_dh(f->mac),vec_init_remote_static,32));
 assert(!noise_dhstate_set_keypair_private(noise_handshakestate_get_local_keypair_dh(f->dell),vec_resp_static,32));
 assert(!noise_dhstate_set_keypair_private(noise_handshakestate_get_fixed_ephemeral_dh(f->mac),vec_init_ephemeral,32));
 assert(!noise_dhstate_set_keypair_private(noise_handshakestate_get_fixed_ephemeral_dh(f->dell),vec_resp_ephemeral,32));
 assert(!noise_handshakestate_set_prologue(f->mac,vec_init_prologue,sizeof vec_init_prologue));
 assert(!noise_handshakestate_set_prologue(f->dell,vec_init_prologue,sizeof vec_init_prologue));
 assert(!noise_handshakestate_start(f->mac)&&!noise_handshakestate_start(f->dell));
 uint8_t message[512],plain[512];NoiseBuffer b,p;
 for(unsigned i=0;i<2;i++){
  noise_buffer_set_output(b,message,sizeof message);noise_buffer_set_input(p,(uint8_t*)vec_payload[i],vec_payload_len[i]);
  assert(!noise_handshakestate_write_message(i?f->dell:f->mac,&b,&p));
  assert(b.size==vec_ciphertext_len[i]&&!memcmp(message,vec_ciphertext[i],b.size));
  noise_buffer_set_output(p,plain,sizeof plain);assert(!noise_handshakestate_read_message(i?f->mac:f->dell,&b,&p));
  assert(p.size==vec_payload_len[i]&&!memcmp(plain,vec_payload[i],p.size));
 }
 uint8_t other[32];assert(!noise_handshakestate_get_handshake_hash(f->mac,f->context.handshake,32));
 assert(!noise_handshakestate_get_handshake_hash(f->dell,other,32)&&!memcmp(other,f->context.handshake,32));
 NoiseHashState*h=NULL;assert(!noise_hashstate_new_by_id(&h,NOISE_HASH_SHA256));
 assert(!noise_hashstate_hash_one(h,vec_init_prologue,sizeof vec_init_prologue,f->context.prologue,32));assert(!noise_hashstate_free(h));
 assert(!noise_handshakestate_split(f->mac,&f->ms,&f->mr));assert(!noise_handshakestate_split(f->dell,&f->ds,&f->dr));
 f->context.epoch=43;memset(f->context.target,3,32);memset(f->context.native,4,32);
}
static void fx_free(Fx*f){
 assert(!noise_cipherstate_free(f->ms)&&!noise_cipherstate_free(f->mr)&&!noise_cipherstate_free(f->ds)&&!noise_cipherstate_free(f->dr));
 assert(!noise_handshakestate_free(f->mac)&&!noise_handshakestate_free(f->dell));memset(f,0,sizeof *f);
}
static void fx_transport_vectors(Fx*f){
 uint8_t p[512];NoiseBuffer b;
 for(unsigned i=2;i<6;i++){
  memcpy(p,vec_payload[i],vec_payload_len[i]);noise_buffer_set_inout(b,p,vec_payload_len[i],sizeof p);
  assert(!noise_cipherstate_encrypt(i%2?f->ds:f->ms,&b));assert(b.size==vec_ciphertext_len[i]&&!memcmp(p,vec_ciphertext[i],b.size));
  assert(!noise_cipherstate_decrypt(i%2?f->mr:f->dr,&b)&&b.size==vec_payload_len[i]&&!memcmp(p,vec_payload[i],b.size));
 }
}
