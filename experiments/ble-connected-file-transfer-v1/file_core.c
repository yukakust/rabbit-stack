#include "file_core.h"
#include "sha256.h"
static uint32_t read32(const uint8_t*p){return p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static void put32(uint8_t*p,uint32_t v){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(v>>(8*i));}
static int equal(const uint8_t*a,const uint8_t*b,size_t n){uint8_t v=0;for(size_t i=0;i<n;i++)v|=a[i]^b[i];return !v;}
static void copy(uint8_t*a,const uint8_t*b,size_t n){for(size_t i=0;i<n;i++)a[i]=b[i];}
void rf_init(RfFile*f,RfApply apply){f->length=f->received=f->counter=0;f->state=RF_IDLE;f->error=0;f->apply=apply;for(unsigned i=0;i<8;i++)f->session[i]=0;for(unsigned i=0;i<32;i++)f->digest[i]=0;}
int rf_control(RfFile*f,const uint8_t*p,size_t n){
 if(!f||!p||!n)return 1;
 if(p[0]==1){ /* BEGIN: version, world-only kind, reserved, nonce, stream length. */
  if(n!=16||p[1]!=1||p[2]!=1||p[3])return 1;
  uint32_t length=read32(p+12);if(length<=32||length>RF_MAX_FILE+32)return 1;
  if(f->state!=RF_IDLE&&equal(f->session,p+4,8))return length!=f->length;
  /* Never abandon another active staging session implicitly. Explicit ABORT
   * must be observed first. A disconnect leaves same-boot staging intact. */
  if(f->state==RF_STAGING)return 1;
  copy(f->session,p+4,8);f->length=length;f->received=0;f->error=0;f->state=RF_STAGING;
  for(unsigned i=0;i<32;i++)f->digest[i]=0;
  return 0;
 }
 if(n!=9||!equal(f->session,p+1,8))return 1;
 if(p[0]==3){f->state=RF_IDLE;f->length=f->received=0;return 0;}
 if(p[0]!=2)return 1;
 if(f->state==RF_APPLIED||f->state==RF_REJECTED)return 0; /* Lost final reply. */
 if(f->state!=RF_STAGING||f->received!=f->length)return 1;
 rabbit_sha256(f->digest,f->stream+32,f->length-32);
 if(!equal(f->digest,f->stream,32)){f->error=1;f->state=RF_REJECTED;return 0;}
 uint32_t counter=f->counter;
 if(!f->apply||f->apply(f->stream+32,f->length-32,&counter)){f->error=2;f->state=RF_REJECTED;return 0;}
 f->counter=counter;f->state=RF_APPLIED;return 0;
}
int rf_data(RfFile*f,const uint8_t*p,size_t n){
 if(!f||!p||f->state!=RF_STAGING||n<=4||n>244)return 1;
 uint32_t offset=read32(p);size_t length=n-4;
 if(offset>f->received||offset>f->length||length>f->length-offset)return 1;
 if(offset<f->received)return length>f->received-offset||!equal(f->stream+offset,p+4,length);
 copy(f->stream+offset,p+4,length);f->received+=(uint32_t)length;return 0;
}
void rf_status(const RfFile*f,uint8_t out[RF_STATUS_SIZE]){
 out[0]='R';out[1]='F';out[2]='S';out[3]=1;copy(out+4,f->session,8);
 put32(out+12,f->received);put32(out+16,f->length);out[20]=f->state;out[21]=f->error;out[22]=out[23]=0;
 put32(out+24,f->counter);copy(out+28,f->digest,32);
}
