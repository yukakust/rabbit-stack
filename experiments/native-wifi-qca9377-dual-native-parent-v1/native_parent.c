#include "native_parent.h"
static int apart(const void*a,size_t n,const void*b,size_t m){return a&&b&&n&&m&&!mod_overlap(a,n,b,m);}
int dn_inventory(const DualNativeParent*p){
 if(!p||!p->attempted||!p->parent_image||!p->epoch)return 0;
 for(unsigned i=0;i<2;i++){
  if(p->owned[i]&&(!p->arena[i]||p->uncertain[i]))return 0;
  if(p->modules.artifact[i].memory&&(!p->owned[i]||p->arena[i]!=p->modules.artifact[i].memory))return 0;
 }
 if(p->arena[0]&&p->arena[1]&&!apart(p->arena[0],MOD_FILE_MAX,p->arena[1],MOD_FILE_MAX))return 0;
 return !p->bound||dual_inventory(&p->modules);
}
int dn_bind(DualNativeParent*p,SystemTable*s,void*h,uint64_t e,const uint8_t owner[32],const uint8_t target[32],const uint8_t hashes[2][32],DualRevoke revoke,void*ctx){
 if(!apart(p,sizeof *p,s,sizeof *s)||!h||!e||!owner||!target||!hashes||!revoke||!apart(p,sizeof *p,owner,32)||!apart(p,sizeof *p,target,32)||!apart(p,sizeof *p,hashes,64)||(ctx&&!apart(p,sizeof *p,ctx,1)))return -1;
 for(size_t i=0;i<sizeof *p;i++)if(((uint8_t*)p)[i])return -1;
 ModEfi ef={0};if(mod_efi_bind(&ef,s,h))return -1;
 void*raw=0;Status status=ef.protocol(h,&loaded_image_guid,&raw);
 if(status||!raw)return -1;LoadedImage*image=raw;
 if(!apart(p,sizeof *p,image,sizeof *image)||image->system!=s||!image->parent||!image->base||!image->size||image->size>MOD_AGGREGATE_MAX||image->size>UINTPTR_MAX-(uintptr_t)image->base)return -1;
 DnAllocate alloc=(DnAllocate)service(s,64);if(!alloc)return -1;
 p->attempted=1;p->efi=ef;p->parent_image=image;p->allocate=alloc;p->epoch=e;p->busy=1;
 for(unsigned i=0;i<2;i++){
  void*a=0;p->allocation_status[i]=alloc(2,MOD_FILE_MAX,&a);p->arena[i]=a;
  if(p->allocation_status[i]||!a){if(a||!p->allocation_status[i])p->uncertain[i]=1;p->fault=1;p->busy=0;return -1;}
  if(!apart(p,sizeof *p,a,MOD_FILE_MAX)||!apart(a,MOD_FILE_MAX,image,sizeof *image)||!apart(a,MOD_FILE_MAX,image->base,image->size)||!apart(a,MOD_FILE_MAX,s,sizeof *s)||(i&&!apart(a,MOD_FILE_MAX,p->arena[0],MOD_FILE_MAX))){p->uncertain[i]=1;p->fault=1;p->busy=0;return -1;}
  p->owned[i]=1;mod_wipe(a,MOD_FILE_MAX);
 }
 if(dual_bind(&p->modules,&p->efi,e,(uint32_t)image->size,owner,target,hashes,revoke,ctx)){p->fault=1;p->busy=0;return -1;}
 p->bound=1;p->busy=0;return dn_inventory(p)?0:-1;
}
int dn_accept(void*context,const uint8_t*b,size_t n){
 DualNativeParent*p=context;if(!p||!p->bound||p->fault||p->closed||p->busy||!dn_inventory(p)||n<MOD_HEADER||!apart(p,sizeof *p,b,n))return -1;
 uint32_t role=(uint32_t)b[196]|(uint32_t)b[197]<<8|(uint32_t)b[198]<<16|(uint32_t)b[199]<<24;if(role<1||role>2||!p->owned[role-1])return -1;
 p->busy=1;int r=dual_accept(&p->modules,b,n,p->arena[role-1],MOD_FILE_MAX);p->busy=0;
 if(!dn_inventory(p)||p->modules.quarantine){p->fault=1;return -1;}return r;
}
int dn_close(DualNativeParent*p,uint64_t e){
 if(!p||!p->attempted||p->busy||p->epoch!=e||!dn_inventory(p))return -1;if(p->closed)return 0;
 if(p->uncertain[0]||p->uncertain[1])return -1;
 p->busy=1;if(p->bound&&dual_close(&p->modules,e)){p->busy=0;return -1;}
 for(unsigned i=0;i<2;i++)if(p->owned[i]){
  mod_wipe(p->arena[i],MOD_FILE_MAX);p->free_status[i]=p->efi.free_pool(p->arena[i]);
  if(p->free_status[i]){p->owned[i]=0;p->uncertain[i]=1;p->fault=1;p->busy=0;return -1;}
  p->arena[i]=0;p->owned[i]=0;
 }
 p->closed=1;p->busy=0;return 0;
}
