#ifndef RABBIT_RNG_PUBLIC_PROVENANCE_H
#define RABBIT_RNG_PUBLIC_PROVENANCE_H
#include <stdint.h>
#include <stddef.h>
#define PR_API __attribute__((ms_abi))
typedef uint64_t PrStatus;
typedef struct {uint32_t a;uint16_t b,c;uint8_t d[8];} PrGuid;
typedef struct {void *get_info,*get_rng;} PrRng;
typedef struct {
 uint32_t revision;void *parent,*system,*device,*file_path,*reserved;
 uint32_t option_bytes;void *options,*base;uint64_t bytes;
 uint32_t code_type,data_type;void *unload;
} PrImage;
_Static_assert(offsetof(PrImage,base)==64 && sizeof(PrImage)==96,"UEFI x64 LoadedImage");
typedef struct {
 PrStatus(PR_API *locate)(PrGuid*,void*,void**);
 PrStatus(PR_API *handles)(uint32_t,PrGuid*,void*,size_t*,void***);
 PrStatus(PR_API *protocol)(void*,PrGuid*,void**);
 PrStatus(PR_API *free_pool)(void*);
} PrApi;
typedef struct {
 uint32_t rva,bytes,characteristics,reserved;uint8_t sha256[32];
} PrCode;
typedef struct {
 uint8_t magic[8];uint32_t version,bytes;uint64_t epoch;
 uint8_t adapter_sha256[32];uint32_t phase,error,provider_count,image_count;
 uint32_t matching_images,code_sections,owned_pools,uncertain_pools;
 uint64_t status,image_bytes;uint32_t info_offset,rng_offset;
 uint8_t fv_file_guid[16],fv_volume_guid[16];PrCode info_code,rng_code;
 uint32_t provenance_identified,entropy_approved,random_calls,msr_calls;
 uint8_t reserved[32];
} PrPublic;
typedef struct {
 PrApi api;void **rng_handles,**image_handles;PrRng *provider;
 size_t rng_count,image_count;unsigned rng_uncertain,image_uncertain;
 unsigned attempted,borrowed,closed;PrPublic public;
} PrSession;
/* Trusted firmware protocols are the pointer/mapping boundary. This does not
 * establish arbitrary-pointer validity or entropy provenance. Never invokes
 * GetRNG, an RNG instruction, MSR, flash, protocol write or unload callback.
 * Only read-only executable non-writable PE sections may be hashed. */
int pr_capture(PrSession*,const PrApi*,uint64_t,const uint8_t code_sha256[32]);
int pr_cleanup(PrSession*);
int pr_code(const uint8_t *loaded,size_t bytes,uintptr_t method,PrCode *out);
int pr_public(const PrSession*,PrPublic*);
extern const PrGuid pr_rng_guid,pr_loaded_guid;
#endif
