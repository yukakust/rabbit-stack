/* Reversible legacy bootstrap indication from pinned ath10k pci.c/hw.h. */
#include "boot_irq.h"
#include "power_core.h"
#include "pci_identity.h"
#define BOOT_MASK 0x7fc00u
#define MSI_FW_MASK 0x800u
#define INTX_DISABLE 0x400u
typedef Status(EFIAPI *Config)(void*,uint32_t,uint32_t,uint64_t,void*);
typedef Status(EFIAPI *Memory)(void*,uint32_t,uint8_t,uint64_t,uint64_t,void*);
static int valid(QcaUefiPort*p){return p&&p->claimed&&p->validated&&p->pci&&p->memory_ready&&p->wake_owned&&p->bar_extent>=0x3a018;}
static void*method(QcaBootIrq*q,unsigned off){return *(void**)((uint8_t*)q->port->pci+off);}
static int fail(QcaBootIrq*q,unsigned e){q->error=(uint8_t)e;return -1;}
static uint16_t word(const uint8_t*p){return (uint16_t)p[0]|((uint16_t)p[1]<<8);}
static int config_read(QcaBootIrq*q,unsigned off,uint16_t*out){return ((Config)method(q,48))(q->port->pci,1,off,1,out)?-1:0;}
static int command(QcaBootIrq*q,uint16_t value){
 if(((Config)method(q,56))(q->port->pci,1,4,1,&value)||config_read(q,4,&q->command_readback)||q->command_readback!=value)return -1;
 return 0;
}
static int read32(QcaBootIrq*q,unsigned off,uint32_t*out){
 if(((Memory)method(q,16))(q->port->pci,2,0,0x3a000+off,1,out)||*out==UINT32_MAX)return -1;
 return 0;
}
static int write32(QcaBootIrq*q,unsigned off,uint32_t value){
 q->writes++;return ((Memory)method(q,24))(q->port->pci,2,0,0x3a000+off,1,&value)?-1:0;
}
static int write_verify(QcaBootIrq*q,unsigned off,uint32_t value,uint32_t*out){return write32(q,off,value)||read32(q,off,out)||*out!=value?-1:0;}
static int msi_disabled(QcaBootIrq*q){
 uint16_t v=0;
 if(q->msi&&(config_read(q,q->msi+2,&v)||(v&1)))return -1;
 if(q->msix&&(config_read(q,q->msix+2,&v)||(v&0x8000)))return -1;
 return 0;
}
static int host_masked(QcaBootIrq*q){
 if(!valid(q->port)||q->port->dma_users||config_read(q,4,&q->command_readback)
  ||q->command_readback!=(uint16_t)(q->original_command|INTX_DISABLE)||msi_disabled(q))return -1;
 return 0;
}
static int disable_clear(QcaBootIrq*q){
 /* W1C after enable zero; extra read explicitly flushes the posted clear. */
 if(write_verify(q,8,0,&q->last_enable)||write32(q,0x14,BOOT_MASK)||read32(q,8,&q->last_enable)||q->last_enable)return -1;
 if(read32(q,0xc,&q->cause)||(q->cause&BOOT_MASK))return -1;
 return 0;
}
int qca_boot_irq_begin(QcaBootIrq*q,QcaUefiPort*p){
 if(!q||q->owned||!valid(p)||p->boot_irq_owned||p->dma_users)return -1;
 q->port=p;q->error=0;q->msi=q->msix=0;
 uint32_t config[64]={0};uint8_t power[16];QcaPciIdentity id;
 if(((Config)method(q,48))(p->pci,2,0,64,config))return fail(q,1);
 qca_power_decode((uint8_t*)config,power);const uint8_t*c=(const uint8_t*)config;
 if(qca_pci_identity(config,&id)||id.subsystem_vendor!=0x1028||id.subsystem_device!=0x1810||id.revision!=0x31
  ||(id.command&4)||power[8]!=1||(power[2]&3))return fail(q,2);
 for(unsigned off=c[0x34];off;off=c[off+1]){
  /* power decoder already proved acyclic aligned bounds for this snapshot. */
  if(c[off]==5){if(q->msi)return fail(q,2);q->msi=(uint16_t)off;if(word(c+off+2)&1)return fail(q,2);}
  if(c[off]==0x11){if(q->msix)return fail(q,2);q->msix=(uint16_t)off;if(word(c+off+2)&0x8000)return fail(q,2);}
 }
 q->original_command=(uint16_t)id.command;
 if(read32(q,8,&q->original_enable)||read32(q,0,&q->original_control)||q->original_enable)return fail(q,3);
 q->last_enable=q->original_enable;q->last_control=q->original_control;
 q->owned=p->boot_irq_owned=1; /* before ambiguous host/device writes */
 if(command(q,(uint16_t)(q->original_command|INTX_DISABLE))||host_masked(q))return fail(q,4);
 if(write_verify(q,0,q->original_control&~MSI_FW_MASK,&q->last_control))return fail(q,5);
 if(disable_clear(q))return fail(q,6);
 return 0;
}
int qca_boot_irq_poll(QcaBootIrq*q){
 if(!q||!q->owned||!q->port->boot_irq_owned)return -1;
 if(host_masked(q))return fail(q,8);
 if(write_verify(q,8,BOOT_MASK,&q->last_enable))return fail(q,9);
 return 0;
}
int qca_boot_irq_close(QcaBootIrq*q){
 if(!q)return -1;
 if(!q->owned)return 0;
 if(!valid(q->port)||!q->port->boot_irq_owned||q->port->dma_users)return fail(q,7);
 uint16_t actual=0;
 if(config_read(q,4,&actual)||(actual!=q->original_command&&actual!=(uint16_t)(q->original_command|INTX_DISABLE)))return fail(q,8);
 int msi_bad=msi_disabled(q);
 if(command(q,(uint16_t)(q->original_command|INTX_DISABLE)))return fail(q,4);
 if(disable_clear(q))return fail(q,11);
 if(msi_bad)return fail(q,8); /* Device masked; retain before restoring host/core. */
 uint32_t control=0;if(read32(q,0,&control))return fail(q,10);
 control=(control&~MSI_FW_MASK)|(q->original_control&MSI_FW_MASK);
 if(write_verify(q,0,control,&q->last_control))return fail(q,10);
 if(command(q,q->original_command))return fail(q,12);
 q->owned=q->port->boot_irq_owned=0;return 0;
}
