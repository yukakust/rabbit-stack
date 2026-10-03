#include "ce_uefi.h"
#include "ce_hw.h"
#include <assert.h>
#include <stdio.h>
static void*methods[20];static uint32_t registers[32];static unsigned writes,ambiguous;
static Status EFIAPI read_memory(void*p,uint32_t width,uint8_t bar,uint64_t address,uint64_t count,void*out){
 assert(p==methods&&width==2&&!bar&&count==1&&address>=0x34400&&address<=0x34450);
 *(uint32_t*)out=registers[(address-0x34400)/4];return 0;
}
static Status EFIAPI write_memory(void*p,uint32_t width,uint8_t bar,uint64_t address,uint64_t count,void*in){
 assert(p==methods&&width==2&&!bar&&count==1&&address>=0x34400&&address<=0x34450);writes++;
 unsigned off=(unsigned)(address-0x34400);uint32_t value=*(uint32_t*)in;
 if(off==0x18)registers[off/4]=value?9:0;
 else if(off==0x30||off==0x38)registers[off/4]&=~value;
 else registers[off/4]=value;
 return ambiguous?1:0;
}
int main(void){
 methods[2]=(void*)read_memory;methods[3]=(void*)write_memory;
 QcaUefiPort p={.pci=methods,.bar_extent=0x200000,.claimed=1,.validated=1,.memory_ready=1,.wake_owned=1};
 QcaDmaBuffer src={.port=&p,.address=0x100000,.bytes=4096,.valid=1,.allocated=1,.mapped=1};
 QcaDmaBuffer dst={.port=&p,.address=0x200000,.bytes=4096,.valid=1,.allocated=1,.mapped=1};
 QcaCeAccess a={0};QcaCeHw c={0};uint32_t v=0;
 assert(!qca_ce_access_init(&a,&p,1));assert(!qca_ce_access_buffer(&a,&src));assert(!qca_ce_access_buffer(&a,&dst));assert(qca_ce_access_buffer(&a,&src)==-1);
 assert(qca_ce_access_read(&a,0x34800,&v)==-1);assert(qca_ce_access_read(&a,0x34401,&v)==-1);assert(qca_ce_access_read(&a,0x34414,&v)==-1);
 p.bar_extent=0x34450;assert(qca_ce_access_read(&a,0x34450,&v)==-1);p.bar_extent=0x200000;
 p.pci=0;assert(qca_ce_access_read(&a,0x34400,&v)==-1);p.pci=methods;
 p.wake_owned=0;assert(qca_ce_access_read(&a,0x34400,&v)==-1);p.wake_owned=1;
 assert(qca_ce_access_write(&a,0x34444,0)==-1);assert(qca_ce_access_write(&a,0x34418,2)==-1);
 assert(qca_ce_access_write(&a,0x34418,0)==-1);assert(qca_ce_access_write(&a,0x34400,src.address)==-1);
 assert(!qca_ce_hw_init(&c,0,qca_ce_access_read,qca_ce_access_write,&a));assert(!qca_ce_hw_stop_begin(&c,0));assert(qca_ce_hw_stop_poll(&c,1)==1);
 unsigned n=writes;
 assert(qca_ce_access_write(&a,0x34400,0x300000)==-1);assert(qca_ce_access_write(&a,0x34400,src.address+1)==-1);assert(writes==n);
 assert(!qca_ce_access_write(&a,0x34400,src.address+4096-8));assert(src.exposed);assert(qca_ce_access_write(&a,0x34404,2)==-1);
 assert(!qca_ce_access_write(&a,0x34400,0));
 assert(qca_ce_access_write(&a,0x3444c,8u<<16)==-1);
 assert(!qca_ce_hw_configure(&c,src.address,8,dst.address,8,256));assert(src.exposed&&dst.exposed);
 src.closing=1;assert(qca_ce_hw_run(&c)==-1&&c.owned);src.closing=0;
 assert(!qca_ce_hw_stop_begin(&c,2));assert(qca_ce_hw_stop_poll(&c,3)==1);
 assert(!qca_ce_hw_configure(&c,src.address,8,dst.address,8,256));assert(!qca_ce_hw_run(&c));assert(!qca_ce_hw_publish(&c,0,7));
 src.closing=1;assert(qca_ce_hw_publish(&c,0,0)==-1&&c.owned);
 /* Teardown remains possible with closing buffers; no new exposure. */
 dst.closing=1;assert(!qca_ce_hw_stop_begin(&c,4));assert(qca_ce_hw_stop_poll(&c,5)==1);
 assert(!registers[0]&&!registers[1]&&!registers[2]&&!registers[3]);
 src.closing=dst.closing=0;src.exposed=0;ambiguous=1;
 assert(qca_ce_access_write(&a,0x34400,src.address)==-1&&src.exposed);ambiguous=0;
 src.valid=0;assert(qca_ce_access_write(&a,0x34404,8)==-1);src.valid=1;
 assert(qca_ce_access_write(&a,0x3442c,1)==-1);assert(qca_ce_access_write(&a,0x34410,0x80000)==-1);
 assert(!qca_ce_hw_stop_begin(&c,6));assert(qca_ce_hw_stop_poll(&c,7)==1);
 /* Source-only queue also works: disabled destination index zero is allowed. */
 assert(!qca_ce_hw_configure(&c,src.address,8,0,0,256));assert(!qca_ce_hw_run(&c));
 assert(!qca_ce_hw_stop_begin(&c,8));assert(qca_ce_hw_stop_poll(&c,9)==1);
 puts("CE UEFI allowlist/mapped-region/closing/ambiguous-write/source-only gates PASS; MOCK ONLY");return 0;
}
