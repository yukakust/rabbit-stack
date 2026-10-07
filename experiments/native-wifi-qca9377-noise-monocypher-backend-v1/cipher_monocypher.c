/* Noise-C-compatible ChaChaPoly provider; no handshake/KDF changes. */
#include "internal.h"
#include "monocypher.h"
#include <string.h>
typedef struct {struct NoiseCipherState_s parent;uint8_t key[32];} QcaMonoCipher;
static void init(NoiseCipherState*s,const uint8_t*k){memcpy(((QcaMonoCipher*)s)->key,k,32);}
static void setup(crypto_aead_ctx*ctx,const QcaMonoCipher*s){
 uint8_t nonce[12]={0};for(unsigned j=0;j<8;j++)nonce[4+j]=(uint8_t)(s->parent.n>>(8*j));
 /* Noise ChaChaPoly nonce: 32 zero bits || LE64(n), IETF, counter0/1.
  * Fresh context each message. Monocypher's streaming rekey is discarded. */
 crypto_aead_init_ietf(ctx,s->key,nonce);crypto_wipe(nonce,sizeof(nonce));
}
static int encrypt(NoiseCipherState*s,const uint8_t*ad,size_t an,uint8_t*p,size_t n){
 crypto_aead_ctx ctx;setup(&ctx,(QcaMonoCipher*)s);
 crypto_aead_write(&ctx,p,p+n,ad,an,p,n);crypto_wipe(&ctx,sizeof(ctx));return NOISE_ERROR_NONE;
}
static int decrypt(NoiseCipherState*s,const uint8_t*ad,size_t an,uint8_t*p,size_t n){
 crypto_aead_ctx ctx;setup(&ctx,(QcaMonoCipher*)s);
 int rc=crypto_aead_read(&ctx,p,p+n,ad,an,p,n);crypto_wipe(&ctx,sizeof(ctx));
 return rc?NOISE_ERROR_MAC_FAILURE:NOISE_ERROR_NONE;
}
NoiseCipherState*noise_chachapoly_new(void){
 QcaMonoCipher*s=noise_new(QcaMonoCipher);if(!s)return 0;
 s->parent.cipher_id=NOISE_CIPHER_CHACHAPOLY;s->parent.key_len=32;s->parent.mac_len=16;
 s->parent.create=noise_chachapoly_new;s->parent.init_key=init;s->parent.encrypt=encrypt;s->parent.decrypt=decrypt;return &s->parent;
}
