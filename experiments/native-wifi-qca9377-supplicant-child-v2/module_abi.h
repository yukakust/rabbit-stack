#ifndef RABBIT_PRIVATE_MODULE_ABI
#define RABBIT_PRIVATE_MODULE_ABI
#include "reference/uefi_abi.h"
#define MOD_REG_MAGIC UINT64_C(0x31474552444f4d52)
/* New parent-private ABI. Privileged native code, NOT a sandbox/bootstrap ABI. */
typedef Status(EFIAPI*ModDispatch)(uint32_t,void*);
typedef struct {uint64_t magic;uint32_t abi,size,role,reserved;uint64_t epoch,counter;uint8_t digest[32],parent_hash[32];ModDispatch dispatch;} ModRegistration;
_Static_assert(sizeof(ModRegistration)==112,"private child registration");
#endif
