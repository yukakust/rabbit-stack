#define main port_previous_main
#include "port_test.c"
#undef main
#include "bringup.h"
#include <stdlib.h>
uint8_t qca_diagnostic[160];void*qca_controller;
static uint32_t result(unsigned offset){return (uint32_t)qca_diagnostic[offset]|((uint32_t)qca_diagnostic[offset+1]<<8)|((uint32_t)qca_diagnostic[offset+2]<<16)|((uint32_t)qca_diagnostic[offset+3]<<24);}
int main(int argc,char**argv){
 assert(argc==2);unsigned scenario=(unsigned)atoi(argv[1]);assert(scenario<=14);
 assert(!port_previous_main());baseline();mode=scenario;
 qca_controller=scenario==14?0:pci;qca_image=&port_system;qca_diagnostic[4]=15;
 qca_start(&port_system,100);qca_poll(scenario==12?99:scenario==13?1100:101);
 if(scenario==0)assert(result(128)==2&&result(132)==0x100&&!result(136)&&result(140)==1);
 if(scenario==11)assert(result(128)==3&&result(132)==0x200&&result(136)==QCA_WAKE_CHIP);
 if(scenario==12)assert(result(128)==3&&result(136)==QCA_WAKE_CLOCK);
 if(scenario==13)assert(result(128)==3&&result(136)==QCA_WAKE_TIMEOUT);
 if(scenario==14)assert(result(128)==4&&!opens&&!mem_reads&&!mem_writes);
 qca_poll(102);qca_poll(103);unsigned writes=mem_writes;
 qca_poll(104);if(scenario!=10)assert(mem_writes==writes);
 if(scenario==10){qca_poll(1100);assert(result(136)==QCA_WAKE_TIMEOUT);}
 mode=0;assert(!qca_stop()&&result(140)==1&&opens==closes&&!attributes);
 writes=mem_writes;qca_start(&port_system,2000);qca_poll(2001);assert(mem_writes==writes);
 printf("One-shot bringup scenario %u: bounded operation, cleanup, no reattach repetition PASS; MOCK ONLY\n",scenario);
 return 0;
}
