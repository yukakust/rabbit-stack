#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wmisleading-indentation"
#pragma GCC diagnostic ignored "-Warray-parameter"
#include "ring.h"
static void w16(uint8_t*p,unsigned v){p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);}
static void w32(uint8_t*p,uint32_t v){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(v>>(8*i));}
static int overlap(const void*a,size_t n,const void*b,size_t m){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;return x>UINTPTR_MAX-n||y>UINTPTR_MAX-m||(x<y?y-x<n:x-y<m);}
static int equal_plan(const QRingRefill*a,const QRingRefill*b){return a->epoch==b->epoch&&a->buffer==b->buffer&&a->slot==b->slot&&a->producer_after==b->producer_after&&a->buffer_paddr==b->buffer_paddr&&a->attention_clear_offset==b->attention_clear_offset&&a->address_entry_offset==b->address_entry_offset&&a->shadow_publish_offset==b->shadow_publish_offset;}
int qca_ring_bind(QRingState*out,const QRingMap*m,uint64_t epoch,uint32_t op,uint32_t type,uint32_t version){
 if(!out||!m||!epoch||op!=3||type!=8||version!=0x05020001||overlap(out,sizeof(*out),m,sizeof(*m)*Q_RING_MAPS))return -1;
 if(!((out->phase==Q_RING_NEW&&!out->epoch&&!out->released_maps)||(out->phase==Q_RING_CLOSED&&out->released_maps==Q_RING_MAPS)))return -1; /* Never discard an unreleased owner ledger. */
 for(unsigned i=0;i<Q_RING_MAPS;i++){
  uint32_t bytes=i<Q_RING_SLABS?65536:12288;if(!m[i].identity||m[i].epoch!=epoch||!m[i].paddr||(m[i].paddr&4095)||m[i].paddr>UINT32_MAX||m[i].bytes!=bytes||m[i].paddr+bytes>0x100000000ULL||m[i].actual_map_valid!=1||m[i].coherent_common!=1||m[i].allocated_masteroff!=1)return -1;
  for(unsigned j=0;j<i;j++)if(m[i].identity==m[j].identity||(m[i].paddr<m[j].paddr+m[j].bytes&&m[j].paddr<m[i].paddr+bytes))return -1;
 }
 QRingState next={0};next.epoch=epoch;next.phase=Q_RING_FILLING;for(unsigned i=0;i<Q_RING_MAPS;i++)next.maps[i]=m[i];for(unsigned i=0;i<Q_RING_SIZE;i++)next.slot_buffer[i]=UINT16_MAX;for(unsigned i=0;i<Q_RING_BUFFERS;i++)next.buffer_slot[i]=UINT16_MAX;*out=next;return 0;
}
int qca_ring_reserve(QRingState*s,uint16_t buffer,QRingRefill*out){
 if(!s||!out||overlap(s,sizeof(*s),out,sizeof(*out))||(s->phase!=Q_RING_FILLING&&s->phase!=Q_RING_CFG_TRANSFERRED)||s->pending_valid||s->fill>=Q_RING_FILL||buffer>=Q_RING_BUFFERS||s->buffer_state[buffer]!=Q_BUFFER_AVAILABLE||s->producer>=Q_RING_SIZE||s->slot_buffer[s->producer]!=UINT16_MAX)return -1;
 QRingRefill p={.epoch=s->epoch,.buffer=buffer,.slot=(uint16_t)s->producer,.producer_after=(uint16_t)((s->producer+1)&(Q_RING_SIZE-1)),.buffer_paddr=(uint32_t)(s->maps[buffer/32].paddr+(buffer%32)*Q_RX_BYTES),.attention_clear_offset=4,.address_entry_offset=s->producer*4,.shadow_publish_offset=8192};
 s->pending=p;s->pending_valid=1;s->buffer_state[buffer]=Q_BUFFER_RESERVED;s->buffer_slot[buffer]=p.slot;s->slot_buffer[p.slot]=buffer;*out=p;return 0;
}
int qca_ring_publish(QRingState*s,const QRingRefill*p,const QRingPublishProof*proof){
 if(!s||!p||!proof||!s->pending_valid||!equal_plan(p,&s->pending)||(s->phase!=Q_RING_FILLING&&s->phase!=Q_RING_CFG_TRANSFERRED))return -1;
 if(proof->attention_cleared!=1||proof->buffer_visible!=1||proof->address_visible!=1||proof->device_barrier_complete!=1||proof->actual_index_published!=1){s->phase=Q_RING_FAULT;return -1;} /* Ambiguity retains maps/reservation. */
 s->producer=p->producer_after;s->fill++;s->buffer_state[p->buffer]=Q_BUFFER_POSTED;s->pending_valid=0;return 0;
}
int qca_ring_cfg(QRingState*s,uint32_t actual,uint8_t*out){
 if(!s||!out||overlap(s,sizeof(*s),out,Q_RING_CFG_BYTES)||s->phase!=Q_RING_FILLING||s->pending_valid||s->cfg_serialized||s->fill!=Q_RING_FILL||s->producer!=Q_RING_FILL||actual!=s->producer)return -1;
 uint8_t v[Q_RING_CFG_BYTES]={2,1,0,0};w32(v+4,(uint32_t)(s->maps[32].paddr+8192));w32(v+8,(uint32_t)s->maps[32].paddr);w16(v+12,Q_RING_SIZE);w16(v+14,Q_RX_BYTES);w16(v+16,65535);w16(v+18,actual);
 static const uint16_t offsets[]={59,75,21,31,3,20,6,10,1,2};for(unsigned i=0;i<10;i++)w16(v+20+2*i,offsets[i]);for(unsigned i=0;i<Q_RING_CFG_BYTES;i++)out[i]=v[i];s->cfg_serialized=1;return 0;
}
int qca_ring_cfg_posted(QRingState*s,uint64_t epoch,uint64_t floor){if(!s||s->phase!=Q_RING_FILLING||!s->cfg_serialized||s->cfg_posted||epoch!=s->epoch)return -1;s->last_indication_completion=floor;s->cfg_posted=1;return 0;} /* Record actual RX watermark immediately before CE4 publication. */
int qca_ring_cfg_dma_complete(QRingState*s,uint64_t epoch,uint64_t complete){if(!s||s->phase!=Q_RING_FILLING||!s->cfg_serialized||!s->cfg_posted||s->pending_valid||epoch!=s->epoch||!complete)return -1;s->phase=Q_RING_CFG_TRANSFERRED;return 0; /* Not firmware accepted/data ready. */}
int qca_ring_claim(QRingState*s,const uint16_t*buffers,unsigned count,uint64_t epoch,uint64_t complete){
 if(!s||!buffers||s->phase!=Q_RING_CFG_TRANSFERRED||s->pending_valid||epoch!=s->epoch||!complete||complete<=s->last_indication_completion||!count||count>255||count>s->fill||overlap(s,sizeof(*s),buffers,count*sizeof(*buffers)))return -1;
 for(unsigned i=0;i<count;i++){unsigned b=buffers[i];if(b>=Q_RING_BUFFERS||s->buffer_state[b]!=Q_BUFFER_POSTED||s->buffer_slot[b]>=Q_RING_SIZE||s->slot_buffer[s->buffer_slot[b]]!=b)return -1;for(unsigned j=0;j<i;j++)if(b==buffers[j])return -1;}
 for(unsigned i=0;i<count;i++){unsigned b=buffers[i];s->buffer_state[b]=Q_BUFFER_OWNED;s->slot_buffer[s->buffer_slot[b]]=UINT16_MAX;s->buffer_slot[b]=UINT16_MAX;}s->fill-=count;s->last_indication_completion=complete;return 0;
}
int qca_ring_copied(QRingState*s,uint16_t b,uint64_t epoch,int acquired,int copied){if(!s||s->phase!=Q_RING_CFG_TRANSFERRED||b>=Q_RING_BUFFERS||s->buffer_state[b]!=Q_BUFFER_OWNED||epoch!=s->epoch||acquired!=1||copied!=1)return -1;s->buffer_state[b]=Q_BUFFER_AVAILABLE;return 0;}
int qca_ring_quiesce(QRingState*s,const QRingQuiesceProof*p){if(!s||!p||s->phase==Q_RING_NEW||s->phase==Q_RING_QUIESCED||s->phase==Q_RING_CLOSED||p->epoch!=s->epoch||!p->completion||p->target_halted!=1||p->bme_off!=1||p->callbacks_stopped!=1||p->device_write_barrier!=1)return -1;s->phase=Q_RING_QUIESCED;return 0;}
int qca_ring_map_released(QRingState*s,uint64_t id,uint64_t epoch,int done){if(!s||s->phase!=Q_RING_QUIESCED||epoch!=s->epoch||done!=1||!id)return -1;unsigned i;for(i=0;i<Q_RING_MAPS;i++)if(s->maps[i].identity==id)break;if(i==Q_RING_MAPS||s->map_released[i])return -1;s->map_released[i]=1;s->released_maps++;if(s->released_maps==Q_RING_MAPS)s->phase=Q_RING_CLOSED;return 0;}

#pragma GCC diagnostic pop
