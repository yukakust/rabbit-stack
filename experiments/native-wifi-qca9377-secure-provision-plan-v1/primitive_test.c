/* PUBLIC deterministic dummy values only. No protocol, RNG, signing or IO. */
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "monocypher.h"
#include "monocypher-ed25519.h"
#include "hkdf-oracle.h"
static unsigned checks;
static uint8_t key[32],nonce[24],ad[160],plain[128],cipher[128],mac[16],out[128];
static void rejected(unsigned n){
 memset(out,0x5a,sizeof out);uint8_t old[128];memcpy(old,out,sizeof old);
 assert(crypto_aead_unlock(out,mac,key,nonce,ad,sizeof ad,cipher,n)==-1);
 assert(!memcmp(out,old,sizeof out));++checks;
}
int main(void){
 for(unsigned i=0;i<32;i++)key[i]=(uint8_t)(i+1);
 for(unsigned i=0;i<24;i++)nonce[i]=(uint8_t)(i+2);
 for(unsigned i=0;i<160;i++)ad[i]=(uint8_t)(i+3);
 for(unsigned i=0;i<128;i++)plain[i]=(uint8_t)(i+4);
 /* Each case is an independent disposable dummy context, not nonce-reuse
  * guidance for a live session. A real live key/nonce pair is single-use. */
 for(unsigned n=0;n<=128;n++){
  nonce[23]=(uint8_t)n;
  crypto_aead_lock(cipher,mac,key,nonce,ad,sizeof ad,plain,n);
  assert(!crypto_aead_unlock(out,mac,key,nonce,ad,sizeof ad,cipher,n));
  assert(!memcmp(out,plain,n));++checks;
  for(unsigned i=0;i<160;i++){ad[i]^=1;rejected(n);ad[i]^=1;}
  for(unsigned i=0;i<24;i++){nonce[i]^=1;rejected(n);nonce[i]^=1;}
  for(unsigned i=0;i<32;i++){key[i]^=1;rejected(n);key[i]^=1;}
  for(unsigned i=0;i<16;i++){mac[i]^=1;rejected(n);mac[i]^=1;}
  for(unsigned i=0;i<n;i++){cipher[i]^=1;rejected(n);cipher[i]^=1;}
 }
 uint8_t a[32],b[32],ap[32],bp[32],ab[32],ba[32],zero[32]={0};
 for(unsigned i=0;i<32;i++){a[i]=(uint8_t)(i+7);b[i]=(uint8_t)(i+37);}
 crypto_x25519_public_key(ap,a);crypto_x25519_public_key(bp,b);
 crypto_x25519(ab,a,bp);crypto_x25519(ba,b,ap);
 assert(!crypto_verify32(ab,ba)&&crypto_verify32(ab,zero));++checks;
 crypto_x25519(ab,a,zero);assert(!crypto_verify32(ab,zero));++checks;
 uint8_t salt[16],okm[64],changed[64];for(unsigned i=0;i<16;i++)salt[i]=(uint8_t)i;
 crypto_sha512_hkdf(okm,64,key,32,salt,16,ad,160);
 assert(!memcmp(okm,hkdf_expected,64));++checks;
 for(unsigned i=0;i<160;i++){ad[i]^=1;crypto_sha512_hkdf(changed,64,key,32,salt,16,ad,160);assert(memcmp(okm,changed,64));ad[i]^=1;++checks;}
 crypto_wipe(okm,sizeof okm);crypto_wipe(changed,sizeof changed);
 /* Low-order result MUST be rejected by the eventual protocol caller. The
  * primitive returns raw secret and does not authenticate either endpoint. */
 crypto_wipe(a,sizeof a);crypto_wipe(b,sizeof b);crypto_wipe(ab,sizeof ab);crypto_wipe(ba,sizeof ba);
 crypto_wipe(key,sizeof key);crypto_wipe(out,sizeof out);
 printf("PASS %u Monocypher dummy AEAD-binding/X25519 checks; NO HANDSHAKE/AUTH/RNG PROOF\n",checks);
 return 0;
}
