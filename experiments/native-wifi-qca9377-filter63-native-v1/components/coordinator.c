#include "coordinator.h"
extern int qca_filter63_archive_take(QcaPersistentRx*,uint32_t);
#include "vdev_wire.h"
static int overlap(const void*a,unsigned n,const void*b,unsigned m){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;
 
 return x>UINTPTR_MAX-n||y>UINTPTR_MAX-m||(x<y?y-x<n:x-y<m);
 
 }
static int fail(QcaScanCoordinator*s,unsigned error){s->error=error;
 
 s->phase=QCA_SC_FAULT;
 
 return -1;
 
 }
static int bound(const QcaScanCoordinator*s){return s&&s->tx&&s->tx->radio&&s->tx->life==&s->tx->radio->life&&s->epoch==s->tx->epoch&&s->epoch==s->tx->life->owners.epoch&&s->pending.credit==s->tx->credit&&qca_radio_accepts_work(s->tx->life);
 
 }
int qca_scan_coordinator_begin(QcaScanCoordinator*s,QcaPersistentTx*tx,const QcaReviewedChannelPolicy*p,const QcaChannelHardware*h,unsigned scan,unsigned request,const uint8_t*ssid,unsigned bytes,uint64_t now,unsigned command_ms,unsigned scan_ms,unsigned credit_ms,unsigned stop_ms){
 if(!s||s->phase||!tx||tx->phase!=QCA_TX_IDLE||!tx->radio||!tx->radio->startup||!tx->credit||tx->life!=&tx->radio->life||tx->epoch!=tx->life->owners.epoch||!qca_radio_accepts_work(tx->life)||!p||!h||!scan||scan>4095||!request||request>4095||!ssid||!bytes||bytes>32||!command_ms||command_ms>10000||!scan_ms||scan_ms>60000||!credit_ms||credit_ms>60000||!stop_ms||stop_ms>60000||now<tx->last)return 0;
 
 
 QcaWmiStartup*w=tx->radio->startup;
 
 
 if(!w->operating||!w->operating->service_valid||h->regdomain!=w->operating->service.regdomain||h->low2!=w->operating->service.low2||h->high2!=w->operating->service.high2||h->low5!=w->operating->service.low5||h->high5!=w->operating->service.high5||w->phase!=2||w->error||w->transaction.phase!=QCA_INIT_RUNNING||!w->transaction.ready_seen||!w->transaction.tx_complete||w->tx_posted||!w->operating||tx->credit!=&w->operating->control.credit)return 0;
 
 
 const void*inputs[]={tx,p,h,ssid,w,tx->radio,tx->credit};
 
 unsigned sizes[]={sizeof(*tx),sizeof(*p),sizeof(*h),bytes,sizeof(*w),sizeof(*tx->radio),sizeof(*tx->credit)};
 
 
 for(unsigned j=0;j<7;j++)if(overlap(s,sizeof(*s),inputs[j],sizes[j]))return 0;
 
 
 uint8_t body[1808];
 
 if(!qca_scan_channels_wire(body,sizeof(body),p,h,tx->credit->max_bytes)||!qca_pdev_regdomain_wire(body,sizeof(body),p,h,tx->credit->max_bytes))return 0;
 
 
 unsigned mac=0;
 
 for(unsigned j=0;j<6;j++)mac|=w->transaction.ready.mac[j];
 
 if(!mac||(w->transaction.ready.mac[0]&1))return 0;
 
 
 uint8_t*z=(uint8_t*)s;
 
 for(unsigned j=0;j<sizeof(*s);j++)z[j]=0;
 
 
 s->tx=tx;
 
 s->policy=*p;
 
 s->hardware=*h;
 
 s->epoch=tx->epoch;
 
 s->last_us=now;
 
 s->command_ms=command_ms;
 
 s->scan_ms=scan_ms;
 
 s->credit_ms=credit_ms;
 
 s->stop_ms=stop_ms;
 
 s->ssid_bytes=(uint8_t)bytes;
 
 
 for(unsigned j=0;j<bytes;j++)s->ssid[j]=ssid[j];
 
 
 s->pending.credit=tx->credit;
 
 s->pending.phase=QCA_STA_READY;
 
 s->pending.count=p->count;
 
 s->pending.scan=scan;
 
 s->pending.request=request;
 
 
 for(unsigned j=0;j<6;j++)s->pending.mac[j]=w->transaction.ready.mac[j];
 
 for(unsigned j=0;j<p->count;j++)s->pending.frequencies[j]=(uint16_t)p->channels[j].frequency;
 
 
 if(!qca_station_dispatch_begin(&s->dispatch,&s->pending,0))return 0;
 
 s->phase=QCA_SC_SETUP;
 
 return 1;
 
 
}
static int submit(QcaScanCoordinator*s,uint64_t now){
 uint8_t body[1808];
 
 unsigned bytes=0;
 
 
 switch(s->stage){case 0:bytes=qca_scan_channels_wire(body,sizeof(body),&s->policy,&s->hardware,s->tx->credit->max_bytes);
 
 break;
 
 case 1:bytes=qca_pdev_regdomain_wire(body,sizeof(body),&s->policy,&s->hardware,s->tx->credit->max_bytes);
 
 break;
 
 case 2:bytes=qca_station_create_wire(body,sizeof(body),0,s->pending.mac);
 
 break;
 
 case 3:bytes=qca_wmi_passive_scan(body,sizeof(body),s->pending.scan,s->pending.request,s->pending.frequencies,s->pending.count);
 
 break;
 
 case 4:bytes=qca_scan_stop_wire(body,sizeof(body),s->pending.scan,s->pending.request);
 
 break;
 
 default:return fail(s,1);
 
 }
 if(!bytes||!qca_tx_submit(s->tx,body,bytes,now,(uint64_t)s->command_ms*1000,&s->request))return fail(s,2);
 
 
 s->frame_bytes=bytes+8;
 
 s->projected=0;
 
 return 0;
 
 
}
static int project(QcaScanCoordinator*s,uint64_t now){
 QcaPersistentTx*t=s->tx;
 
 if(!s->request)return 0;
 
 
 if(t->request!=s->request||t->bytes!=s->frame_bytes)return fail(s,3);
 
 
 if(!s->projected&&(t->phase==QCA_TX_POSTED||t->phase==QCA_TX_DMA_DONE)){
  s->projected=1;
 
 
  if(s->stage==2){s->pending.phase=QCA_STA_CREATE_POSTED;
 
 s->pending.frame_bytes=t->bytes;
 
 }
  if(s->stage==3){s->pending.phase=QCA_STA_SCAN_POSTED;
 
 s->pending.frame_bytes=t->bytes;
 
 s->start_floor=t->radio->rx.completed;
 
 
   if(!qca_owned_scan_stop_begin(&s->stop,&s->dispatch,now/1000,s->scan_ms,s->credit_ms,s->stop_ms))return fail(s,4);
 
 s->stop_begun=1;
 
 }
  if(s->stage==4){if(s->stop.stop.phase!=QCA_STOP_REQUESTED)return fail(s,5);
 
 s->stop.stop.phase=QCA_STOP_POSTED;
 
 s->stop.stop.frame_bytes=t->bytes;
 
 s->stop.stop.stop_deadline=now/1000+s->stop_ms;
 
 }
 }
 if(t->phase!=QCA_TX_DMA_DONE)return 0;
 
 
 if(!s->projected)return fail(s,6);
 
 
 if((s->stage==2||s->stage==3)&&!qca_station_scan_complete(&s->pending,t->bytes))return fail(s,7);
 
 
 if(s->stage==4&&!qca_owned_scan_stop_complete(&s->stop,t->bytes,now/1000))return fail(s,8);
 
 
 if(!qca_tx_retire(t,s->request))return fail(s,9);
 
 s->request=0;
 
 s->stage++;
 
 
 if(s->stage==4)s->phase=QCA_SC_SCANNING;
 
 return 0;
 
 
}
static int received(QcaScanCoordinator*s,uint64_t now){
 QcaPersistentRx*r=&s->tx->radio->rx;
 
 
 if(r->count){const QcaRxEvent*head=&r->events[r->head];
  if(!head->bytes||(head->pipe==1&&head->endpoint==r->htt.endpoint)){
   /* Validated credit-only/HTT belongs to unmatched owner; credits applied once
    * by RX. Never reinterpret it as WMI scan or take+drop an offer failure. */
   if(!qca_filter63_archive_take(r,head->completion))return fail(s,11);
   return 0;
  }
 }
 if(!s->has_orphan&&r->count&&s->dispatch.count<2){QcaRxEvent e;
 
 
  uint32_t id=r->events[r->head].completion;
 
 if(!qca_rx_take(r,id,&e,sizeof(e)))return fail(s,10);
 
 
  if(qca_station_dispatch_offer(&s->dispatch,&e)!=1){s->orphan=e;
 
 s->has_orphan=1;
 
 return fail(s,11);
 
 }
 }
 if(!s->dispatch.count)return 0;
 
 QcaRxEvent*e=&s->dispatch.owned[s->dispatch.head];
 
 
 if(e->pipe==2&&(e->event&0xffffffu)==0x7001){
  QcaWmiBeaconRx b;
 
 int result=qca_wmi_beacon_rx(e->payload,e->bytes,&b);
 
 
  if(result==QCA_BEACON_RX_MALFORMED)return fail(s,12);
 
 
  if(result!=QCA_BEACON_RX_ACCEPTED||!s->pending.started||s->pending.result!=QCA_SCAN_ACTIVE||b.frequency_mhz!=s->live_frequency||e->completion<=s->start_floor)return 0;
 
 
  unsigned selected=0;
 
 for(unsigned j=0;j<s->policy.count;j++)selected|=s->policy.channels[j].frequency==b.frequency_mhz;
 
 if(!selected)return 0;
 
 
  if(s->has_observation||!qca_beacon_ssid_matches(&b.bss,s->ssid,s->ssid_bytes))return 0;
 
 QcaRxEvent copy;
 
 if(!qca_station_dispatch_take(&s->dispatch,e->completion,&copy,sizeof(copy)))return fail(s,13);
 
 
  s->observation.raw=copy;
 
 s->observation.parsed=b;
 
 s->observation.epoch=s->epoch;
 
 s->has_observation=1;
 
 
  if(qca_beacon_ssid_matches(&b.bss,s->ssid,s->ssid_bytes))s->ssid_seen=1;
 
 return 0;
 
 
 }
 if(s->stop_begun){QcaWmiScanEvent stale;
 
 
  if(e->completion<=s->start_floor&&e->event==0x3001&&qca_wmi_scan_event(e->payload,e->bytes,s->pending.scan,s->pending.request,&stale))return fail(s,14);
 
 
 }
 int result=s->stop_begun?qca_owned_scan_stop_head(&s->stop,now/1000):qca_station_dispatch_head(&s->dispatch);
 
 
 if(result<0)return fail(s,15);
 
 
 if(result==QCA_DISPATCH_SCAN){unsigned type=s->pending.last_event.type;
 
 if(type==8)s->live_frequency=s->pending.last_event.frequency;
 
 else if(type==2||type==16||type==64||type==256)s->live_frequency=0;
 
 }
 return 0;
 
 
}
static int terminal(QcaScanCoordinator*s,uint64_t now){
 if(!s->stop_begun||s->stop.stop.phase!=QCA_STOP_ENDED)return 0;
 
 
 if(s->request&&s->stage==4&&(s->tx->phase==QCA_TX_WAIT_CREDIT||s->tx->phase==QCA_TX_RESERVED)){
  if(!qca_tx_cancel(s->tx,s->request,now)||!qca_tx_retire(s->tx,s->request))return fail(s,19);
 
 s->request=0;
 
 
 }
 if(!s->request){s->phase=QCA_SC_ENDED;
 
 return 1;
 
 }return 0;
 
 
}
int qca_scan_coordinator_poll(QcaScanCoordinator*s,uint64_t now){
 if(!s||!s->phase||s->phase==QCA_SC_FAULT)return -1;
 
 
 if(!bound(s)||now<s->last_us)return fail(s,16);
 
 s->last_us=now;
 
 
 /* Observe already-owned terminal events before advancing an unposted TX. */
 if(qca_persistent_poll(s->tx->radio,now)!=1)return fail(s,17);
 
 
 if(received(s,now)<0)return -1;
 
 
 if(s->stop_begun&&!qca_owned_scan_stop_tick(&s->stop,now/1000))return fail(s,18);
 
 
 int ended=terminal(s,now);
 
 if(ended)return ended;
 
 
 if(qca_tx_poll(s->tx,now)<0)return fail(s,17);
 
 
 if(project(s,now)<0)return -1;
 
 
 ended=terminal(s,now);
 
 if(ended)return ended;
 
 
 if(s->phase==QCA_SC_ENDED)return 1;
 
 
 if(!s->request&&s->tx->phase==QCA_TX_IDLE){
  if(s->stage<4)return submit(s,now);
 
 
  if(s->stage==4&&s->stop.stop.phase==QCA_STOP_REQUESTED){s->phase=QCA_SC_STOPPING;
 
 return submit(s,now);
 
 }
 }
 return 0;
 
 
}
int qca_scan_coordinator_stop(QcaScanCoordinator*s,uint64_t now){if(!s||!s->phase||s->phase==QCA_SC_FAULT)return 0;
 
 if(!bound(s)||now<s->last_us){(void)fail(s,16);
 
 return 0;
 
 }if(!s->stop_begun)return 0;
 
 s->last_us=now;
 
 return qca_owned_scan_stop_request(&s->stop,now/1000);
 
 }
