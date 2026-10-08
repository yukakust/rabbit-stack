#include "data_path.h"
#include <stdatomic.h>
static void copy(void*d,const void*s,size_t n){volatile uint8_t*a=d;const uint8_t*b=s;while(n--)*a++=*b++;}
static void zero(void*d,size_t n){volatile uint8_t*a=d;while(n--)*a++=0;}
static int same(const void*a,const void*b,size_t n){const uint8_t*x=a,*y=b;unsigned diff=0;while(n--)diff|=*x++^*y++;return !diff;}
static int apart(const void*a,size_t n,const void*b,size_t m){return a&&b&&(uintptr_t)a<=UINTPTR_MAX-n&&(uintptr_t)b<=UINTPTR_MAX-m&&((uintptr_t)a+n<=(uintptr_t)b||(uintptr_t)b+m<=(uintptr_t)a);}
static QcaInitAdapter*adapter(QcaPersistentNative*p){return p->startup->operating->boot->board->setup->read.full.adapter;}
void qdp_quarantine(QcaHttDataPath*s,unsigned error){if(!s)return;if(!s->error)s->error=error;s->phase=QDP_QUARANTINED;if(s->radio&&s->radio->epoch==s->epoch)(void)qca_persistent_quiesce(s->radio,s->last);/* Revoke work; retain maps, callbacks and packet until actual target stop exists. */}
static void tx_join(QcaHttDataPath*);
static int live(QcaHttDataPath*s,uint64_t now){
 if(!s||!s->runtime||!s->radio||s->phase==QDP_QUARANTINED||now<s->last||s->radio->htt_owner!=s||s->epoch!=s->runtime->epoch||s->epoch!=s->radio->epoch||qca_persistent_poll(s->radio,now)!=1||!qca_htt_runtime_inventory(s->runtime))return 0;
 QcaInitAdapter*a=adapter(s->radio);QcaCeRing*r=&a->channels.rings[4];QcaHttBinding b;
 if(s->runtime->port!=a->mapped.irq->port||s->runtime->ce!=a->channels.buffers||!qca_htt_version_bind(&s->radio->startup->operating->control.session,3,&b)||b.endpoint!=s->binding.endpoint||b.max_bytes!=s->binding.max_bytes||!r->owned||r->fault||r->entries!=8||r->receive||r->descriptors!=a->channels.buffers[8].host||r->context!=&a->channels.routes[4]||a->channels.routes[4].pipe!=4||a->channels.routes[4].bus!=&a->bus||r->write!=r->published)return 0;
 s->last=now;return 1;
}
int qdp_begin(QcaHttDataPath*s,QcaHttRuntime*r,QcaPersistentNative*p,QcaHttNative*q,QcaNativeScan*capture,uint64_t now){
 if(!s||!r||!p||!q||!capture||capture->radio!=p||capture->epoch!=p->epoch||!apart(s,sizeof(*s),capture,sizeof(*capture))||!apart(s,sizeof(*s),r,sizeof(*r))||!apart(s,sizeof(*s),p,sizeof(*p))||!apart(s,sizeof(*s),q,sizeof(*q))||s->phase||!p->startup||!p->startup->operating||p->htt_owner!=q||q->radio!=p||q->phase!=QCA_HTTN_READY||q->epoch!=p->epoch||r->epoch!=p->epoch||!q->version_seen||!q->dma_completed||q->stop_requested||q->version.major!=3||q->version.minor!=56||!q->response_completion||!q->response||q->response->completion!=q->response_completion||r->phase!=HTT_RUNTIME_MAPPED||r->callback_owners||r->tx_owners||r->rx_copy_owners||r->ring.phase||!qca_htt_runtime_inventory(r)||qca_persistent_poll(p,now)!=1)return 0;
 QcaHtcFrame vf;QcaHttVersion vv;
 if(q->response->pipe!=1||q->response->endpoint!=q->binding.endpoint||q->response->completion>p->rx.completed||!qca_htc_decode(q->response->raw,q->response->raw_bytes,&vf)||vf.endpoint!=q->binding.endpoint||vf.payload_bytes!=q->response->bytes||!qca_htt_version_conf(&q->binding,vf.payload,vf.payload_bytes,&vv)||vv.major!=3||vv.minor!=56)return 0;
 QcaOperating*o=p->startup->operating;QcaHtcFrame f;QcaWmiServiceInfo info;QcaHttBinding binding;
 if(!o->service_valid||o->service_bytes>2048||!qca_htc_decode(o->service_frame,o->service_bytes,&f)||f.endpoint!=o->control.session.wmi.endpoint||!qca_wmi_service_info(f.payload,f.payload_bytes,&info)||info.service_count<17||!(info.service_words[16]&2)||!same(&info,&o->service,sizeof(info))||!qca_htt_version_bind(&o->control.session,3,&binding))return 0;
 for(unsigned i=0;i<QCA_HTC_ENDPOINTS;i++)if(f.credits[i])return 0;
 QcaInitAdapter*a=adapter(p);QcaCeRing*ce=&a->channels.rings[4];if(ce->read!=ce->write||ce->write!=ce->published||a->channels.buffers[9].bytes!=4096)return 0;
 if(!qca_htt_runtime_bind_ring(r,3,8,0x05020001))return 0;
 s->version_raw=*q->response;if(!qca63_query_handover(capture,q))return 0;s->runtime=r;s->radio=p;s->epoch=p->epoch;s->last=now;s->floor=p->rx.completed;s->binding=binding;s->phase=QDP_FILLING;s->cfg_cookie=0xb0000001;s->service_bytes=o->service_bytes;copy(s->service_raw,o->service_frame,o->service_bytes);
 s->rx=(QRxRing){3,3,56,1,s->epoch,s->floor,s->floor,1023,r->owners};r->service65_proven=1;r->callback_owners=1;
 p->htt_owner=s;q->radio=0;q->response=0;q->archive=0;return 1;
}
int qdp_refill_initial(QcaHttDataPath*s,uint64_t now){if(!live(s,now)||s->phase!=QDP_FILLING||s->runtime->ring.fill>=1023)return 0;return qca_htt_runtime_refill_one(s->runtime,(uint16_t)s->runtime->ring.fill);}
int qdp_publish_cfg(QcaHttDataPath*s,uint64_t now){
 if(!live(s,now)||s->phase!=QDP_FILLING||now>UINT64_MAX-3000000||s->runtime->ring.fill!=1023||s->runtime->tx_owners)return 0;
 QcaInitAdapter*a=adapter(s->radio);QcaCeRing*ce=&a->channels.rings[4];uint8_t*p=a->channels.buffers[9].host;if(ce->read!=ce->write)return 0;
 uint32_t index=*(volatile uint32_t*)((uint8_t*)s->runtime->extra[32].host+8192);
 if(!qca_htc_header(p,4096,s->binding.endpoint,40,s->radio->startup->operating->control.session.sequence,0)||qca_ring_cfg(&s->runtime->ring,index,p+8))return 0;
 s->floor=s->radio->rx.completed;s->rx.floor=s->rx.last=s->floor;s->cfg_bytes=48;s->runtime->tx_owners=1;s->phase=QDP_CFG_POSTED;s->transfer_deadline=now+3000000;
 if(qca_ring_cfg_posted(&s->runtime->ring,s->epoch,s->floor)){qdp_quarantine(s,1);return -1;}
 s->radio->startup->operating->control.session.sequence++;atomic_thread_fence(memory_order_release);
 if(qca_ce_post(ce,a->channels.buffers[9].address,48,s->cfg_cookie,s->binding.endpoint,0)){qdp_quarantine(s,2);return -1;}return 1;
}
int qdp_publish_aggr(QcaHttDataPath*s,uint64_t now){
 if(!live(s,now)||s->phase!=QDP_RX_ACTIVE||s->aggr_done||s->runtime->tx_owners||now>UINT64_MAX-3000000)return 0;
 QcaInitAdapter*a=adapter(s->radio);QcaCeRing*ce=&a->channels.rings[4];uint8_t*p=a->channels.buffers[9].host;if(ce->read!=ce->write)return 0;
 if(!qca_htc_header(p,4096,s->binding.endpoint,3,s->radio->startup->operating->control.session.sequence,0))return 0;
 p[8]=5;p[9]=1;p[10]=1; /* Primary-supported bounded one-subframe profile. */
 s->aggr_cookie=0xb0000002;s->phase=QDP_AGGR_POSTED;s->runtime->tx_owners=1;s->transfer_deadline=now+3000000;s->radio->startup->operating->control.session.sequence++;
 atomic_thread_fence(memory_order_release);if(qca_ce_post(ce,a->channels.buffers[9].address,11,s->aggr_cookie,s->binding.endpoint,0)){qdp_quarantine(s,22);return -1;}return 1;
}
int qdp_poll_dma(QcaHttDataPath*s,uint64_t now){
 if(!live(s,now))return -1;
 if(s->phase!=QDP_CFG_POSTED&&s->phase!=QDP_AGGR_POSTED&&!s->tx_posted)return 0;
 if(now>s->transfer_deadline){qdp_quarantine(s,20);return -1;}
 QcaInitAdapter*a=adapter(s->radio);unsigned index;uint32_t cookie,n;
 if(qca_ce_hw_index(&a->bus.engines[4],0,&index)){qdp_quarantine(s,3);return -1;}
 int rc=qca_ce_complete(&a->channels.rings[4],index,&cookie,&n);if(rc>0)return 0;if(rc<0){qdp_quarantine(s,4);return -1;}
 if(s->ce_completions==UINT64_MAX){qdp_quarantine(s,7);return -1;}s->ce_completions++;
 if(s->phase==QDP_CFG_POSTED){if(cookie!=s->cfg_cookie||n!=48||qca_ring_cfg_dma_complete(&s->runtime->ring,s->epoch,s->ce_completions)){qdp_quarantine(s,5);return -1;}s->runtime->tx_owners=0;s->phase=QDP_RX_ACTIVE;return 1;}
 if(s->phase==QDP_AGGR_POSTED){if(cookie!=s->aggr_cookie||n!=11){qdp_quarantine(s,23);return -1;}s->runtime->tx_owners=0;s->aggr_done=1;s->phase=QDP_RX_ACTIVE;return 1;}
 if(cookie!=s->tx_cookie||n!=s->tx_bytes||s->tx_dma_done){qdp_quarantine(s,6);return -1;}s->tx_dma_done=1;tx_join(s);return 1;
}
static void tx_join(QcaHttDataPath*s){if(s->tx_posted&&s->tx_dma_done&&s->tx_htt_done){s->tx_posted=0;s->runtime->tx_owners=0;}}
static unsigned u16(const uint8_t*p){return p[0]|((unsigned)p[1]<<8);}
static void w16(uint8_t*p,unsigned n){p[0]=(uint8_t)n;p[1]=(uint8_t)(n>>8);}
static void w32(uint8_t*p,uint32_t n){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(n>>(8*i));}
static int reject_event(QcaHttDataPath*s,const QcaRxEvent*e,unsigned error){if(e&&e->raw_bytes<=2048){s->rejected_bytes=e->raw_bytes;copy(s->rejected_raw,e->raw,e->raw_bytes);}qdp_quarantine(s,error);return -1;}
int qdp_receive(QcaHttDataPath*s,const QcaRxEvent*e,uint64_t now){
 if(!live(s,now)||s->phase!=QDP_RX_ACTIVE||!s->aggr_done||!e||!apart(e,sizeof(*e),s,sizeof(*s))||e->raw_bytes>2048||e->completion<=s->floor||e->completion>s->radio->rx.completed||e->pipe!=1||e->endpoint!=s->binding.endpoint||e->event)return 0;
 QcaHtcFrame f;if(!qca_htc_decode(e->raw,e->raw_bytes,&f)||f.endpoint!=e->endpoint||f.payload_bytes!=e->bytes)return reject_event(s,e,10);
 /* Credits were applied by the sole persistent RX producer, never here. */
 if(!f.payload_bytes)return 0;
 if(f.payload[0]==7){
  const uint8_t*p=f.payload;unsigned n=f.payload_bytes;
  if(now>s->transfer_deadline)return reject_event(s,e,20);
  if(!s->tx_posted||s->tx_htt_done||e->completion<=s->tx_floor||n!=6||p[2]!=1||p[3]||(p[1]&7)>3||u16(p+4)!=s->tx_id)return reject_event(s,e,11);
  s->tx_raw_bytes=e->raw_bytes;copy(s->tx_raw,e->raw,e->raw_bytes);s->tx_status=p[1]&7;s->tx_rx_completion=e->completion;s->tx_htt_done=1;tx_join(s);return 1;
 }
 if(s->pending_valid||s->output_count==4)return 0; /* leave owned raw with caller */
 QRxInd ind;if(qrx_indication(3,3,56,s->epoch,e->completion,s->rx.last,f.payload,f.payload_bytes,&ind)!=1||ind.kind!=0x12||!ind.usable)return reject_event(s,e,12);
 /* Validate both ledgers on a disjoint bounded shadow before committing either.
  * Single owner/callback serialization must exclude concurrent ledger changes. */
 copy(s->validation_owners,s->runtime->owners,sizeof(s->validation_owners));QRxRing check=s->rx;check.owners=s->validation_owners;
 if(!qrx_claim(&check,&ind))return reject_event(s,e,13);
 uint16_t buffers[255];for(unsigned i=0;i<ind.count;i++){unsigned b;for(b=0;b<1023;b++)if(s->runtime->owners[b].paddr==ind.paddr[i])break;if(b==1023)return reject_event(s,e,14);buffers[i]=(uint16_t)b;}
 if(qca_ring_claim(&s->runtime->ring,buffers,ind.count,s->epoch,ind.completion)||!qrx_claim(&s->rx,&ind))return reject_event(s,e,15);
 s->pending=ind;s->pending_index=0;s->pending_valid=1;s->runtime->rx_copy_owners=1;return 1;
}
int qdp_copy_one(QcaHttDataPath*s,uint64_t now){
 if(!live(s,now)||s->phase!=QDP_RX_ACTIVE||!s->pending_valid||s->output_count==4)return 0;
 unsigned i=s->pending_index,b;uint32_t addr=s->pending.paddr[i];for(b=0;b<1023;b++)if(s->runtime->owners[b].paddr==addr)break;
 if(b==1023||s->runtime->owners[b].state!=2||s->runtime->owners[b].completion!=s->pending.completion){qdp_quarantine(s,16);return -1;}
 QcaDmaBuffer*d=&s->runtime->extra[b/32];const uint8_t*raw=(uint8_t*)d->host+(b%32)*2048;QRxFrame frame;
 atomic_thread_fence(memory_order_acquire);
 if(!qrx_frame(raw,2048,s->pending.length[i],&frame)){s->rejected_bytes=2048;copy(s->rejected_raw,raw,2048);qdp_quarantine(s,17);return -1;}
 /* No key epoch/GTK-RSC/PN/MIC authority has been integrated. Hardware
  * classification, full reorder or a descriptor DONE bit cannot grant it. */
 if(frame.encrypted||((raw[15]>>4)!=7)||(u16(frame.payload)&0x4000)||(frame.attention&0x01000000u)){s->rejected_bytes=2048;copy(s->rejected_raw,raw,2048);qdp_quarantine(s,21);return -1;}
 unsigned at=(s->output_head+s->output_count)&3;s->output[at]=frame;s->output_paddr[at]=addr;s->output_completion[at]=s->pending.completion;s->output_count++;
 if(!qrx_retire(&s->rx,addr,s->epoch,s->pending.completion)||qca_ring_copied(&s->runtime->ring,(uint16_t)b,s->epoch,1,1)||!qca_htt_runtime_refill_one(s->runtime,(uint16_t)b)){qdp_quarantine(s,18);return -1;}
 s->pending_index++;if(s->pending_index==s->pending.count){s->pending_valid=0;s->runtime->rx_copy_owners=0;}return 1;
}
int qdp_take_frame(QcaHttDataPath*s,QRxFrame*out,uint64_t*completion){
 if(!s||!out||!completion||!apart(s,sizeof(*s),out,sizeof(*out))||!apart(s,sizeof(*s),completion,sizeof(*completion))||!apart(out,sizeof(*out),completion,sizeof(*completion))||!s->output_count||s->output_count>4||s->output_head>3)return 0;
 *out=s->output[s->output_head];*completion=s->output_completion[s->output_head];s->output_head=(s->output_head+1)&3;s->output_count--;return 1;
}
static int submit_frame(QcaHttDataPath*s,const uint8_t*frame,unsigned bytes,uint16_t id,unsigned vdev,unsigned tid,unsigned mode,uint64_t now){
 if(!live(s,now)||s->phase!=QDP_RX_ACTIVE||!s->aggr_done||now>UINT64_MAX-3000000||!frame||bytes<24||bytes>2048||!id||id==65535||id<=s->tx_id||vdev>63||tid>17||s->tx_posted||s->runtime->tx_owners||!apart(s,sizeof(*s),frame,bytes))return 0;
 unsigned fc=u16(frame);if((fc&0x4400)||(u16(frame+22)&15)||(fc&3)||((mode==3&&(fc&12)!=0)||(mode==0&&(fc&12)!=8)))return 0; /* no protected/MIC/fragment ambiguity */
 QcaInitAdapter*a=adapter(s->radio);QcaCeRing*ce=&a->channels.rings[4];QcaDmaBuffer*d=&a->channels.buffers[9];if(ce->read!=ce->write||!apart(d->host,4096,frame,bytes))return 0;
 uint8_t*p=d->host;unsigned prefetch=((bytes<50?bytes:50)+3)&~3u;zero(p,40+prefetch);copy(p+1024,frame,bytes);copy(p+40,frame,bytes<prefetch?bytes:prefetch);
 w32(p,(uint32_t)d->address+1024);w32(p+4,bytes); /* frag1 terminator remains zero */
 if(!qca_htc_header(p+16,4096-16,s->binding.endpoint,16+prefetch,0,0))return 0;
 p[24]=1;p[25]=(uint8_t)(7|(mode<<5));w16(p+26,vdev|(tid<<6)|0x800);w16(p+28,bytes);w16(p+30,id);w32(p+32,(uint32_t)d->address+(mode==3?1024:0));w32(p+36,65535);
 s->tx_cookie=0xc0000000u|id;s->tx_id=id;s->tx_bytes=24+prefetch;s->tx_floor=s->radio->rx.completed;s->tx_dma_done=s->tx_htt_done=0;s->tx_posted=1;s->runtime->tx_owners=1;s->transfer_deadline=now+3000000;
 atomic_thread_fence(memory_order_release);if(qca_ce_post(ce,d->address+16,s->tx_bytes,s->tx_cookie,s->binding.endpoint,0)){qdp_quarantine(s,19);return -1;}return 1;
}

int qdp_submit_raw(QcaHttDataPath*s,const uint8_t*f,unsigned n,uint16_t id,unsigned vdev,unsigned tid,uint64_t now){if(tid>16)return 0;return submit_frame(s,f,n,id,vdev,tid,0,now);}
int qdp_submit_mgmt(QcaHttDataPath*s,const uint8_t*f,unsigned n,uint16_t id,unsigned vdev,uint64_t now){return submit_frame(s,f,n,id,vdev,17,3,now);}
