/* QCA9377 UEFI target adapter. Physical lifecycle evidence is version-specific.
 * No direct physical dereference, bus-master enable, reset or firmware upload.
 */
#include "uefi_port.h"
#include "pci_identity.h"
static const Guid pci_guid={0x4cf5b200,0x68b8,0x4ca5,{0x9e,0xec,0xb2,0x3e,0x3f,0x50,0x02,0x9a}};
typedef Status(EFIAPI *Open)(void*,const Guid*,void**,void*,void*,uint32_t);
typedef Status(EFIAPI *Close)(void*,const Guid*,void*,void*);
typedef Status(EFIAPI *Free)(void*);
typedef Status(EFIAPI *ConfigRead)(void*,uint32_t,uint32_t,uint64_t,void*);
typedef Status(EFIAPI *ConfigWrite)(void*,uint32_t,uint32_t,uint64_t,void*);
typedef Status(EFIAPI *Bar)(void*,uint8_t,uint64_t*,void**);
typedef Status(EFIAPI *Attributes)(void*,uint32_t,uint64_t,uint64_t*);
typedef Status(EFIAPI *Memory)(void*,uint32_t,uint8_t,uint64_t,uint64_t,void*);
static void*method(void*p,unsigned offset){return *(void**)((uint8_t*)p+offset);}
static uint64_t little(const uint8_t*p,unsigned bytes){uint64_t r=0;for(unsigned i=0;i<bytes;i++)r|=(uint64_t)p[i]<<(8*i);return r;}
static int port_error(QcaUefiPort*p,unsigned step,Status status){p->error=(step<<8)|(uint32_t)(status&255);return -1;}
int qca_port_open(QcaUefiPort*p,SystemTable*st,void*image,void*controller,const QcaPciTarget*target){
 if(!p||p->claimed||p->dma_users||p->link_owned||p->boot_irq_owned||!st||!st->boot||!image||!controller||!target)return -1;
 p->system=st;p->image=image;p->controller=controller;p->pci=0;p->resource=0;
 p->memory_attempted=p->memory_ready=p->validated=p->wake_owned=0;
 p->error=0;
 Status rc=((Open)service(st,280))(controller,&pci_guid,&p->pci,image,controller,0x30);
 if(rc)return port_error(p,1,rc);
 p->claimed=1;
 if(!p->pci)return port_error(p,2,0);
 uint32_t config[16]={0};QcaPciIdentity identity;uint64_t supported=0;
 rc=((ConfigRead)method(p->pci,48))(p->pci,2,0,16,config);
 if(rc)return port_error(p,3,rc);
 if(qca_pci_identity(config,&identity)
  ||identity.subsystem_vendor!=target->subsystem_vendor||identity.subsystem_device!=target->subsystem_device
  ||identity.revision!=target->revision||(identity.command&4))return port_error(p,4,0);
 p->original_command=(uint16_t)config[1];
 Attributes attr=(Attributes)method(p->pci,120);
 rc=attr(p->pci,4,0,&supported);if(rc||!(supported&0x200))return port_error(p,5,rc);
 rc=attr(p->pci,0,0,&p->original_attributes);
 if(rc||(p->original_attributes&0x400))return port_error(p,6,rc);
 rc=((Bar)method(p->pci,128))(p->pci,0,&supported,&p->resource);
 if(rc||!p->resource)return port_error(p,7,rc);
 const uint8_t*r=p->resource;
 /* ACPI QWord address-space descriptor + EndTag. Reject IO, translation,
 * unsupported geometry and insufficient extent before allowing MEM access. */
 if(r[0]!=0x8a||little(r+1,2)!=43||r[3]||r[46]!=0x79
  ||(little(r+6,8)!=32&&little(r+6,8)!=64)||little(r+14,8)!=identity.bar0
  ||little(r+30,8)||little(r+38,8)<0x80008||little(r+38,8)>0x1000000
  ||identity.bar0>UINT64_MAX-little(r+38,8))return port_error(p,8,0);
 /* GetBarAttributes AddrRangeMax may encode alignment (EDK2), not end.
  * Extent checks therefore use only translated base + AddrLen. */
 p->bar_extent=little(r+38,8);
 rc=((Free)service(st,72))(p->resource);if(rc)return port_error(p,9,rc);
 p->resource=0;p->validated=1;return 0;
}
int qca_port_enable_memory(QcaUefiPort*p){
 if(!p||!p->claimed||!p->validated||p->memory_attempted)return -1;
 /* Mark BEFORE the write: an error does not prove the device was untouched. */
 p->memory_attempted=1;
 Status rc=((Attributes)method(p->pci,120))(p->pci,2,0x200,0);
 if(rc)return port_error(p,10,rc);
 uint16_t command=0;
 rc=((ConfigRead)method(p->pci,48))(p->pci,1,4,1,&command);
 if(rc||command!=(uint16_t)(p->original_command|2))return port_error(p,11,rc);
 p->memory_ready=1;return 0;
}
int qca_port_read32(void*context,uint32_t address,uint32_t*out){
 QcaUefiPort*p=context;
 if(!p||!out||!p->memory_ready||(address!=0x80000&&address!=0x8f0)||address>p->bar_extent-4)return -1;
 return ((Memory)method(p->pci,16))(p->pci,2,0,address,1,out)?-1:0;
}
int qca_port_write32(void*context,uint32_t address,uint32_t value){
 QcaUefiPort*p=context;
 if(!p||!p->memory_ready||address!=0x80004||value>1||address>p->bar_extent-4)return -1;
 if(value)p->wake_owned=1;
 if(((Memory)method(p->pci,24))(p->pci,2,0,address,1,&value))return -1;
 if(!value)p->wake_owned=0;
 return 0;
}
int qca_port_close(QcaUefiPort*p,QcaWake*w){
 if(!p||p->dma_users||p->link_owned||p->boot_irq_owned)return -1;
 if(p->wake_owned&&(!w||!w->owned))return -1;
 if(w&&w->owned){
  if(w->context!=p||qca_wake_close(w))return -1;
 }
 if(!p->claimed)return 0;
 if(p->memory_attempted){
  if(((Attributes)method(p->pci,120))(p->pci,1,p->original_attributes,0))return -1;
  /* Attribute flags may be cached. Actual PCI Command is authoritative.
   * Write16 only: a Write32 would also touch PCI Status W1C bits. */
  uint16_t command=0;
  Status rc=((ConfigRead)method(p->pci,48))(p->pci,1,4,1,&command);
  if(rc)return port_error(p,12,rc);
  if(command!=p->original_command){
   command=p->original_command;
   rc=((ConfigWrite)method(p->pci,56))(p->pci,1,4,1,&command);
   if(rc)return port_error(p,13,rc);
   rc=((ConfigRead)method(p->pci,48))(p->pci,1,4,1,&command);
   if(rc||command!=p->original_command)return port_error(p,14,rc);
  }
  p->memory_attempted=p->memory_ready=0;
 }
 if(p->resource){if(((Free)service(p->system,72))(p->resource))return -1;p->resource=0;}
 if(((Close)service(p->system,288))(p->controller,&pci_guid,p->image,p->controller))return -1;
 p->claimed=p->validated=0;p->pci=0;return 0;
}
