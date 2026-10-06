#include "lifecycle.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static unsigned checks;
#define CHECK(x) do { assert(x); checks++; } while(0)
static QcaRadioOwners live(void){QcaRadioOwners o={0};o.epoch=42;o.mappings=o.dma_users=14;
 o.pci=o.wake=o.link=o.irq=o.pin=o.bus=o.bus_master=o.init_ready=1;return o;}
static QcaRadioLifecycle start(void){QcaRadioLifecycle s={0};QcaRadioOwners o=live();
 CHECK(qca_radio_begin(&s,&o,100));CHECK(qca_radio_accepts_work(&s));
 CHECK(!qca_radio_can_release(&s));CHECK(!qca_radio_can_unload(&s));return s;}
static void vary(QcaRadioOwners*o,unsigned field,unsigned v){
 switch(field){case 0:o->pci=v;break;case 1:o->wake=v;break;case 2:o->link=v;break;
 case 3:o->irq=v;break;case 4:o->pin=v;break;case 5:o->bus=v;break;
 case 6:o->bus_master=v;break;case 7:o->init_ready=v;break;case 8:o->stop_verified=v;break;}
}
int main(void){
 /* Missing or malformed boot ownership must never establish persistent mode. */
 for(unsigned f=0;f<9;f++)for(unsigned v=0;v<4;v++){
  QcaRadioLifecycle s={0};QcaRadioOwners o=live();vary(&o,f,v);
  unsigned wanted=f==8?0:1;
  CHECK(qca_radio_begin(&s,&o,100)==(v==wanted));
  CHECK(qca_radio_accepts_work(&s)==(v==wanted));CHECK(!qca_radio_can_unload(&s));
 }
 for(unsigned n=0;n<17;n++){
  QcaRadioLifecycle s={0};QcaRadioOwners o=live();o.mappings=n;
  CHECK(qca_radio_begin(&s,&o,100)==(n==14));
  s=(QcaRadioLifecycle){0};o=live();o.dma_users=n;CHECK(qca_radio_begin(&s,&o,100)==(n==14));
 }
 QcaRadioLifecycle s=start();QcaRadioOwners o=live();
 for(unsigned i=0;i<1000;i++)CHECK(qca_radio_observe(&s,&o,100+i));
 CHECK(qca_radio_accepts_work(&s));CHECK(!qca_radio_can_unload(&s));
 QcaRadioLifecycle before=s;o.epoch++;
 CHECK(!qca_radio_observe(&s,&o,1100));CHECK(s.phase==QCA_RADIO_RETAINED);
 CHECK(!qca_radio_accepts_work(&s));CHECK(!qca_radio_can_release(&s));CHECK(!qca_radio_can_unload(&s));
 CHECK(!memcmp(&s.owners,&before.owners,sizeof(s.owners)));s=before;o=live();
 CHECK(!qca_radio_quiesce(&s,1100,0));CHECK(!qca_radio_quiesce(&s,UINT64_MAX,1));
 CHECK(qca_radio_quiesce(&s,1100,100));CHECK(!qca_radio_accepts_work(&s));CHECK(!qca_radio_can_release(&s));
 CHECK(qca_radio_observe(&s,&o,1101));o.bus_master=0;
 CHECK(qca_radio_observe(&s,&o,1102));CHECK(!qca_radio_can_release(&s));
 o.stop_verified=1;CHECK(qca_radio_observe(&s,&o,1103));CHECK(qca_radio_can_release(&s));
 CHECK(!qca_radio_can_unload(&s));
 /* Stop verification is not a release; every mapping remains counted. */
 o.bus=0;CHECK(qca_radio_observe(&s,&o,1104));
 for(unsigned n=14;n>0;n--){o.mappings=o.dma_users=n-1;CHECK(qca_radio_observe(&s,&o,1105+14-n));CHECK(!qca_radio_can_unload(&s));}
 o.pin=0;CHECK(qca_radio_observe(&s,&o,1120));CHECK(!qca_radio_can_unload(&s));
 o.irq=o.link=o.wake=0;CHECK(qca_radio_observe(&s,&o,1121));CHECK(!qca_radio_can_unload(&s));
 o.pci=0;CHECK(qca_radio_observe(&s,&o,1122));CHECK(qca_radio_can_unload(&s));
 CHECK(!qca_radio_accepts_work(&s));CHECK(!qca_radio_can_release(&s));
 before=s;o=live();CHECK(!qca_radio_observe(&s,&o,1123));CHECK(!memcmp(&s,&before,sizeof(s)));
 /* Enumerate timeout boundaries; no late claimed stop/release can rescue it. */
 for(unsigned t=0;t<4;t++){
  s=start();o=live();CHECK(qca_radio_quiesce(&s,100,20));
  if(t&1){o.bus_master=0;o.stop_verified=1;CHECK(qca_radio_observe(&s,&o,101));}
  uint64_t at=(t&2)?121:120;
  CHECK(!qca_radio_observe(&s,&o,at));CHECK(s.error==QCA_RADIO_TIMEOUT);
  CHECK(!qca_radio_can_unload(&s));CHECK(!qca_radio_can_release(&s));
 }
 /* Premature releases, lost stop proof, re-acquisition, rollback of clock. */
 for(unsigned f=0;f<6;f++){
  s=start();o=live();CHECK(qca_radio_quiesce(&s,100,100));vary(&o,f,0);
  CHECK(!qca_radio_observe(&s,&o,101));CHECK(s.phase==QCA_RADIO_RETAINED);CHECK(!qca_radio_can_unload(&s));
 }
 for(unsigned f=0;f<9;f++){
  s=start();o=live();vary(&o,f,f==8?1:0);
  CHECK(!qca_radio_observe(&s,&o,101));CHECK(s.phase==QCA_RADIO_RETAINED);CHECK(!qca_radio_accepts_work(&s));
 }
 for(unsigned f=0;f<6;f++){
  s=start();o=live();CHECK(qca_radio_quiesce(&s,100,100));o.bus_master=0;o.stop_verified=1;
  CHECK(qca_radio_observe(&s,&o,101));vary(&o,f,0);
  if(f==5)CHECK(qca_radio_observe(&s,&o,102));else CHECK(!qca_radio_observe(&s,&o,102));
  CHECK(!qca_radio_can_unload(&s));
 }
 for(unsigned f=0;f<3;f++){
  s=start();o=live();CHECK(qca_radio_quiesce(&s,100,100));o.bus_master=0;o.stop_verified=1;
  CHECK(qca_radio_observe(&s,&o,101));
  if(f==0)o.stop_verified=0;if(f==1)o.bus_master=1;
  if(f==2){o.bus=0;o.mappings=o.dma_users=0;CHECK(qca_radio_observe(&s,&o,102));o.mappings=o.dma_users=1;}
  CHECK(!qca_radio_observe(&s,&o,103));CHECK(s.phase==QCA_RADIO_RETAINED);CHECK(!qca_radio_can_unload(&s));
 }
 for(unsigned phase=0;phase<3;phase++){
  s=start();o=live();if(phase){CHECK(qca_radio_quiesce(&s,100,100));}
  if(phase==2){o.bus_master=0;o.stop_verified=1;CHECK(qca_radio_observe(&s,&o,101));}
  CHECK(!qca_radio_observe(&s,&o,99));CHECK(s.error==QCA_RADIO_CLOCK);CHECK(!qca_radio_can_unload(&s));
 }
 /* Bad/stale observations must revoke previous valid work/release proofs. */
 for(unsigned phase=0;phase<3;phase++)for(unsigned bad=0;bad<14;bad++){
  s=start();o=live();
  if(phase)CHECK(qca_radio_quiesce(&s,100,100));
  if(phase==2){o.bus_master=0;o.stop_verified=1;CHECK(qca_radio_observe(&s,&o,101));CHECK(qca_radio_can_release(&s));}
  QcaRadioOwners retained=s.owners;
  if(bad<9)vary(&o,bad,2);
  if(bad==9)o.epoch++;
  if(bad==10)o.epoch=0;
  if(bad==11)o.mappings=15;
  if(bad==12)o.dma_users=15;
  CHECK(!qca_radio_observe(&s,bad==13?0:&o,102));
  CHECK(s.phase==QCA_RADIO_RETAINED);CHECK(s.error==QCA_RADIO_OWNERS);
  CHECK(!qca_radio_accepts_work(&s));CHECK(!qca_radio_can_release(&s));CHECK(!qca_radio_can_unload(&s));
  CHECK(!memcmp(&s.owners,&retained,sizeof(retained)));
 }
 CHECK(!qca_radio_begin(0,&o,0));CHECK(!qca_radio_observe(0,&o,0));
 CHECK(!qca_radio_can_unload(0));CHECK(!qca_radio_accepts_work(0));CHECK(!qca_radio_can_release(0));
 printf("persistent lifecycle: %u checks PASS\n",checks);return 0;
}
