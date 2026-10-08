/* PCIe link policy from ath10k hif_power_up, reversible native adapter. */
#include "pcie_link.h"
#include "power_core.h"
#include "pci_identity.h"
typedef Status(EFIAPI *Config)(void*,uint32_t,uint32_t,uint64_t,void*);
static int valid(QcaUefiPort*p){return p&&p->claimed&&p->validated&&p->pci;}
static void*method(QcaPcieLink*l,unsigned off){return *(void**)((uint8_t*)l->port->pci+off);}
static int fail(QcaPcieLink*l,unsigned error){l->error=(uint8_t)error;return -1;}
static int snapshot(QcaPcieLink*l,uint16_t*offset,uint16_t*value){
 uint32_t config[64]={0};uint8_t power[16];QcaPciIdentity id;
 if(!valid(l->port)||((Config)method(l,48))(l->port->pci,2,0,64,config))return fail(l,1);
 qca_power_decode((uint8_t*)config,power);
 if(qca_pci_identity(config,&id)||id.subsystem_vendor!=0x1028||id.subsystem_device!=0x1810||id.revision!=0x31
  ||(id.command&4)||power[8]!=1||(power[2]&3))return fail(l,2);
 unsigned cap=power[4]|((unsigned)power[5]<<8);const uint8_t*c=(const uint8_t*)config;
 if(!cap||cap>0xec||((c[cap+2]&15)!=1&&(c[cap+2]&15)!=2)||(c[cap+2]&0xf0))return fail(l,3);
 *offset=(uint16_t)(cap+0x10);*value=(uint16_t)(power[6]|((uint16_t)power[7]<<8));return 0;
}
static int write_verify(QcaPcieLink*l,uint16_t value){
 if(((Config)method(l,56))(l->port->pci,1,l->offset,1,&value))return fail(l,4);
 if(((Config)method(l,48))(l->port->pci,1,l->offset,1,&l->readback)||l->readback!=value)return fail(l,5);
 return 0;
}
int qca_pcie_pause(QcaPcieLink*l,QcaUefiPort*p){
 if(!l||l->owned||!valid(p)||p->link_owned||p->dma_users)return -1;
 l->port=p;l->error=0;
 if(snapshot(l,&l->offset,&l->original))return -1;
 l->readback=l->original;l->owned=p->link_owned=1;
 return write_verify(l,(uint16_t)(l->original&~3u));
}
int qca_pcie_recheck(QcaPcieLink*l){
 if(!l||!l->owned||!valid(l->port)||!l->port->link_owned||l->port->dma_users)return -1;
 uint16_t offset=0,value=0;
 if(snapshot(l,&offset,&value)||offset!=l->offset)return fail(l,7);
 l->readback=value;
 if(value&3)return write_verify(l,(uint16_t)(value&~3u));
 return 0;
}
int qca_pcie_restore(QcaPcieLink*l){
 if(!l)return -1;
 if(!l->owned)return 0;
 if(!valid(l->port)||!l->port->link_owned||l->port->dma_users)return fail(l,6);
 uint16_t offset=0,value=0;
 if(snapshot(l,&offset,&value)||offset!=l->offset)return fail(l,7);
 if(write_verify(l,l->original))return -1;
 l->owned=l->port->link_owned=0;return 0;
}
