#include "board_query.h"
#include "sha256.h"
static int fail(QcaBoardQuery*q,unsigned e){q->error=e;q->phase=6;return -1;}
static void put(uint8_t*p,uint32_t v){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(v>>(8*i));}
int qca_board_begin(QcaBoardQuery*q,QcaConfigSetup*s,const uint8_t*helper,unsigned n,const uint8_t digest[32]){
 if(!q||q->phase||!s||!helper||!digest||n!=24193||s->phase!=4||s->error||s->op!=10
  ||s->write_mask!=31||s->readback_mask!=31||s->write_attempts!=5||!s->cpu_attempted
  ||s->bmi.phase!=QCA_BMI_DONE||s->bmi.error||s->bmi.type!=8||s->bmi.version!=0x05020001
  ||s->bmi.info_length!=12||s->bmi.bytes!=12||!s->bmi.tx_done||!s->bmi.rx_done)return -1;
 QcaInitAdapter*a=s->read.full.adapter;
 if(!a||s->bmi.bus!=&a->bus||s->bmi.tx!=&a->channels.rings[0]||s->bmi.rx!=&a->channels.rings[1]
  ||s->bmi.request!=&a->channels.buffers[1]||s->bmi.response!=&a->channels.buffers[3]||a->phase!=QCA_INIT_READY||a->error||a->cancelled||qca_mapped_irq_active_guard(&a->mapped))return -1;
 uint8_t hash[32];rabbit_sha256(hash,helper,n);for(unsigned i=0;i<32;i++)if(hash[i]!=digest[i])return -1;
 q->setup=s;q->helper=helper;q->helper_bytes=n;q->phase=1;return 0;
}
int qca_board_poll(QcaBoardQuery*q,uint64_t now){
 if(!q||q->error)return -1;
 if(q->phase==5)return 1;
 if(!q->phase||q->phase>4)return -1;
 QcaInitAdapter*a=q->setup->read.full.adapter;
 if(a->phase!=QCA_INIT_READY||a->error||a->cancelled||qca_mapped_irq_active_guard(&a->mapped))return fail(q,1);
 if(q->io.wire.phase==QCA_BMI_WAIT){
  q->polls++;int rc=qca_bmi_loader_poll(&q->io,now);if(rc<0)return fail(q,0x100|q->io.wire.error);if(!rc)return 0;
  if(q->phase==1)q->phase=2;
  else if(q->phase==2){q->offset+=q->io.request_bytes-8;if(q->offset>=q->helper_bytes)q->phase=3;}
  else if(q->phase==3)q->phase=4;
  else{const volatile uint8_t*p=q->io.wire.response->host;for(unsigned i=0;i<4;i++)q->result|=(uint32_t)p[i]<<(8*i);
   q->board_id=(uint8_t)((q->result&0x7c00)>>10);q->chip_id=(uint8_t)((q->result&0x18000)>>15);q->extended=!!(q->result&0x40000);q->phase=5;return 1;}
  q->io=(QcaBmiLoader){0};return 0;
 }
 uint8_t request[256]={0};unsigned n=8;
 if(q->phase==1||q->phase==3){put(request,13);put(request+4,q->phase==1?0x1234:0);}
 else if(q->phase==2){
  unsigned remaining=q->helper_bytes-q->offset,bytes=remaining<248?remaining:248;unsigned padded=(bytes+3)&~3u;
  put(request,14);put(request+4,padded);for(unsigned i=0;i<bytes;i++)request[8+i]=q->helper[q->offset+i];n=8+padded;
 }else{put(request,4);put(request+4,0x1234);put(request+8,0x10);n=12;}
 q->submitted++;
 if(qca_bmi_loader_begin(&q->io,&a->bus,&a->channels.rings[0],&a->channels.rings[1],&a->channels.buffers[1],&a->channels.buffers[3],request,n,now))return fail(q,2);
 return 0;
}
