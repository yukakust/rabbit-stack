#include "full_read.h"
static int fail(QcaFullRead*r,unsigned error){
 if(!r->error)r->error=error;
 if(r->exchange.phase!=QCA_DIAG_DONE)r->exchange.phase=QCA_DIAG_FAULT;
 return -1;
}
int qca_full_read_begin(QcaFullRead*r,QcaInitAdapter*a,uint32_t chip,uint64_t bar,uint64_t now){
 if(!r||r->started||!a||a->phase!=QCA_INIT_READY||a->warm.phase!=QCA_WARM_DONE
  ||a->warm.error||a->warm.owned||a->recovery.owned||a->error||a->cancelled
  ||bar!=a->mapped.bar||chip!=0x003821ff||now>UINT64_MAX-3000000)return -1;
 r->adapter=a;r->started=1;
 if(qca_channels_prepared(&a->channels)||qca_mapped_irq_guard(&a->mapped)
  ||qca_mapped_irq_quiesce(&a->mapped))return fail(r,1);
 /* Only callback/context ownership changes. Descriptor addresses, rings and
  * data pages remain those checked by the full-channel inventory above. */
 for(unsigned i=0;i<2;i++){
  QcaCeRing*ring=&a->channels.rings[5+i];
  if(ring->read!=ring->write||ring->read!=ring->published)return fail(r,2);
  r->routes[i]=(QcaDiagPipe){&a->bus,(uint8_t)i};
  ring->context=&r->routes[i];ring->publish=qca_diag_publish;ring->stop=qca_diag_stop;
 }
 if(qca_ce_bus_start(&a->bus))return fail(r,3);
 if(qca_mapped_irq_active_guard(&a->mapped))return fail(r,4);
 if(qca_diag_begin(&r->exchange,&a->bus,&a->channels.rings[5],&a->channels.rings[6],
  &a->channels.buffers[13],chip,bar,now))return fail(r,5);
 return 0;
}
int qca_full_read_poll(QcaFullRead*r,uint64_t now){
 if(!r||!r->started||!r->adapter||r->error)return -1;
 if(qca_mapped_irq_active_guard(&r->adapter->mapped))return fail(r,6);
 int rc=qca_diag_poll(&r->exchange,now);
 if(rc<0)return fail(r,0x100|r->exchange.error);
 if(rc>0&&r->exchange.value!=0x00401ee0)return fail(r,7);
 return rc;
}
