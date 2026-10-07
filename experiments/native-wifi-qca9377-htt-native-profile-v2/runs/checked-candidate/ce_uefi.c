/* PCI IO CE allowlist. No unchecked physical dereference or bus-master enable. */
#include "ce_uefi.h"
typedef Status(EFIAPI *Memory)(void*,uint32_t,uint8_t,uint64_t,uint64_t,void*);
static void*method(QcaCeAccess*a,unsigned offset){return *(void**)((uint8_t*)a->port->pci+offset);}
static int register_offset(QcaCeAccess*a,uint32_t address,unsigned*off){
 if(!a||!a->port||!a->port->claimed||!a->port->pci||!a->port->validated||!a->port->memory_ready||!a->port->wake_owned
  ||address<0x34400||address>0x36050||(address&3)||a->port->bar_extent<0x34454||address>a->port->bar_extent-4)return -1;
 unsigned id=(address-0x34400)/0x400;*off=(address-0x34400)%0x400;
 if(!(a->mask&(1u<<id)))return -1;
 switch(*off){case 0:case 4:case 8:case 0xc:case 0x10:case 0x18:case 0x2c:case 0x30:case 0x34:case 0x38:case 0x3c:case 0x40:case 0x44:case 0x48:case 0x4c:case 0x50:return 0;default:return -1;}
}
int qca_ce_access_init(QcaCeAccess*a,QcaUefiPort*p,unsigned mask){
 if(!a||a->count||!p||!p->claimed||!p->pci||!p->validated||!p->memory_ready||!p->wake_owned||!mask||mask>255)return -1;
 a->port=p;a->mask=(uint8_t)mask;return 0;
}
int qca_ce_access_buffer(QcaCeAccess*a,QcaDmaBuffer*d){
 if(!a||!a->port||!d||d->port!=a->port||!d->valid||!d->mapped||d->closing||a->count>=16)return -1;
 for(unsigned i=0;i<a->count;i++)if(a->buffers[i]==d)return -1;
 a->buffers[a->count++]=d;return 0;
}
int qca_ce_access_read(void*context,uint32_t address,uint32_t*out){
 QcaCeAccess*a=context;unsigned off;
 if(!out||register_offset(a,address,&off))return -1;
 return ((Memory)method(a,16))(a->port->pci,2,0,address,1,out)?-1:0;
}
static QcaDmaBuffer*region(QcaCeAccess*a,uint32_t base,uint32_t bytes){
 for(unsigned i=0;i<a->count;i++){
  QcaDmaBuffer*d=a->buffers[i];
  if(d->valid&&d->mapped&&!d->closing&&base>=d->address&&bytes<=d->bytes&&(uint64_t)base-d->address<=d->bytes-bytes)return d;
 }
 return 0;
}
static int queue(QcaCeAccess*a,uint32_t engine,int receive,uint32_t*n){
 uint32_t base=0;
 if(qca_ce_access_read(a,engine+(receive?0xc:4),n)||qca_ce_access_read(a,engine+(receive?8:0),&base))return -1;
 if(!*n)return base?-1:0;
 if(*n<2||*n>32||(*n&(*n-1))||(base&7))return -1;
 QcaDmaBuffer*d=region(a,base,*n*8);
 return !d||qca_dma_expose(d)?-1:0;
}
int qca_ce_access_write(void*context,uint32_t address,uint32_t value){
 QcaCeAccess*a=context;unsigned off;if(register_offset(a,address,&off))return -1;
 uint32_t engine=address-off;
 if(off==0x44||off==0x48)return -1; /* hardware read indices are read-only */
 if(off==0x18){
  if(value>1)return -1;
  if(!value){uint32_t ns=0,nd=0;if(queue(a,engine,0,&ns)||queue(a,engine,1,&nd)||(!ns&&!nd))return -1;}
 }
 else if(off==0x3c||off==0x40){
  uint32_t n=0,command=0;
  if(qca_ce_access_read(a,engine+0x18,&command)||queue(a,engine,off==0x40,&n))return -1;
  if(n?value>=n:(value||((command&9)!=9)))return -1;
 }
 else{
  uint32_t command=0;if(qca_ce_access_read(a,engine+0x18,&command)||(command&9)!=9)return -1;
  if(off==0||off==8){
   if(value){QcaDmaBuffer*d=region(a,value,8);if((value&7)||!d||qca_dma_expose(d))return -1;}
  }
  else if(off==4||off==0xc){
   if(value){uint32_t base=0;if(value<2||value>32||(value&(value-1))||qca_ce_access_read(a,engine+(off==4?0:8),&base)||!region(a,base,value*8))return -1;}
  }
  else if(off==0x10){if(value&~0x7ffffu)return -1;}
  else if(off==0x2c||off==0x34){if(value)return -1;}
  else if(off==0x30){if(value&~0x1fu)return -1;}
  else if(off==0x38){if(value&~0x7e0u)return -1;}
  else if(off==0x4c||off==0x50){if((value>>16)||((value&65535)>32))return -1;}
 }
 return ((Memory)method(a,24))(a->port->pci,2,0,address,1,&value)?-1:0;
}
