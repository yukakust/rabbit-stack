#include "scan_native.h"
#include "scan_policy.h"
static int halt(QcaNativeScan*s,unsigned error){s->error=error;s->phase=error?QCA_NATIVE_SCAN_FAULT:QCA_NATIVE_SCAN_QUIESCING;
 if(!s->quiesce_requested){s->quiesce_requested=1;return 1;}return 0;}
int qca_native_scan_begin(QcaNativeScan*s,QcaPersistentNative*r,uint64_t now){
 if(!s||s->phase||!r||!r->startup||!r->startup->operating||!qca_radio_accepts_work(&r->life)||now>UINT64_MAX-25000000)return 0;
 s->radio=r;s->epoch=r->life.owners.epoch;s->started=s->last=now;
 if(!qca_tx_begin(&s->tx,r,now)){s->phase=QCA_NATIVE_SCAN_FAULT;s->error=1;return 0;}
 const QcaWmiServiceInfo*i=&r->startup->operating->service;
 QcaChannelHardware h={0};h.regdomain=i->regdomain;h.low2=i->low2;h.high2=i->high2;h.low5=i->low5;h.high5=i->high5;
 for(unsigned j=0;j<32;j++)h.target[j]=scan_policy.target[j];
 /* Bound signed proposal to observed physical52/53 capabilities; don't turn
  * capability limits or CTLs into an inferred frequency allowlist. */
 if(h.regdomain!=108||h.low2!=2312||h.high2!=2732||h.low5!=4920||h.high5!=6100){s->phase=QCA_NATIVE_SCAN_FAULT;s->error=2;return 0;}
 static const uint8_t ssid[16]={'S','I','L','K','_','5','6','E','3','5','E','_','P','l','u','s'};
 if(!qca_scan_coordinator_begin(&s->scan,&s->tx,&scan_policy,&h,7,8,ssid,16,now,2000,7000,2000,3000)){s->phase=QCA_NATIVE_SCAN_FAULT;s->error=3;return 0;}
 s->phase=QCA_NATIVE_SCAN_RUNNING;return 1;
}
static int archive_head(QcaNativeScan*s){
 if(s->archive_count==2)return 0;
 QcaScanCoordinator*c=&s->scan;
 int unmatched=c->has_orphan;
 if(!unmatched&&c->dispatch.count){
  QcaRxEvent*e=&c->dispatch.owned[c->dispatch.head];
  QcaWmiScanEvent parsed;
  unmatched=(e->event&0xffffffu)!=0x3001&&(e->event&0xffffffu)!=0x7001;
  if(!unmatched&&(e->event&0xffffffu)==0x3001&&!qca_wmi_scan_event(e->payload,e->bytes,c->pending.scan,c->pending.request,&parsed)){
   /* Archive only a structurally valid FOREIGN scan, not malformed input. */
   unsigned pos=0;QcaWmiTlv t;unsigned scan=0,request=0;
   while(e->bytes>=4&&qca_wmi_tlv(e->payload+4,e->bytes-4,&pos,&t)==1)if(t.tag==36&&t.bytes==24){
    const uint8_t*p=t.value;uint32_t a=0,b=0;
    for(unsigned j=0;j<4;j++){a|=(uint32_t)p[12+j]<<(8*j);b|=(uint32_t)p[16+j]<<(8*j);}
    if((a&~0xfffu)==0xa000&&(b&~0xfffu)==0xa000){request=a&0xfff;scan=b&0xfff;}
   }
   unmatched=scan&&request&&qca_wmi_scan_event(e->payload,e->bytes,scan,request,&parsed);
  }
  if(!unmatched&&(e->event&0xffffffu)==0x7001){QcaWmiBeaconRx b;
   int rc=qca_wmi_beacon_rx(e->payload,e->bytes,&b);
   unmatched=rc==QCA_BEACON_RX_UNSUPPORTED||rc==QCA_BEACON_RX_OTHER_EVENT
    ||(rc==QCA_BEACON_RX_ACCEPTED&&b.frequency_mhz!=c->live_frequency);
  }
 }
 if(unmatched&&qca_scan_coordinator_take_unmatched(c,&s->archive[s->archive_count])){s->archive_count++;return 1;}
 return 0;
}
int qca_native_scan_poll(QcaNativeScan*s,uint64_t now){
 if(!s||!s->phase)return 0;
 if(s->quiesce_requested)return 0;
 if(now<s->last||s->epoch!=s->radio->life.owners.epoch)return halt(s,4);
 s->last=now;
 if(now-s->started>=25000000)return halt(s,5);
 if(s->scan.phase==QCA_SC_FAULT)return halt(s,6);
 (void)archive_head(s); /* explicit owned transfer, never discard */
 int rc=qca_scan_coordinator_poll(&s->scan,now);
 if(rc<0)return halt(s,6);
 if(rc>0)return halt(s,0); /* terminal observed, actual platform stop still required */
 if((s->scan.ssid_seen||s->archive_count==2||s->radio->rx.backpressure)&&!s->stop_requested&&s->scan.stop_begun){
  if(!qca_scan_coordinator_stop(&s->scan,now))return halt(s,7);
  s->stop_requested=1;s->phase=QCA_NATIVE_SCAN_STOPPING;
 }
 return 0;
}
static const QcaRxEvent*event(const QcaNativeScan*s,unsigned slot){
 if(!s||!s->phase)return 0;
 if(slot<2)return slot<s->archive_count?&s->archive[slot]:0;
 if(slot==2)return s->scan.has_observation?&s->scan.observation.raw:0;
 if(slot==3)return s->scan.has_orphan?&s->scan.orphan:0;
 if(slot<6){unsigned n=slot-4;return n<s->scan.dispatch.count?&s->scan.dispatch.owned[(s->scan.dispatch.head+n)&1]:0;}
 if(slot<8&&s->radio){unsigned n=slot-6;return n<s->radio->rx.count?&s->radio->rx.events[(s->radio->rx.head+n)&1]:0;}
 return 0;
}
unsigned qca_native_scan_export(const QcaNativeScan*s,unsigned page,uint8_t*out,unsigned cap){
 /* Fixed2084-byte slot: magic8,9u32 metadata,owned2040-byte payload.
  * No hidden discard; stable after radio quiesce before a later native unload. */
 if(!s||!out||page>=40||cap<512)return 0;
 uintptr_t a=(uintptr_t)s,b=(uintptr_t)out;
 if(a>UINTPTR_MAX-sizeof(*s)||b>UINTPTR_MAX-512||(a<b?b-a<sizeof(*s):a-b<512))return 0;
 if(s->radio){a=(uintptr_t)s->radio;if(a>UINTPTR_MAX-sizeof(*s->radio)||(a<b?b-a<sizeof(*s->radio):a-b<512))return 0;}
 unsigned slot=page/5,offset=(page%5)*512,n=2084-offset;if(n>512)n=512;
 const QcaRxEvent*e=event(s,slot);const uint8_t magic[8]={'Q','E','X','P','0','0','0','1'};
 uint32_t fields[9]={slot,e?1u:0u,e?e->completion:0u,(uint32_t)s->epoch,(uint32_t)(s->epoch>>32),e?e->endpoint:0u,e?e->pipe:0u,e?e->bytes:0u,e?e->event:0u};
 for(unsigned j=0;j<n;j++){unsigned k=offset+j;
  if(k<8)out[j]=magic[k];else if(k<44)out[j]=(uint8_t)(fields[(k-8)/4]>>(((k-8)%4)*8));
  else out[j]=e?e->payload[k-44]:0;
 }
 return n;
}
