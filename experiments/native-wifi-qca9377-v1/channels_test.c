#include "channels_core.h"
#include "warm_core.h"
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static void*methods[20];static uint32_t reg[8][32];static uint16_t command=0x102;
static unsigned mode,allocations,flushes,unmaps,frees;static QcaCeBus bus;static QcaChannels channels;
static _Alignas(4096) uint8_t hosts[14][4096];
static uint32_t warm_reset=0x100,warm_lf=0x14,warm_indicator=2;
static uint64_t warm_now;static unsigned warm_pipes_phase,warm_pipes_completed;
static int warm_read(void*c,uint32_t address,uint32_t*out){
 (void)c;assert(address==0x800||address==0x850||address==0x3a028);
 *out=address==0x800?warm_reset:address==0x850?warm_lf:warm_indicator;return 0;
}
static int warm_write(void*c,uint32_t address,uint32_t value){
 (void)c;assert(!(command&4)&&!frees&&!unmaps&&allocations==14);
 if(address==0x800){warm_reset=value&~0x40u;if(value&0x40)warm_indicator=2;}
 else if(address==0x850)warm_lf=value;
 else{assert(address==0x3a028&&!value);warm_indicator=0;}
 return 0;
}
static int warm_guard(void*c){(void)c;return command&4?-1:0;}
static int warm_pipes(void*c){
 (void)c;
 if(!warm_pipes_phase){assert(!qca_ce_bus_stop_begin(&bus,warm_now));warm_pipes_phase=1;return 0;}
 int rc=qca_ce_bus_stop_poll(&bus,warm_now);
 if(rc<=0)return rc;
 rc=warm_pipes_completed?qca_channels_reconfigure(&channels):qca_channels_configure(&channels);
 if(rc)return -1;
 warm_pipes_completed++;warm_pipes_phase=0;return 1;
}
static Status EFIAPI memread(void*p,uint32_t w,uint8_t bar,uint64_t a,uint64_t n,void*out){
 assert(p==methods&&w==2&&!bar&&n==1&&a>=0x34400);unsigned id=(unsigned)(a-0x34400)/0x400,off=(unsigned)(a-0x34400)%0x400;assert(id<8&&off<=0x50);
 *(uint32_t*)out=reg[id][off/4];return 0;
}
static Status EFIAPI memwrite(void*p,uint32_t w,uint8_t bar,uint64_t a,uint64_t n,void*in){
 assert(p==methods&&w==2&&!bar&&n==1&&a>=0x34400);unsigned id=(unsigned)(a-0x34400)/0x400,off=(unsigned)(a-0x34400)%0x400;assert(id<8&&off<=0x50);
 uint32_t v=*(uint32_t*)in;
 if(off==0x18)reg[id][off/4]=v?((mode==16&&id==7)?1:9):0;
 else if(off==0x30||off==0x38)reg[id][off/4]&=~v;
 else reg[id][off/4]=v;
 if(mode==20&&id==2&&off==0x40)return 1;
 if(mode==25&&id==2&&off==8&&v)return 1;
 return 0;
}
static Status EFIAPI configread(void*p,uint32_t w,uint32_t off,uint64_t n,void*out){
 assert(p==methods&&w==1&&off==4&&n==1);*(uint16_t*)out=command;return 0;
}
static Status EFIAPI configwrite(void*p,uint32_t w,uint32_t off,uint64_t n,void*in){
 assert(p==methods&&w==1&&off==4&&n==1);command=*(uint16_t*)in;return mode==15&&(command&4)?1:0;
}
static Status EFIAPI allocate(void*p,uint32_t type,uint32_t memory,uint64_t pages,void**out,uint64_t attrs){
 assert(p==methods&&!type&&memory==4&&pages==1&&!attrs&&!(command&4)&&allocations<14);
 unsigned i=allocations++;*out=hosts[mode==22&&i==1?0:i];return 0;
}
static Status EFIAPI map(void*p,uint32_t op,void*host,uint64_t*n,uint64_t*a,void**token){
 assert(p==methods&&op==2&&*n==4096);unsigned i=(unsigned)(((uint8_t*)host-hosts[0])/4096);assert(i<14);
 *a=0x100000+4096*(mode==21&&i==13?0:i);*token=host;return mode==i+1?1:0;
}
static Status EFIAPI flush(void*p){assert(p==methods&&!(command&4));flushes++;return mode==17?1:0;}
static Status EFIAPI unmap(void*p,void*token){assert(p==methods&&token&&!(command&4)&&flushes);unmaps++;return mode==18?1:0;}
static Status EFIAPI freebuffer(void*p,uint64_t pages,void*host){
 assert(p==methods&&pages==1&&host&&!(command&4)&&unmaps);assert(!qca_ce_bus_released(&bus));
 if(mode==19)return 1;
 frees++;return 0;
}
static void stop_bus(uint64_t t){assert(!qca_ce_bus_stop_begin(&bus,t));assert(qca_ce_bus_stop_poll(&bus,t+1)==1);assert(!(command&4));}
int main(int argc,char**argv){
 assert(argc==2);unsigned scenario=(unsigned)atoi(argv[1]);assert(scenario<=26);
 methods[2]=(void*)memread;methods[3]=(void*)memwrite;methods[6]=(void*)configread;methods[7]=(void*)configwrite;
 methods[9]=(void*)map;methods[10]=(void*)unmap;methods[11]=(void*)allocate;methods[12]=(void*)freebuffer;methods[13]=(void*)flush;
 QcaUefiPort port={.pci=methods,.bar_extent=0x200000,.claimed=1,.validated=1,.memory_ready=1,.wake_owned=1};
 QcaCeAccess access={0};assert(!qca_ce_access_init(&access,&port,255));assert(!qca_ce_bus_init(&bus,&access));
 assert(qca_channels_begin(&channels,&bus)==-1);stop_bus(0);assert(!qca_channels_begin(&channels,&bus));
 assert(qca_channels_begin(&channels,&bus)==-1);assert(qca_channels_configure(&channels)==-1);
 if((scenario>=1&&scenario<=14)||scenario==21||scenario==22)mode=scenario;
 for(unsigned i=0;i<14;i++){
  int rc=qca_channels_prepare_step(&channels);
  if(rc<0){assert(mode);break;}
  assert(rc==(i==13));assert(!(command&4));
 }
 if(channels.phase==QCA_CHANNEL_FAULT){
  assert((scenario>=1&&scenario<=14)||scenario==21||scenario==22);
  assert(!frees&&!unmaps);mode=0;
  if(scenario==22){
   assert(channels.buffers[0].allocation_uncertain&&channels.buffers[1].allocation_uncertain);
   assert(qca_channels_close_step(&channels)==-1&&!frees&&!unmaps&&port.dma_users==2);
   puts("Aliased allocator retained; unload forbidden; MOCK ONLY");return 0;
  }
 }else{
  assert(channels.phase==QCA_CHANNEL_READY&&port.dma_users==14&&access.count==14);
  assert(qca_channels_prepare_step(&channels)==-1&&allocations==14);
  if(scenario==26){
   QcaWarm warm={0};assert(!qca_warm_begin(&warm,warm_read,warm_write,warm_guard,warm_pipes,0,0));
   for(warm_now=0;warm_now<100000;warm_now+=1000)if(qca_warm_poll(&warm,warm_now))break;
   assert(warm.phase==QCA_WARM_DONE&&!warm.owned&&warm.cpu_resets==2&&warm.pipe_inits==2);
   assert(warm_pipes_completed==2&&allocations==14&&!frees&&!unmaps&&!(command&4));
   assert(!qca_channels_prepared(&channels));stop_bus(100000);
   assert(!qca_channels_reconfigure(&channels));
  }
  if(scenario==25)mode=25;
  int configured=scenario==26?0:qca_channels_configure(&channels);
  if(scenario==25){assert(configured==-1&&channels.phase==QCA_CHANNEL_FAULT&&!frees);mode=0;stop_bus(2);}
  else{
   assert(!configured&&!qca_channels_prepared(&channels));assert(qca_channels_post_receive(&channels)==-1);
   command|=4;assert(qca_channels_prepared(&channels)==-1);command&=~4u;
   port.claimed=0;assert(qca_channels_prepared(&channels)==-1);port.claimed=1;
   access.count=13;assert(qca_channels_prepared(&channels)==-1);access.count=14;
   channels.buffers[1].address=channels.buffers[0].address;assert(qca_channels_prepared(&channels)==-1);channels.buffers[1].address=0x101000;
   channels.buffers[1].pages=2;assert(qca_channels_prepared(&channels)==-1);channels.buffers[1].pages=1;
   channels.buffers[1].context=0;assert(qca_channels_prepared(&channels)==-1);channels.buffers[1].context=&bus;
   channels.rings[2].receive=0;assert(qca_channels_prepared(&channels)==-1);channels.rings[2].receive=1;
   bus.engines[5].phase=QCA_CE_HW_CONFIGURED;assert(qca_channels_prepared(&channels)==-1);bus.engines[5].phase=QCA_CE_HW_STOPPED;
   assert(reg[5][0]==0&&reg[5][2]==0&&reg[6][0]==0&&reg[6][2]==0);
   if(scenario==23){reg[2][2]+=4096;assert(qca_channels_prepared(&channels)==-1);reg[2][2]-=4096;}
   if(scenario==24){channels.buffers[3].valid=0;assert(qca_channels_prepared(&channels)==-1);channels.buffers[3].valid=1;}
   if(scenario==15)mode=15;
   int rc=qca_ce_bus_start(&bus);
   if(scenario==15){assert(rc==-1&&bus.owned&&(command&4));assert(qca_channels_prepared(&channels)==-1);}
   else{
    assert(!rc&&!qca_channels_prepared(&channels));
    channels.buffers[9].exposed=0;assert(qca_channels_prepared(&channels)==-1);channels.buffers[9].exposed=1;
    if(scenario==20)mode=20;
    rc=qca_channels_post_receive(&channels);
    if(scenario==20){assert(rc==-1&&channels.rings[2].fault&&channels.phase==QCA_CHANNEL_FAULT);}
    else{
     assert(!rc&&channels.phase==QCA_CHANNEL_POSTED&&!qca_channels_prepared(&channels));
     assert(reg[1][0x40/4]==1&&reg[2][0x40/4]==1&&reg[7][0x40/4]==0);
     assert(channels.rings[1].capacity[0]==2048&&channels.rings[2].capacity[0]==2048);
     assert(qca_channels_post_receive(&channels)==-1);
    }
   }
   assert(qca_channels_close_step(&channels)==-1&&!frees&&!unmaps&&!channels.cleanup_slot);
   mode=scenario==16?16:0;
   if(scenario==16){assert(!qca_ce_bus_stop_begin(&bus,10));assert(!qca_ce_bus_stop_poll(&bus,11));assert(qca_ce_bus_stop_poll(&bus,1000010)==-1);assert(!(command&4)&&bus.owned);assert(qca_channels_close_step(&channels)==-1&&!frees);mode=0;}
   stop_bus(1000020);
  }
 }
 if(scenario>=17&&scenario<=19){mode=scenario;assert(qca_channels_close_step(&channels)==-1&&channels.cleanup_slot==0&&!frees);mode=0;}
 for(unsigned i=0;i<14;i++){assert(qca_channels_close_step(&channels)==0);assert(channels.cleanup_slot==i+1);}
 assert(qca_channels_close_step(&channels)==1&&channels.phase==QCA_CHANNEL_CLOSED);
 assert(frees==allocations&&!port.dma_users&&!access.count&&!bus.owned&&!(command&4));
 for(unsigned i=0;i<14;i++)assert(!channels.buffers[i].mapped&&!channels.buffers[i].allocated);
 assert(qca_channels_close_step(&channels)==1);
 printf("Full channels scenario %u: mapped ownership, RX, all-eight stop, guarded cleanup PASS; MOCK ONLY\n",scenario);return 0;
}
