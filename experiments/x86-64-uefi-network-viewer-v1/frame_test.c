#include "frame_core.h"
#include "monocypher-ed25519.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint8_t wire[RF_MAX_WIRE],seed[32],sk[64],pk[32],stream[16];
static uint32_t pixels[RF_MAX_PIXELS];
static unsigned checks;
static void put16(unsigned at,unsigned x){wire[at]=(uint8_t)x;wire[at+1]=(uint8_t)(x>>8);}
static void put32(unsigned at,unsigned x){put16(at,x);put16(at+2,x>>16);}
static size_t raw(unsigned w,unsigned h){
 memset(wire,0,sizeof(wire));memcpy(wire,"RPF1",4);wire[4]=1;wire[5]=1;
 put16(6,64);put16(8,w);put16(10,h);put32(12,w*h*3);wire[16]=1;
 for(unsigned i=0;i<w*h*3;i++)wire[64+i]=(uint8_t)i;
 return 128+w*h*3;
}
static void sign_frame(size_t n){crypto_ed25519_sign(wire+n-64,sk,wire,n-64);}
static void reject(size_t n){
 RfFrame state={0,5,7},before=state;
 for(unsigned i=0;i<RF_MAX_PIXELS;i++)pixels[i]=0x12345678;
 assert(rf_accept(wire,n,stream,pk,&state,pixels,RF_MAX_PIXELS));
 assert(!memcmp(&state,&before,sizeof(state)));
 for(unsigned i=0;i<RF_MAX_PIXELS;i++)assert(pixels[i]==0x12345678);
 checks++;
}
int main(void){
 crypto_ed25519_key_pair(sk,pk,seed);
 size_t n=raw(2,2);sign_frame(n);RfFrame state={0};
 assert(!rf_accept(wire,n,stream,pk,&state,pixels,RF_MAX_PIXELS));
 assert(pixels[0]==0x000102&&pixels[3]==0x090a0b&&state.sequence==1);checks++;
 assert(rf_accept(wire,n,stream,pk,&state,pixels,RF_MAX_PIXELS));checks++;
 /* Independently mutate every header byte, including reserved bytes and ID. */
 for(unsigned i=0;i<64;i++){n=raw(2,2);sign_frame(n);wire[i]^=128;reject(n);}
 for(unsigned i=64;i<n;i++){n=raw(2,2);sign_frame(n);wire[i]^=1;reject(n);}
 n=raw(2,2);sign_frame(n);for(size_t i=0;i<n;i++)reject(i);
 n=raw(2,2);sign_frame(n);reject(n+1);
 n=raw(2,2);put16(8,641);sign_frame(n);reject(n);
 n=raw(2,2);put16(10,361);sign_frame(n);reject(n);
 n=raw(2,2);put32(12,0xffffffffu);reject(n);
 /* Valid RLE, plus SIGNED malformed runs (not only bad signature cases). */
 n=raw(2,2);wire[5]=2;put32(12,5);put16(64,4);
 wire[66]=0xaa;wire[67]=0xbb;wire[68]=0xcc;n=133;sign_frame(n);state.sequence=0;
 assert(!rf_accept(wire,n,stream,pk,&state,pixels,RF_MAX_PIXELS));
 assert(pixels[0]==0xaabbcc&&pixels[3]==0xaabbcc);checks++;
 put16(64,0);sign_frame(n);reject(n);
 put16(64,5);sign_frame(n);reject(n);
 put16(64,3);sign_frame(n);reject(n);
 put32(12,4);n=132;sign_frame(n);reject(n);
 n=raw(640,360);sign_frame(n);state.sequence=0;
 assert(!rf_accept(wire,n,stream,pk,&state,pixels,RF_MAX_PIXELS));checks++;
 state.sequence=0;assert(rf_accept(wire,n,stream,pk,&state,pixels,1));checks++;
 puts("PASS authenticated bounded RGB/RLE decoder, replay and unchanged-on-rejection");
 printf("checks=%u max_pixels=%u max_wire=%u\n",checks,RF_MAX_PIXELS,RF_MAX_WIRE);
 return 0;
}
