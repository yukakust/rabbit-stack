#ifndef RABBIT_QCA_BOOT_IMAGE_H
#define RABBIT_QCA_BOOT_IMAGE_H
#include <stdint.h>
#include <stddef.h>
typedef struct {
 const uint8_t *board,*helper,*main;
 uint32_t board_bytes,helper_bytes,main_bytes;
} QcaBootAssets;
typedef struct {
 QcaBootAssets assets;
 uint32_t phase,error,offset,board_address,option_flags,submitted,completed,calibration_result;
 uint32_t request_bytes,response_bytes,issued_phase,issued_bytes;
 uint8_t request[256],pending;
} QcaBootImage;
/* Pure command planner, not a DMA adapter. Caller must separately prove fresh
 * exclusive setup, exact PCI/SMBIOS/board query and pinned asset ownership.
 * Hashes below admit only the reviewed Dell 1028:1810 data and pinned images.
 * Completion 20 means BMI_DONE completed, NOT HTC/WMI ready or Wi-Fi connected.
 * No SOC, NVRAM, flash-section or permanent OTP programming command exists. */
int qca_boot_image_begin(QcaBootImage*,const QcaBootAssets*);
int qca_boot_image_request(QcaBootImage*,const uint8_t**,unsigned*,unsigned*);
int qca_boot_image_complete(QcaBootImage*,const uint8_t*,unsigned);
int qca_boot_image_validate(const QcaBootImage*);
#endif
