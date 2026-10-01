/* Reviewed QEMU fixtures only. EFI boot-services driver, not a world package. */
#include "abi.h"
#ifndef MODULE_MODE
#define MODULE_MODE 1
#endif
static int EFIAPI initialize(RabbitState *state) {
    if (state->tag != STATE_TAG || state->reserved) return 1;
#if MODULE_MODE == 5
    const char *marker="NATIVE HUNG INIT ENTERED\n";
    for(unsigned i=0;marker[i];i++)
        __asm__ volatile("outb %0, %1"::"a"((uint8_t)marker[i]),"Nd"((uint16_t)0xe9));
    for (;;) __asm__ volatile("pause"); /* Deliberate cooperative-interrupt hang. */
#elif MODULE_MODE == 3
    state->ticks = 999; state->color = 0; return 1; /* Trial must not leak state. */
#else
    state->color = MODULE_MODE == 1 ? 0x22cc66u : 0x3366ffu;
    return 0;
#endif
}
static int EFIAPI tick(RabbitState *state) {
    if (state->tag != STATE_TAG || state->ticks >= 1000) return 1;
    state->ticks++; return 0;
}
static Status EFIAPI unload(void *handle) { (void)handle; return 0; }
Status EFIAPI module_entry(void *handle, SystemTable *system) {
    LoadedImage *image = 0;
    HandleProtocol query = (HandleProtocol)service(system,152);
    if (query(handle,&loaded_image_guid,(void **)&image) || !image ||
        image->options_size != sizeof(ModuleRegistration) || !image->options)
        return EFI_ERROR(2);
    ModuleRegistration *registration = image->options;
    if (registration->magic != REGISTRATION_MAGIC || registration->abi != 1 ||
        registration->size != sizeof(*registration) || registration->state_abi != 1)
        return EFI_ERROR(2);
    registration->init = initialize; registration->tick = tick;
#if MODULE_MODE == 4
    registration->abi = 2; /* Signed but incompatible module handshake. */
#endif
    image->unload = unload;
    return 0; /* Driver remains resident; an EFI application would be unloaded. */
}
