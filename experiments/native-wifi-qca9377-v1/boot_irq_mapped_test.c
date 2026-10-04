#define main previous_channels_main
#include "channels_test.c"
#undef main
#include "boot_irq_mapped.h"
static uint32_t core[6]={0x12300e88};
static unsigned operation_count,fail_at,irq_writes,header_kind;
static int fault(void){return ++operation_count==fail_at;}
static Status EFIAPI irq_memread(void*p,uint32_t w,uint8_t bar,uint64_t a,uint64_t n,void*out){
 if(a>=0x34400&&a<=0x36050)return memread(p,w,bar,a,n,out);
 assert(p==methods&&w==2&&!bar&&n==1);
 if(fault())return 1;
 if(a==0x80000){*(uint32_t*)out=header_kind==20?UINT32_MAX:header_kind==21?2:3;return 0;}
 if(a==0x8f0){*(uint32_t*)out=header_kind==22?0:0x003821ff;return 0;}
 assert(a>=0x3a000&&a<=0x3a014);*(uint32_t*)out=header_kind==23?UINT32_MAX:core[(a-0x3a000)/4];return 0;
}
static Status EFIAPI irq_memwrite(void*p,uint32_t w,uint8_t bar,uint64_t a,uint64_t n,void*in){
 if(a>=0x34400&&a<=0x36050)return memwrite(p,w,bar,a,n,in);
 assert(p==methods&&w==2&&!bar&&n==1&&(a==0x3a000||a==0x3a008||a==0x3a014));
 assert((command&0x404)==0x400);irq_writes++;
 uint32_t v=*(uint32_t*)in;if(a==0x3a014)core[3]&=~v;else core[(a-0x3a000)/4]=v;
 return fault()?1:0; /* Ambiguous accepted write. */
}
static Status EFIAPI irq_configread(void*p,uint32_t w,uint32_t off,uint64_t n,void*out){
 assert(p==methods);
 if(fault())return 1;
 if(w==1&&off==4&&n==1){*(uint16_t*)out=header_kind==24?(command^4):command;return 0;}
 assert(w==2&&!off&&n==64);uint32_t*c=out;memset(out,0,256);
 c[0]=header_kind==10?0x0042168d:0x0042168c;c[1]=0x00100000|command;
 c[2]=header_kind==11?0x02800030:0x02800031;c[4]=header_kind==12?0xd2000000:0xd1000000;
 c[11]=header_kind==13?0x18111028:0x18101028;c[13]=0x40;c[16]=0x7001;c[17]=header_kind==14?3:0;
 c[28]=header_kind==15?0x7010:0x10;c[32]=header_kind==16?0x143:0x140;
 if(header_kind==17){c[28]=0xb010;c[44]=0x00010005;}
 if(header_kind==18){c[28]=0xb010;c[44]=0x80000011;}
 if(header_kind==19){c[28]=0xb010;c[44]=0x00000005;}
 return 0;
}
int mapped_irq_fixture_main(int argc,char**argv){
 assert(argc==2);unsigned scenario=(unsigned)atoi(argv[1]);assert(scenario<=35);
 methods[2]=(void*)irq_memread;methods[3]=(void*)irq_memwrite;methods[6]=(void*)irq_configread;methods[7]=(void*)configwrite;
 methods[9]=(void*)map;methods[10]=(void*)unmap;methods[11]=(void*)allocate;methods[12]=(void*)freebuffer;methods[13]=(void*)flush;
 QcaUefiPort p={.pci=methods,.bar_extent=0x200000,.claimed=1,.validated=1,.memory_ready=1,.wake_owned=1,.link_owned=1};
 QcaBootIrq irq={0};assert(!qca_boot_irq_begin(&irq,&p));assert(command==0x502&&irq.owned);
 QcaCeAccess access={0};assert(!qca_ce_access_init(&access,&p,255));assert(!qca_ce_bus_init(&bus,&access));stop_bus(0);
 assert(!qca_channels_begin(&channels,&bus));for(unsigned i=0;i<14;i++)assert(qca_channels_prepare_step(&channels)==(i==13));
 /* No CE configuration is needed for retained/BM-off ROM boot polling. */
 QcaMappedIrq mapped={.irq=&irq,.channels=&channels,.bar=0xd1000000,.link_offset=0x80};
 assert(!qca_mapped_irq_guard(&mapped));unsigned before=irq_writes;
 assert(qca_boot_irq_poll(&irq)==-1&&irq_writes==before&&irq.owned&&p.dma_users==14);
 assert(qca_boot_irq_close(&irq)==-1&&irq_writes==before&&irq.owned);
 core[0]|=0x800;operation_count=irq_writes=0;
 if(scenario<=9)fail_at=scenario;else if(scenario<=24)header_kind=scenario;
 if(scenario==25)command|=4;
 if(scenario==26)command&=~0x400;
 if(scenario==27)p.wake_owned=0;
 if(scenario==28)p.link_owned=0;
 if(scenario==29)channels.buffers[9].valid=0;
 if(scenario==30)p.dma_users=13;
 if(scenario==31)irq.owned=0;
 if(scenario==32)p.boot_irq_owned=0;
 if(scenario==33)mapped.bar=0xd2000000;
 if(scenario==34)channels.buffers[5].closing=1;
 if(scenario==35)channels.buffers[5].address=channels.buffers[0].address;
 int rc=qca_mapped_irq_poll(&mapped);
 if(!scenario){assert(!rc&&operation_count==9&&irq_writes==2&&core[2]==0x7fc00&&!(core[0]&0x800));}
 else assert(rc==-1);
 if(scenario>=10)assert(!irq_writes);
 assert(!frees&&!unmaps&&allocations==14);
 fail_at=header_kind=0;command=0x502;p.wake_owned=p.link_owned=p.boot_irq_owned=irq.owned=1;p.dma_users=14;
 channels.buffers[9].valid=1;channels.buffers[5].closing=0;channels.buffers[5].address=0x105000;mapped.bar=0xd1000000;
 assert(!qca_mapped_irq_quiesce(&mapped)&&!core[2]&&!core[3]&&irq.owned);
 for(unsigned i=0;i<14;i++){assert(!qca_channels_close_step(&channels));}
 assert(qca_channels_close_step(&channels)==1);
 assert(!qca_boot_irq_close(&irq)&&!irq.owned&&!p.boot_irq_owned&&command==0x102);
 assert(core[0]==0x12300e88&&frees==14&&unmaps==14&&!p.dma_users);
 printf("Mapped IRQ scope scenario %u PASS: fresh identity/D0/BM-off/INTx/MSI and retained pages; MOCK ONLY\n",scenario);return 0;
}
#ifndef MAPPED_IRQ_NO_MAIN
int main(int argc,char**argv){return mapped_irq_fixture_main(argc,argv);}
#endif
