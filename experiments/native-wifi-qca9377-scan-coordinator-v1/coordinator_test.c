#include "coordinator.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static QcaInitAdapter adapter;static QcaConfigSetup setup;static QcaBoardQuery board;static QcaBootNative boot;static QcaOperating operating;static QcaWmiStartup startup;static QcaPersistentNative radio;static QcaPersistentTx publisher;static QcaScanCoordinator scan;
static _Alignas(8) uint8_t memory[14][2048];static unsigned hw[8],posts,credit_pending,freeze_tx,credit_suppressed,checks,scenario;static uint32_t commands[8];static unsigned backend_stopped,release_count;
#define CHECK(x) do{assert(x);checks++;}while(0)
static uint32_t word(const uint8_t*p){return p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static void put(uint8_t*p,uint32_t v){for(unsigned j=0;j<4;j++)p[j]=(uint8_t)(v>>(8*j));}
static int stop_ring(void*context){(void)context;return backend_stopped?0:-1;}
static int publish(void*context,uint32_t value){QcaChannelRoute*r=context;if(r->pipe==3){CHECK(posts<8);commands[posts++]=word(memory[7]+8);credit_pending++;if(!freeze_tx)hw[3]=value;}return 0;}
int qca_ce_hw_index(QcaCeHw*engine,int receive,unsigned*out){(void)receive;unsigned i=(unsigned)(engine-adapter.bus.engines);if(i>=8)return -1;*out=hw[i];return 0;}
int qca_channels_retained(QcaChannels*c){return c!=&adapter.channels||c->allocated!=14;}
int qca_operating_poll(QcaOperating*o,uint64_t now){(void)now;return o==&operating&&o->phase==2?1:-1;}
int qca_persistent_poll(QcaPersistentNative*r,uint64_t now){if(r!=&radio||!qca_radio_accepts_work(&r->life))return -1;return qca_rx_poll(&r->rx,&r->life,now)==1?1:-1;}
static void emit(unsigned pipe,const uint8_t*p,unsigned n,int credit){QcaCeRing*r=&adapter.channels.rings[pipe];CHECK(radio.rx.posted[pipe-1]);uint8_t*dst=memory[2*pipe+1];memset(dst,0,2048);dst[0]=pipe==1?0:1;unsigned bytes=n;
 if(credit){dst[1]=2;dst[4]=8;bytes+=8;}dst[2]=bytes;dst[3]=bytes>>8;memcpy(dst+8,p,n);
 if(credit){dst[8+n]=1;dst[9+n]=4;dst[12+n]=1;dst[13+n]=(uint8_t)credit;}
 unsigned total=bytes+8;volatile uint8_t*d=r->descriptors+8*r->read;d[4]=total;d[5]=total>>8;hw[pipe]=(r->read+1)&7;
}
static void fw_credit(void){if(credit_pending&&!credit_suppressed&&radio.rx.posted[0]&&hw[1]==adapter.channels.rings[1].read){emit(1,(const uint8_t*)"",0,1);credit_pending--;}}
static void scan_event(unsigned type,unsigned reason,unsigned frequency,unsigned request){uint8_t p[32]={0};put(p,0x3001);put(p+4,24|(36u<<16));put(p+8,type);put(p+12,reason);put(p+16,frequency);put(p+20,0xa000|request);put(p+24,0xa007);emit(2,p,32,0);}
static void mgmt(unsigned channel,int malformed){uint8_t p[128]={0};put(p,0x7001);put(p+4,40|(44u<<16));put(p+8,channel);put(p+24,45);put(p+48,48|(17u<<16));uint8_t*f=p+52;f[0]=0x80;for(unsigned j=0;j<6;j++){f[4+j]=255;f[10+j]=f[16+j]=(uint8_t)(j+2);}f[32]=100;f[34]=0x11;f[36]=0;f[37]=4;memcpy(f+38,"test",4);f[42]=3;f[43]=1;f[44]=(uint8_t)channel;if(malformed)p[4]=39;emit(2,p,100,0);}
static void init(void){memset(&adapter,0,sizeof(adapter));memset(&setup,0,sizeof(setup));memset(&board,0,sizeof(board));memset(&boot,0,sizeof(boot));memset(&operating,0,sizeof(operating));memset(&startup,0,sizeof(startup));memset(&radio,0,sizeof(radio));memset(&publisher,0,sizeof(publisher));memset(&scan,0,sizeof(scan));memset(memory,0,sizeof(memory));memset(hw,0,sizeof(hw));posts=credit_pending=freeze_tx=credit_suppressed=backend_stopped=release_count=0;
 setup.read.full.adapter=&adapter;board.setup=&setup;boot.board=&board;operating.boot=&boot;operating.phase=2;
 QcaHtcReady ready={.credits=2,.credit_size=1792,.endpoints=4};QcaHtcConnection wmi={.service=256,.endpoint=1,.max_bytes=1784};CHECK(qca_htc_credit_begin(&operating.control.credit,&ready,&wmi));
 operating.control.session.phase=QCA_HTC_RUNNING;operating.control.session.ready=ready;operating.control.session.wmi=wmi;operating.control.session.htt=(QcaHtcConnection){.service=768,.endpoint=2,.max_bytes=1784};operating.service_valid=1;operating.service.regdomain=108;operating.service.low2=2312;operating.service.high2=2732;operating.service.low5=4920;operating.service.high5=6100;
 startup.operating=&operating;startup.phase=2;startup.transaction.phase=QCA_INIT_RUNNING;startup.transaction.ready_seen=startup.transaction.tx_complete=1;
 uint8_t payload[60]={0};put(payload,2);put(payload+4,52|(35u<<16));put(payload+8,0x1000000);put(payload+12,574);put(payload+16,0x5f414351);put(payload+20,0x4c4d);payload[32]=2;payload[33]=3;payload[34]=4;payload[35]=5;payload[36]=6;payload[37]=7;CHECK(qca_wmi_ready_info(payload,sizeof(payload),&startup.transaction.ready));
 radio.startup=&startup;QcaRadioOwners owner={.epoch=9,.mappings=14,.dma_users=14,.pci=1,.wake=1,.link=1,.irq=1,.pin=1,.bus=1,.bus_master=1,.init_ready=1};CHECK(qca_radio_begin(&radio.life,&owner,0));radio.epoch=9;
 adapter.channels.bus=&adapter.bus;adapter.channels.allocated=14;
 for(unsigned j=0;j<14;j++){adapter.channels.buffers[j].host=memory[j];adapter.channels.buffers[j].address=0x100000+4096*j;}
 for(unsigned j=0;j<7;j++){adapter.channels.routes[j]=(QcaChannelRoute){.bus=&adapter.bus,.pipe=j,.receive=j==1||j==2};CHECK(!qca_ce_init(&adapter.channels.rings[j],memory[2*j],0x100000+8192*j,8,j==1||j==2,publish,stop_ring,&adapter.channels.routes[j]));}
 CHECK(qca_rx_begin(&radio.rx,&startup,&radio.life,0));CHECK(qca_tx_begin(&publisher,&radio,0));
 QcaReviewedChannelPolicy policy={0};QcaChannelHardware hardware={0};policy.version=1;policy.hardware_regdomain=policy.regdomain=policy.regdomain2=policy.regdomain5=hardware.regdomain=108;policy.ctl2=policy.ctl5=255;policy.alpha2[0]='G';policy.alpha2[1]='E';policy.count=2;
 for(unsigned j=0;j<32;j++){policy.target[j]=hardware.target[j]=j+1;policy.reviewed_digest[j]=j+2;policy.ruleset_digest[j]=j+3;policy.location_digest[j]=j+4;}
 hardware.low2=2312;hardware.high2=2732;hardware.low5=4920;hardware.high5=6100;
 for(unsigned j=0;j<2;j++)policy.channels[j]=(QcaPolicyChannel){.frequency=2412+25*j,.centre1=2412+25*j,.width=20,.passive=1,.mode=1,.max_power_dbm=20,.max_reg_power_dbm=20};
 CHECK(qca_scan_coordinator_begin(&scan,&publisher,&policy,&hardware,7,8,(const uint8_t*)"test",4,0,20,40,20,20));
}
static void close_model(uint64_t now){CHECK(!qca_tx_clear(&publisher));CHECK(!qca_rx_clear(&radio.rx,&radio.life));CHECK(!qca_radio_can_unload(&radio.life));
 CHECK(qca_radio_quiesce(&radio.life,now,1000));QcaRadioOwners o=radio.life.owners;o.bus_master=0;o.stop_verified=1;CHECK(qca_radio_observe(&radio.life,&o,now+1));CHECK(qca_radio_can_release(&radio.life));backend_stopped=1;
 for(unsigned j=0;j<7;j++)CHECK(!qca_ce_close(&adapter.channels.rings[j]));for(unsigned j=0;j<14;j++)release_count++;
 o.mappings=o.dma_users=0;o.pci=o.wake=o.link=o.irq=o.pin=o.bus=0;CHECK(qca_radio_observe(&radio.life,&o,now+2));CHECK(qca_radio_can_unload(&radio.life));unsigned retained_credit=operating.control.credit.outstanding;CHECK(qca_tx_clear(&publisher));CHECK(operating.control.credit.outstanding==retained_credit);CHECK(qca_rx_clear(&radio.rx,&radio.life));CHECK(release_count==14);
}
int main(void){setvbuf(stdout,NULL,_IONBF,0);unsigned terminal_cases=0;for(scenario=0;scenario<15;scenario++){
 init();if(scenario==7)credit_suppressed=1;unsigned emitted=0,unmatched=0,unknown_sent=0;uint64_t now=0;for(unsigned tick=1;tick<2000;tick++){
  now=tick*100;fw_credit();
  if(scenario==1&&scan.stage==3&&publisher.phase==QCA_TX_RESERVED)freeze_tx=1;
  if(scan.stop_begun&&radio.rx.posted[1]&&hw[2]==adapter.channels.rings[2].read){
   if(emitted==0){if(scenario==4){scan_event(1,0,0,9);emitted=10;}else if(scenario==13){uint8_t p[8]={0x56,0x34,0x12};emit(2,p,8,0);emitted=10;}else {scan_event(1,0,0,8);emitted=1;}}
   else if(emitted==10&&unmatched){scan_event(1,0,0,8);emitted=1;}
   else if(emitted==1&&scan.pending.started){scan_event(8,0,2412,8);emitted=2;}
   else if(emitted==2&&scan.live_frequency==2412){if(scenario==5)mgmt(6,0);else mgmt(1,scenario==6);emitted=3;}
   else if(emitted==3&&(scan.ssid_seen||unmatched||scenario==6)){
    if(scenario==2||scenario==3||scenario==12||scenario==11){CHECK(qca_scan_coordinator_stop(&scan,now));emitted=4;}else {scan_event(2,0,0,8);emitted=5;}
   }
   else if(emitted==4&&(publisher.phase==QCA_TX_WAIT_CREDIT||publisher.phase==QCA_TX_RESERVED)&&(scenario==3||(scenario==12&&publisher.phase==QCA_TX_RESERVED))){scan_event(2,0,0,8);emitted=5;}
   else if(emitted==4&&publisher.phase==QCA_TX_POSTED&&scan.stage==4&&scenario==2){scan_event(2,1,0,8);emitted=5;}
  }
  if(scenario==1&&emitted>=2){hw[3]=adapter.channels.rings[3].write;freeze_tx=0;}
  
  if(scenario==8&&scan.stop_begun)now=scan.last_us-1;
  if(scenario==9&&scan.stop_begun)radio.life.owners.epoch++;
  if(scenario==10&&scan.stop_begun&&!unknown_sent){uint8_t p[8]={0x56,0x34,0x12};if(radio.rx.posted[0]&&hw[1]==adapter.channels.rings[1].read){emit(1,p,8,0);unknown_sent=1;}}
  if(scenario==14&&scan.stage==2&&publisher.phase==QCA_TX_POSTED&&radio.rx.posted[1]&&hw[2]==adapter.channels.rings[2].read)scan_event(1,0,0,8);
  if(scenario==11&&scan.stage==4&&publisher.phase==QCA_TX_RESERVED){freeze_tx=1;credit_suppressed=1;}
  int result=qca_scan_coordinator_poll(&scan,now);CHECK(!scan.pending.ticket&&!scan.stop.stop.ticket);
  QcaScanObservation observation;if(scan.has_observation){CHECK(qca_scan_coordinator_take_observation(&scan,&observation));CHECK(observation.epoch==9&&observation.parsed.frequency_mhz==2412&&observation.raw.completion>scan.start_floor);}
  if(scan.dispatch.count&&!scan.has_observation){QcaRxEvent*e=&scan.dispatch.owned[scan.dispatch.head];if(e->event!=0x3001||word(e->payload+20)==0xa009){QcaRxEvent copy;CHECK(qca_scan_coordinator_take_unmatched(&scan,&copy));CHECK(copy.completion==e->completion);unmatched++;}}
  if(result!=0){if(result>0){CHECK(scan.phase==QCA_SC_ENDED&&scan.stop.stop.terminal_seen&&!scan.request);terminal_cases++;}else CHECK(scan.phase==QCA_SC_FAULT);break;}
 }
 printf("trace scenario=%u phase=%u err=%u stage=%u found=%u publisher=%u posts=%u\n",scenario,scan.phase,scan.error,scan.stage,scan.ssid_seen,publisher.phase,posts);CHECK(scan.phase==QCA_SC_ENDED||scan.phase==QCA_SC_FAULT);
 if(scenario!=9)close_model(now+1000);else{CHECK(!qca_tx_clear(&publisher)&&!qca_rx_clear(&radio.rx,&radio.life));CHECK(release_count==0&&adapter.channels.allocated==14);}
 if(scenario==0||scenario==1||scenario==2||scenario==3||scenario==4)CHECK(scan.ssid_seen);
 if(scenario==5||scenario==6||scenario==7||scenario==14)CHECK(!scan.ssid_seen);
 if(scenario==7||scenario==11||scenario==14)CHECK(scan.phase==QCA_SC_FAULT);
 if(scenario==10||scenario==13)CHECK(unmatched&&scan.ssid_seen);
 CHECK(commands[0]==0x3003&&commands[1]==0x4001);
 printf("scan_model scenario=%u phase=%u posted=%u found=%u unmatched=%u release=%u PASS\n",scenario,scan.phase,posts,scan.ssid_seen,unmatched,release_count);
 }
 CHECK(terminal_cases>=8);init();QcaScanCoordinator rejected={0};QcaChannelHardware wrong=scan.hardware;wrong.low2++;QcaPersistentTx tx_before=publisher;CHECK(!qca_scan_coordinator_begin(&rejected,&publisher,&scan.policy,&wrong,7,8,(const uint8_t*)"test",4,0,20,40,20,20));CHECK(!rejected.phase&&!memcmp(&tx_before,&publisher,sizeof(publisher)));
 CHECK(!qca_scan_coordinator_stop(&scan,0)&&scan.phase==QCA_SC_SETUP);CHECK(!qca_scan_coordinator_take_unmatched(&scan,(QcaRxEvent*)&publisher));scan.last_us=100;CHECK(!qca_scan_coordinator_stop(&scan,99)&&scan.phase==QCA_SC_FAULT);close_model(1000);
 printf("checks=%u actual-TX-RX-CE-bookkeeping/coordinator model PASS\n",checks);return 0;}
