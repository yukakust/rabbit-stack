#include "dma_buffer.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static _Alignas(4096) uint8_t memory[131072];static void*methods[18];
static unsigned mode,allocs,frees,maps,unmaps,flushes,stops,master,events[32],event_count;
static void event(unsigned n){if(event_count<32)events[event_count++]=n;}
static Status EFIAPI read_config(void*p,uint32_t w,uint32_t o,uint64_t n,void*out){
 assert(p==methods&&w==1&&o==4&&n==1);event(2);
 if(mode==15)return EFI_ERROR(7);
 *(uint16_t*)out=(uint16_t)(0x102|master);return 0;
}
static Status EFIAPI allocate(void*p,uint32_t type,uint32_t memtype,uint64_t pages,void**out,uint64_t attributes){
 assert(p==methods&&!type&&memtype==4&&pages>=1&&pages<=16&&!attributes);event(0);
 if(mode==1)return EFI_ERROR(9);
 assert(allocs<2);*out=memory+(allocs++*65536)+(mode==16?1:0);return mode==2?EFI_ERROR(7):0;
}
static Status EFIAPI map(void*p,uint32_t op,void*host,uint64_t*bytes,uint64_t*address,void**mapping){
 assert(p==methods&&op==2&&host&&*bytes>=4096&&*bytes<=65536);maps++;event(0);
 if(mode==3)return EFI_ERROR(7);
 
 *mapping=mode==9?0:host;*address=0x100000+((uint8_t*)host-memory);
 if(mode==4)return EFI_ERROR(7);
 
 if(mode==5)*bytes-=1;
 if(mode==6)*address=0x100000000ULL;
 if(mode==7)*address+=1;
 if(mode==8)*address=0xfffff000;
 return 0;
}
static Status EFIAPI unmap(void*p,void*token){assert(p==methods&&(token||mode==9));event(4);
 if(mode==13)return EFI_ERROR(7);
 unmaps++;return 0;}
static Status EFIAPI free_buffer(void*p,uint64_t pages,void*host){assert(p==methods&&pages&&host);event(5);
 if(mode==14)return EFI_ERROR(7);
 frees++;return 0;}
static Status EFIAPI flush(void*p){assert(p==methods);event(3);
 if(mode==12)return EFI_ERROR(7);
 flushes++;return 0;}
static int stop(void*c){assert(c==methods);event(1);stops++;
 if(mode==10)return -1;
 if(mode!=11)master=0;
 return 0;}
int main(int argc,char**argv){
 assert(argc==2);mode=(unsigned)atoi(argv[1]);assert(mode<=17);unsigned scenario=mode;
 methods[48/8]=read_config;methods[72/8]=map;methods[80/8]=unmap;methods[88/8]=allocate;methods[96/8]=free_buffer;methods[104/8]=flush;
 memset(memory,0xaa,sizeof(memory));QcaUefiPort port={0};port.pci=methods;port.claimed=port.validated=1;
 QcaDmaBuffer d={0};int opened=qca_dma_open(&d,&port,mode==8?2:1,stop,methods);
 if(mode==1||mode==15){assert(opened==-1&&!d.allocated&&!port.dma_users&&!frees);return 0;}
 assert(d.allocated&&port.dma_users==1&&qca_port_close(&port,0)==-1);
 if(mode==2){assert(opened==-1&&d.allocation_uncertain&&qca_dma_close(&d)==-1&&!frees&&port.dma_users==1);return 0;}
 if(mode==3||mode==4||mode==5||mode==6||mode==7||mode==8||mode==16)assert(opened==-1&&!d.valid);
 else{assert(!opened&&d.valid&&d.mapped&&!memory[0]&&!memory[4095]);assert(!qca_dma_expose(&d));master=4;}
 if(mode==17){QcaDmaBuffer other={0};master=0;assert(!qca_dma_open(&other,&port,1,stop,methods)&&port.dma_users==2);assert(!qca_dma_close(&d)&&port.dma_users==1&&qca_port_close(&port,0)==-1);assert(!qca_dma_close(&other)&&!port.dma_users&&frees==2);return 0;}
 event_count=0;int closed=qca_dma_close(&d);
 if(mode>=10&&mode<=14){assert(closed==-1&&d.allocated&&port.dma_users==1&&!frees);assert(qca_dma_expose(&d)==-1);mode=0;assert(!qca_dma_close(&d));}
 else assert(!closed);
 assert(!d.allocated&&!d.mapped&&!d.host&&!port.dma_users&&frees==1);
 unsigned old=frees+unmaps+flushes;assert(!qca_dma_close(&d)&&old==frees+unmaps+flushes);
 if(scenario==0){assert(event_count==5&&events[0]==1&&events[1]==2&&events[2]==3&&events[3]==4&&events[4]==5);}
 if(scenario==9)assert(unmaps==1);
 if(scenario==3)assert(!unmaps);
 if(scenario==4)assert(unmaps==1);
 printf("DMA scenario %u: common-buffer geometry, stop/master/flush/unmap/free order and retained failure lifetime PASS; MOCK ONLY\n",scenario);return 0;
}
