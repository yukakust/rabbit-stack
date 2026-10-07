#ifndef QCA_HTT_FIRMWARE_OP_H
#define QCA_HTT_FIRMWARE_OP_H
#include "boot_native.h"
typedef struct {
 uint32_t valid,error,htt_op,wmi_op,htt_offset,main_offset,main_bytes;
 uint64_t generation;uint8_t digest[32],main_digest[32];
} QcaHttFirmwareProof;
/* Requires the existing authenticated, immutable pinned full asset. Copies
 * metadata/digests only; never re-pins, replaces firmware or issues commands. */
int qca_htt_firmware_proof(QcaHttFirmwareProof*,const QcaBootNative*);
#endif
