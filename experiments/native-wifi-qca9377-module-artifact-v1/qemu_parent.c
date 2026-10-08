/* Dedicated QEMU bootstrap fixture only, not the immutable Dell bootstrap. */
#include "loader.h"
#include "fixture.h"
static ModArtifact artifact;static ModLoader loader;static ModBudget budget;static uint8_t memory[MOD_FILE_MAX];
static void say(const char*s){while(*s){__asm__ volatile("outb %0,%1"::"a"((uint8_t)*s++),"Nd"((uint16_t)0xe9));}}
Status EFIAPI probe_entry(void*parent,SystemTable*st){
 ModEfi e;if(mod_efi_bind(&e,st,parent)){say("FAIL EFI BIND\n");return EFI_ERROR(3);}
 budget.mapped=2224128;budget.epoch=7;budget.last_counter=1;for(unsigned i=0;i<32;i++)budget.parent_hash[i]=fixture_policy.parent_hash[i];
 if(mod_begin(&artifact,&fixture_policy,memory,sizeof(memory))){say("FAIL BEGIN\n");return EFI_ERROR(3);}
 for(unsigned i=0;i<FIXTURE_CHUNKS;i++)if(mod_accept(&artifact,fixture_frames[i],fixture_sizes[i])){say("FAIL SIGNED CHUNK\n");return EFI_ERROR(3);}say("REAL OWNER FIXTURE SIGNATURES VERIFIED\n");
 if(mod_load(&loader,&artifact,&budget,&e)){say("FAIL LOAD START REGISTRATION\n");return EFI_ERROR(3);}say("REAL UEFI LOAD START PRIVATE OPTIONS PASS\n");
 typedef struct {uint64_t epoch;uint32_t initialized,ready,fault,heap_live,quarantine;int tls_error;} PublicStatus;
 PublicStatus status={.epoch=7};if(loader.registration.dispatch(7,&status)||status.initialized||status.ready||status.heap_live){say("FAIL UNINITIALIZED STATUS\n");return EFI_ERROR(3);}
 if(mod_unload(&loader)||artifact.memory||budget.mapped!=2224128){say("FAIL UNLOAD BEFORE WIPE\n");return EFI_ERROR(3);}say("REAL UEFI UNLOAD BEFORE ARTIFACT WIPE PASS\n");
 for(unsigned i=0;i<sizeof(memory);i++)if(memory[i]){say("FAIL WIPE\n");return EFI_ERROR(3);}say("MODULE CHILD QEMU PASS NO RNG TLS CREDENTIAL RADIO CALLS\n");return 0;
}
