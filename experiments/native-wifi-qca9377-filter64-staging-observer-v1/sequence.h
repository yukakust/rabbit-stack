/* HOST sender sequencing only. No native driver, timers or transport policy. */
#ifndef ASSET_OBSERVER_SEQUENCE_H
#define ASSET_OBSERVER_SEQUENCE_H
#include <stdint.h>
enum {AO_IDLE=0,AO_ASSET_READ=1,AO_PREFIX_READ=2,AO_WRITE=3,AO_STOP=4};
typedef struct {unsigned pending,observe;uint32_t floor;int action;} AoSequence;
static inline int ao_read(AoSequence*s,unsigned kind){if(!s||s->pending!=AO_IDLE||(kind!=AO_ASSET_READ&&kind!=AO_PREFIX_READ))return 0;s->pending=kind;return 1;}
static inline int ao_receipt(AoSequence*s,int action,uint32_t floor){if(!s||s->pending!=AO_ASSET_READ)return 0;s->pending=AO_IDLE;s->floor=floor;s->action=action;return 1;}
static inline int ao_prefix(AoSequence*s,int valid,uint32_t floor){if(!s||s->pending!=AO_PREFIX_READ)return 0;if(!valid||floor!=s->floor){s->pending=AO_STOP;return 0;}s->pending=AO_IDLE;return 1;}
static inline int ao_write(AoSequence*s,int sending){if(!s||!sending||s->pending!=AO_IDLE)return 0;s->pending=AO_WRITE;return 1;}
static inline int ao_ack(AoSequence*s){if(!s||s->pending!=AO_WRITE)return 0;s->pending=AO_IDLE;return 1;}
static inline void ao_stop(AoSequence*s){if(s)s->pending=AO_STOP;}
#endif
