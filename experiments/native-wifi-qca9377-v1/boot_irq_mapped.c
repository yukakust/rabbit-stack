/* Scoped ROM boot indication with retained DMA, never active DMA. */
#include "boot_irq_mapped.h"
#include "pci_identity.h"
#include "power_core.h"
#define BOOT_MASK 0x7fc00u
typedef Status(EFIAPI *Config)(void*,uint32_t,uint32_t,uint64_t,void*);
typedef Status(EFIAPI *Memory)(void*,uint32_t,uint8_t,uint64_t,uint64_t,void*);
static int fail(QcaMappedIrq*m,unsigned e){if(m)m->error=e;return -1;}
static void*method(QcaMappedIrq*m,unsigned off){return *(void**)((uint8_t*)m->irq->port->pci+off);}
static int read32(QcaMappedIrq*m,unsigned off,uint32_t*out){
 m->reads++;return ((Memory)method(m,16))(m->irq->port->pci,2,0,0x3a000+off,1,out)||*out==UINT32_MAX?-1:0;
}
static int write32(QcaMappedIrq*m,unsigned off,uint32_t value){
 m->writes++;m->irq->writes++;return ((Memory)method(m,24))(m->irq->port->pci,2,0,0x3a000+off,1,&value)?-1:0;
}
int qca_mapped_irq_pci_guard(QcaMappedIrq*m){
 if(!m||!m->irq||!m->channels||!m->channels->bus||!m->channels->bus->access)return fail(m,1);
 QcaBootIrq*q=m->irq;QcaUefiPort*p=q->port;
 if(!p||!p->pci||!q->owned||!p->boot_irq_owned||!p->claimed||!p->validated||!p->memory_ready
  ||!p->wake_owned||!p->link_owned||p->bar_extent<0x80004||m->channels->bus->access->port!=p
  ||qca_channels_retained(m->channels)||!m->bar||!m->link_offset)return fail(m,1);
 uint32_t config[64]={0};uint8_t power[16];QcaPciIdentity id;
 m->reads++;
 if(((Config)method(m,48))(p->pci,2,0,64,config))return fail(m,2);
 qca_power_decode((const uint8_t*)config,power);
 if(qca_pci_identity(config,&id)||id.bar0!=m->bar||id.subsystem_vendor!=0x1028||id.subsystem_device!=0x1810||id.revision!=0x31
  ||id.command!=(uint16_t)(q->original_command|0x400u)||!(id.command&2)||(id.command&4)
  ||power[8]!=1||(power[2]&3)||!power[4]
  ||(uint16_t)((power[4]|((uint16_t)power[5]<<8))+0x10)!=m->link_offset)return fail(m,3);
 m->link_control=(uint16_t)(power[6]|((uint16_t)power[7]<<8));
 const uint8_t*c=(const uint8_t*)config;unsigned msi=0,msix=0;
 /* power decoder proved finite/acyclic/aligned conventional capability list. */
 for(unsigned off=c[0x34];off;off=c[off+1]){
  if(c[off]==5){if(msi||off>0xfc||(c[off+2]&1))return fail(m,4);msi=off;}
  if(c[off]==0x11){if(msix||off>0xfc||(c[off+3]&0x80))return fail(m,4);msix=off;}
 }
 if(msi!=q->msi||msix!=q->msix)return fail(m,4);
 /* Fresh Command16 catches change after the header snapshot. */
 uint16_t command=0;m->reads++;
 if(((Config)method(m,48))(p->pci,1,4,1,&command)||command!=id.command)return fail(m,5);
 q->command_readback=command;return 0;
}
int qca_mapped_irq_guard(QcaMappedIrq*m){
 if(qca_mapped_irq_pci_guard(m))return -1;
 if(m->link_control&3)return fail(m,3);
 QcaUefiPort*p=m->irq->port;uint32_t state=0,chip=0;m->reads+=2;
 if(((Memory)method(m,16))(p->pci,2,0,0x80000,1,&state)||(state&7)!=3
  ||((Memory)method(m,16))(p->pci,2,0,0x8f0,1,&chip)||chip!=0x003821ff)return fail(m,10);
 return 0;
}
int qca_mapped_irq_poll(QcaMappedIrq*m){
 if(qca_mapped_irq_guard(m))return -1;
 uint32_t control=0;
 if(read32(m,0,&control))return fail(m,6);
 if(control&0x800){
  if(write32(m,0,control&~0x800u)||read32(m,0,&m->irq->last_control)||m->irq->last_control!=(control&~0x800u))return fail(m,7);
 }else m->irq->last_control=control;
 if(write32(m,8,BOOT_MASK)||read32(m,8,&m->irq->last_enable)||m->irq->last_enable!=BOOT_MASK)return fail(m,8);
 return 0;
}
int qca_mapped_irq_quiesce(QcaMappedIrq*m){
 if(qca_mapped_irq_guard(m))return -1;
 if(write32(m,8,0)||read32(m,8,&m->irq->last_enable)||m->irq->last_enable
  ||write32(m,0x14,BOOT_MASK)||read32(m,8,&m->irq->last_enable)||m->irq->last_enable
  ||read32(m,0xc,&m->irq->cause)||(m->irq->cause&BOOT_MASK))return fail(m,9);
 return 0;
}
