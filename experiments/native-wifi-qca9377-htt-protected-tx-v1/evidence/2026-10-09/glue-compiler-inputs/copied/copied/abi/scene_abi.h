#ifndef RABBIT_SCENE_ABI_H
#define RABBIT_SCENE_ABI_H
#include "abi.h"
#define SCENE_MAGIC 0x52525332u
#define SNAPSHOT_MAX (32u+65535u+16u*16u)
#define SURFACE_PIXELS (480u*270u)
typedef struct { uint32_t *pixels; uint32_t width,height,stride,format; } Surface;
typedef int (EFIAPI *SceneInit)(const uint8_t *,uint32_t,Surface *);
typedef int (EFIAPI *SceneTick)(Surface *);
typedef int (EFIAPI *SceneFrame)(const uint8_t *,Surface *);
typedef int (EFIAPI *SceneExport)(uint8_t *,uint32_t,uint32_t *);
typedef uint32_t (EFIAPI *SceneValue)(void);
typedef struct {
 uint32_t magic,abi,size,state_abi;
 SceneInit init; SceneTick tick; SceneFrame frame; SceneExport snapshot;
 SceneValue receipt,counter;
} SceneRegistration;
void EFIAPI rabbit_supervisor_entry(void *,SystemTable *);
int EFIAPI rabbit_scene_bootstrap(void *);
int EFIAPI rabbit_scene_tick(void *);
int EFIAPI rabbit_package_frame(const uint8_t *,void *);
void EFIAPI rabbit_receipt_write(uint8_t *);
#endif
