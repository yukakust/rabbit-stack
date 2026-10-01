/* QEMU-only native execution/recovery probe. NOT a physical BLE updater. */
#include "abi.h"
#include "verify_core.h"
#include "sha256.h"
#include "transport_core.h"
#include "fixtures.h"
typedef Status (EFIAPI *Watchdog)(uint64_t,uint64_t,uint64_t,uint16_t *);
typedef Status (EFIAPI *LoadImage)(uint8_t,void *,void *,void *,uint64_t,void **);
typedef Status (EFIAPI *StartImage)(void *,uint64_t *,uint16_t **);
typedef Status (EFIAPI *UnloadImage)(void *);
typedef Status (EFIAPI *Stall)(uint64_t);
typedef Status (EFIAPI *FreePool)(void *);
static SystemTable *system;
static void *parent,*active_handle;
static ModuleRegistration active_module;
static RabbitState active_state={0,0x9966ff,STATE_TAG,0};
static UpdatePolicy policy;
static int tested;
static uint8_t receipt_identity[32];
static int receipt_status;
static int equal(const uint8_t*a,const uint8_t*b,size_t n){uint8_t x=0;for(size_t i=0;i<n;i++)x|=a[i]^b[i];return !x;}
static uint32_t le32(const uint8_t*p){return p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static uint64_t le64(const uint8_t*p){return le32(p)|((uint64_t)le32(p+4)<<32);}
static void say(const char *text){
 uint16_t line[192];unsigned i=0;
 for(;text[i]&&i<189;i++){
  line[i]=(uint8_t)text[i];
  __asm__ volatile("outb %0, %1"::"a"((uint8_t)text[i]),"Nd"((uint16_t)0xe9));
 }
 line[i++]='\r';line[i++]='\n';line[i]=0;
 __asm__ volatile("outb %0, %1"::"a"((uint8_t)'\n'),"Nd"((uint16_t)0xe9));
 typedef Status(EFIAPI *Output)(void*,uint16_t*);
 Output output=*(Output*)((uint8_t*)system->output+8);output(system->output,line);
}
static int guard(uint64_t seconds){
 return ((Watchdog)service(system,256))(seconds,0x52414242,0,0)!=0;
}
static int callback_in_code(ModuleCall call,const LoadedImage*image,const uint8_t*pe){
 uintptr_t address=(uintptr_t)call,base=(uintptr_t)image->base;
 if(address<base||address-base>=image->size)return 0;
 uint32_t offset=le32(pe+60);unsigned count=pe[offset+6]|((unsigned)pe[offset+7]<<8);
 size_t sections=offset+24+240;
 for(unsigned i=0;i<count;i++){
  const uint8_t*s=pe+sections+i*40;
  uint32_t rva=le32(s+12),size=le32(s+8),flags=le32(s+36);
  if((flags&0x20000000)&&address-base>=rva&&address-base-rva<size)return 1;
 }
 return 0;
}
/* Returns 1 committed, 2 unhealthy retained, 3 invalid, 4 unavailable recovery,
 * 5 ABI failure. Keeping bytes cannot isolate arbitrary native corruption. */
static int update(const uint8_t*p,size_t n){
 uint8_t identity[32];rabbit_sha256(identity,p,n);
 if(receipt_status&&equal(identity,receipt_identity,32))return 6; /* Receipt-only retry. */
 rabbit_sha256(policy.state,(const uint8_t*)&active_state,sizeof(active_state));
 if(rabbit_update_verify(p,n,&policy)){say("GATE: RRT1 VERIFICATION REJECTED");return 3;}
 /* Owner's domain-separated signature is the release authorization. The Mac
  * signer requires explicit reviewed SHA-256; no payload allowlist is baked in. */
 if(rabbit_module_pe(p+192,n-256)){say("GATE: PE STRUCTURE REJECTED");return 3;}
 policy.counter=le64(p+24);
 if(guard(5))return 4; /* No execution if firmware refuses trial watchdog. */
 void *child=0;Status status=((LoadImage)service(system,200))(0,parent,0,(void*)(p+192),n-256,&child);
 if(status){if(child)((UnloadImage)service(system,224))(child);guard(0);return 3;}
 LoadedImage *image=0;
 status=((HandleProtocol)service(system,152))(child,&loaded_image_guid,(void**)&image);
 ModuleRegistration candidate={REGISTRATION_MAGIC,1,sizeof(ModuleRegistration),1,0,0};
 if(status||!image){((UnloadImage)service(system,224))(child);guard(0);return 5;}
 image->options=&candidate;image->options_size=sizeof(candidate);
 uint64_t exit_size=0;uint16_t *exit_data=0;
 status=((StartImage)service(system,208))(child,&exit_size,&exit_data);
 if(exit_data)((FreePool)service(system,72))(exit_data);
 if(status){guard(0);return 5;} /* Failed driver start already unloads image. */
 image->options=0;image->options_size=0;
 if(candidate.magic!=REGISTRATION_MAGIC||candidate.abi!=1||candidate.size!=sizeof(candidate)||candidate.state_abi!=1||
    !callback_in_code(candidate.init,image,p+192)||!callback_in_code(candidate.tick,image,p+192)){
  ((UnloadImage)service(system,224))(child);guard(0);return 5;
 }
 RabbitState trial=active_state;
 int unhealthy=candidate.init(&trial)||candidate.tick(&trial)||trial.tag!=STATE_TAG||trial.reserved||trial.ticks>1000;
 if(unhealthy){
  ((UnloadImage)service(system,224))(child);
  if(guard(0))return 4;
  for(unsigned i=0;i<32;i++)receipt_identity[i]=identity[i];
  receipt_status=2;return 2;
 }
 /* Reviewed cooperative module: no other callback is running at this boundary. */
 void *previous=active_handle;
 active_handle=child;active_module=candidate;active_state=trial;
 for(unsigned i=0;i<32;i++)policy.base[i]=p[96+i];
 if(previous&&((UnloadImage)service(system,224))(previous)){
  say("PREVIOUS MODULE UNLOAD FAILED; STOP");for(;;)__asm__ volatile("pause");
 }
 if(guard(0)){say("WATCHDOG DISARM FAILED; STOP");for(;;)__asm__ volatile("pause");}
 for(unsigned i=0;i<32;i++)receipt_identity[i]=identity[i];
 receipt_status=1;
 return 1;
}
static int receive(const uint8_t *frames,size_t n){
 int result=0;
 for(size_t i=0;i+16<=n;i+=16){
  int rx=rabbit_rx_frame(frames+i);
  if(rx==1)return 3;
  if(rx==2)result=update(rabbit_rx_data(),rabbit_rx_length());
 }
 return result;
}
static int demo(void){
 if(tested)return 1;
 tested=1;
 if(receive(frames_a,sizeof(frames_a))!=1){say("FAIL: A");return 0;}
 say("NATIVE A COMMITTED FROM SIGNED RAM PAYLOAD");
 if(active_state.color!=0x22cc66||active_state.ticks!=1)return 0;
 if(receive(frames_b,sizeof(frames_b))!=1){say("FAIL: B");return 0;}
 say("NATIVE B COMMITTED; PREVIOUS DRIVER UNLOADED");
 if(active_state.color!=0x3366ff||active_state.ticks!=2)return 0;
 if(receive(frames_b,sizeof(frames_b))!=6||active_state.ticks!=2)return 0;
 say("EXACT RETRY REPEATED RECEIPT ONLY; NATIVE EFFECT NOT REPEATED");
 RabbitState previous=active_state;void *handle=active_handle;uint8_t identity[32];
 for(unsigned i=0;i<32;i++)identity[i]=policy.base[i];
 if(receive(frames_unhealthy,sizeof(frames_unhealthy))!=2||
    !equal((const uint8_t*)&active_state,(const uint8_t*)&previous,sizeof(previous))||active_handle!=handle||!equal(identity,policy.base,32))return 0;
 say("FAILED NATIVE HEALTH RETAINED EXACT B AND STATE");
 if(receive(frames_tampered,sizeof(frames_tampered))!=3)return 0;
 say("TAMPERED SIGNATURE REJECTED BEFORE LOADIMAGE");
 if(receive(frames_b,sizeof(frames_b))!=3)return 0;
 say("STALE RUNTIME COUNTER REJECTED BEFORE LOADIMAGE");
 if(receive(frames_abi,sizeof(frames_abi))!=5||active_handle!=handle||!equal(identity,policy.base,32))return 0;
 say("INCOMPATIBLE SIGNED MODULE ABI RETAINED B");
 say("NATIVE RAM UPDATE DEMO PASS; NO BLUETOOTH OR STORAGE WRITES");
 return 1;
}
Status EFIAPI rabbit_entry(void *handle,SystemTable *st){
 parent=handle;system=st;
 if(guard(0))return EFI_ERROR(3);
 for(unsigned i=0;i<32;i++){policy.target[i]=fixture_target[i];policy.owner[i]=fixture_owner[i];policy.base[i]=fixture_base[i];}
 say("RABBIT NATIVE SUPERVISOR v0.1 - QEMU ONLY");
 say("BOOTSTRAP FALLBACK ACTIVE; VOLATILE UPDATES CLEARED");
 say("T: TWO SIGNED NATIVE UPDATES AND FAILURE TESTS");
 say("AFTER PASS, H: HUNG INIT WATCHDOG RESET; ESC: EXIT");
 typedef struct{uint16_t scan,character;} Key;
 typedef Status(EFIAPI *ReadKey)(void*,Key*);
 ReadKey read=*(ReadKey*)((uint8_t*)system->input+8);
 for(;;){
  Key key={0};
  if(!read(system->input,&key)){
   if(key.scan==0x17){
    if(active_handle){
     if(guard(5))return EFI_ERROR(3);
     if(((UnloadImage)service(system,224))(active_handle))return EFI_ERROR(3);
    }
    if(guard(0))return EFI_ERROR(3);
    return 0;
   }
   if((key.character=='t'||key.character=='T')&&!tested){if(!demo())say("NATIVE RAM UPDATE DEMO FAILED");}
   if((key.character=='h'||key.character=='H')&&tested&&active_state.ticks==2){
    say("STARTING SIGNED HUNG INIT; EXPECT WATCHDOG RESET TO BOOTSTRAP");
    int result=receive(frames_hang,sizeof(frames_hang));
    if(result==4)say("WATCHDOG UNSUPPORTED; HUNG MODULE NOT EXECUTED");
    else say("FAIL: HUNG MODULE UNEXPECTEDLY RETURNED");
   }
  }
  ((Stall)service(system,248))(10000);
 }
}
