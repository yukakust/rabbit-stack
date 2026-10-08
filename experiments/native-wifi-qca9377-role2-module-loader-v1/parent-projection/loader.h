#ifndef RABBIT_PRIVATE_MODULE_LOADER
#define RABBIT_PRIVATE_MODULE_LOADER
#include "artifact.h"
#include "module_abi.h"
typedef Status(EFIAPI*ModLoad)(uint8_t,void*,void*,void*,uint64_t,void**);
typedef Status(EFIAPI*ModStart)(void*,uint64_t*,uint16_t**);
typedef Status(EFIAPI*ModUnload)(void*);
typedef Status(EFIAPI*ModFree)(void*);
typedef struct {SystemTable*system;void*parent;ModLoad load;ModStart start;ModUnload unload;HandleProtocol protocol;ModFree free_pool;} ModEfi;
typedef struct {uint32_t mapped;uint64_t last_counter,epoch;uint8_t parent_hash[32];} ModBudget;
typedef struct {ModArtifact*artifact;ModBudget*budget;ModEfi efi;void*handle;LoadedImage*image;ModRegistration registration;uint32_t reserved_mapped,active,quarantine,attempted,unload_attempted,stage;uint64_t status,unload_status;uint16_t*exit_data;uint64_t exit_size;} ModLoader;
/* Caller owns valid reviewed firmware pointers. Bound services are never mocked
 * as production. Injected services in tests are explicit synthetic firmware. */
int mod_efi_bind(ModEfi*,SystemTable*,void*);
int mod_load(ModLoader*,ModArtifact*,ModBudget*,const ModEfi*);
/* op0 is mandatory child lifetime close. Never wipe code before UnloadImage. */
int mod_unload(ModLoader*);
#endif
