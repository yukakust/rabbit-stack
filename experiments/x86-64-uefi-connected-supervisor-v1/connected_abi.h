#ifndef RABBIT_CONNECTED_ABI_H
#define RABBIT_CONNECTED_ABI_H
#include "scene_abi.h"
#include "file_core.h"
/* Privileged reviewed module, NOT a sandbox. init/health have no radio attach.
 * Exactly one root loop invokes poll. close must prove radio quiescence before
 * unload; failed close forbids unload. Root owns file staging/final receipt. */
#define CONNECTED_MAGIC 0x52434333u
typedef int(EFIAPI *DriverAttach)(SystemTable *,RfFile *);
typedef int(EFIAPI *DriverPoll)(void);
typedef int(EFIAPI *DriverClose)(void);
typedef uint32_t(EFIAPI *DriverCommand)(void);
typedef int(EFIAPI *DriverWorld)(const uint8_t *,uint32_t,Surface *,uint32_t *);
typedef struct {
 uint32_t magic,abi,size,state_abi;
 SceneInit init;SceneTick tick;SceneFrame frame;SceneExport snapshot;
 SceneValue receipt,counter;
 DriverAttach attach;DriverPoll poll;DriverClose close;
 DriverCommand command;DriverWorld world;
} ConnectedRegistration;
#endif
