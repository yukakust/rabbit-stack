#ifndef RABBIT_GATT_CORE_H
#define RABBIT_GATT_CORE_H
#include "file_core.h"
#define RG_MTU_MAX 247u
typedef struct { RfFile file; RfFile *shared; uint16_t mtu; } RgServer;
void rg_init(RgServer *,RfApply);
void rg_init_shared(RgServer *,RfFile *); /* Supervisor owns staging across unload. */
void rg_disconnected(RgServer *); /* Retain staging, reset negotiated bearer MTU. */
size_t rg_att(RgServer *,const uint8_t *,size_t,uint8_t *,size_t);
#endif
