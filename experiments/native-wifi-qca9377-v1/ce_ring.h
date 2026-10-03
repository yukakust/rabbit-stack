#ifndef RABBIT_QCA_CE_RING_H
#define RABBIT_QCA_CE_RING_H
#include <stdint.h>
#define QCA_CE_MAX_ENTRIES 32u
/* QCA9377 descriptor is little-endian address32/length16/flags16. */
typedef int (*QcaCePublish)(void*,uint32_t);
typedef int (*QcaCeStop)(void*);
typedef struct {
 volatile uint8_t*descriptors;
 QcaCePublish publish;QcaCeStop stop;void*context;
 uint32_t cookie[QCA_CE_MAX_ENTRIES],address[QCA_CE_MAX_ENTRIES];
 uint16_t capacity[QCA_CE_MAX_ENTRIES];
 uint8_t entries,read,write,published,receive,owned,fault;
} QcaCeRing;
/* Zero initialize the ring before first init. DMA mapping belongs to adapter. */
int qca_ce_init(QcaCeRing*,volatile uint8_t*,uint64_t,uint32_t,int,QcaCePublish,QcaCeStop,void*);
/* meta <=0x3fff; flags bit0=gather, bit1=byte swap, target facts. RX flags/meta0. */
/* Adapter proves engine halted; seed only an empty ring before hardware run. */
int qca_ce_seed(QcaCeRing*,unsigned);
int qca_ce_post(QcaCeRing*,uint64_t,uint32_t,uint32_t,uint32_t,uint32_t);
/* index is the adapter-decoded hardware read index. Never trust a device pointer. */
int qca_ce_complete(QcaCeRing*,uint32_t,uint32_t*,uint32_t*);
/* stop MUST verify engines stopped, bus master off, and DMA flush before success.
 * Failed stop retains descriptors/mapping; caller cannot free/unmap memory. */
int qca_ce_close(QcaCeRing*);
#endif
