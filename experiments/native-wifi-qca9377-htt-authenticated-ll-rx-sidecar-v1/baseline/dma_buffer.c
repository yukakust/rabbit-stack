/* UEFI common-buffer lifetime. No bus-master enable or CE MMIO operation. */
#include "dma_buffer.h"
typedef Status(EFIAPI *ConfigRead)(void*,uint32_t,uint32_t,uint64_t,void*);
typedef Status(EFIAPI *Allocate)(void*,uint32_t,uint32_t,uint64_t,void**,uint64_t);
typedef Status(EFIAPI *Map)(void*,uint32_t,void*,uint64_t*,uint64_t*,void**);
typedef Status(EFIAPI *Unmap)(void*,void*);
typedef Status(EFIAPI *Free)(void*,uint64_t,void*);
typedef Status(EFIAPI *Flush)(void*);
static void*method(QcaDmaBuffer*d,unsigned offset){return *(void**)((uint8_t*)d->port->pci+offset);}
static int error(QcaDmaBuffer*d,unsigned step,Status rc){d->error=(step<<8)|(uint32_t)(rc&255);return -1;}
static int master_off(QcaDmaBuffer*d){
 uint16_t command=0;Status rc=((ConfigRead)method(d,48))(d->port->pci,1,4,1,&command);
 if(rc||(command&4))return error(d,1,rc);
 return 0;
}
int qca_dma_open(QcaDmaBuffer*d,QcaUefiPort*p,uint32_t pages,QcaDmaStop stop,void*context){
 if(!d||d->allocated||d->mapped||!p||!p->claimed||!p->validated||!p->pci||p->dma_users>=64||!pages||pages>16||!stop)return -1;
 d->port=p;d->stop=stop;d->context=context;d->pages=pages;d->bytes=(uint64_t)pages*4096;
 d->host=d->mapping=0;d->address=UINT64_MAX;d->valid=d->exposed=d->allocation_uncertain=d->closing=0;d->error=0;
 if(master_off(d))return -1;
 /* AllocateAnyPages, BootServicesData, no DAC attribute. */
 Status rc=((Allocate)method(d,88))(p->pci,0,4,pages,&d->host,0);
 if(d->host){d->allocated=1;p->dma_users++;}
 if(rc){d->allocation_uncertain=d->allocated;return error(d,2,rc);}
 if(!d->host)return error(d,2,0);
 if((uintptr_t)d->host&4095)return error(d,3,0);
 uint64_t bytes=d->bytes;
 rc=((Map)method(d,72))(p->pci,2,d->host,&bytes,&d->address,&d->mapping);
 /* EDK2 can return mapping then fail IOMMU SetAttribute; retain that token. */
 d->mapped=!rc||d->mapping!=0;
 if(rc)return error(d,4,rc);
 if(bytes!=d->bytes||(d->address&4095)||d->address>UINT32_MAX||d->address>UINT32_MAX-(d->bytes-1))return error(d,5,0);
 for(uint64_t i=0;i<d->bytes;i++)((uint8_t*)d->host)[i]=0;
 d->valid=1;return 0;
}
int qca_dma_expose(QcaDmaBuffer*d){
 if(!d||!d->valid||d->closing||!d->allocated||!d->mapped||!d->port->claimed)return -1;
 d->exposed=1;return 0;
}
int qca_dma_close(QcaDmaBuffer*d){
 if(!d)return -1;
 if(!d->allocated&&!d->mapped)return 0;
 d->closing=1;
 if(!d->port||!d->port->claimed||!d->port->pci||d->allocation_uncertain)return -1;
 if(d->exposed&&d->stop(d->context))return error(d,6,0);
 if(master_off(d))return -1;
 Status rc=((Flush)method(d,104))(d->port->pci);if(rc)return error(d,7,rc);
 if(d->mapped){
  /* NULL mapping returned by successful Map is still passed to Unmap. */
  rc=((Unmap)method(d,80))(d->port->pci,d->mapping);if(rc)return error(d,8,rc);
  d->mapped=0;d->mapping=0;d->valid=0;
 }
 if(d->allocated){
  rc=((Free)method(d,96))(d->port->pci,d->pages,d->host);if(rc)return error(d,9,rc);
  d->allocated=0;d->host=0;d->port->dma_users--;
 }
 d->exposed=0;return 0;
}
