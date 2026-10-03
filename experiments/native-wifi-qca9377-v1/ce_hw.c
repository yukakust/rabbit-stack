/* SPDX-License-Identifier: GPL-2.0-only
 * QCA9377 CE register profile derived from pinned ath10k qcax_ce_regs. */
#include "ce_hw.h"
#include <stdatomic.h>
static int fail(QcaCeHw*c,unsigned step){c->error=step;c->phase=QCA_CE_HW_FAULT;return -1;}
static int rd(QcaCeHw*c,unsigned off,uint32_t*v){return c->read(c->context,c->base+off,v)||*v==0xffffffffu?-1:0;}
static int wr(QcaCeHw*c,unsigned off,uint32_t v){return c->write(c->context,c->base+off,v);}
static int count(unsigned n){return !n||(n>=2&&n<=32&&!(n&(n-1)));}
int qca_ce_hw_init(QcaCeHw*c,unsigned id,QcaRead32 read,QcaWrite32 write,void*context){
 if(!c||c->owned||id>=8||!read||!write)return -1;
 c->base=0x34400+id*0x400;c->read=read;c->write=write;c->context=context;c->timeout=1000000;
 c->phase=QCA_CE_HW_IDLE;c->error=0;c->src_entries=c->dst_entries=0;return 0;
}
int qca_ce_hw_stop_begin(QcaCeHw*c,uint64_t now){
 if(!c||!c->read||!c->write)return -1;
 c->started=c->last=now;c->phase=QCA_CE_HW_HALTING;c->owned=1;c->error=0;
 /* Mark before ambiguous write; a failed request cannot release DMA resources. */
 if(wr(c,0x18,1)){c->error=1;return -1;}return 0;
}
int qca_ce_hw_stop_poll(QcaCeHw*c,uint64_t now){
 if(!c)return -1;
 if(c->phase==QCA_CE_HW_STOPPED)return 1;
 if(c->phase!=QCA_CE_HW_HALTING||!c->owned)return -1;
 if(now<c->last)return fail(c,2);
 c->last=now;
 if(now-c->started>=c->timeout)return fail(c,3);
 uint32_t cmd=0;if(rd(c,0x18,&cmd))return fail(c,4);if(!(cmd&1))return fail(c,12);
 if(!(cmd&8))return 0;
 /* Halt ACK is necessary but DMA release ALSO requires bus-master-off + flush. */
 static const unsigned off[]={0x2c,0x34,0,4,8,0xc,0x4c,0x50};
 for(unsigned i=0;i<sizeof(off)/sizeof(off[0]);i++){
  uint32_t value=1;if(wr(c,off[i],0)||rd(c,off[i],&value)||value)return fail(c,5);
 }
 c->src_entries=c->dst_entries=0;c->phase=QCA_CE_HW_STOPPED;c->owned=0;return 1;
}
int qca_ce_hw_configure(QcaCeHw*c,uint64_t src,unsigned ns,uint64_t dst,unsigned nd,unsigned maxbytes){
 if(!c||c->phase!=QCA_CE_HW_STOPPED||!count(ns)||!count(nd)||(!ns&&!nd)||(!maxbytes&&ns)||maxbytes>65535
  ||(ns&&((src&7)||src>UINT32_MAX||src>UINT32_MAX-(ns*8-1)))
  ||(nd&&((dst&7)||dst>UINT32_MAX||dst>UINT32_MAX-(nd*8-1))))return -1;
 uint32_t control=0,si=0,di=0,cmd=0;
 if(rd(c,0x18,&cmd)||(cmd&9)!=9)return fail(c,12);
 if(rd(c,0x10,&control)||rd(c,0x44,&si)||rd(c,0x48,&di)||(control&~0x7ffffu)||(si&~65535u)||(di&~65535u))return fail(c,6);
 c->src_index=ns?(uint16_t)(si&(ns-1)):0;c->dst_index=nd?(uint16_t)(di&(nd-1)):0;
 unsigned off[]={0x2c,0x34,0x30,0x38,0,4,8,0xc,0x10,0x4c,0x50,0x3c,0x40};
 uint32_t val[]={0,0,0x1f,0x7e0,ns?(uint32_t)src:0,ns,nd?(uint32_t)dst:0,nd,
  (control&~0x3ffffu)|(ns?maxbytes:0),ns,nd,c->src_index,c->dst_index};
 c->owned=1;
 for(unsigned i=0;i<sizeof(off)/sizeof(off[0]);i++){
  if(wr(c,off[i],val[i]))return fail(c,7);
  if(off[i]!=0x30&&off[i]!=0x38){uint32_t v=0;if(rd(c,off[i],&v)||v!=val[i])return fail(c,8);}
 }
 c->src_entries=(uint16_t)ns;c->dst_entries=(uint16_t)nd;c->phase=QCA_CE_HW_CONFIGURED;return 0;
}
int qca_ce_hw_run(QcaCeHw*c){
 if(!c||c->phase!=QCA_CE_HW_CONFIGURED||!c->owned)return -1;
 atomic_thread_fence(memory_order_release);if(wr(c,0x18,0))return fail(c,9);
 c->phase=QCA_CE_HW_RUNNING;return 0;
}
int qca_ce_hw_publish(QcaCeHw*c,int receive,unsigned index){
 if(!c||c->phase!=QCA_CE_HW_RUNNING||!c->owned||receive<0||receive>1
  ||index>=(receive?c->dst_entries:c->src_entries))return -1;
 if(wr(c,receive?0x40:0x3c,index))return fail(c,10);
 return 0;
}
int qca_ce_hw_index(QcaCeHw*c,int receive,unsigned*out){
 if(!c||!out||c->phase!=QCA_CE_HW_RUNNING||receive<0||receive>1)return -1;
 unsigned entries=receive?c->dst_entries:c->src_entries;uint32_t index=0;
 if(!entries)return -1;
 if(rd(c,receive?0x48:0x44,&index)||index>=entries)return fail(c,11);
 *out=index;return 0;
}
