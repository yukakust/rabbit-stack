#ifndef QCA_PURE_HTT_RX_DECODE_H
#define QCA_PURE_HTT_RX_DECODE_H
#include <stdint.h>
#define QRX_MAX 255
#define QRX_OWNER_MAX 2048
#define QRX_RAW 2048
/* Local bounded profile, not firmware constants. States POSTED1/OWNED2/RETIRED3. */
typedef struct {uint32_t paddr,bytes,state;uint64_t epoch,completion,map_identity;} QRxOwner;
typedef struct {unsigned op,major,minor,full_reorder;uint64_t epoch,floor,last;unsigned count;QRxOwner *owners;} QRxRing;
typedef struct {unsigned kind,usable,reason,tid,peer,vdev,count,fw_bytes,ranges,mpdu_count,flush,release,offload,frag;uint32_t paddr[QRX_MAX];uint16_t length[QRX_MAX];uint8_t fw_desc[QRX_MAX],range_status[QRX_MAX],range_count[QRX_MAX];uint64_t epoch,completion;unsigned raw_bytes;uint8_t raw[QRX_RAW];} QRxInd;
typedef struct {unsigned bytes,attention,seq,decap,first,last,encrypted;uint8_t payload[1748];} QRxFrame;
/* Return0 malformed/no output;1 known structural message;2 owned unknown raw. */
int qrx_indication(unsigned op,unsigned major,unsigned minor,uint64_t epoch,uint64_t completion,uint64_t floor,const uint8_t*,unsigned,QRxInd*);
/* INORD only; all addresses atomically POSTED->OWNED. No dereference/unmap/free. */
int qrx_claim(QRxRing*,const QRxInd*);
int qrx_retire(QRxRing*,uint32_t paddr,uint64_t epoch,uint64_t completion);
/* Caller supplies coherent completed descriptor bytes; raw singleMSDU only. */
int qrx_frame(const uint8_t*,unsigned,unsigned expected_length,QRxFrame*);
#endif
