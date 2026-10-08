#include "parent_glue.h"
#include "loader.h"
#include "inventory.h"
#include "module_platform.h"
#include "reference/monocypher-ed25519.h"
typedef Status(EFIAPI*InstallParentProtocol)(void**,const Guid*,uint32_t,void*);
typedef Status(EFIAPI*UninstallParentProtocol)(void*,const Guid*,void*);
static const Guid parent_module_protocol_guid={0xd8cbf3de,0xd7ae,0x4a64,{0x97,0xe1,0x77,0x9a,0x6e,0xc8,0x8d,0xad}};
static struct {ModEfi efi;ModBudget budget;ModArtifact artifact;ModLoader loader;ProtectedArena arena;RngBootApi boot;InvRecord cpu;uint8_t owner[32],target[32];unsigned bound,quarantine,closing,users,busy,installed,install_attempted,uninstall_attempted;void*protocol_handle;InstallParentProtocol install;UninstallParentProtocol uninstall;ParentModuleProtocol protocol;} parent;
static int PARENT_PROTO_API protocol_lease(uint64_t e){if(!parent.bound||parent.quarantine||parent.closing||parent.users||e!=parent.budget.epoch)return 0;parent.users=1;return 1;}
static int PARENT_PROTO_API protocol_release(uint64_t e){if(parent.busy||parent.users!=1||e!=parent.budget.epoch)return 0;parent.users=0;return 1;}
static int PARENT_PROTO_API protocol_accept(const uint8_t*p,size_t n){if(parent.users!=1||parent.busy||parent.closing)return -1;parent.busy=1;int result=parent_module_accept(p,n);parent.busy=0;return result;}
static int PARENT_PROTO_API protocol_cpu(void*p,size_t n){if(parent.users!=1||parent.busy)return 0;parent.busy=1;int result=parent_cpu_export(p,n);parent.busy=0;return result;}
extern int runtime_rng_public(RngPublicDiagnostic*);
static int PARENT_PROTO_API protocol_rng_info(void*out,size_t n){if(parent.users!=1||parent.busy||!out||n!=sizeof(RngPublicDiagnostic)||mod_overlap(out,n,&parent,sizeof(parent)))return 0;RngPublicDiagnostic value;parent.busy=1;int result=runtime_rng_public(&value);if(result){uint8_t*d=out,*s=(uint8_t*)&value;for(size_t i=0;i<n;i++)d[i]=s[i];}mod_wipe(&value,sizeof(value));parent.busy=0;return result;}
static uint32_t le32(const uint8_t*p){return p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static uint64_t le64(const uint8_t*p){return le32(p)|((uint64_t)le32(p+4)<<32);}
static int same(const uint8_t*a,const uint8_t*b,size_t n){uint8_t x=0;for(size_t i=0;i<n;i++)x|=a[i]^b[i];return !x;}
int parent_module_bind(void*handle,void*system,uint64_t epoch,const uint8_t owner[32],const uint8_t target[32],const uint8_t code[32]){
 if(parent.bound||parent.quarantine||!handle||!system||!epoch||!owner||!target||!code||mod_overlap(owner,32,&parent,sizeof(parent))||mod_overlap(target,32,&parent,sizeof(parent))||mod_overlap(code,32,&parent,sizeof(parent)))return 0;
 ModEfi e;if(mod_efi_bind(&e,system,handle)||!module_protected_boot_api(system,&parent.boot))return 0;
 void*p=0;if(e.protocol(handle,&loaded_image_guid,&p)||!p)return 0;LoadedImage*image=p;
 if(image->system!=system||!image->base||!image->size||image->size>MOD_AGGREGATE_MAX||image->size>UINTPTR_MAX-(uintptr_t)image->base)return 0;
 uint8_t a=0,b=0;for(unsigned i=0;i<32;i++){a|=owner[i];b|=target[i];}if(!a||!b)return 0;
 parent.efi=e;parent.budget.mapped=(uint32_t)image->size;parent.budget.epoch=epoch;for(unsigned i=0;i<32;i++){parent.owner[i]=owner[i];parent.target[i]=target[i];}
 /* CPU instructions only public inventory, never hardware RNG or MSR. */
 if(inv_capture(&parent.cpu,inv_cpuid_native,0,epoch,code))return 0;
 parent.bound=1;parent.install=(InstallParentProtocol)service(system,128);parent.uninstall=(UninstallParentProtocol)service(system,144);if(!parent.install||!parent.uninstall){parent.quarantine=1;return 0;}
 parent.protocol=(ParentModuleProtocol){PARENT_MODULE_PROTOCOL_MAGIC,1,sizeof(ParentModuleProtocol),epoch,0,0,protocol_lease,protocol_release,protocol_accept,protocol_cpu,protocol_rng_info};parent.protocol_handle=handle;parent.install_attempted=1;
 Status installed=parent.install(&parent.protocol_handle,&parent_module_protocol_guid,0,&parent.protocol);if(installed||parent.protocol_handle!=handle){parent.quarantine=1;return 0;}parent.installed=1;return 1;
}
int parent_module_accept(const uint8_t*p,size_t n){
 if(!parent.bound||parent.quarantine||parent.closing||!p||n<MOD_HEADER||n>MOD_HEADER+MOD_CHUNK||mod_overlap(p,n,&parent,sizeof(parent)))return -1;
 if(!parent.artifact.memory){
  if(parent.loader.attempted||!same(p,(const uint8_t*)"RABMOD01",8)||!same(p+8,parent.owner,32)||!same(p+40,parent.target,32)||le64(p+168)!=parent.budget.epoch||le64(p+176)<=parent.budget.last_counter||le32(p+196)!=1||le32(p+200)!=1||crypto_ed25519_check(p+224,parent.owner,p,224))return -1;
  ModPolicy q={0};for(unsigned i=0;i<32;i++){q.owner[i]=parent.owner[i];q.target[i]=parent.target[i];q.parent_hash[i]=p[72+i];q.digest[i]=p[104+i];}q.epoch=parent.budget.epoch;q.counter=le64(p+176);q.last_counter=parent.budget.last_counter;q.total=le32(p+184);q.mapped=le32(p+204);q.role=1;q.abi=1;
  if(!q.total||q.total>MOD_FILE_MAX||!q.mapped||q.mapped>MOD_AGGREGATE_MAX-parent.budget.mapped)return -1;
  if(!module_protected_arena_open(&parent.arena,&parent.boot,q.epoch,MOD_FILE_MAX)){parent.quarantine=1;return -1;}
  /* Exact parent file hash is owner assertion, not relocation-blind selfhash.
   * Root must verify actual installed signed parent before child signing. */
  for(unsigned i=0;i<32;i++)parent.budget.parent_hash[i]=q.parent_hash[i];
  void*loan=0;size_t loan_bytes=0;if(!module_protected_arena_borrow(&parent.arena,q.epoch,0,&loan,&loan_bytes)){parent.quarantine=1;return -1;}
  if(mod_begin(&parent.artifact,&q,loan,loan_bytes)){parent.quarantine=1;return -1;}
 }
 int rc=mod_accept(&parent.artifact,p,n);if(rc<0)return rc;
 if(parent.artifact.ready&&!parent.loader.attempted){if(mod_load(&parent.loader,&parent.artifact,&parent.budget,&parent.efi)){parent.quarantine=1;return -1;}}
 return rc;
}
int parent_module_close(void){
 if(parent.quarantine||parent.loader.quarantine||parent.arena.uncertain||parent.users||parent.busy)return 0;
 parent.closing=1;
 if(parent.loader.active&&mod_unload(&parent.loader)){parent.quarantine=1;return 0;}
 if(parent.artifact.pinned)return 0;
 if(parent.artifact.memory&&mod_cancel(&parent.artifact)){parent.quarantine=1;return 0;}
 if(parent.arena.users&&!module_protected_arena_return(&parent.arena,parent.budget.epoch,0)){parent.quarantine=1;return 0;}
 if(parent.arena.base&&!module_protected_arena_close(&parent.arena,parent.budget.epoch)){parent.quarantine=1;return 0;}
 if(parent.installed){if(parent.uninstall_attempted){parent.quarantine=1;return 0;}parent.uninstall_attempted=1;Status removed=parent.uninstall(parent.protocol_handle,&parent_module_protocol_guid,&parent.protocol);if(removed){parent.quarantine=1;return 0;}parent.installed=0;parent.protocol_handle=0;}
 return parent_module_released();
}
int parent_module_released(void){return !parent.quarantine&&!parent.users&&!parent.busy&&!parent.installed&&!parent.loader.active&&!parent.loader.handle&&!parent.loader.quarantine&&!parent.artifact.memory&&!parent.artifact.pinned&&!parent.arena.base&&!parent.arena.users&&!parent.arena.uncertain;}
int parent_cpu_export(void*out,size_t n){if(!parent.bound||!out||n!=sizeof(parent.cpu)||mod_overlap(out,n,&parent,sizeof(parent)))return 0;uint8_t*d=out,*s=(uint8_t*)&parent.cpu;for(size_t i=0;i<n;i++)d[i]=s[i];return 1;}
