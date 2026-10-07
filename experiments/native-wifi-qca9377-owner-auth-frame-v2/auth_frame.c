#include "auth_frame.h"
#include "internal.h"
#include "monocypher-ed25519.h"
static int range(const void*p,size_t n){return p&&n&&n<=UINTPTR_MAX-(uintptr_t)p;}
static int apart(const void*a,size_t n,const void*b,size_t m){return range(a,n)&&range(b,m)&&((uintptr_t)a+n<=(uintptr_t)b||(uintptr_t)b+m<=(uintptr_t)a);}
static void copy(void*d,const void*s,size_t n){uint8_t*a=d;const uint8_t*b=s;while(n--)*a++=*b++;}
static void wipe(void*p,size_t n){volatile uint8_t*b=p;while(n--)*b++=0;}
static int same(const void*a,const void*b,size_t n){const uint8_t*x=a,*y=b;unsigned diff=0;while(n--)diff|=*x++^*y++;return !diff;}
static void put32(uint8_t*p,uint32_t n){for(unsigned i=0;i<4;i++){p[i]=(uint8_t)n;n>>=8;}}
static void put64(uint8_t*p,uint64_t n){for(unsigned i=0;i<8;i++){p[i]=(uint8_t)n;n>>=8;}}
static int nonzero(const uint8_t*p,size_t n){unsigned a=0;while(n--)a|=*p++;return !!a;}
static int context_ok(const OaContext*c){return range(c,sizeof *c)&&c->epoch&&nonzero(c->handshake,32)&&nonzero(c->prologue,32)&&nonzero(c->target,32)&&nonzero(c->native,32)&&nonzero(c->owner,32);}
static void prefix(const OaContext*c,unsigned type,uint8_t*p){
 copy(p,"ROWN0001",8);put32(p+8,1);put32(p+12,type);put32(p+16,type);put32(p+20,0);put64(p+24,0);put64(p+32,c->epoch);
 copy(p+40,c->handshake,32);copy(p+72,c->prologue,32);copy(p+104,c->target,32);copy(p+136,c->native,32);copy(p+168,c->owner,32);
}
static void header(unsigned type,uint8_t*p){copy(p,"RNOISE01",8);put32(p+8,1);put32(p+12,type);put32(p+16,type);put32(p+20,280);}
/* The pinned public API has no nonce getter; this exact pinned internal ABI is
 * deliberately checked, not guessed or changed. It does not prove Split origin. */
