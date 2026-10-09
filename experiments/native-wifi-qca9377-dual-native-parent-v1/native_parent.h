#ifndef RABBIT_DIRECT_DUAL_NATIVE_PARENT
#define RABBIT_DIRECT_DUAL_NATIVE_PARENT
#include "dual.h"
typedef Status(EFIAPI*DnAllocate)(uint32_t,uint64_t,void**);
typedef struct {
 DualModules modules;ModEfi efi;LoadedImage*parent_image;
 DnAllocate allocate;uint8_t*arena[2];
 unsigned owned[2],uncertain[2],attempted,bound,busy,closed,fault;
 uint64_t epoch,allocation_status[2],free_status[2];
} DualNativeParent;
/* Called only by validated native module_entry with its actual h/st, compiled
 * candidate epoch/owner/target/exact reviewed child file digests. No GATT bind
 * request or extra installed public protocol. Root separately proves current
 * signed parent file hash before signing child assertions; relocated-image
 * hashing is not that proof. Base mapped charge comes from real LoadedImage. */
int dn_bind(DualNativeParent*,SystemTable*,void*,uint64_t,const uint8_t[32],const uint8_t[32],const uint8_t[2][32],DualRevoke,void*);
/* Private deferred mt_accept hook outside all ATT/HCI callbacks. */
int dn_accept(void*,const uint8_t*,size_t);
int dn_inventory(const DualNativeParent*);
int dn_close(DualNativeParent*,uint64_t);
#endif
