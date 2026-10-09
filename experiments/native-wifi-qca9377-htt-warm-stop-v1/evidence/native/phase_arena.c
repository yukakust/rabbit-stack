#include "phase_arena.h"
static QcaHttPhaseOwner*holder;
static int range(const void*p,size_t n){return p&&n&&(uintptr_t)p<=UINTPTR_MAX-n;}
static int overlap(const void*a,size_t n,const void*b,size_t m){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;return x<y?y-x<n:x-y<m;}
static void wipe(void*p,size_t n){volatile uint8_t*b=p;while(n--)*b++=0;}
int qca_htt_phase_acquire(QcaHttPhaseOwner*s,const QcaHttPoolBoot*b,uint64_t epoch){
 if(!range(s,sizeof(*s))||!range(b,sizeof(*b))||holder||!epoch||s->raw||s->arena||s->uncertain||!(s->phase==HTT_POOL_EMPTY||s->phase==HTT_POOL_RELEASED)||!b->allocate||!b->release||overlap(s,sizeof(*s),b,sizeof(*b)))return 0;
 s->boot=*b;s->epoch=epoch;s->bytes=sizeof(QcaHttPhaseArena)+_Alignof(QcaHttPhaseArena)-1;s->free_attempted=s->wiped=0;holder=s;void*raw=0;s->status=b->allocate(2,s->bytes,&raw);s->raw=raw;
 if(s->status||!range(raw,s->bytes)||overlap(raw,s->bytes,s,sizeof(*s))||overlap(raw,s->bytes,b,sizeof(*b))){s->uncertain=raw!=0;s->phase=raw?HTT_POOL_UNCERTAIN:HTT_POOL_FAILED;s->error=1;if(!raw)holder=0;return 0;}
 uintptr_t a=((uintptr_t)raw+_Alignof(QcaHttPhaseArena)-1)&~(uintptr_t)(_Alignof(QcaHttPhaseArena)-1);s->arena=(QcaHttPhaseArena*)a;wipe(raw,s->bytes);s->phase=HTT_POOL_OWNED;return 1;
}
const QcaHttPhaseArena*qca_htt_phase_view(const QcaHttPhaseOwner*s){return s&&holder==s&&s->phase==HTT_POOL_OWNED&&!s->uncertain?s->arena:0;}
int qca_htt_phase_reader_open(QcaHttPhaseOwner*s,uint64_t epoch,const QcaHttPhaseArena**out){
 if(!s||!out||epoch!=s->epoch||s->capture_readers==UINT32_MAX||!qca_htt_phase_view(s))return 0;
 s->capture_readers++;*out=s->arena;return 1;
}
int qca_htt_phase_reader_close(QcaHttPhaseOwner*s,uint64_t epoch,const QcaHttPhaseArena*p){
 if(!s||holder!=s||s->phase!=HTT_POOL_OWNED||epoch!=s->epoch||p!=s->arena||!s->capture_readers)return 0;
 s->capture_readers--;return 1;
}
void qca_htt_phase_empty_pipeline(uint8_t out[544],uint32_t generation){
 if(!out)return;
 for(unsigned i=0;i<544;i++)out[i]=0;
 const uint8_t magic[8]={'Q','F','6','4','0','0','0','1'};for(unsigned i=0;i<8;i++)out[i]=magic[i];
 for(unsigned i=0;i<4;i++){out[244+i]=(uint8_t)(generation>>(8*i));out[432+i]=out[436+i]=255;}
 out[440]=1; /* absent arena never implies radio/READY/owner-release success */
}
unsigned qca_htt_phase_empty_raw(unsigned page,uint8_t*out,unsigned cap){
 if(!out||cap<512||page>=110)return 0;
 unsigned n=page%5==4?56:512;for(unsigned i=0;i<n;i++)out[i]=0;
 if(page%5==0){const uint8_t magic[8]={'Q','F','E','X','0','0','0','1'};for(unsigned i=0;i<8;i++)out[i]=magic[i];out[8]=(uint8_t)(page/5);}
 return n;
}
int qca_htt_phase_detach(QcaHttPhaseOwner*s,QcaHttNative*q){
 if(!s||holder!=s||s->phase!=HTT_POOL_OWNED||s->uncertain||!s->arena||s->capture_readers)return 0;
 QcaHttPhaseArena*a=s->arena;QcaHttRuntime*r=&a->runtime;
 if(r->phase&&(r->epoch!=s->epoch||!qca_htt_runtime_detachable(r)))return 0;
 if(!qca_htt_public_rng_released(&a->rng))return 0;
 if(r->port&&(r->port->claimed||r->port->dma_users||r->port->wake_owned||r->port->link_owned||r->port->boot_irq_owned))return 0;
 if(r->callback_owners||r->rx_copy_owners||r->tx_owners)return 0;
 QcaPersistentNative*p=a->scan.radio;
 if(p){
  if(p->epoch!=s->epoch||p->life.phase!=QCA_RADIO_CLOSED||p->life.owners.mappings||p->life.owners.dma_users||p->life.owners.bus_master||p->rx.posted[0]||p->rx.posted[1]||a->scan.tx.ticket||(a->scan.tx.credit&&a->scan.tx.credit->reserved))return 0;
  if(p->htt_owner&&p->htt_owner!=q)return 0;
  if(q&&q->radio&&q->radio!=p)return 0;
  if(q){q->response=0;q->archive=0;q->radio=0;p->htt_owner=0;}
 }
 a->scan.tx.radio=0;a->scan.tx.life=0;a->scan.tx.credit=0;a->scan.radio=0;s->phase=HTT_POOL_RELEASED;return 1; /* Revokes view; raw remains until explicit release. */
}
int qca_htt_phase_release(QcaHttPhaseOwner*s){
 if(!s)return 0;
 if(!s->raw&&!s->arena&&s->phase==HTT_POOL_RELEASED)return 1;
 if(holder!=s||s->phase!=HTT_POOL_RELEASED||s->uncertain||s->free_attempted||!range(s->raw,s->bytes)||s->bytes!=sizeof(QcaHttPhaseArena)+_Alignof(QcaHttPhaseArena)-1)return 0;
 wipe(s->raw,s->bytes);s->wiped=1;s->free_attempted=1;s->status=s->boot.release(s->raw);
 if(s->status){s->uncertain=1;s->phase=HTT_POOL_FREE_RETAINED;s->error=2;return 0;}
 s->raw=0;s->arena=0;s->bytes=0;holder=0;return 1;
}
