#include "selection.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static unsigned checks;
#define C(x) do{assert(x);checks++;}while(0)
static void put(uint8_t*p,uint32_t v){for(unsigned j=0;j<4;j++)p[j]=(uint8_t)(v>>(8*j));}
static QcaSelectionContext ctx(void){QcaSelectionContext c={0};c.epoch=9;c.now_us=1000000;c.ttl_us=5000000;c.rx_floor=10;c.live_frequency=2412;c.native_rates=0xfff;c.wmi_endpoint=1;c.active=1;c.ready_mac[0]=2;c.native_capabilities=7;c.frequency_count=2;c.frequencies[0]=2412;c.frequencies[1]=2437;memset(c.capability_source,1,32);memset(c.policy_digest,2,32);return c;}
static QcaRxEvent packet(unsigned id,unsigned snr,unsigned bssid){QcaRxEvent e={0};uint8_t*p=e.payload;put(p,0x7001);put(p+4,40|(44u<<16));put(p+8,1);put(p+12,snr);uint8_t*f=p+52;f[0]=0x80;memset(f+4,255,6);for(unsigned j=0;j<6;j++)f[10+j]=f[16+j]=(uint8_t)(2+j);f[15]=f[21]=(uint8_t)bssid;f[32]=100;f[34]=0x11;unsigned at=36;
 f[at++]=1;f[at++]=4;f[at++]=0x82;f[at++]=0x84;f[at++]=0x8b;f[at++]=0x96;
 f[at++]=0;f[at++]=10;memcpy(f+at,"iPhone (9)",10);at+=10;f[at++]=3;f[at++]=1;f[at++]=1;
 static const uint8_t rsn[]={1,0,0,15,172,4,1,0,0,15,172,4,1,0,0,15,172,2,0,0};f[at++]=48;f[at++]=20;memcpy(f+at,rsn,20);at+=20;put(p+24,at);unsigned padded=(at+3)&~3u;put(p+48,padded|(17u<<16));e.bytes=(uint16_t)(52+padded);e.raw_bytes=e.bytes+8;e.pipe=2;e.endpoint=1;e.event=0x7001;e.completion=id;e.raw[0]=1;e.raw[2]=(uint8_t)e.bytes;e.raw[3]=(uint8_t)(e.bytes>>8);return e;}
