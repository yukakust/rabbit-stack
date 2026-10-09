#include "config_setup.h"
static int fail(QcaConfigSetup*s,unsigned e){s->error=e;s->phase=5;return -1;}
typedef Status(EFIAPI *Memory)(void*,uint32_t,uint8_t,uint64_t,uint64_t,void*);
static void*method(QcaUefiPort*p,unsigned off){return *(void**)((uint8_t*)p->pci+off);}
int qca_config_setup_poll(QcaConfigSetup*s,uint64_t now){
 if(!s||s->error)return -1;
 if(s->phase==4)return 1;
 if(!s->phase){int rc=qca_config_read_poll(&s->read,now);if(rc<=0)return rc;s->phase=1;}
 QcaInitAdapter*a=s->read.full.adapter;
 if(qca_mapped_irq_active_guard(&a->mapped))return fail(s,1);
 if(s->phase==1){
  unsigned bit=1u<<(s->op/2);
  uint8_t expected[204];uint32_t address;unsigned bytes;
  if(qca_diag_setup_bytes(&s->read,s->op,&address,&bytes,expected))return fail(s,2);
  if(s->io.phase==QCA_DIAG_IDLE){
   if(!(s->op&1)){
    /* done marker cannot be posted before EVERY preceding readback. */
    if(s->op==8&&(s->write_mask!=15||s->readback_mask!=15))return fail(s,3);
    s->write_attempts++;
   }else if(!(s->write_mask&bit))return fail(s,4);
   if(qca_diag_setup_begin(&s->io,&s->read,s->op,now))return fail(s,5);
   return 0;
  }
  int rc=qca_diag_poll(&s->io,now);if(rc<0)return fail(s,0x100|s->io.error);if(!rc)return 0;
  if(s->op&1){
   const volatile uint8_t*p=s->io.response->host;
   for(unsigned i=0;i<bytes;i++)if(p[i]!=expected[i])return fail(s,6);
   s->readback_mask|=bit;
  }else s->write_mask|=bit;
  s->io=(QcaDiagExchange){0};
  if(++s->op==10)s->phase=2;
  return 0;
 }
 if(s->phase==2){
  if(s->write_mask!=31||s->readback_mask!=31)return fail(s,7);
  QcaUefiPort*p=a->access.port;
  if(((Memory)method(p,16))(p->pci,2,0,0x3a000,1,&s->cpu_before)||s->cpu_before==UINT32_MAX)return fail(s,8);
  uint32_t value=s->cpu_before|0x2000u;s->cpu_attempted=1;
  if(((Memory)method(p,24))(p->pci,2,0,0x3a000,1,&value)
   ||((Memory)method(p,16))(p->pci,2,0,0x3a000,1,&s->cpu_readback)||s->cpu_readback==UINT32_MAX
   ||((s->cpu_readback^value)&~0x2000u))return fail(s,9);
  /* CPU interrupt may self-clear; do not require a sticky bit. */
  for(unsigned i=0;i<2;i++){
   QcaCeRing*r=&a->channels.rings[i];
   if(r->read!=r->write||r->read!=r->published)return fail(s,10);
   s->bmi_routes[i]=(QcaBmiPipe){&a->bus,(uint8_t)i};
   r->context=&s->bmi_routes[i];r->publish=qca_bmi_publish;r->stop=qca_bmi_ring_stop;
  }
  if(qca_bmi_info_begin(&s->bmi,&a->bus,&a->channels.rings[0],&a->channels.rings[1],&a->channels.buffers[1],&a->channels.buffers[3],now))return fail(s,11);
  s->phase=3;return 0;
 }
 s->bmi_polls++;int rc=qca_bmi_poll(&s->bmi,now);
 if(rc<0)return fail(s,0x200|s->bmi.error);
 if(rc>0){s->phase=4;return 1;}
 return 0;
}
