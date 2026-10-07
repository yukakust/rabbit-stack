#include "backend_entropy.h"
static RngProtocol provider;static RngSession rng;static RngReview review;
static uint8_t mock_pool[256];static size_t pool_len;static unsigned pool_live,entropy_calls,provider_mode;
static RngStatus RNG_EFIAPI plocate(RngGuid*g,void*x,void**out){CHECK(!x&&!memcmp(g,&rng_protocol_guid,16));*out=&provider;return 0;}
static RngStatus RNG_EFIAPI palloc(uint32_t t,size_t n,void**out){CHECK(t==2&&n<=256&&!pool_live);pool_live=1;pool_len=n;memset(mock_pool,0xa5,n);*out=mock_pool;return 0;}
static RngStatus RNG_EFIAPI pfree(void*p){CHECK(p==mock_pool&&pool_live);for(size_t j=0;j<pool_len;j++)CHECK(!mock_pool[j]);if(provider_mode==2)return UINT64_C(0x8000000000000002);pool_live=0;return 0;}
static RngStatus RNG_EFIAPI pinfo(RngProtocol*p,size_t*n,RngGuid*g){CHECK(p==&provider);if(!g){*n=16;return UINT64_C(0x8000000000000005);}CHECK(*n==16);*g=rng_ctr_guid;return 0;}
static RngStatus RNG_EFIAPI pget(RngProtocol*p,RngGuid*g,size_t n,uint8_t*out){CHECK(p==&provider&&!memcmp(g,&rng_ctr_guid,16)&&out==mock_pool&&n==32);entropy_calls++;memset(out,0x6b,n);return provider_mode==1?UINT64_C(0x8000000000000007):0;}
static void setup_rng(void){provider=(RngProtocol){pinfo,pget};rng=(RngSession){0};review=(RngReview){.provider=&provider,.epoch=19,.algorithm=rng_ctr_guid,.provider_provenance_sha256={1}};RngBootApi b={plocate,palloc,pfree};CHECK(rng_discover(&rng,&b,19));}
extern const uint64_t qca_noise_port_abi[11];
static void port_model(void){
 const uint64_t expected[]={sizeof(QcaNoisePort),_Alignof(QcaNoisePort),sizeof(size_t),sizeof(void*),offsetof(QcaNoisePort,bytes),offsetof(QcaNoisePort,lengths),offsetof(QcaNoisePort,states),offsetof(QcaNoisePort,epoch),offsetof(QcaNoisePort,rng),sizeof(RngProtocol),offsetof(RngProtocol,get_rng)};
 CHECK(!memcmp(qca_noise_port_abi,expected,sizeof(expected)));CHECK(sizeof(size_t)==8&&sizeof(void*)==8);
 CHECK(qca_native_reset(&port,19)&&qca_native_bind(&port));
 CHECK(!qca_native_bind((QcaNoisePort*)((uint8_t*)&port+1))&&!qca_native_reset((QcaNoisePort*)((uint8_t*)&port+1),19));
 CHECK(!qca_port_malloc(0)&&!qca_port_malloc(513)&&!qca_port_calloc(SIZE_MAX,2));
 for(size_t n=0;n<=513;n++){
  CHECK(qca_native_reset(&port,19));uint8_t*x=qca_port_malloc(n);CHECK((x!=0)==(n>=1&&n<=512));
  if(x){memset(x,0x42,n);qca_noise_free(x,n);for(unsigned j=0;j<512;j++)CHECK(!x[j]);}
  CHECK(!live&&!port.quarantined);
 }
 CHECK(qca_nk_new((NoiseHandshakeState**)(UINTPTR_MAX-1),NOISE_ROLE_RESPONDER)==NOISE_ERROR_INVALID_PARAM);
 void*p[64];for(unsigned j=0;j<64;j++){p[j]=qca_port_malloc(1+j);CHECK(p[j]);for(unsigned k=0;k<1+j;k++)CHECK(!((uint8_t*)p[j])[k]);}
 CHECK(!qca_port_malloc(1)&&live==64);for(unsigned j=0;j<64;j++)qca_noise_free(p[j],1+j);
 CHECK(!live&&!qca_port_malloc(1));CHECK(qca_native_reset(&port,19));
 for(int at=0;at<20;at++){
  CHECK(qca_native_reset(&port,19));port.fail_after=at;NoiseHandshakeState*h=(NoiseHandshakeState*)(uintptr_t)1;
  int rc=qca_nk_new(&h,NOISE_ROLE_RESPONDER);port.fail_after=-1;CHECK(rc==NOISE_ERROR_NONE||rc==NOISE_ERROR_NO_MEMORY);
  if(rc)CHECK(!h);else CHECK(!noise_handshakestate_free(h));CHECK(!live&&!port.quarantined);
 }
 CHECK(qca_native_reset(&port,19));NoiseHandshakeState*unchanged=(NoiseHandshakeState*)(uintptr_t)1;
 CHECK(qca_nk_new((NoiseHandshakeState**)port.bytes,NOISE_ROLE_RESPONDER)==NOISE_ERROR_INVALID_PARAM);
 CHECK(qca_nk_new(&unchanged,99)==NOISE_ERROR_INVALID_STATE&&!unchanged&&!live);
 CHECK(!qca_native_rng_bind((RngSession*)port.bytes,&review));
 uint8_t forbidden[32];CHECK(qca_noise_entropy(forbidden,32)!=0);
 for(unsigned mode=0;mode<6;mode++){
  CHECK(qca_native_reset(&port,19));provider_mode=0;setup_rng();
  if(mode==1)memset(review.provider_provenance_sha256,0,32);
  if(mode==2)review.epoch=20;
  if(mode==3)provider_mode=1;
  CHECK(qca_native_rng_bind(&rng,&review)==(mode!=2));
  NoiseHandshakeState*h=0;uint8_t pub[32],msg[64],empty[1];NoiseBuffer w,b;
  CHECK(!qca_nk_new(&h,NOISE_ROLE_INITIATOR));memcpy(pub,vec_init_remote_static,32);
  CHECK(!noise_dhstate_set_public_key(noise_handshakestate_get_remote_public_key_dh(h),pub,32));CHECK(!noise_handshakestate_start(h));
  if(mode==4)provider.get_rng=0;if(mode==5)provider_mode=2;
  noise_buffer_set_output(w,msg,sizeof(msg));noise_buffer_set_input(b,empty,0);unsigned before=entropy_calls;
  int rc=noise_handshakestate_write_message(h,&w,&b);CHECK(rc==(mode?NOISE_ERROR_SYSTEM:NOISE_ERROR_NONE));
  if(mode){CHECK(!w.size&&noise_handshakestate_get_action(h)==NOISE_ACTION_FAILED);if(mode<=2||mode==4)CHECK(entropy_calls==before);}
  else CHECK(w.size==48&&entropy_calls==before+1);
  CHECK(!noise_handshakestate_free(h)&&!live);
  if(mode==5){CHECK(rng.pool&&pool_live&&!qca_native_reset(&port,20));provider_mode=0;CHECK(rng_cleanup(&rng));}
  CHECK(!pool_live);
 }
 CHECK(qca_native_reset(&port,19));
}
/* Each ambiguity mode runs in a fresh process: quarantine is irreversible here. */
static void quarantine_model(const char*mode){
 CHECK(qca_native_reset(&port,19)&&qca_native_bind(&port));void*p=qca_port_malloc(32),*other=qca_port_malloc(32);CHECK(p&&other);memset(p,0x4c,32);memset(other,0x9a,32);
 if(!strcmp(mode,"foreign"))qca_noise_free((void*)(uintptr_t)1,32);
 else if(!strcmp(mode,"interior"))qca_noise_free((uint8_t*)p+1,31);
 else if(!strcmp(mode,"size"))qca_noise_free(p,31);
 else {qca_noise_free(p,32);qca_noise_free(p,32);}
 CHECK(port.quarantined&&!qca_port_malloc(1)&&!qca_native_reset(&port,20));
 for(unsigned j=0;j<32;j++)CHECK(((uint8_t*)other)[j]==0x9a);
 NoiseHandshakeState*h=(NoiseHandshakeState*)(uintptr_t)1;CHECK(qca_nk_new(&h,NOISE_ROLE_RESPONDER)==NOISE_ERROR_INVALID_STATE&&!h);
 if(strcmp(mode,"double"))qca_noise_free(p,32);qca_noise_free(other,32);CHECK(!live&&port.quarantined);
 printf("PASS %u native allocator quarantine %s no foreign dereference/owner release invention\n",checks,mode);
}
