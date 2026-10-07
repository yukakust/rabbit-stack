/* Reference factories are compiled with symbol renames; upstream bodies unchanged. */
#include "backend_entropy.h"
#include "internal.h"
NoiseCipherState*qca_reference_chachapoly_new(void);
NoiseDHState*qca_reference_curve25519_new(void);
static void differential(void){
 uint8_t key[32],ad[65],a[528],b[528],bad[528],pub[32],x[32],y[32];
 for(unsigned j=0;j<32;j++)key[j]=(uint8_t)(j+9);for(unsigned j=0;j<65;j++)ad[j]=(uint8_t)j;
 const uint64_t nonces[]={0,1,0xffffffffULL,0x100000000ULL,0x0102030405060708ULL,UINT64_MAX-1};
 for(unsigned ni=0;ni<sizeof(nonces)/sizeof(nonces[0]);ni++)for(unsigned an=0;an<=65;an++)for(unsigned n=0;n<=512;n+=16){
  NoiseCipherState*mono=noise_chachapoly_new(),*ref=qca_reference_chachapoly_new();CHECK(mono&&ref);
  CHECK(!noise_cipherstate_init_key(mono,key,32));CHECK(!noise_cipherstate_init_key(ref,key,32));
  CHECK(!noise_cipherstate_set_nonce(mono,nonces[ni]));CHECK(!noise_cipherstate_set_nonce(ref,nonces[ni]));
  for(unsigned j=0;j<n;j++)a[j]=b[j]=(uint8_t)(j^n);NoiseBuffer ab,bb;
  noise_buffer_set_inout(ab,a,n,sizeof(a));noise_buffer_set_inout(bb,b,n,sizeof(b));
  CHECK(!noise_cipherstate_encrypt_with_ad(mono,ad,an,&ab));CHECK(!noise_cipherstate_encrypt_with_ad(ref,ad,an,&bb));
  CHECK(ab.size==n+16&&bb.size==ab.size&&!memcmp(a,b,ab.size));memcpy(bad,a,ab.size);bad[n]^=1;
  CHECK(noise_cipherstate_set_nonce(mono,nonces[ni])==NOISE_ERROR_INVALID_NONCE);
  /* Fresh receive state for the reference comparison, test-only reinitialization. */
  CHECK(!noise_cipherstate_init_key(mono,key,32));CHECK(!noise_cipherstate_init_key(ref,key,32));
  CHECK(!noise_cipherstate_set_nonce(mono,nonces[ni]));CHECK(!noise_cipherstate_set_nonce(ref,nonces[ni]));
  NoiseBuffer corrupted;noise_buffer_set_inout(corrupted,bad,n+16,sizeof(bad));
  CHECK(noise_cipherstate_decrypt_with_ad(mono,ad,an,&corrupted)==NOISE_ERROR_MAC_FAILURE);
  CHECK(corrupted.size==n+16&&bad[n]==(uint8_t)(a[n]^1));
  CHECK(mono->n==nonces[ni]); /* no nonce advance on MAC failure */
  CHECK(!noise_cipherstate_decrypt_with_ad(mono,ad,an,&ab));CHECK(!noise_cipherstate_decrypt_with_ad(ref,ad,an,&bb));
  CHECK(ab.size==n&&bb.size==n&&!memcmp(a,b,n));for(unsigned j=0;j<n;j++)CHECK(a[j]==(uint8_t)(j^n));
  CHECK(!noise_cipherstate_set_nonce(mono,UINT64_MAX));noise_buffer_set_inout(ab,a,0,sizeof(a));
  CHECK(noise_cipherstate_encrypt(mono,&ab)==NOISE_ERROR_INVALID_NONCE);
  CHECK(!noise_cipherstate_free(mono));CHECK(!noise_cipherstate_free(ref));CHECK(!live);
 }
 NoiseDHState*mono=noise_curve25519_new(),*ref=qca_reference_curve25519_new(),*remote=noise_curve25519_new();CHECK(mono&&ref&&remote);
 CHECK(noise_dhstate_generate_keypair(mono)==NOISE_ERROR_SYSTEM);CHECK(entropy_attempts==1);
 for(unsigned j=0;j<32;j++)CHECK(!mono->private_key[j]&&!mono->public_key[j]);
 for(unsigned k=0;k<256;k++){
  for(unsigned j=0;j<32;j++)key[j]=(uint8_t)(k+j*7);
  CHECK(!noise_dhstate_set_keypair_private(mono,key,32));CHECK(!noise_dhstate_set_keypair_private(ref,key,32));
  CHECK(!noise_dhstate_get_public_key(mono,x,32));CHECK(!noise_dhstate_get_public_key(ref,y,32));CHECK(!memcmp(x,y,32));
  for(unsigned j=0;j<32;j++)pub[j]=(uint8_t)(k+j*13);
  CHECK(!noise_dhstate_set_public_key(remote,pub,32));CHECK(!noise_dhstate_calculate(mono,remote,x,32));CHECK(!noise_dhstate_calculate(ref,remote,y,32));CHECK(!memcmp(x,y,32));
 }
 /* Published X25519 low-order 0,1,p-1,p,p+1 encodings; accepted zero DH per Noise. */
 for(unsigned k=0;k<5;k++){
  memset(pub,0,32);if(k==1)pub[0]=1;if(k>=2){memset(pub,255,32);pub[31]=127;pub[0]=(uint8_t)(236+k-2);}
  CHECK(!noise_dhstate_set_public_key(remote,pub,32));CHECK(!noise_dhstate_calculate(mono,remote,x,32));CHECK(!noise_dhstate_calculate(ref,remote,y,32));CHECK(!memcmp(x,y,32));
  for(unsigned j=0;j<32;j++)CHECK(!x[j]);
 }
 CHECK(!noise_dhstate_set_keypair_private(mono,key,32));memcpy(pub,mono->public_key,32);pub[0]^=1;
 CHECK(noise_dhstate_set_keypair(mono,key,32,pub,32)==NOISE_ERROR_INVALID_PUBLIC_KEY);
 CHECK(noise_dhstate_calculate(mono,remote,x,31)==NOISE_ERROR_INVALID_LENGTH);
 CHECK(!noise_dhstate_free(mono));CHECK(!noise_dhstate_free(ref));CHECK(!noise_dhstate_free(remote));CHECK(!live);
 NoiseHandshakeState*h=0;NoiseBuffer w,payload;uint8_t wire[64],empty[1];
 CHECK(!noise_handshakestate_new_by_name(&h,"Noise_NK_25519_ChaChaPoly_SHA256",NOISE_ROLE_INITIATOR));
 CHECK(!noise_dhstate_set_public_key(noise_handshakestate_get_remote_public_key_dh(h),pub,32));
 CHECK(!noise_handshakestate_start(h));noise_buffer_set_output(w,wire,sizeof(wire));noise_buffer_set_input(payload,empty,0);
 CHECK(noise_handshakestate_write_message(h,&w,&payload)==NOISE_ERROR_SYSTEM);
 CHECK(!w.size&&noise_handshakestate_get_action(h)==NOISE_ACTION_FAILED);CHECK(entropy_attempts==2);
 CHECK(!noise_handshakestate_free(h));CHECK(!live);
 unsigned dangling_errors=0;
 for(int at=0;at<20;at++){
  fail_after=at;h=0;int rc=noise_handshakestate_new_by_name(&h,"Noise_NK_25519_ChaChaPoly_SHA256",NOISE_ROLE_RESPONDER);fail_after=-1;
  CHECK(rc==NOISE_ERROR_NO_MEMORY||rc==NOISE_ERROR_NONE);
  if(!rc)CHECK(!noise_handshakestate_free(h));else {if(h)dangling_errors++;h=0;} /* library error output is never an owned object */
  CHECK(!live);
 }
 CHECK(dangling_errors>0);printf("dangling_error_outputs=%u constructor failures never reused or freed PASS\n",dangling_errors);

}
