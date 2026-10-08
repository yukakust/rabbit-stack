#ifndef QCA_FIRMWARE_CHUNKS_H
#define QCA_FIRMWARE_CHUNKS_H
#include <stdint.h>
#include <stddef.h>
#define QCA_FW_CHUNK 65536u
#define QCA_FW_MAX (32u * QCA_FW_CHUNK)
#define QCA_FW_HEADER 224u
/* Policy comes from the reviewed owner/target adapter, never from a packet.
 * The adapter must obtain type/version from the physical BMI reply first. */
typedef struct {
 uint8_t owner[32],target[32],digest[32];
 uint32_t total,type,version,kind;
 uint64_t generation;
} QcaFirmwarePolicy;
typedef struct {
 QcaFirmwarePolicy policy;
 uint8_t *memory;
 size_t capacity;
 uint32_t received;
 uint8_t ready,poisoned,pinned;
} QcaFirmwareChunks;
int qca_fw_begin(QcaFirmwareChunks*,const QcaFirmwarePolicy*,uint8_t*,size_t);
/* 0 accepted, 1 exact duplicate, negative rejected. No hardware operation. */
int qca_fw_accept(QcaFirmwareChunks*,const uint8_t*,size_t);
int qca_fw_pin(QcaFirmwareChunks*,const uint8_t**,size_t*);
int qca_fw_unpin(QcaFirmwareChunks*);
int qca_fw_cancel(QcaFirmwareChunks*);
#endif
