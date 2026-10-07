/* OFFLINE PUBLIC VECTOR TEST IMAGE ONLY. Never a physical/native candidate. */
#include "native_port.h"
#include "noise_vector.h"
#include <string.h>
#include "qemu_target.h"
#include "pool_target.h"
static QcaPoolOwner pool;static QcaPoolBoot real_boot;static unsigned observed_wipe;
static RngStatus RNG_EFIAPI observed_free(void*p){
 if(p!=pool.raw||pool.bound||!pool.wiped||pool.bytes!=33407)return 1;
 for(size_t j=0;j<pool.bytes;j++)if(((uint8_t*)p)[j])return 1;
 observed_wipe=1;emit("ACTUAL WHOLE RAW POOL ZERO BEFORE FREE OBSERVED\n");
#ifdef QCA_FREE_FAILURE
 emit("INJECTED FREEPOOL FAILURE RETAINS REAL ALLOCATION\n");return UINT64_C(0x8000000000000002);
#else
 return real_boot.release(p);
#endif
}
static int cleanup_pool(void){
 int rc=qca_pool_cleanup(&pool);
#ifdef QCA_FREE_FAILURE
 if(!rc&&observed_wipe&&pool.raw&&pool.phase==POOL_FREE_RETAINED&&pool.uncertain&&!pool.bound&&qca_native_live()==0){
  if(qca_pool_cleanup(&pool))finish(0);emit("FREE FAILURE RETAINED NO RETRY NO BOUND DANGLING POINTER PASS\n");finish(0);
 }
#endif
 return rc&&observed_wipe&&!pool.raw&&!pool.bound&&qca_native_live()==0;
}
uint64_t __attribute__((ms_abi)) efi_main(void*image,void*system){
 (void)image;emit("QEMU PUBLIC VECTOR ENTRY\n");if(!memory_probe()||!large_stack_probe())finish(0);NoiseHandshakeState*mac=0,*dell=0;QcaNoisePort*arena=0;uint8_t message[128],payload[64],ha[32],hb[32];NoiseBuffer w,p;int ok=0,rejected=0;
 QcaPoolBoot boot;if(!qca_pool_api_from_system(system,&real_boot))goto done;boot=real_boot;boot.release=observed_free;if(!qca_pool_acquire(&pool,&boot,1))goto done;
 arena=pool.port;emit("REAL BOOTSERVICES POOL ALIGNED OWNED PASS\n");
 if(qca_nk_new(&mac,NOISE_ROLE_INITIATOR)||qca_nk_new(&dell,NOISE_ROLE_RESPONDER))goto done;
 if(noise_dhstate_set_public_key(noise_handshakestate_get_remote_public_key_dh(mac),vec_init_remote_static,32)||noise_dhstate_set_keypair_private(noise_handshakestate_get_local_keypair_dh(dell),vec_resp_static,32))goto done;
 if(noise_dhstate_set_keypair_private(noise_handshakestate_get_fixed_ephemeral_dh(mac),vec_init_ephemeral,32)||noise_dhstate_set_keypair_private(noise_handshakestate_get_fixed_ephemeral_dh(dell),vec_resp_ephemeral,32))goto done;
 if(noise_handshakestate_set_prologue(mac,vec_init_prologue,sizeof(vec_init_prologue))||noise_handshakestate_set_prologue(dell,vec_init_prologue,sizeof(vec_init_prologue))||noise_handshakestate_start(mac)||noise_handshakestate_start(dell))goto done;
 for(unsigned i=0;i<2;i++){
  noise_buffer_set_output(w,message,sizeof(message));noise_buffer_set_input(p,(uint8_t*)vec_payload[i],vec_payload_len[i]);
  if(noise_handshakestate_write_message(i?dell:mac,&w,&p)||w.size!=vec_ciphertext_len[i]||memcmp(message,vec_ciphertext[i],w.size))goto done;
  noise_buffer_set_output(p,payload,sizeof(payload));
#ifdef QCA_FORCE_NEGATIVE
  if(!i){message[w.size-1]^=1;emit("DELIBERATE MAC TAG CORRUPTION\n");}
#endif
  int decode=noise_handshakestate_read_message(i?mac:dell,&w,&p);
#ifdef QCA_FORCE_NEGATIVE
  if(!i&&decode==NOISE_ERROR_MAC_FAILURE&&!p.size&&noise_handshakestate_get_action(dell)==NOISE_ACTION_FAILED){rejected=1;goto done;}
#endif
  if(decode||p.size!=vec_payload_len[i]||memcmp(payload,vec_payload[i],p.size))goto done;
 }
 if(noise_handshakestate_get_handshake_hash(mac,ha,32)||noise_handshakestate_get_handshake_hash(dell,hb,32)||memcmp(ha,hb,32))goto done;
 ok=1;
done:
 if(mac)noise_handshakestate_free(mac);if(dell)noise_handshakestate_free(dell);mac=0;dell=0;
 if(!pool.port||qca_native_live()||pool.port->quarantined){if(pool.raw&&!pool.uncertain)(void)qca_pool_cleanup(&pool);finish(0);}
 for(unsigned j=0;j<pool.port->used;j++)for(unsigned k=0;k<512;k++)if(pool.port->bytes[j][k])finish(0);
 #ifdef QCA_FORCE_NEGATIVE
 if(!ok&&rejected){if(!cleanup_pool())finish(0);emit("REAL POOL DETACH WIPE FREE PASS\n");emit("MAC FAILURE ZERO PAYLOAD FAILED STATE AND ARENA WIPE PASS\n");finish(0);}
#endif
 if(!ok)finish(0);emit("NK TWO PUBLISHED MESSAGES HASH AND ARENA WIPE PASS\n");
 if(!mock_rng_check(arena))finish(0);emit("EXPLICIT MOCK RNG CALLBACK SUCCESS FAILURE WIPE PASS\n");
if(!cleanup_pool())finish(0);emit("REAL POOL DETACH WIPE FREE PASS\n");
 emit("QEMU RUNTIME EFI COMPLETE PASS\n");finish(1);
 return 0;
}
