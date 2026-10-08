#include "selection.h"
static int equal(const uint8_t*a,const uint8_t*b,unsigned n){for(unsigned j=0;j<n;j++)if(a[j]!=b[j])return 0;return 1;}
int qca_selection_offer_live(QcaBssSelection*s,const QcaSelectionContext*c,const QcaPersistentNative*p,const QcaRxEvent*e,uint64_t observed){
 if(!s||!c||!p||!e||p->error||p->stop_latched||p->epoch!=c->epoch||p->life.phase!=QCA_RADIO_ACTIVE||p->life.error||p->life.owners.epoch!=p->epoch||p->life.owners.init_ready!=1||p->life.owners.stop_verified||!p->life.owners.mappings||p->life.owners.dma_users!=p->life.owners.mappings||p->life.owners.pci!=1||p->life.owners.wake!=1||p->life.owners.link!=1||p->life.owners.irq!=1||p->life.owners.pin!=1||p->life.owners.bus!=1||p->life.owners.bus_master!=1||p->life.last>c->now_us||c->now_us-p->life.last>c->ttl_us||p->rx.phase!=QCA_RX_ACTIVE||p->rx.error||p->rx.epoch!=p->epoch||p->rx.completed<e->completion||p->rx.life!=&p->life||p->rx.startup!=p->startup||!p->startup)return QCA_SELECT_POLICY;
 const QcaWmiStartup*w=p->startup;
 if(w->phase!=2||w->error||w->cancelled||w->transaction.phase!=QCA_INIT_RUNNING||w->transaction.ready_seen!=1||w->transaction.tx_complete!=1||!equal(w->transaction.ready.mac,c->ready_mac,6)||!w->operating||w->operating->error||w->operating->control.session.phase!=QCA_HTC_RUNNING||w->operating->control.session.wmi.endpoint!=c->wmi_endpoint)return QCA_SELECT_POLICY;
 /* Caller pins actual scan.live_frequency in c. An allocation pool has no
  * channel/capability authority; those remain explicit coordinator inputs. */
 return qca_selection_offer(s,c,e,observed);
}
