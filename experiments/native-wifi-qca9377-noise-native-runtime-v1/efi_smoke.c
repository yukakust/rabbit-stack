/* OFFLINE PUBLIC VECTOR TEST IMAGE ONLY. Never a physical/native candidate. */
#include "native_port.h"
#include "noise_vector.h"
#include <string.h>
static QcaNoisePort arena;
uint64_t __attribute__((ms_abi)) efi_main(void*image,void*system){
 (void)image;(void)system;NoiseHandshakeState*mac=0,*dell=0;uint8_t message[128],payload[64],ha[32],hb[32];NoiseBuffer w,p;int ok=0;
 if(!qca_native_reset(&arena,1)||!qca_native_bind(&arena))goto done;
 if(qca_nk_new(&mac,NOISE_ROLE_INITIATOR)||qca_nk_new(&dell,NOISE_ROLE_RESPONDER))goto done;
 if(noise_dhstate_set_public_key(noise_handshakestate_get_remote_public_key_dh(mac),vec_init_remote_static,32)||noise_dhstate_set_keypair_private(noise_handshakestate_get_local_keypair_dh(dell),vec_resp_static,32))goto done;
 if(noise_dhstate_set_keypair_private(noise_handshakestate_get_fixed_ephemeral_dh(mac),vec_init_ephemeral,32)||noise_dhstate_set_keypair_private(noise_handshakestate_get_fixed_ephemeral_dh(dell),vec_resp_ephemeral,32))goto done;
 if(noise_handshakestate_set_prologue(mac,vec_init_prologue,sizeof(vec_init_prologue))||noise_handshakestate_set_prologue(dell,vec_init_prologue,sizeof(vec_init_prologue))||noise_handshakestate_start(mac)||noise_handshakestate_start(dell))goto done;
 for(unsigned i=0;i<2;i++){
  noise_buffer_set_output(w,message,sizeof(message));noise_buffer_set_input(p,(uint8_t*)vec_payload[i],vec_payload_len[i]);
  if(noise_handshakestate_write_message(i?dell:mac,&w,&p)||w.size!=vec_ciphertext_len[i]||memcmp(message,vec_ciphertext[i],w.size))goto done;
  noise_buffer_set_output(p,payload,sizeof(payload));if(noise_handshakestate_read_message(i?mac:dell,&w,&p)||p.size!=vec_payload_len[i]||memcmp(payload,vec_payload[i],p.size))goto done;
 }
 if(noise_handshakestate_get_handshake_hash(mac,ha,32)||noise_handshakestate_get_handshake_hash(dell,hb,32)||memcmp(ha,hb,32))goto done;
 ok=1;
done:
 if(mac)noise_handshakestate_free(mac);if(dell)noise_handshakestate_free(dell);
 return ok&&!qca_native_live()&&!arena.quarantined?0:UINT64_C(0x8000000000000007);
}
