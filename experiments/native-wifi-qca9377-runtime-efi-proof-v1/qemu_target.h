/* Isolated QEMU-only Target Pack: serial3f8 + isa-debug-exitf4; NEVER physical. */
static void out8(uint16_t p,uint8_t v){__asm__ volatile("outb %0,%1"::"a"(v),"Nd"(p));}
static uint8_t in8(uint16_t p){uint8_t v;__asm__ volatile("inb %1,%0":"=a"(v):"Nd"(p));return v;}
static void emit(const char*s){while(*s){for(unsigned k=0;k<100000&&!(in8(0x3fd)&32);k++){}out8(0x3f8,(uint8_t)*s++);}}
static __attribute__((noreturn)) void finish(int ok){out8(0xf4,ok?0x10:0x11);for(;;)__asm__ volatile("hlt");}
static __attribute__((noinline)) int large_stack_probe(void){
 volatile uint8_t frame[32768];unsigned sum=0;for(unsigned j=0;j<8;j++){frame[j*4096]=(uint8_t)(j+1);sum+=frame[j*4096];}frame[32767]=0x53;
 if(sum!=36||frame[32767]!=0x53)return 0;emit("REAL LARGE FRAME PROBE PASS\n");return 1;
}
static int memory_probe(void){
 uint8_t a[160],b[160];for(unsigned j=0;j<160;j++)a[j]=(uint8_t)j;
 memcpy(b+1,a+2,127);if(memcmp(b+1,a+2,127))return 0;memset(b+4,0x67,101);for(unsigned j=4;j<105;j++)if(b[j]!=0x67)return 0;
 if(strlen("public fixture")!=14||memchr(a,111,160)!=a+111)return 0;emit("ACTUAL EFI MEMORY SHIMS PASS\n");return 1;
}
static RngProtocol mock_provider;static RngSession mock_session;static RngReview mock_review;
static uint8_t mock_pool[256];static unsigned mock_live,mock_mode,mock_calls;static size_t mock_n;
static RngStatus RNG_EFIAPI loc(RngGuid*g,void*x,void**out){if(x||memcmp(g,&rng_protocol_guid,16))return 1;*out=&mock_provider;return 0;}
static RngStatus RNG_EFIAPI alloc(uint32_t t,size_t n,void**out){if(t!=2||n>256||mock_live)return 1;mock_live=1;mock_n=n;memset(mock_pool,0x42,n);*out=mock_pool;return 0;}
static RngStatus RNG_EFIAPI release(void*p){if(p!=mock_pool||!mock_live)return 1;for(size_t j=0;j<mock_n;j++)if(mock_pool[j])return 1;mock_live=0;return 0;}
static RngStatus RNG_EFIAPI info(RngProtocol*p,size_t*n,RngGuid*g){if(p!=&mock_provider)return 1;if(!g){*n=16;return UINT64_C(0x8000000000000005);}if(*n!=16)return 1;*g=rng_ctr_guid;return 0;}
static RngStatus RNG_EFIAPI get(RngProtocol*p,RngGuid*g,size_t n,uint8_t*out){if(p!=&mock_provider||memcmp(g,&rng_ctr_guid,16)||n!=32||out!=mock_pool)return 1;mock_calls++;memset(out,0x6b,n);return mock_mode?UINT64_C(0x8000000000000007):0;}
static int mock_rng_check(QcaNoisePort*port){
 for(unsigned mode=0;mode<2;mode++){
  if(!qca_native_reset(port,1))return 0;mock_mode=mode;mock_provider=(RngProtocol){info,get};mock_session=(RngSession){0};
  mock_review=(RngReview){.provider=&mock_provider,.epoch=1,.algorithm=rng_ctr_guid,.provider_provenance_sha256={1}};
  RngBootApi boot={loc,alloc,release};if(!rng_discover(&mock_session,&boot,1)||!qca_native_rng_bind(&mock_session,&mock_review))return 0;
  NoiseHandshakeState*h=0;uint8_t wire[64],empty[1];NoiseBuffer w,p;
  if(qca_nk_new(&h,NOISE_ROLE_INITIATOR))return 0;
  int rc=noise_dhstate_set_public_key(noise_handshakestate_get_remote_public_key_dh(h),vec_init_remote_static,32);
  if(rc||noise_handshakestate_start(h))return 0;
  noise_buffer_set_output(w,wire,sizeof(wire));noise_buffer_set_input(p,empty,0);unsigned before=mock_calls;
  rc=noise_handshakestate_write_message(h,&w,&p);
  int good=mock_calls==before+1&&(mode?(rc==NOISE_ERROR_SYSTEM&&!w.size&&noise_handshakestate_get_action(h)==NOISE_ACTION_FAILED):(!rc&&w.size==48));
  noise_handshakestate_free(h);if(!good||qca_native_live()||mock_live||port->quarantined)return 0;
  for(unsigned j=0;j<port->used;j++)for(unsigned k=0;k<512;k++)if(port->bytes[j][k])return 0;
 }
 return 1;
}
