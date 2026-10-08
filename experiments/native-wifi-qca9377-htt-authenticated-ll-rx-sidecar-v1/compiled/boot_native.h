#ifndef RABBIT_QCA_BOOT_NATIVE_H
#define RABBIT_QCA_BOOT_NATIVE_H
#include "boot_transport.h"
#include "board_query.h"
#include "board_smbios.h"
#include "firmware_chunks.h"
typedef struct {
 QcaBootImage plan;QcaBmiLoader io;QcaBoardQuery*board;QcaFirmwareChunks*asset;
 uint64_t started,last;uint32_t phase,error,ready_bytes,credit_count,credit_size,max_endpoints;
 uint8_t owns_pin,ready[256];
} QcaBootNative;
/* Fresh active setup/query and exact PCI fallback: zero board/chip IDs, no
 * extended data, valid SMBIOS without BDF suffix. Full container is pinned
 * and rehashed before any command; main image and calibration hashes fixed. */
int qca_boot_native_begin(QcaBootNative*,QcaBoardQuery*,const QcaBoardSmbios*,QcaFirmwareChunks*,const uint8_t*,unsigned,uint64_t);
int qca_boot_native_poll(QcaBootNative*,uint64_t);
/* Caller has already stopped ALL CE DMA and released the actual adapter.
 * Otherwise retains asset pin and refuses unload, including after errors. */
int qca_boot_native_close(QcaBootNative*);
#endif
