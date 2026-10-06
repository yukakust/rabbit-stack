#include "resources.h"
#include "init_wire.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
void reference(uint32_t out[44],const uint32_t map[32]);
static unsigned checks;
int main(void){
 QcaWmiServiceInfo i={0};i.service_count=32;i.chains=1;
 QcaTlvResources out={0};uint32_t expected[44],seed=9377;
 for(unsigned trial=0;trial<4096;trial++){
  for(unsigned n=0;n<32;n++){seed=1664525*seed+1013904223;i.service_words[n]=seed;}
  for(unsigned reorder=0;reorder<2;reorder++){
   i.service_words[16]=(i.service_words[16]&~2u)|(reorder<<1);
   reference(expected,i.service_words);
   assert(qca_tlv_resources(&i,&out)&&!memcmp(out.words,expected,sizeof(expected)));
   assert(out.memory.vdevs==4&&out.memory.peers==33&&!out.memory.active_peers&&out.memory.budget_bytes==16777216);checks++;
  }
 }
 /* A conventional service65 bit is in word2/bit1: must not enable reorder. */
 memset(i.service_words,0,sizeof(i.service_words));i.service_words[2]=2;
 assert(qca_tlv_resources(&i,&out)&&!out.words[2]&&!out.words[3]);checks++;
 /* High unused bits in correct word also confer no capability. */
 i.service_words[16]=0xfffffff0;assert(qca_tlv_resources(&i,&out)&&!out.words[2]);checks++;
 for(unsigned count=0;count<=128;count++)if(count!=32){
  i.service_count=count;QcaTlvResources old=out;
  assert(!qca_tlv_resources(&i,&out)&&!memcmp(&old,&out,sizeof(old)));checks++;
 }
 i.service_count=32;
 for(unsigned chains=0;chains<=5;chains++){
  i.chains=chains;QcaTlvResources old=out;int ok=qca_tlv_resources(&i,&out);
  assert(ok==(chains>0&&chains<=4));if(!ok)assert(!memcmp(&old,&out,sizeof(old)));checks++;
 }
 i.chains=1;QcaWmiServiceInfo old=i;
 assert(!qca_tlv_resources(&i,(QcaTlvResources*)&i)&&!memcmp(&old,&i,sizeof(i)));checks++;
 assert(!qca_tlv_resources(0,&out)&&!qca_tlv_resources(&i,0));checks++;
 i.memory_count=0;assert(qca_tlv_resources(&i,&out));
 for(unsigned count=0;count<=16;count++){
  QcaWmiMemoryPlan plan;QcaWmiHostChunk chunks[16];uint8_t frame[540];
  i.memory_count=count;
  for(unsigned n=0;n<count;n++)i.memory[n]=(QcaWmiMemoryRequest){n,12,1u<<(n%3),0};
  assert(!qca_wmi_memory_plan(&i,&out.memory,&plan)&&plan.count==count);
  for(unsigned n=0;n<count;n++)chunks[n]=(QcaWmiHostChunk){plan.item[n].id,plan.item[n].bytes,0x100000+4096*n};
  assert(qca_wmi_init_wire(frame,sizeof(frame),out.words,&i,&out.memory,chunks,count)==220+20*count);checks++;
 }
 printf("QCA9377 PCI TLV resource vector / pinned Linux assignments checks=%u PASS\n",checks);
}
