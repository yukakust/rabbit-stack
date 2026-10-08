#include "runtime_pool.h"
#include "owner47.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static void*methods[16];static uint16_t command;static uint64_t next_address=0x100000;static unsigned allocs,maps,unmaps,frees,flushes,stops,fault;
static Status EFIAPI read_config(void*p,uint32_t width,uint32_t off,uint64_t n,void*out){assert(p==methods&&width==1&&off==4&&n==1);memcpy(out,&command,2);return 0;}
static Status EFIAPI allocate(void*p,uint32_t kind,uint32_t memory,uint64_t pages,void**out,uint64_t flags){assert(p==methods&&!kind&&memory==4&&!flags&&pages&&pages<=16);*out=aligned_alloc(4096,(size_t)pages*4096);assert(*out);allocs++;return 0;}
static Status EFIAPI map(void*p,uint32_t op,void*host,uint64_t*n,uint64_t*addr,void**token){assert(p==methods&&op==2&&host&&*n);*addr=next_address;next_address+=*n+4096;*token=host;maps++;return 0;}
static Status EFIAPI unmap(void*p,void*token){assert(p==methods&&token);if(fault==1)return EFI_ERROR(7);unmaps++;return 0;}
static Status EFIAPI release(void*p,uint64_t pages,void*host){assert(p==methods&&pages&&host);if(fault==2)return EFI_ERROR(7);free(host);frees++;return 0;}
static Status EFIAPI flush(void*p){assert(p==methods);flushes++;return fault==3?EFI_ERROR(7):0;}
static int stop(void*p){assert(p==methods);stops++;return fault==4;}
static unsigned pool_allocs,pool_frees;
static Status EFIAPI pool_allocate(uint32_t type,size_t n,void**p){assert(type==2&&n==sizeof(QcaHttRuntime)+_Alignof(QcaHttRuntime)-1);*p=malloc(n);assert(*p);pool_allocs++;return 0;}
static Status EFIAPI pool_release(void*p){assert(p);for(size_t i=0;i<sizeof(QcaHttRuntime)+_Alignof(QcaHttRuntime)-1;i++)assert(!((uint8_t*)p)[i]);free(p);pool_frees++;return 0;}
int main(void){methods[6]=(void*)read_config;methods[11]=(void*)allocate;methods[9]=(void*)map;methods[10]=(void*)unmap;methods[12]=(void*)release;methods[13]=(void*)flush;QcaUefiPort port={.claimed=1,.validated=1,.pci=methods};QcaDmaBuffer ce[14]={0};
 for(unsigned i=0;i<14;i++)assert(!qca_dma_open(&ce[i],&port,1,stop,methods));assert(port.dma_users==14);
 QcaHttPool owner={0};QcaHttPoolBoot boot={pool_allocate,pool_release};assert(qca_htt_pool_acquire(&owner,&boot,11));QcaHttRuntime*s=owner.runtime;assert(qca_htt_pool_attach(&owner,&port,ce,stop,methods));assert(!qca_htt_pool_release(&owner));QcaHttPool rival={0};assert(!qca_htt_pool_acquire(&rival,&boot,12));
 for(unsigned i=0;i<33;i++){assert(qca_htt_runtime_allocate_one(s)==1);assert(port.dma_users==15+i);}
 QcaRadioOwners basis={.epoch=11,.mappings=14,.dma_users=47,.pci=1,.wake=1,.link=1,.irq=1,.pin=1,.bus=1,.bus_master=1,.init_ready=1},snapshot;
 assert(qca_htt_owner47_snapshot(s,&basis,&snapshot)&&snapshot.mappings==47&&snapshot.dma_users==47);
 QcaRadioLifecycle life={0};assert(qca_radio47_begin(&life,&snapshot,1)&&qca_radio47_accepts_work(&life));
 basis.dma_users=14;assert(!qca_htt_owner47_snapshot(s,&basis,&snapshot));basis.dma_users=47;
 assert(qca_radio47_quiesce(&life,2,1000));basis.bus_master=0;basis.stop_verified=1;assert(qca_htt_owner47_snapshot(s,&basis,&snapshot)&&qca_radio47_observe(&life,&snapshot,3));
 assert(allocs==47&&maps==47&&port.dma_users==47&&qca_htt_runtime_inventory(s));
 assert(qca_htt_runtime_bind_ring(s,3,8,0x05020001));assert(s->ring.phase==Q_RING_FILLING&&s->owners[1023].paddr==(uint32_t)(s->extra[31].address+31*2048));
 for(unsigned i=0;i<1023;i++)assert(qca_htt_runtime_refill_one(s,(uint16_t)i));assert(s->ring.fill==1023&&*(uint32_t*)((uint8_t*)s->extra[32].host+8192)==1023&&!qca_htt_runtime_refill_one(s,1023));
 uint8_t cfg[40];assert(!qca_ring_cfg(&s->ring,1023,cfg)&&cfg[0]==2&&cfg[1]==1);
 port.dma_users--;assert(!qca_htt_runtime_inventory(s));port.dma_users++;
 s->tx_owners=1;assert(!qca_htt_runtime_close_one(s)&&!qca_htt_runtime_detachable(s));s->tx_owners=0;
 assert(!qca_dma_expose(&s->extra[0]));command=4;assert(!qca_htt_runtime_close_one(s)&&s->extra[0].allocated&&port.dma_users==47);command=0;
 fault=3;assert(!qca_htt_runtime_close_one(s)&&s->extra[0].mapped&&port.dma_users==47);fault=0;
 for(unsigned mode=1;mode<=4;mode++){fault=mode;assert(!qca_htt_runtime_close_one(s)&&port.dma_users==47&&s->extra[0].allocated);if(mode==1)assert(s->extra[0].mapped);fault=0;}
 for(unsigned i=0;i<33;i++){assert(qca_htt_runtime_close_one(s));basis.dma_users=port.dma_users;assert(qca_htt_owner47_snapshot(s,&basis,&snapshot)&&snapshot.mappings==47-i-1&&qca_radio47_observe(&life,&snapshot,4+i));}assert(qca_htt_runtime_close_one(s)&&qca_htt_runtime_detachable(s)&&port.dma_users==14);
 for(unsigned i=0;i<14;i++)assert(!qca_dma_close(&ce[i]));assert(!port.dma_users&&frees==47&&unmaps==47);assert(qca_htt_pool_release(&owner)&&pool_allocs==1&&pool_frees==1);
 printf("ACTUAL-C-FAKE-PCI47 owner alloc/map/32bit/disjoint/BME/flush/close PASS runtime=%zu ring=%zu rxowner=%zu dma=%zu DMAbytes=2109440 pool_not_image; physicalfalse\n",sizeof(QcaHttRuntime),sizeof(QRingState),sizeof(QRxOwner),sizeof(QcaDmaBuffer));return 0;}
