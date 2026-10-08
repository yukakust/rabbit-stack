#include "config_read.h"
static int fail(QcaConfigRead*r,unsigned e){r->error=e;r->phase=5;return -1;}
int qca_config_read_poll(QcaConfigRead*r,uint64_t now){
 if(!r||r->error)return -1;
 if(r->phase==4)return 1;
 int rc=1;
 if(r->full.exchange.phase!=QCA_DIAG_DONE){rc=qca_full_read_poll(&r->full,now);if(rc<=0)return rc;}
 if(r->full.error)return -1;
 if(qca_mapped_irq_active_guard(&r->full.adapter->mapped))return fail(r,1);
 QcaDiagExchange*x=&r->reads[r->slot];
 if(x->phase==QCA_DIAG_IDLE){
  r->phase=(uint8_t)(r->slot+1);
  if(qca_diag_config_begin(x,&r->full.exchange,r->slot,now))return fail(r,2);
  return 0;
 }
 rc=qca_diag_poll(x,now);
 if(rc<0)return fail(r,0x100|x->error);
 if(!rc)return 0;
 const volatile uint8_t*p=x->response->host;
 unsigned count=r->slot?1:9,offset=r->slot?8+r->slot:0;
 for(unsigned k=0;k<count;k++){
  uint32_t word=0;for(unsigned j=0;j<4;j++)word|=(uint32_t)p[k*4+j]<<(j*8);
  r->words[offset+k]=word;
 }
 r->mask|=1u<<r->slot;
 if(++r->slot==3){r->phase=4;return 1;}
 return 0;
}
