/* Reviewed privileged Scene driver. It is not a native-code sandbox.
 * The old monolithic core is compiled unchanged into this resident driver.
 * Its GOP bootstrap is never invoked: all rendering uses a supervisor surface. */
#include "scene_abi.h"
#include "runtime_core.c"
#ifndef SCENE_REVISION
#define SCENE_REVISION 1
#endif
static void put16(uint8_t*p,uint16_t v){p[0]=v;p[1]=v>>8;}
static void put32(uint8_t*p,uint32_t v){put16(p,v);put16(p+2,v>>16);}
static int surface(Surface*s){
 if(!s||!s->pixels||s->width!=480||s->height!=270||s->stride!=480||s->format!=1)return 1;
 framebuffer=s->pixels;width=s->width;height=s->height;stride=s->stride;pixel_format=s->format;ready=1;return 0;
}
static int EFIAPI scene_export(uint8_t*out,uint32_t capacity,uint32_t*n){
 uint32_t length=32+active_length+object_count*16;
 if(!out||!n||capacity<length)return 1;
 for(uint32_t i=0;i<length;i++)out[i]=0;
 out[0]='R';out[1]='S';out[2]='S';out[3]='2';put32(out+4,length);
 put32(out+8,tick);put32(out+12,last_counter);put32(out+16,active_length);out[20]=object_count;
 for(uint32_t i=0;i<active_length;i++)out[32+i]=active_package[i];
 for(uint8_t i=0;i<object_count;i++){
  uint8_t*p=out+32+active_length+i*16;struct object_state*o=objects+i;
  p[0]=o->id;p[1]=o->sprite;p[2]=o->program;p[3]=o->frame;put16(p+4,o->x);put16(p+6,o->y);
  p[8]=o->vx;p[9]=o->vy;p[10]=o->target;
 }
 *n=length;return 0;
}
static int EFIAPI scene_init(const uint8_t*p,uint32_t n,Surface*s){
 if(surface(s)||!p||n<32||n>SNAPSHOT_MAX||p[0]!='R'||p[1]!='S'||p[2]!='S'||p[3]!='2'||le32(p+4)!=n)return 1;
 uint32_t length=le32(p+16);uint8_t count=p[20],checked=0;
 if(length>MAX_PACKAGE||count>16||n!=32+length+count*16)return 1;
 for(unsigned i=21;i<32;i++)if(p[i])return 1;
 if(!length){if(count||le32(p+12))return 1;}
 else if(validate_package(p+32,length,0,provisional,&checked)||checked!=count||le32(p+12)!=le32(p+40))return 1;
 for(uint8_t i=0;i<count;i++){
  const uint8_t*q=p+32+length+i*16;struct object_state*o=provisional+i;
  if(q[0]!=o->id||q[1]!=o->sprite||q[2]!=o->program||q[10]!=o->target||q[11]||le32(q+12))return 1;
  int x=(int16_t)le16(q+4),y=(int16_t)le16(q+6),vx=(int8_t)q[8],vy=(int8_t)q[9];
  if(x<-16||x>160||y<-16||y>90||vx<-8||vx>8||vy<-8||vy>8)return 1;
  o->x=x;o->y=y;o->vx=vx;o->vy=vy;o->frame=q[3];
 }
 for(uint32_t i=0;i<length;i++)active_package[i]=p[32+i];
 for(uint8_t i=0;i<count;i++)objects[i]=provisional[i];
 active_length=length;object_count=count;last_counter=le32(p+12);tick=le32(p+8);
 receiving=0;last_hash=length?fnv(active_package,length):0;
 staging_transfer=(uint8_t)last_hash;if(!staging_transfer)staging_transfer=1;
 if(length)draw_scene(active_package,objects,count);else fill(0x121826);
#if SCENE_REVISION == 3
 return 1; /* Deliberate reviewed unhealthy driver fixture. */
#else
 return 0;
#endif
}
static int EFIAPI scene_tick(Surface*s){
 if(surface(s))return 1;
 int result=rabbit_scene_tick(0);
#if SCENE_REVISION == 2
 /* Visible engine-only revision; asset/world bytes are not changed. */
 for(unsigned x=0;x<480;x++)framebuffer[269*480+x]=0x3366ff;
#endif
 return result;
}
static int EFIAPI scene_frame(const uint8_t*f,Surface*s){if(surface(s))return 3;return rabbit_package_frame(f,0);}
static uint32_t EFIAPI scene_receipt(void){return rabbit_package_last_hash();}
static uint32_t EFIAPI scene_counter(void){return last_counter;}
static Status EFIAPI unload(void*h){(void)h;return 0;}
Status EFIAPI module_entry(void *handle,SystemTable *st){
 LoadedImage *image=0;
 if(((HandleProtocol)service(st,152))(handle,&loaded_image_guid,(void**)&image)||!image||image->options_size!=sizeof(SceneRegistration)||!image->options)return EFI_ERROR(2);
 SceneRegistration*r=image->options;
 if(r->magic!=SCENE_MAGIC||r->abi!=2||r->state_abi!=2||r->size!=sizeof(*r))return EFI_ERROR(2);
 r->init=scene_init;r->tick=scene_tick;r->frame=scene_frame;r->snapshot=scene_export;r->receipt=scene_receipt;r->counter=scene_counter;
 image->unload=unload;return 0;
}