static int output_safe(QcaScanCoordinator*s,void*out,unsigned bytes){
 if(!s||!out||overlap(s,sizeof(*s),out,bytes))return 0;
 
 
 if(s->tx&&(overlap(s->tx,sizeof(*s->tx),out,bytes)||(s->tx->radio&&overlap(s->tx->radio,sizeof(*s->tx->radio),out,bytes))||(s->tx->credit&&overlap(s->tx->credit,sizeof(*s->tx->credit),out,bytes))))return 0;
 
 
 return 1;
 
 
}
int qca_scan_coordinator_take_unmatched(QcaScanCoordinator*s,QcaRxEvent*out){
 if(!output_safe(s,out,sizeof(*out)))return 0;
 
 
 if(s->has_orphan){*out=s->orphan;
 
 s->has_orphan=0;
 
 return 1;
 
 }
 if(!s->dispatch.count)return 0;
 
 QcaRxEvent*e=&s->dispatch.owned[s->dispatch.head];
 
 return qca_station_dispatch_take(&s->dispatch,e->completion,out,sizeof(*out));
 
 
}
int qca_scan_coordinator_take_observation(QcaScanCoordinator*s,QcaScanObservation*out){if(!s||!s->has_observation||!output_safe(s,out,sizeof(*out)))return 0;
 
 *out=s->observation;
 
 s->has_observation=0;
 
 return 1;
 
 }
