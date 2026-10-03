#ifndef RABBIT_QCA_ROM_READY_H
#define RABBIT_QCA_ROM_READY_H
#include "uefi_port.h"
enum {QCA_ROM_IDLE,QCA_ROM_WAIT,QCA_ROM_READY,QCA_ROM_FAULT};
typedef struct {QcaUefiPort*port;uint64_t started,last,next;uint32_t indicator,reads,error;uint8_t phase;} QcaRomReady;
/* Call only after reset completion, validated PCI/MEM/D0 and wake acquisition. */
int qca_rom_begin(QcaRomReady*,QcaUefiPort*,uint64_t);
int qca_rom_poll(QcaRomReady*,uint64_t);
#endif
