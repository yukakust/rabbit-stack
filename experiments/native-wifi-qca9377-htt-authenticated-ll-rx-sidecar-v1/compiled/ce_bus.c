/* Exclusive PCI bus-master lifetime, no firmware commands. */
#include "ce_bus.h"
#include <stdatomic.h>
typedef Status(EFIAPI *Config)(void*,uint32_t,uint32_t,uint64_t,void*);
static void*method(QcaCeBus*b,unsigned off){return *(void**)((uint8_t*)b->access->port->pci+off);}
static int valid(QcaCeBus*b){return b&&b->access&&b->access->port&&b->access->port->claimed&&b->access->port->validated&&b->access->port->pci;}
static int command_read(QcaCeBus*b,uint16_t*out){if(!valid(b))return -1;return ((Config)method(b,48))(b->access->port->pci,1,4,1,out)?-1:0;}
static int command_write(QcaCeBus*b,uint16_t value){if(!valid(b))return -1;return ((Config)method(b,56))(b->access->port->pci,1,4,1,&value)?-1:0;}
static int fail(QcaCeBus*b,unsigned error){b->error=error;b->phase=QCA_BUS_FAULT;return -1;}
static int off(QcaCeBus*b){
 uint16_t c=0;if(command_read(b,&c))return -1;
 /* Preserve actual unrelated command bits; only modify Bus Master Enable. */
 if(c&4){if(command_write(b,(uint16_t)(c&~4u)))return -1;}
 uint16_t readback=0;if(command_read(b,&readback)||readback!=(uint16_t)(c&~4u))return -1;
 return 0;
}
int qca_ce_bus_init(QcaCeBus*b,QcaCeAccess*a){
 if(!b||b->owned||!a||a->mask!=255||!a->port||!a->port->claimed||!a->port->validated||!a->port->memory_ready||!a->port->wake_owned)return -1;
 b->access=a;uint16_t c=0;if(command_read(b,&c)||(c&4)||!(c&2))return -1;
 for(unsigned i=0;i<8;i++)if(qca_ce_hw_init(&b->engines[i],i,qca_ce_access_read,qca_ce_access_write,a))return -1;
 b->command=c;b->phase=QCA_BUS_IDLE;b->error=0;return 0;
}
int qca_ce_bus_start(QcaCeBus*b){
 if(!b||b->phase!=QCA_BUS_OFF||b->owned||!b->access->count)return -1;
 uint16_t c=0;if(command_read(b,&c)||c!=b->command)return fail(b,1);
 unsigned configured=0;
 for(unsigned i=0;i<8;i++){
  QcaCeHw*e=&b->engines[i];
  if(e->phase==QCA_CE_HW_CONFIGURED)configured++;
  else if(e->phase!=QCA_CE_HW_STOPPED)return fail(b,2);
 }
 if(!configured)return -1;
 /* Mark every descriptor AND data buffer before any possible hardware start. */
 for(unsigned i=0;i<b->access->count;i++)if(qca_dma_expose(b->access->buffers[i]))return fail(b,3);
 b->owned=1;
 for(unsigned i=0;i<8;i++)if(b->engines[i].phase==QCA_CE_HW_CONFIGURED&&qca_ce_hw_run(&b->engines[i]))return fail(b,4);
 atomic_thread_fence(memory_order_release);
 if(command_write(b,(uint16_t)(c|4)))return fail(b,5);
 uint16_t actual=0;if(command_read(b,&actual)||actual!=(uint16_t)(c|4))return fail(b,6);
 b->phase=QCA_BUS_ACTIVE;return 0;
}
int qca_ce_bus_stop_begin(QcaCeBus*b,uint64_t now){
 if(!b||!b->access)return -1;
 b->owned=1;b->phase=QCA_BUS_STOPPING;b->error=0;
 int error=0;for(unsigned i=0;i<8;i++)if(qca_ce_hw_stop_begin(&b->engines[i],now))error=1;
 /* On ambiguity reduce DMA capability, but retain all buffers/claim. */
 if(error){(void)off(b);b->error=7;return -1;}return 0;
}
int qca_ce_bus_stop_poll(QcaCeBus*b,uint64_t now){
 if(!b||b->phase!=QCA_BUS_STOPPING)return -1;
 unsigned waiting=0,error=0;
 for(unsigned i=0;i<8;i++){
  int rc=qca_ce_hw_stop_poll(&b->engines[i],now);
  if(rc<0)error=1;else if(!rc)waiting=1;
 }
 if(error){(void)off(b);return fail(b,8);}
 if(waiting)return 0;
 if(off(b))return fail(b,9);
 b->phase=QCA_BUS_OFF;b->owned=0;return 1;
}
int qca_ce_bus_released(void*context){
 QcaCeBus*b=context;
 if(!b||b->phase!=QCA_BUS_OFF||b->owned)return -1;
 uint16_t command=0;if(command_read(b,&command)||(command&4))return -1;
 for(unsigned i=0;i<8;i++){
  QcaCeHw*e=&b->engines[i];uint32_t v=0;
  if(e->phase!=QCA_CE_HW_STOPPED||e->owned||qca_ce_access_read(b->access,e->base+0x18,&v)||(v&9)!=9)return -1;
  for(unsigned j=0;j<4;j++)if(qca_ce_access_read(b->access,e->base+j*4,&v)||v)return -1;
 }
 return 0;
}
