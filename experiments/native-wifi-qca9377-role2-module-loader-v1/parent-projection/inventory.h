#ifndef RABBIT_PUBLIC_CPUID_INVENTORY
#define RABBIT_PUBLIC_CPUID_INVENTORY
#include <stdint.h>
#include <stddef.h>
#define INV_API __attribute__((ms_abi))
typedef struct {uint32_t a,b,c,d;} InvLeaf;
typedef int(INV_API*InvCpuid)(void*,uint32_t,uint32_t,InvLeaf*);
typedef struct {uint8_t magic[8];uint32_t version,size;uint64_t epoch;uint8_t source_sha256[32];uint32_t flags,leaf_count;InvLeaf leaf[7];uint8_t vendor[12],brand[48];uint32_t entropy_approved,msr_status,reserved[2];} InvRecord;
_Static_assert(sizeof(InvRecord)==256,"public diagnostic exactly256");
/* flags:1 GenuineIntel,2 RDSEED enumerated,4 hypervisor,8 SRBDS_CTRL.
 * msr_status always0=NOT_READ; entropy_approved always0. No entropy output. */
int inv_capture(InvRecord*,InvCpuid,void*,uint64_t,const uint8_t[32]);
/* Real x86 CPUID wrapper exists for future explicit parent invocation. Tests
 * ONLY inject synthetic CPUID, NEVER call this function or hardware RNG/MSR. */
int INV_API inv_cpuid_native(void*,uint32_t,uint32_t,InvLeaf*);
#endif
