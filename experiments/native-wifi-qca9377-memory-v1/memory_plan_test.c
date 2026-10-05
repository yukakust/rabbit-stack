#include "memory_plan.h"
#include "upstream-memory-oracle.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static unsigned cases;
static void reject(QcaWmiServiceInfo*i,QcaWmiResources*r){
 QcaWmiMemoryPlan out,before;memset(&out,0xa5,sizeof(out));before=out;
 assert(qca_wmi_memory_plan(i,r,&out)<0);assert(!memcmp(&out,&before,sizeof(out)));cases++;
}
int main(void){
 QcaWmiServiceInfo i={0};QcaWmiResources r={1,2,0,16*1024*1024};QcaWmiMemoryPlan p;
 assert(!qca_wmi_memory_plan(&i,&r,&p)&&!p.count&&!p.total_bytes);cases++;
 i.memory_count=1;
 for(unsigned v=1;v<=4;v++)for(unsigned peers=1;peers<=32;peers++)for(unsigned active=0;active<=peers;active++)for(unsigned flags=0;flags<8;flags++)for(unsigned size=1;size<=257;size++){
  r.vdevs=v;r.peers=peers;r.active_peers=active;
  i.memory[0]=(QcaWmiMemoryRequest){17,size,flags,7};
  assert(!qca_wmi_memory_plan(&i,&r,&p));
  struct oracle_resources resources={v,peers,active};
  uint32_t units=oracle_units(&resources,flags,7),bytes=oracle_bytes(units,size);
  assert(p.count==1&&p.total_bytes==bytes&&p.item[0].id==17&&p.item[0].units==units&&p.item[0].bytes==bytes);cases++;
 }
 r=(QcaWmiResources){1,2,0,4096};i=(QcaWmiServiceInfo){0};i.memory_count=16;
 for(unsigned j=0;j<16;j++)i.memory[j]=(QcaWmiMemoryRequest){j+1,7,0,4};
 assert(!qca_wmi_memory_plan(&i,&r,&p)&&p.count==16&&p.total_bytes==512);cases++;
 r.budget_bytes=512;assert(!qca_wmi_memory_plan(&i,&r,&p));cases++;
 r.budget_bytes=511;reject(&i,&r);r.budget_bytes=4096;
 i.memory[15].id=1;reject(&i,&r);i.memory[15].id=16;
 for(unsigned j=0;j<16;j++){
  QcaWmiMemoryRequest q=i.memory[j];
  i.memory[j].unit_size=0;reject(&i,&r);i.memory[j]=q;
  i.memory[j].unit_size=0xffffffffu;reject(&i,&r);i.memory[j]=q;
  i.memory[j].unit_size=0xfffffffcu;i.memory[j].units=0xffffffffu;reject(&i,&r);i.memory[j]=q;
  i.memory[j].unit_flags=8;reject(&i,&r);i.memory[j]=q;
  i.memory[j].units=0;reject(&i,&r);i.memory[j]=q;
 }
 i.memory_count=17;reject(&i,&r);i.memory_count=16;
 QcaWmiResources good=r;
 r.vdevs=0;reject(&i,&r);r=good;r.vdevs=17;reject(&i,&r);r=good;
 r.peers=0;reject(&i,&r);r=good;r.peers=2049;reject(&i,&r);r=good;
 r.active_peers=3;reject(&i,&r);r=good;r.budget_bytes=0;reject(&i,&r);r=good;
 r.budget_bytes=16*1024*1024+1;reject(&i,&r);r=good;
 assert(qca_wmi_memory_plan(0,&r,&p)<0&&qca_wmi_memory_plan(&i,0,&p)<0&&qca_wmi_memory_plan(&i,&r,0)<0);cases++;
 /* Largest supported resource counts still require actual byte-budget checks. */
 i.memory_count=1;i.memory[0]=(QcaWmiMemoryRequest){0,4,7,0};r=(QcaWmiResources){16,2048,2048,8196};
 assert(!qca_wmi_memory_plan(&i,&r,&p)&&p.item[0].units==2049&&p.total_bytes==8196);cases++;
 r.budget_bytes=8195;reject(&i,&r);
 printf("WMI MEMORY PLAN %u pinned-source differential/overflow/budget/duplicate cases PASS; NO ALLOCATION OR DEVICE ACCESS\n",cases);
 return 0;
}
