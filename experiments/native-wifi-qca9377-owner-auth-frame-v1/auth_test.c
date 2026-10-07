#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "auth_frame.h"
#include "canonical_fixture.h"
#include "internal.h"
#include "monocypher-ed25519.h"
static unsigned checks;
static const uint8_t pk[32]={0xd7,0x5a,0x98,0x01,0x82,0xb1,0x0a,0xb7,0xd5,0x4b,0xfe,0xd3,0xc9,0x64,0x07,0x3a,0x0e,0xe1,0x72,0xf3,0xda,0xa6,0x23,0x25,0xaf,0x02,0x1a,0x68,0xf7,0x07,0x51,0x1a};
static const uint8_t kat[64]={0xe5,0x56,0x43,0x00,0xc3,0x60,0xac,0x72,0x90,0x86,0xe2,0xcc,0x80,0x6e,0x82,0x8a,0x84,0x87,0x7f,0x1e,0xb8,0xe5,0xd9,0x74,0xd8,0x73,0xe0,0x65,0x22,0x49,0x01,0x55,0x5f,0xb8,0x82,0x15,0x90,0xa3,0x3b,0xac,0xc6,0x1e,0x39,0x70,0x1c,0xf9,0xb4,0x6b,0xd2,0x5b,0xf5,0xf0,0x59,0x5b,0xbe,0x24,0x65,0x51,0x41,0x43,0x8e,0x7a,0x10,0x0b};
static OaContext context(void){OaContext c={.epoch=43};memset(c.handshake,1,32);memset(c.prologue,2,32);memset(c.target,3,32);memset(c.native,4,32);memcpy(c.owner,pk,32);return c;}
static void pair(NoiseCipherState **s,NoiseCipherState **r){
 uint8_t key[32];memset(key,0x35,32);assert(!noise_cipherstate_new_by_id(s,NOISE_CIPHER_CHACHAPOLY));assert(!noise_cipherstate_new_by_id(r,NOISE_CIPHER_CHACHAPOLY));assert(!noise_cipherstate_init_key(*s,key,32));assert(!noise_cipherstate_init_key(*r,key,32));
}
static void done(NoiseCipherState*s,NoiseCipherState*r){assert(!noise_cipherstate_free(s));assert(!noise_cipherstate_free(r));}
static void put32(uint8_t*p,uint32_t v){for(unsigned i=0;i<4;i++){p[i]=(uint8_t)v;v>>=8;}}
static void encode(NoiseCipherState*s,unsigned type,const uint8_t*p,uint8_t*wire){
 memcpy(wire,"RNOISE01",8);put32(wire+8,1);put32(wire+12,type);put32(wire+16,type);put32(wire+20,280);memcpy(wire+24,p,264);NoiseBuffer b;noise_buffer_set_inout(b,wire+24,264,280);assert(!noise_cipherstate_encrypt_with_ad(s,wire,24,&b)&&b.size==280);
}
int main(void){
 /* Actual ordinary Ed25519 primitive KAT only, NOT a signed AUTH fixture. */
 assert(!crypto_ed25519_check(kat,pk,NULL,0));checks++;
 OaContext c=context();uint8_t signed_frame[OA_SIGNED],wire[OA_WIRE],sig[64]={0},oldwire[OA_WIRE];assert(oa_signed_message(&c,signed_frame));assert(!memcmp(signed_frame,canonical_fixture,OA_SIGNED));checks++;
 assert(crypto_ed25519_check(kat,pk,signed_frame,OA_SIGNED));checks++;
 for(unsigned i=0;i<64;i++){
  NoiseCipherState*s,*r;pair(&s,&r);OaSession q={0};assert(oa_init(&q,&c,1,s,r));memset(wire,0x55,sizeof wire);memcpy(oldwire,wire,sizeof wire);sig[i]=1;
  assert(!oa_mac_credentials_allowed(&q)&&!oa_mac_auth(&q,sig,wire));assert(!memcmp(wire,oldwire,sizeof wire)&&s->n==0&&!oa_mac_credentials_allowed(&q));sig[i]=0;checks++;done(s,r);
 }
 /* Authentic Noise ciphertext is insufficient without a real owner AUTH. */
 for(unsigned i=0;i<OA_PLAIN;i++){
  NoiseCipherState *s,*r;pair(&s,&r);OaSession q={0};assert(oa_init(&q,&c,2,r,s));uint8_t p[OA_PLAIN]={0};memcpy(p,signed_frame,OA_SIGNED);p[i]^=1;encode(s,1,p,wire);
  assert(!oa_dell_auth(&q,wire,sizeof wire));assert(q.phase==4&&!oa_dell_ack(&q,oldwire)&&!oa_mac_credentials_allowed(&q));checks++;done(s,r);
 }
 for(unsigned n=1;n<OA_WIRE+17;n++){
  NoiseCipherState *s,*r;pair(&s,&r);OaSession q={0};assert(oa_init(&q,&c,2,r,s));uint8_t p[OA_PLAIN]={0};memcpy(p,signed_frame,OA_SIGNED);encode(s,1,p,wire);uint8_t padded[OA_WIRE+16]={0};memcpy(padded,wire,OA_WIRE);
  assert(!oa_dell_auth(&q,padded,n));assert(!oa_mac_credentials_allowed(&q));checks++;done(s,r);
 }
 for(unsigned i=0;i<OA_WIRE;i++){
  NoiseCipherState *s,*r;pair(&s,&r);OaSession q={0};assert(oa_init(&q,&c,2,r,s));uint8_t p[OA_PLAIN]={0};memcpy(p,signed_frame,OA_SIGNED);encode(s,1,p,wire);wire[i]^=1;
  assert(!oa_dell_auth(&q,wire,sizeof wire));assert(q.phase==4&&!oa_mac_credentials_allowed(&q));checks++;done(s,r);
 }
 for(unsigned k=0;k<8;k++){
  NoiseCipherState*s,*r;pair(&s,&r);OaContext x=c;OaSession q={0};
  if(k==0)x.epoch=0;if(k==1)memset(x.handshake,0,32);if(k==2)memset(x.prologue,0,32);if(k==3)memset(x.target,0,32);if(k==4)memset(x.native,0,32);if(k==5)memset(x.owner,0,32);if(k==6)noise_cipherstate_set_nonce(s,1);
  assert(!oa_init(&q,&x,k==7?3:1,s,r));assert(!oa_mac_credentials_allowed(&q));checks++;done(s,r);
 }
 /* Session/output and full backend allocation aliases are rejected before RNG
  * or cipher invocation; no hidden backend key overwrite. No RNG is linked. */
 for(unsigned k=0;k<5;k++){
  NoiseCipherState*s,*r;pair(&s,&r);OaSession q={0};assert(oa_init(&q,&c,1,s,r));OaSession prior=q;uint8_t*o=NULL;
  if(k==0)o=(uint8_t*)&q;if(k==1)o=(uint8_t*)s+sizeof *s;if(k==2)o=(uint8_t*)r+sizeof *r;if(k==3)o=(uint8_t*)sig;if(k==4)o=(uint8_t*)(UINTPTR_MAX-8);
  assert(!oa_mac_auth(&q,sig,o)&&!memcmp(&q,&prior,sizeof q)&&s->n==0&&r->n==0);checks++;done(s,r);
 }
 /* Explicit SYNTHETIC pre-authenticated phase fixtures: this tests actual
  * encrypted ACK correlation/gating, NOT successful Ed25519 AUTH or Split. */
 for(unsigned variant=0;variant<1+OA_WIRE+OA_PLAIN;variant++){
  NoiseCipherState*ds,*mr;pair(&ds,&mr);NoiseCipherState*ms,*dr;pair(&ms,&dr);
  OaSession mac={0},dell={0};assert(oa_init(&mac,&c,1,ms,mr));assert(oa_init(&dell,&c,2,ds,dr));
  mac.phase=dell.phase=2;memset(mac.auth_hash,0x26,64);memcpy(dell.auth_hash,mac.auth_hash,64);
  assert(!oa_mac_credentials_allowed(&mac));
  if(variant<=OA_WIRE){assert(oa_dell_ack(&dell,wire));if(variant)wire[variant-1]^=1;}
  else {uint8_t p[OA_PLAIN];assert(oa_signed_message(&c,p));put32(p+12,2);put32(p+16,2);memcpy(p+OA_SIGNED,mac.auth_hash,64);p[variant-1-OA_WIRE]^=1;encode(ds,2,p,wire);}
  /* A synthetic initiator AUTH already used sendnonce0: no actual signature
   * or AUTH bypass exists in production code. This adjustment is fixture-only. */
  assert(!noise_cipherstate_set_nonce(ms,1));
  assert(oa_mac_ack(&mac,wire,sizeof wire)==(!variant));assert(oa_mac_credentials_allowed(&mac)==(!variant));
  if(!variant){assert(!oa_mac_ack(&mac,wire,sizeof wire));assert(oa_mac_credentials_allowed(&mac));assert(!oa_dell_ack(&dell,oldwire));}
  else assert(mac.phase==4);checks++;done(ds,mr);done(ms,dr);
 }
 /* ACK is rejected before AUTH even if its AEAD is perfectly valid. */
 {NoiseCipherState*send,*recv;pair(&send,&recv);OaSession q={0};assert(oa_init(&q,&c,1,send,recv));memset(wire,0,sizeof wire);assert(!oa_mac_ack(&q,wire,sizeof wire)&&!oa_mac_credentials_allowed(&q));OaSession prior=q;assert(!oa_init(&q,&c,1,send,recv)&&!memcmp(&q,&prior,sizeof q));checks++;done(send,recv);}
 printf("PASS %u OWNER AUTH actual crypto negative/KAT cases; NO SIGNED AUTH POSITIVE FIXTURE; only SYNTHETIC pre-auth ACK phase tested; NO credentials\n",checks);return 0;
}
