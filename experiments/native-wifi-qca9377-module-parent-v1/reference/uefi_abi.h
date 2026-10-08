#ifndef RABBIT_SUPERVISOR_ABI_H
#define RABBIT_SUPERVISOR_ABI_H
#include <stdint.h>
#include <stddef.h>
#define EFIAPI __attribute__((ms_abi))
typedef uint64_t Status;
typedef struct { uint32_t a; uint16_t b,c; uint8_t d[8]; } Guid;
typedef struct { uint64_t signature; uint32_t revision,size,crc,reserved; } TableHeader;
typedef struct {
    TableHeader header; void *vendor; uint32_t revision,padding;
    void *in_handle,*input,*out_handle,*output,*err_handle,*error,*runtime,*boot;
    uint64_t tables; void *configuration;
} SystemTable;
typedef struct LoadedImage LoadedImage;
struct LoadedImage {
    uint32_t revision,padding; void *parent; SystemTable *system;
    void *device,*path,*reserved; uint32_t options_size,padding2; void *options;
    void *base; uint64_t size; uint32_t code_type,data_type;
    Status (EFIAPI *unload)(void *);
};
static const Guid loaded_image_guid = {0x5b1b31a1,0x9562,0x11d2,{0x8e,0x3f,0,0xa0,0xc9,0x69,0x72,0x3b}};
typedef struct { uint32_t ticks,color,tag,reserved; } RabbitState;
typedef int (EFIAPI *ModuleCall)(RabbitState *);
typedef struct { uint32_t magic,abi,size,state_abi; ModuleCall init,tick; } ModuleRegistration;
#define REGISTRATION_MAGIC 0x52525431u
#define STATE_TAG 0x52414242u
#define EFI_ERROR(x) (0x8000000000000000ull | (x))
static inline void *service(SystemTable *st, size_t offset) {
    return *(void **)((uint8_t *)st->boot + offset);
}
typedef Status (EFIAPI *HandleProtocol)(void *, const Guid *, void **);
_Static_assert(offsetof(SystemTable,output)==64,"ConOut offset");
_Static_assert(offsetof(SystemTable,boot)==96,"BootServices offset");
_Static_assert(offsetof(LoadedImage,options)==56,"LoadOptions offset");
_Static_assert(sizeof(RabbitState)==16,"state ABI");
#endif
