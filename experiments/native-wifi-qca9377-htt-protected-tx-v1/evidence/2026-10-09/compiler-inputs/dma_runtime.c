#include "dma_runtime.h"
#include <stdatomic.h>
#include "guarded_dma.h"
static QcaHttRuntime*holder;
static int overlap(uint64_t a,uint64_t n,uint64_t b,uint64_t m){return a<b?b-a<n:a-b<m;}
static int mapped(QcaDmaBuffer*d,QcaUefiPort*p,unsigned pages){return d->port==p&&d->allocated&&d->mapped&&d->valid&&!d->closing&&!d->allocation_uncertain&&d->pages==pages&&d->bytes==(uint64_t)pages*4096&&d->host&&!(d->address&4095)&&d->address<=UINT32_MAX-(d->bytes-1);}
int qca_htt_runtime_inventory(QcaHttRuntime*s){
 if(!s||holder!=s||!s->port||!s->ce||s->allocated>33||!s->port->claimed||!s->port->validated)return 0;
 unsigned actual=0;
 for(unsigned i=0;i<14+s->allocated;i++){
  QcaDmaBuffer*d=i<14?&s->ce[i]:&s->extra[i-14];unsigned pages=i<14?1:i<46?16:3;
  if(!mapped(d,s->port,pages))return 0;
  actual++;
  for(unsigned j=0;j<i;j++){
   QcaDmaBuffer*prior=j<14?&s->ce[j]:&s->extra[j-14];
   if(d==prior||overlap(d->address,d->bytes,prior->address,prior->bytes)||overlap((uintptr_t)d->host,d->bytes,(uintptr_t)prior->host,prior->bytes)||((d->mapping||prior->mapping)&&d->mapping==prior->mapping))return 0;
  }
 }
 return actual==s->port->dma_users;
}
int qca_htt_runtime_begin(QcaHttRuntime*s,QcaUefiPort*p,QcaDmaBuffer ce[14],uint64_t epoch,QcaDmaStop stop,void*context){
 if(!s||holder||!p||!ce||!epoch||!stop||s->phase||s->port||!p->claimed||!p->validated||p->dma_users!=14)return 0;
 s->port=p;s->ce=ce;s->epoch=epoch;s->stop=stop;s->stop_context=context;s->phase=HTT_RUNTIME_ALLOCATING;holder=s;
 if(!qca_htt_runtime_inventory(s)){s->error=1;s->phase=HTT_RUNTIME_FAULT;return 0;}return 1;
}
static int guard_allocation(void*context,const void*host,uint64_t bytes){
 QcaHttRuntime*s=context;uint64_t h=(uintptr_t)host;
 if(!host||h>UINTPTR_MAX-bytes||overlap(h,bytes,(uintptr_t)s,sizeof(*s))||overlap(h,bytes,(uintptr_t)s->ce,14*sizeof(QcaDmaBuffer))||overlap(h,bytes,(uintptr_t)s->port,sizeof(QcaUefiPort))||overlap(h,bytes,(uintptr_t)s->port->pci,112))return 0;
 for(unsigned i=0;i<14+s->allocated;i++){const QcaDmaBuffer*d=i<14?&s->ce[i]:&s->extra[i-14];if(d->host&&overlap(h,bytes,(uintptr_t)d->host,d->bytes))return 0;}
 return 1;
}
int qca_htt_runtime_allocate_one(QcaHttRuntime*s){
 if(!s||holder!=s||s->phase!=HTT_RUNTIME_ALLOCATING||s->allocated>=33||!qca_htt_runtime_inventory(s))return 0;
 unsigned i=s->allocated;QcaDmaBuffer*d=&s->extra[i];int rc=qca_dma_open_protected(d,s->port,i<32?16:3,s->stop,s->stop_context,guard_allocation,s);
 if(d->allocated||d->mapped)s->allocated++;
 if(rc||!d->valid){s->error=2;s->phase=HTT_RUNTIME_FAULT;return -1;}
 s->maps[i]=(QRingMap){.identity=(uintptr_t)d,.epoch=s->epoch,.paddr=d->address,.bytes=(uint32_t)d->bytes,.actual_map_valid=1,.coherent_common=1,.allocated_masteroff=1};
 if(!qca_htt_runtime_inventory(s)){s->error=3;s->phase=HTT_RUNTIME_FAULT;return -1;}
 if(s->allocated==33)s->phase=HTT_RUNTIME_MAPPED;
 return 1;
}
int qca_htt_runtime_bind_ring(QcaHttRuntime*s,unsigned op,unsigned type,unsigned version){
 if(!s||s->phase!=HTT_RUNTIME_MAPPED||s->allocated!=33||!qca_htt_runtime_inventory(s))return 0;
 for(unsigned i=0;i<33;i++){const QRingMap*m=&s->maps[i];const QcaDmaBuffer*d=&s->extra[i];if(m->identity!=(uintptr_t)d||m->epoch!=s->epoch||m->paddr!=d->address||m->bytes!=d->bytes||m->actual_map_valid!=1||m->coherent_common!=1||m->allocated_masteroff!=1)return 0;}
 if(qca_ring_bind(&s->ring,s->maps,s->epoch,op,type,version))return 0;
 for(unsigned i=0;i<1024;i++){QcaDmaBuffer*d=&s->extra[i/32];s->owners[i]=(QRxOwner){.paddr=(uint32_t)(d->address+2048*(i%32)),.bytes=2048,.epoch=s->epoch,.map_identity=(uintptr_t)d};}
 return 1;
}
static void put32(volatile uint8_t*p,uint32_t n){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(n>>(8*i));}
int qca_htt_runtime_refill_one(QcaHttRuntime*s,uint16_t buffer){
 if(!s||s->phase!=HTT_RUNTIME_MAPPED||buffer>=1023||!qca_htt_runtime_inventory(s))return 0;
 QRingRefill plan;if(qca_ring_reserve(&s->ring,buffer,&plan))return 0;
 QcaDmaBuffer*d=&s->extra[buffer/32],*index=&s->extra[32];
 if(qca_dma_expose(d)||qca_dma_expose(index)){s->phase=HTT_RUNTIME_FAULT;s->error=5;return 0;}
 put32((volatile uint8_t*)d->host+(buffer%32)*2048+plan.attention_clear_offset,0);
 put32((volatile uint8_t*)index->host+plan.address_entry_offset,plan.buffer_paddr);
 atomic_thread_fence(memory_order_seq_cst);
 *(volatile uint32_t*)((uint8_t*)index->host+plan.shadow_publish_offset)=plan.producer_after;
 QRingPublishProof proof={1,1,1,1,1};
 if(qca_ring_publish(&s->ring,&plan,&proof)){s->phase=HTT_RUNTIME_FAULT;s->error=6;return 0;}
 s->owners[buffer].state=1;return 1;
}
int qca_htt_runtime_close_one(QcaHttRuntime*s){
 if(!s||holder!=s||s->phase==HTT_RUNTIME_ACTIVE||s->callback_owners||s->rx_copy_owners||s->tx_owners)return 0;
 s->phase=HTT_RUNTIME_CLOSING;
 while(s->cleanup<s->allocated){QcaDmaBuffer*d=&s->extra[s->cleanup];if(qca_dma_close(d)){s->error=4;return 0;}s->cleanup++;return 1;}
 if(s->port->dma_users!=14)return 0;
 s->phase=HTT_RUNTIME_CLOSED;holder=0;return 1;
}
int qca_htt_runtime_detachable(const QcaHttRuntime*s){
 if(!s||s->phase!=HTT_RUNTIME_CLOSED||s->callback_owners||s->rx_copy_owners||s->tx_owners||s->cleanup!=s->allocated)return 0;
 for(unsigned i=0;i<33;i++)if(s->extra[i].allocated||s->extra[i].mapped||s->extra[i].allocation_uncertain)return 0;
 return 1;
}
