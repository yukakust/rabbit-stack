#include "boot_native.h"
#include <stdatomic.h>
static const uint8_t container_hash[32]={0x8f,0x8b,0x00,0x2f,0xcc,0xfe,0x81,0xd4,0x22,0x38,0xf2,0x7d,0xd1,0xf5,0x6d,0x18,0x96,0x04,0xf1,0x80,0xbd,0x47,0x72,0xc7,0xc8,0xe7,0x5a,0xe1,0xfe,0xf1,0x6f,0x01};
static uint32_t word(const uint8_t*p){uint32_t v=0;for(unsigned i=0;i<4;i++)v|=(uint32_t)p[i]<<(8*i);return v;}
static unsigned half(const uint8_t*p){return p[0]|((unsigned)p[1]<<8);}
static int fail(QcaBootNative*s,unsigned e){s->error=e;s->phase=6;return -1;}
static QcaInitAdapter*adapter(QcaBootNative*s){return s->board->setup->read.full.adapter;}
static int active(QcaBootNative*s){
 QcaInitAdapter*a=adapter(s);
 return !s->owns_pin||!s->asset->pinned||!s->asset->ready||s->asset->poisoned
  ||a->phase!=QCA_INIT_READY||a->error||a->cancelled||qca_mapped_irq_active_guard(&a->mapped);
}
int qca_boot_native_begin(QcaBootNative*s,QcaBoardQuery*q,const QcaBoardSmbios*m,QcaFirmwareChunks*asset,const uint8_t*board,unsigned n,uint64_t now){
 if(!s||s->phase||!q||q->phase!=5||q->error||q->result||q->board_id||q->chip_id||q->extended
  ||q->submitted!=101||q->offset!=24196||q->helper_bytes!=24193||!q->setup
  ||!m||m->state!=2||m->error||m->variant[0]||!asset||!asset->ready||asset->pinned||asset->poisoned
  ||asset->policy.total!=751436||asset->policy.type!=8||asset->policy.version!=0x05020001||asset->policy.kind!=1
  ||n!=8124||!board||now>UINT64_MAX-20000000)return -1;
 for(unsigned i=0;i<32;i++)if(asset->policy.digest[i]!=container_hash[i])return -1;
 QcaConfigSetup*x=q->setup;QcaInitAdapter*a=x->read.full.adapter;
 if(!a||x->phase!=4||x->error||x->op!=10||x->write_mask!=31||x->readback_mask!=31||x->write_attempts!=5
  ||x->read.phase!=4||x->read.error||x->read.mask!=7||x->read.slot!=3||x->read.full.error
  ||x->read.full.exchange.phase!=QCA_DIAG_DONE||x->read.full.exchange.value!=0x401ee0
  ||!x->cpu_attempted||x->bmi.phase!=QCA_BMI_DONE||x->bmi.error||x->bmi.type!=8||x->bmi.version!=0x05020001
  ||x->bmi.info_length!=12||x->bmi.bytes!=12||!x->bmi.tx_done||!x->bmi.rx_done
  ||x->bmi.bus!=&a->bus||x->bmi.tx!=&a->channels.rings[0]||x->bmi.rx!=&a->channels.rings[1]
  ||x->bmi.request!=&a->channels.buffers[1]||x->bmi.response!=&a->channels.buffers[3]
  ||a->phase!=QCA_INIT_READY||a->error||a->cancelled||qca_mapped_irq_active_guard(&a->mapped))return -1;
 const uint8_t*data;size_t length;
 if(qca_fw_pin(asset,&data,&length))return -1;
 s->board=q;s->asset=asset;s->owns_pin=1;s->started=s->last=now;
 /* Parse only the exact full container; no trusting network-supplied offsets.
  * Admit the known scalar/feature/image IEs; forbid duplicates/code-swap. */
 const uint8_t magic[11]={'Q','C','A','-','A','T','H','1','0','K',0};
 if(length!=751436)return fail(s,1);
 for(unsigned i=0;i<11;i++)if(data[i]!=magic[i])return fail(s,1);
 QcaBootAssets assets={.board=board,.board_bytes=n};uint32_t seen=0;
 for(size_t pos=12;pos<length;){
  if(length-pos<8)return fail(s,2);
  uint32_t tag=word(data+pos),bytes=word(data+pos+4);pos+=8;
  if(tag>6||(seen&(1u<<tag))||bytes>length-pos||(((uint64_t)bytes+3u)&~3ull)>length-pos)return fail(s,2);
  seen|=1u<<tag;
  if(tag==3){assets.main=data+pos;assets.main_bytes=bytes;}
  if(tag==4){assets.helper=data+pos;assets.helper_bytes=bytes;}
  pos+=((uint64_t)bytes+3u)&~3ull;
 }
 if(qca_boot_image_begin(&s->plan,&assets))return fail(s,3);
 s->phase=1;return 0;
}
int qca_boot_native_poll(QcaBootNative*s,uint64_t now){
 if(!s||!s->phase||s->error)return -1;
 if(s->phase==5)return 1;
 if(now<s->last)return fail(s,4);
 s->last=now;if(active(s))return fail(s,5);
 QcaInitAdapter*a=adapter(s);QcaCeRing*rx=&a->channels.rings[1];QcaDmaBuffer*response=&a->channels.buffers[3];
 if(s->phase==1){
  if(s->io.wire.phase==QCA_BMI_WAIT){
   int rc=qca_boot_transport_poll(&s->io,now);if(rc<0)return fail(s,0x100|s->io.wire.error);if(!rc)return 0;
   rc=qca_boot_image_complete(&s->plan,response->host,s->io.response_bytes);
   if(rc<0)return fail(s,0x200|s->plan.error);
   if(s->plan.phase==3&&!s->plan.offset){
    const uint32_t*w=s->board->setup->read.words;
    const uint32_t bases[4]={w[0],w[1],0x401ee0,0x400800},sizes[4]={168,204,36,0x124};
    for(unsigned i=0;i<4;i++){
     if((bases[i]&3)||bases[i]<0x400000||bases[i]>0x410000-sizes[i])return fail(s,18);
     if(s->plan.board_address<bases[i]+sizes[i]&&bases[i]<s->plan.board_address+8124)return fail(s,19);
    }
   }
   s->io=(QcaBmiLoader){0};
   if(rc>0){s->phase=2;s->started=now;}return 0;
  }
  const uint8_t*request;unsigned n,reply;
  if(qca_boot_image_request(&s->plan,&request,&n,&reply))return fail(s,6);
  if(qca_boot_transport_begin(&s->io,&a->bus,&a->channels.rings[0],rx,&a->channels.buffers[1],response,&s->plan,now))return fail(s,7);
  return 0;
 }
 if(s->phase==2){
  if(rx->read!=rx->write||rx->read!=rx->published||!response->valid||!response->mapped||response->closing||response->bytes<256
   ||!response->allocated||!response->host||!response->exposed||response->port!=a->bus.access->port)return fail(s,8);
  for(unsigned i=0;i<256;i++)((uint8_t*)response->host)[i]=0;
  atomic_thread_fence(memory_order_release);
  if(qca_ce_post(rx,response->address,256,3,0,0))return fail(s,9);
  s->phase=3;return 0;
 }
 if(s->phase!=3)return fail(s,10);
 unsigned index=0;uint32_t cookie=0,bytes=0;
 if(qca_ce_hw_index(&a->bus.engines[1],1,&index))return fail(s,11);
 int rc=qca_ce_complete(rx,index,&cookie,&bytes);if(rc<0)return fail(s,12);
 if(rc)return now-s->started>=20000000?fail(s,13):0;
 if(cookie!=3||bytes<16||bytes>256)return fail(s,14);
 atomic_thread_fence(memory_order_acquire);
 const uint8_t*p=response->host;for(unsigned i=0;i<bytes;i++)s->ready[i]=p[i];s->ready_bytes=bytes;
 /* Initial endpoint0 ready only; bundles/trailers require later integration. */
 if(p[0]||p[1]||p[4]||p[6]||p[7]||half(p+2)!=bytes-8||half(p+8)!=1
  ||(bytes!=16&&bytes!=20))return fail(s,15);
 s->credit_count=half(p+10);s->credit_size=half(p+12);s->max_endpoints=p[14];
 if(!s->credit_count||!s->credit_size||!s->max_endpoints||s->max_endpoints>9)return fail(s,16);
 if(bytes==20&&p[16]>1)return fail(s,17);
 s->phase=5;return 1;
}
int qca_boot_native_close(QcaBootNative*s){
 if(!s)return -1;
 if(!s->owns_pin)return 0;
 QcaInitAdapter*a=adapter(s);
 if(!qca_init_adapter_released(a)||a->bus.owned||a->access.count||a->mapped.irq->port->dma_users)return -1;
 if(qca_fw_unpin(s->asset))return -1;
 s->owns_pin=0;return 0;
}