static size_t cipher_span(const NoiseCipherState*c){return range(c,sizeof *c)&&c->size>=sizeof *c&&c->size<=512&&range(c,c->size)?c->size:0;}
static int cipher_ok(const NoiseCipherState*c,uint64_t nonce){return cipher_span(c)&&c->cipher_id==NOISE_CIPHER_CHACHAPOLY&&c->has_key&&c->key_len==32&&c->mac_len==16&&c->n==nonce;}
int oa_init(OaSession*s,const OaContext*c,unsigned role,NoiseCipherState*send,NoiseCipherState*receive){
 if(!apart(s,sizeof *s,c,sizeof *c)||s->phase||s->send||s->receive||!context_ok(c)||!apart(s,sizeof *s,send,cipher_span(send))||!apart(s,sizeof *s,receive,cipher_span(receive))||!apart(send,cipher_span(send),receive,cipher_span(receive))||!apart(c,sizeof *c,send,cipher_span(send))||!apart(c,sizeof *c,receive,cipher_span(receive))||!cipher_ok(send,0)||!cipher_ok(receive,0)||(role!=1&&role!=2))return 0;
 OaSession t={0};t.context=*c;t.role=role;t.phase=1;t.send=send;t.receive=receive;copy(s,&t,sizeof t);return 1;
}
int oa_signed_message(const OaContext*c,uint8_t*out){if(!apart(c,sizeof *c,out,OA_SIGNED)||!context_ok(c))return 0;prefix(c,1,out);return 1;}
static int buffers(const OaSession*s,const void*p,size_t n){return apart(s,sizeof *s,p,n)&&apart(s->send,cipher_span(s->send),p,n)&&apart(s->receive,cipher_span(s->receive),p,n);}
static int encrypt(OaSession*s,unsigned type,uint8_t*p,uint8_t*out){
 uint8_t wire[OA_WIRE];header(type,wire);copy(wire+24,p,OA_PLAIN);NoiseBuffer b;noise_buffer_set_inout(b,wire+24,OA_PLAIN,280);
 int ok=cipher_ok(s->send,0)&&noise_cipherstate_encrypt_with_ad(s->send,wire,24,&b)==0&&b.size==280;
 if(ok)copy(out,wire,OA_WIRE);else s->phase=4;wipe(wire,sizeof wire);return ok;
}
int oa_mac_auth(OaSession*s,const uint8_t*signature,uint8_t*out){
 if(!range(s,sizeof *s)||!buffers(s,signature,64)||!buffers(s,out,OA_WIRE)||!apart(signature,64,out,OA_WIRE)||s->role!=1||s->phase!=1)return 0;
 uint8_t p[OA_PLAIN];prefix(&s->context,1,p);copy(p+OA_SIGNED,signature,64);
 if(crypto_ed25519_check(signature,s->context.owner,p,OA_SIGNED)){wipe(p,sizeof p);s->phase=4;return 0;}
 int ok=encrypt(s,1,p,out);if(ok){crypto_sha512(s->auth_hash,p,sizeof p);s->phase=2;}wipe(p,sizeof p);return ok;
}
static int decrypt(OaSession*s,unsigned type,const uint8_t*wire,size_t n,uint8_t*p){
 uint8_t h[24],scratch[280];header(type,h);
 if(n!=OA_WIRE||!same(h,wire,24)||!cipher_ok(s->receive,0))return 0;
 copy(scratch,wire+24,280);NoiseBuffer b;noise_buffer_set_inout(b,scratch,280,280);
 int ok=noise_cipherstate_decrypt_with_ad(s->receive,h,24,&b)==0&&b.size==OA_PLAIN;
 if(ok)copy(p,scratch,OA_PLAIN);wipe(scratch,sizeof scratch);return ok;
}
int oa_dell_auth(OaSession*s,const uint8_t*wire,size_t n){
 if(!range(s,sizeof *s)||!buffers(s,wire,n)||s->role!=2||s->phase!=1)return 0;
 uint8_t p[OA_PLAIN]={0},expected[OA_SIGNED];prefix(&s->context,1,expected);
 int ok=decrypt(s,1,wire,n,p)&&same(p,expected,OA_SIGNED)&&crypto_ed25519_check(p+OA_SIGNED,s->context.owner,p,OA_SIGNED)==0;
 if(ok){crypto_sha512(s->auth_hash,p,sizeof p);s->phase=2;}else s->phase=4;
 wipe(p,sizeof p);wipe(expected,sizeof expected);return ok;
}
int oa_dell_ack(OaSession*s,uint8_t*out){
 if(!range(s,sizeof *s)||!buffers(s,out,OA_WIRE)||s->role!=2||s->phase!=2)return 0;
 uint8_t p[OA_PLAIN];prefix(&s->context,2,p);copy(p+OA_SIGNED,s->auth_hash,64);
 int ok=encrypt(s,2,p,out);if(ok)s->phase=3;wipe(p,sizeof p);return ok;
}
int oa_mac_ack(OaSession*s,const uint8_t*wire,size_t n){
 if(!range(s,sizeof *s)||!buffers(s,wire,n)||s->role!=1||s->phase!=2)return 0;
 uint8_t p[OA_PLAIN]={0},expected[OA_PLAIN];prefix(&s->context,2,expected);copy(expected+OA_SIGNED,s->auth_hash,64);
 int ok=decrypt(s,2,wire,n,p)&&same(p,expected,sizeof expected);
 s->phase=ok?3:4;wipe(p,sizeof p);wipe(expected,sizeof expected);return ok;
}
int oa_mac_credentials_allowed(const OaSession*s){return range(s,sizeof *s)&&s->role==1&&s->phase==3&&cipher_ok(s->send,1)&&cipher_ok(s->receive,1);}
