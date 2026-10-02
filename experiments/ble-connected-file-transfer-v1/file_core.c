#include "file_core.h"
#include "sha256.h"
static uint32_t read32(const uint8_t*p){return p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static void put32(uint8_t*p,uint32_t v){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(v>>(8*i));}
static int equal(const uint8_t*a,const uint8_t*b,size_t n){uint8_t v=0;for(size_t i=0;i<n;i++)v|=a[i]^b[i];return !v;}
static void copy(uint8_t*a,const uint8_t*b,size_t n){for(size_t i=0;i<n;i++)a[i]=b[i];}
void rf_init(RfFile*f,RfApply apply){f->length=f->received=f->counter=0;f->state=RF_IDLE;f->error=0;f->kind=1;f->apply=apply;f->dispatch=0;for(unsigned i=0;i<8;i++)f->session[i]=0;for(unsigned i=0;i<32;i++)f->digest[i]=0;}
void rf_init_owner(RfFile*f,RfDispatch dispatch){rf_init(f,0);f->dispatch=dispatch;}
int rf_finish(RfFile*f,int failed,uint32_t counter){
 if(!f||f->state!=RF_PENDING||f->received!=f->length)return 1;
 f->counter=counter;f->error=failed?2:0;f->state=failed?RF_REJECTED:RF_APPLIED;return 0;
}
int rf_control(RfFile*f,const uint8_t*p,size_t n){
 if(!f||!p||!n)return 1;
 if(p[0]==1){ /* BEGIN: version, kind, reserved, nonce, stream length. */
  if(n!=16||p[1]!=1||p[3]||(p[2]!=1&&(p[2]!=2||!f->dispatch)))return 1;
  uint32_t length=read32(p+12),maximum=p[2]==1?RF_MAX_FILE:RF_MAX_NATIVE;
  if(length<=32||length>maximum+32)return 1;
  if(f->state!=RF_IDLE&&equal(f->session,p+4,8))return length!=f->length||p[2]!=f->kind;
  /* Never abandon another active staging session implicitly. Explicit ABORT
   * must be observed first. A disconnect leaves same-boot staging intact. */
  if(f->state==RF_STAGING||f->state==RF_PENDING)return 1;
  copy(f->session,p+4,8);f->kind=p[2];f->length=length;f->received=0;f->error=0;f->state=RF_STAGING;
  for(unsigned i=0;i<32;i++)f->digest[i]=0;
  return 0;
 }
 if(n!=9||!equal(f->session,p+1,8))return 1;
 if(p[0]==3){if(f->state==RF_PENDING)return 1;f->state=RF_IDLE;f->length=f->received=0;return 0;}
 if(p[0]!=2)return 1;
 if(f->state==RF_APPLIED||f->state==RF_REJECTED||f->state==RF_PENDING)return 0; /* Lost final reply. */
 if(f->state!=RF_STAGING||f->received!=f->length)return 1;
 rabbit_sha256(f->digest,f->stream+32,f->length-32);
 if(!equal(f->digest,f->stream,32)){f->error=1;f->state=RF_REJECTED;return 0;}
 uint32_t counter=f->counter;
 int applied=f->dispatch?f->dispatch(f->kind,f->stream+32,f->length-32,&counter):
  f->apply?f->apply(f->stream+32,f->length-32,&counter):1;
 if(applied==2&&f->dispatch){f->state=RF_PENDING;return 0;}
 if(applied){f->error=2;f->state=RF_REJECTED;return 0;}
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