static void reject(QcaBssSelection*s,QcaSelectionContext*c,QcaRxEvent*e,uint64_t t){QcaBssSelection old=*s;C(qca_selection_offer(s,c,e,t)!=1);C(!memcmp(s,&old,sizeof(old)));}
int main(void){QcaBssSelection s={0};QcaSelectionContext c=ctx();QcaSelectedBss out;C(qca_selection_begin(&s,&c));C(!qca_selection_begin(&s,&c));QcaRxEvent e=packet(11,30,8);C(qca_selection_offer(&s,&c,&e,900000)==1);C(qca_selection_best(&s,&c,&out));C(out.snr==30&&out.estimated_signal_dbm==-65&&out.security.beacon.bss.ssid_bytes==10&&out.security.selected_pairwise==0xfac04);reject(&s,&c,&e,900000);
 e=packet(12,40,9);C(qca_selection_offer(&s,&c,&e,950000)==1);C(qca_selection_best(&s,&c,&out)&&out.snr==40);memset(&e,0,sizeof(e));C(out.owned.completion==12&&out.owned.raw[0]==1);
 e=packet(13,20,8);for(unsigned k=0;k<15;k++){QcaSelectionContext bad=c;QcaRxEvent x=e;uint64_t t=990000;switch(k){case 0:bad.active=0;break;case 1:bad.epoch++;break;case 2:bad.native_capabilities=0;break;case 3:bad.native_rates=1;break;case 4:memset(bad.capability_source,0,32);break;case 5:bad.rx_floor++;break;case 6:bad.live_frequency=2437;break;case 7:x.endpoint=2;break;case 8:x.pipe=1;break;case 9:x.event++;break;case 10:x.bytes--;break;case 11:x.raw_bytes=2049;break;case 12:t=c.now_us+1;break;case 13:t=1;bad.now_us=7000000;break;case 14:bad.ready_mac[0]=1;break;}reject(&s,&bad,&x,t);}
 QcaRxEvent x=e;x.payload[52]=0x50;reject(&s,&c,&x,990000);x=e;put(x.payload+12,UINT32_MAX);reject(&s,&c,&x,990000);
 x=e;put(x.payload,0x9001);x.event=0x9001;QcaRxEvent raw_saved=x;reject(&s,&c,&x,990000);C(!memcmp(&x,&raw_saved,sizeof(x)));
 /* Exact TTL inclusive, TTL+1 exclusive; outputs remain immutable on fail. */
 QcaSelectionContext boundary=c;boundary.now_us=5950000;C(qca_selection_best(&s,&boundary,&out));boundary.now_us++;QcaSelectedBss saved=out;C(!qca_selection_best(&s,&boundary,&out));C(!memcmp(&saved,&out,sizeof(out)));
 QcaBssSelection alias={0};C(!qca_selection_begin(&alias,(const QcaSelectionContext*)&alias));C(!qca_selection_best(&s,&c,(QcaSelectedBss*)&s));
 unsigned n=e.raw_bytes;for(unsigned cut=0;cut<n;cut++){QcaRxEvent x=e;x.raw_bytes=(uint16_t)cut;reject(&s,&c,&x,990000);}
 /* Every single-byte mutation preserves bounds and transactional rejects. */
 for(unsigned at=0;at<n;at++)for(unsigned v=0;v<256;v++){QcaBssSelection t=s,old=t;QcaRxEvent x=e;x.raw[at]=(uint8_t)v;int rc=qca_selection_offer(&t,&c,&x,990000);checks++;if(rc==1){C(qca_selection_best(&t,&c,&out));C(out.security.group_suite==0xfac04&&out.security.pairwise_count==1&&out.security.akm_count==1&&out.security.selected_akm==0xfac02&&out.security.beacon.bss.ssid_bytes==10);}else C(!memcmp(&t,&old,sizeof(t)));}
 /* Table bounds, stale eviction, ties and native proof changes. */
 QcaBssSelection full={0};C(qca_selection_begin(&full,&c));for(unsigned j=0;j<8;j++){e=packet(11+j,50,20+j);C(qca_selection_offer(&full,&c,&e,990000)==1);}e=packet(19,90,40);reject(&full,&c,&e,990000);C(qca_selection_best(&full,&c,&out)&&out.security.beacon.bss.bssid[5]==20);
 c.now_us=6000001;C(!qca_selection_best(&s,&c,&out));e=packet(19,60,40);C(qca_selection_offer(&full,&c,&e,c.now_us)==1);C(qca_selection_best(&full,&c,&out)&&out.snr==60);c.capability_source[0]++;C(!qca_selection_best(&full,&c,&out));
 /* Real production header adapter: READY/session/lifetime/RX joins. */
 c=ctx();QcaPersistentNative p={0};QcaWmiStartup w={0};QcaOperating op={0};p.startup=&w;p.epoch=9;p.life.phase=QCA_RADIO_ACTIVE;p.life.last=c.now_us;p.life.owners=(QcaRadioOwners){9,14,14,1,1,1,1,1,1,1,1,0};p.rx.startup=&w;p.rx.life=&p.life;p.rx.epoch=9;p.rx.phase=QCA_RX_ACTIVE;p.rx.completed=30;w.phase=2;w.transaction.phase=QCA_INIT_RUNNING;w.transaction.ready_seen=w.transaction.tx_complete=1;memcpy(w.transaction.ready.mac,c.ready_mac,6);w.operating=&op;op.control.session.phase=QCA_HTC_RUNNING;op.control.session.wmi.endpoint=1;
 QcaBssSelection bridge={0};C(qca_selection_begin(&bridge,&c));e=packet(11,35,70);C(qca_selection_offer_live(&bridge,&c,&p,&e,990000)==1);
 for(unsigned k=0;k<12;k++){QcaPersistentNative bad=p;bad.rx.life=&bad.life;QcaWmiStartup bw=w;bad.startup=bad.rx.startup=&bw;switch(k){case 0:bad.stop_latched=1;break;case 1:bad.life.phase=QCA_RADIO_CLOSED;break;case 2:bad.life.owners.epoch++;break;case 3:bad.life.owners.bus_master=0;break;case 4:bad.rx.epoch++;break;case 5:bad.rx.completed=1;break;case 6:bw.transaction.ready_seen=0;break;case 7:bw.transaction.ready.mac[0]++;break;case 8:bw.error=1;break;case 9:bad.life.owners.dma_users--;break;case 10:bad.life.last=c.now_us+1;break;case 11:bad.rx.phase=QCA_RX_FAULT;break;}QcaBssSelection old=bridge;e=packet(12,50,71);C(qca_selection_offer_live(&bridge,&c,&bad,&e,990000)!=1);C(!memcmp(&bridge,&old,sizeof(bridge)));}
 printf("checks=%u owned-WMI BSS strict-RSN/rates freshness transactional fuzz PASS\n",checks);return 0;}
