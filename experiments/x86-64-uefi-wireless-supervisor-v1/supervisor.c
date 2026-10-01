/* Resident hardware owner. Native drivers are privileged, owner-reviewed code. */
#include "scene_abi.h"
#include "verify_core.h"
#include "sha256.h"
#include "transport_core.h"
#include "bootstrap.h"
typedef Status (EFIAPI *Watchdog)(uint64_t,uint64_t,uint64_t,uint16_t *);
typedef Status (EFIAPI *LoadImage)(uint8_t,void *,void *,void *,uint64_t,void **);
typedef Status (EFIAPI *StartImage)(void *,uint64_t *,uint16_t **);
typedef Status (EFIAPI *UnloadImage)(void *);
typedef Status (EFIAPI *FreePool)(void *);
static SystemTable *system;
static void *parent,*active_handle;
static SceneRegistration active;
static UpdatePolicy policy;
static uint32_t pixels[SURFACE_PIXELS],trial_pixels[SURFACE_PIXELS];
static Surface front={pixels,480,270,480,1},trial={trial_pixels,480,270,480,1};
static uint8_t snapshot[SNAPSHOT_MAX],checked_snapshot[SNAPSHOT_MAX],latest_identity[32],receipt[16];
static uint32_t snapshot_length,latest_hash;
static uint8_t latest_status,ready,fault;
static uint32_t *physical;
static uint32_t physical_stride,physical_format;
static uint32_t le32(const uint8_t*p){return p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static uint64_t le64(const uint8_t*p){return le32(p)|((uint64_t)le32(p+4)<<32);}
static uint32_t fnv(const uint8_t*p,size_t n){uint32_t h=0x811c9dc5;for(size_t i=0;i<n;i++)h=(h^p[i])*0x01000193;return h;}
static int same(const uint8_t*a,const uint8_t*b,size_t n){uint8_t x=0;for(size_t i=0;i<n;i++)x|=a[i]^b[i];return !x;}
static void copy(void*a,const void*b,size_t n){uint8_t*d=a;const uint8_t*s=b;for(size_t i=0;i<n;i++)d[i]=s[i];}
static void putbe(uint8_t*p,uint32_t v){p[0]=v>>24;p[1]=v>>16;p[2]=v>>8;p[3]=v;}
static int guard(uint64_t seconds){return ((Watchdog)service(system,256))(seconds,0x52414242,0,0)!=0;}
static void result(uint8_t kind,uint8_t transfer,uint32_t hash,uint32_t counter){
 receipt[0]='R';receipt[1]='A';receipt[2]=kind;receipt[3]=transfer;
 putbe(receipt+4,hash);putbe(receipt+8,counter);putbe(receipt+12,fnv(receipt,12));
}
void EFIAPI rabbit_receipt_write(uint8_t*out){copy(out,receipt,16);}
void EFIAPI rabbit_supervisor_entry(void*h,SystemTable*st){parent=h;system=st;}
void EFIAPI rabbit_supervisor_print_ascii(const char*text){
 typedef Status(EFIAPI *Output)(void*,uint16_t*);
 uint16_t line[320];unsigned n=0;
 while(text[n]&&n<319){line[n]=(uint8_t)text[n];n++;}line[n]=0;
 if(system&&system->output)((Output)*(void**)((uint8_t*)system->output+8))(system->output,line);
}
static int code_pointer(uintptr_t address,const LoadedImage*image,const uint8_t*pe){
 uintptr_t base=(uintptr_t)image->base;if(address<base||address-base>=image->size)return 0;
 uint32_t offset=le32(pe+60);unsigned count=pe[offset+6]|((unsigned)pe[offset+7]<<8);
 for(unsigned i=0;i<count;i++){
  const uint8_t*s=pe+offset+24+240+i*40;
  uint32_t rva=le32(s+12),size=le32(s+8),flags=le32(s+36);
  if((flags&0x20000000)&&address-base>=rva&&address-base-rva<size)return 1;
 }return 0;
}
static int load(const uint8_t*pe,size_t n,void**handle,SceneRegistration*r){
 if(rabbit_module_pe(pe,n))return 1;
 Status status=((LoadImage)service(system,200))(0,parent,0,(void*)pe,n,handle);
 if(status){if(*handle)((UnloadImage)service(system,224))(*handle);*handle=0;return 1;}
 LoadedImage*image=0;
 if(((HandleProtocol)service(system,152))(*handle,&loaded_image_guid,(void**)&image)||!image){((UnloadImage)service(system,224))(*handle);*handle=0;return 1;}
 *r=(SceneRegistration){SCENE_MAGIC,2,sizeof(*r),2,0,0,0,0,0,0};
 image->options=r;image->options_size=sizeof(*r);
 uint64_t exit_size=0;uint16_t*exit_data=0;
 status=((StartImage)service(system,208))(*handle,&exit_size,&exit_data);
 if(exit_data)((FreePool)service(system,72))(exit_data);
 if(status){*handle=0;return 1;} /* UEFI unloads a driver whose entry failed. */
 image->options=0;image->options_size=0;
 if(r->magic!=SCENE_MAGIC||r->abi!=2||r->state_abi!=2||r->size!=sizeof(*r)||
 !code_pointer((uintptr_t)r->init,image,pe)||!code_pointer((uintptr_t)r->tick,image,pe)||!code_pointer((uintptr_t)r->frame,image,pe)||
 !code_pointer((uintptr_t)r->snapshot,image,pe)||!code_pointer((uintptr_t)r->receipt,image,pe)||!code_pointer((uintptr_t)r->counter,image,pe)){
  ((UnloadImage)service(system,224))(*handle);*handle=0;return 1;
 }return 0;
}
static int export_state(void){
 if(active.snapshot(snapshot,sizeof(snapshot),&snapshot_length)||snapshot_length<32||snapshot_length>SNAPSHOT_MAX||
    !same(snapshot,(const uint8_t*)"RSS2",4)||le32(snapshot+4)!=snapshot_length)return 1;
 uint32_t n=le32(snapshot+16);
 if(n>65535||snapshot[20]>16||snapshot_length!=32+n+snapshot[20]*16)return 1;
 rabbit_sha256(policy.state,snapshot+32,n);return 0;
}
static void present(void){
 if(!physical)return;
 for(unsigned y=0;y<270;y++)for(unsigned x=0;x<480;x++){
  uint32_t c=pixels[y*480+x];
  if(!physical_format)c=((c&255)<<16)|(c&0xff00)|((c>>16)&255);
  physical[y*physical_stride+x]=c;
 }
}
static int bind_display(void){
 typedef Status(EFIAPI *Locate)(const void*,void*,void**);
 static const uint8_t guid[16]={0xde,0xa9,0x42,0x90,0xdc,0x23,0x38,0x4a,0x96,0xfb,0x7a,0xde,0xd0,0x80,0x51,0x6a};
 void*gop=0;if(((Locate)service(system,320))(guid,0,&gop)||!gop)return 1;
 uint8_t*mode=*(uint8_t**)((uint8_t*)gop+24);if(!mode)return 1;
 uint8_t*info=*(uint8_t**)(mode+8);if(!info)return 1;
 uint32_t w=le32(info+4),h=le32(info+8),stride=le32(info+32),fmt=le32(info+12);
 physical=*(uint32_t**)(mode+24);
 if(w<480||h<270||w>8192||h>8192||stride<w||stride>16384||fmt>1||!physical||*(uint64_t*)(mode+32)<(uint64_t)stride*h*4){physical=0;return 1;}
 physical_stride=stride;physical_format=fmt;return 0;
}
int EFIAPI rabbit_scene_bootstrap(void*st){
 if(!system||st!=system||ready||bind_display()||guard(5))return 1;
 copy(policy.target,bootstrap_target,32);copy(policy.owner,bootstrap_owner,32);rabbit_sha256(policy.base,bootstrap_module,sizeof(bootstrap_module));
 snapshot_length=32;for(unsigned i=0;i<32;i++)snapshot[i]=0;
 copy(snapshot,"RSS2",4);snapshot[4]=32;
 if(load(bootstrap_module,sizeof(bootstrap_module),&active_handle,&active)||active.init(snapshot,32,&front)||export_state()){guard(0);return 1;}
 ready=1;present();return guard(0);
}
int EFIAPI rabbit_scene_tick(void*st){
 if(!ready||fault||st!=system||guard(5))return 1;
 int failed=active.tick(&front);if(guard(0))return 1;
 if(failed)return 1;
 present();return 0;
}
void EFIAPI rabbit_scene_shutdown(void){
 if(!active_handle)return;
 if(guard(5))for(;;)__asm__ volatile("pause"); /* Owner power-off if recovery service failed. */
 if(((UnloadImage)service(system,224))(active_handle))for(;;)__asm__ volatile("pause");
 active_handle=0;ready=0;
 if(guard(0))for(;;)__asm__ volatile("pause");
}
static int runtime_update(const uint8_t*p,size_t n,uint8_t transfer){
 uint8_t identity[32];rabbit_sha256(identity,p,n);uint32_t hash=fnv(p,n);
 if(latest_status&&same(identity,latest_identity,32)){
  result(latest_status,transfer,latest_hash,(uint32_t)policy.counter);return 4;
 }
 if(guard(5))return 3;
 if(export_state()||rabbit_update_verify(p,n,&policy)||rabbit_module_pe(p+192,n-256)){
  if(guard(0)){fault=1;return 3;}
  result(0x23,transfer,hash,(uint32_t)policy.counter);return 4;
 }
 policy.counter=le64(p+24); /* Authorized failed trials consume their counter. */
 copy(trial_pixels,pixels,sizeof(pixels));void*child=0;SceneRegistration candidate;
 int failed=load(p+192,n-256,&child,&candidate);
 uint32_t checked=0;
 if(!failed)failed=candidate.init(snapshot,snapshot_length,&trial)||
  candidate.snapshot(checked_snapshot,sizeof(checked_snapshot),&checked)||checked!=snapshot_length||!same(snapshot,checked_snapshot,checked)||candidate.tick(&trial);
 if(failed){if(child&&((UnloadImage)service(system,224))(child)){fault=1;return 3;}}
 else{
  void*previous=active_handle;active_handle=child;active=candidate;copy(pixels,trial_pixels,sizeof(pixels));copy(policy.base,p+96,32);
  if(previous&&((UnloadImage)service(system,224))(previous)){fault=1;return 3;} /* Remain under watchdog. */
  present();
 }
 if(guard(0)){fault=1;return 3;}
 copy(latest_identity,identity,32);latest_hash=hash;latest_status=failed?0x23:0x21;
 result(latest_status,transfer,hash,(uint32_t)policy.counter);return 4;
}
int EFIAPI rabbit_package_frame(const uint8_t*f,void*st){
 if(!ready||st!=system)return 3;
 if(f[0]!='R'||f[1]!='P'||fnv(f,12)!=((uint32_t)f[12]<<24|((uint32_t)f[13]<<16)|((uint32_t)f[14]<<8)|f[15]))return 0;
 if((f[2]>>4)==3){
  int rx=rabbit_rx_frame(f);
  if(rx==3){result(0x22,f[3],fnv(rabbit_rx_data(),rabbit_rx_length()),(uint32_t)policy.counter);return 4;}
  if(rx==2)return runtime_update(rabbit_rx_data(),rabbit_rx_length(),f[3]);
  return 0;
 }
 if((f[2]>>4)!=2)return 0;
 if(guard(5))return 3;
 int applied=active.frame(f,&front);uint32_t hash=active.receipt(),counter=active.counter();
 if(guard(0))return 3;
 if(applied==1||applied==4||applied==5){result(0x11,f[3],hash,counter);if(applied==1)present();return 4;}
 return applied;
}
#ifdef RABBIT_INTEGRATION_TEST
/* Host/QEMU observability only, not present in the Dell bootstrap. */
int rabbit_test_snapshot(uint8_t*out,uint32_t*n){if(guard(5))return 1;int r=export_state();if(!r){copy(out,snapshot,snapshot_length);*n=snapshot_length;}return guard(0)||r;}
const uint8_t *rabbit_test_base(void){return policy.base;}
uint32_t rabbit_test_pixel(unsigned i){return i<SURFACE_PIXELS?pixels[i]:0;}
#endif
