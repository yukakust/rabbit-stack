/* SPDX-License-Identifier: GPL-2.0-only
 * Bounded CE ring bookkeeping adapted from ath10k ce.c/ce.h; no MMIO here. */
#include "ce_ring.h"
#include <stddef.h>
static void put(volatile uint8_t*p,uint64_t v,unsigned n){for(unsigned i=0;i<n;i++)p[i]=(uint8_t)(v>>(8*i));}
static uint32_t get(const volatile uint8_t*p,unsigned n){uint32_t v=0;for(unsigned i=0;i<n;i++)v|=(uint32_t)p[i]<<(8*i);return v;}
static unsigned delta(const QcaCeRing*r,unsigned a,unsigned b){return (a-b)&(r->entries-1);}
int qca_ce_init(QcaCeRing*r,volatile uint8_t*memory,uint64_t dma,uint32_t entries,int receive,QcaCePublish publish,QcaCeStop stop,void*context){
 if(!r||r->owned||!memory||((uintptr_t)memory&7)||(dma&7)||dma>UINT32_MAX||entries<2||entries>QCA_CE_MAX_ENTRIES
  ||(entries&(entries-1))||dma>UINT32_MAX-(entries*8-1)||receive<0||receive>1||!publish||!stop)return -1;
 r->descriptors=memory;r->entries=(uint8_t)entries;r->receive=(uint8_t)receive;
 r->publish=publish;r->stop=stop;r->context=context;r->read=r->write=r->published=r->fault=0;
 for(unsigned i=0;i<entries;i++){put(memory+8*i,0,8);r->cookie[i]=r->address[i]=r->capacity[i]=0;}
 r->owned=1;return 0;
}
int qca_ce_post(QcaCeRing*r,uint64_t address,uint32_t bytes,uint32_t cookie,uint32_t meta,uint32_t flags){
 if(!r||!r->owned||r->fault||address>UINT32_MAX||!bytes||bytes>65535||address>UINT32_MAX-(bytes-1)
  ||meta>0x3fff||flags>3||(r->receive&&(meta||flags)))return -1;
 unsigned next=(r->write+1)&(r->entries-1);if(next==r->read)return 1;
 unsigned index=r->write;volatile uint8_t*d=r->descriptors+8*index;
 r->cookie[index]=cookie;r->address[index]=(uint32_t)address;r->capacity[index]=(uint16_t)bytes;
 put(d,(uint32_t)address,4);put(d+4,r->receive?0:bytes,2);put(d+6,(meta<<2)|flags,2);
 /* Ownership/bookkeeping precede ambiguous doorbell write. */
 r->write=(uint8_t)next;__atomic_thread_fence(__ATOMIC_RELEASE);
 if(!(flags&1)){
  if(r->publish(r->context,next)){r->fault=1;return -1;}
  r->published=(uint8_t)next;
 }
 return 0;
}
int qca_ce_complete(QcaCeRing*r,uint32_t hardware_index,uint32_t*cookie,uint32_t*bytes){
 if(!r||!r->owned||r->fault||!cookie||!bytes)return -1;
 if(hardware_index>=r->entries||delta(r,hardware_index,r->read)>delta(r,r->published,r->read)){r->fault=1;return -1;}
 if(hardware_index==r->read)return 1;
 __atomic_thread_fence(__ATOMIC_ACQUIRE);unsigned i=r->read;volatile uint8_t*d=r->descriptors+8*i;
 uint32_t n=get(d+4,2);
 /* ath10k: hardware index may advance before RX descriptor length arrives. */
 if(r->receive&&!n)return 1;
 if(get(d,4)!=r->address[i]||!n||n>r->capacity[i]||(!r->receive&&n!=r->capacity[i])){r->fault=1;return -1;}
 *cookie=r->cookie[i];*bytes=n;put(d+4,0,2);r->cookie[i]=r->address[i]=r->capacity[i]=0;
 r->read=(uint8_t)((i+1)&(r->entries-1));return 0;
}
int qca_ce_close(QcaCeRing*r){
 if(!r)return -1;
 if(!r->owned)return 0;
 if(r->stop(r->context))return -1;
 __atomic_thread_fence(__ATOMIC_ACQUIRE);
 for(unsigned i=0;i<r->entries;i++)put(r->descriptors+8*i,0,8);
 r->owned=0;r->read=r->write=r->published=0;return 0;
}
