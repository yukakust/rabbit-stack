#include "auth_native.h"
#include "firmware_policy.h"
#ifdef QAUTH_MODEL_TRACE
#include <stdio.h>
#endif
static int failed(unsigned line){
#ifdef QAUTH_MODEL_TRACE
 fprintf(stderr,"AUTH_REJECT_LINE=%u\n",line);
#else
 (void)line;
#endif
 return 0;
}
static int same(const uint8_t*a,const uint8_t*b,unsigned n){for(unsigned j=0;j<n;j++)if(a[j]!=b[j])return failed(__LINE__);return 1;}
static int apart(const void*a,unsigned n,const void*b,unsigned m){uintptr_t x=(uintptr_t)a,y=(uintptr_t)b;return a&&b&&x<=UINTPTR_MAX-n&&y<=UINTPTR_MAX-m&&(x+n<=y||y+m<=x);}
static int key(const QsgKeyOp*k,QsgNative*g,QpnLedger*p,unsigned index){
 if(index>3||!k||k->glue!=g||k->pn!=p||k->epoch!=g->epoch||k->phase!=QSK_CONFIRMED||k->index!=index||k->sec_seen!=1||k->dma_seen!=1||!k->request||!k->pub_cookie||!k->dma_serial||!k->tx||k->tx->completed<k->dma_serial||k->tx->radio!=g->data->radio||k->tx->epoch!=g->epoch||k->sec_raw.completion<=k->pub_floor||k->sec_raw.completion>g->data->radio->rx.completed||p->key[index].sec_completion!=k->sec_raw.completion||!p->key[index].attempted||!p->key[index].confirmed)return failed(__LINE__);
 StaEvent e={0};
 if(sta_decode_htt_bound(&k->sec_raw,&p->htt,&p->version,&e)!=1||e.kind!=STA_SEC_IND||e.peer_id!=p->peer_id||e.cipher!=6||e.unicast!=(index==0))return failed(__LINE__);
 if((k->rsc_bytes!=0&&k->rsc_bytes!=6)||(index&&k->rsc_bytes!=6))return failed(__LINE__);
 uint64_t rsc=0;for(unsigned j=0;j<k->rsc_bytes;j++)rsc|=(uint64_t)k->rsc[j]<<(8*j);
 return k->rsc_bytes<=6&&rsc==p->key[index].initial;
}
int qauth_native_candidate(QsgNative*g,const QsgKeyOp*ptk,const QsgKeyOp*gtk,QpnLedger*p,uint64_t now,QauthRawCandidate*out){
 if(!g||!g->data||!g->station||!p||!out||g->fault||!g->epoch||g->epoch!=p->epoch||p->quarantined||p->pending)return failed(__LINE__);
 QcaHttDataPath*d=g->data;QcaPersistentNative*r=d->radio;QcaHttRuntime*t=d->runtime;
 /* The sole qdp dispatcher must have refreshed actual PCI/RX/lifecycle
  * observations at this exact cooperative tick; do not pump callbacks here. */
 if(!r||!t||d->epoch!=g->epoch||r->epoch!=g->epoch||t->epoch!=g->epoch||r->htt_owner!=d||d->phase!=QDP_RX_ACTIVE||!d->aggr_done||now!=d->last||now!=r->life.last||!qca_radio_accepts_work(&r->life)||!qca_htt_runtime_inventory(t)||t->allocated!=33||t->port->dma_users!=47||!d->pending_valid||d->pending_index>=d->pending.count||!t->rx_copy_owners||d->rx.owners!=t->owners||!r->startup||!r->startup->operating||!apart(out,sizeof(*out),d,sizeof(*d))||!apart(out,sizeof(*out),t,sizeof(*t))||!apart(out,sizeof(*out),g,sizeof(*g))||!apart(out,sizeof(*out),g->station,sizeof(*g->station))||!apart(out,sizeof(*out),ptk,sizeof(*ptk))||!apart(out,sizeof(*out),gtk,sizeof(*gtk)))return failed(__LINE__);
 QcaBootNative*b=r->startup->operating->boot;
#ifdef QAUTH_MODEL_TRACE
 if(b&&b->asset)fprintf(stderr,"AUTH_BOOT phase=%u err=%u plan=%u pin=%u ready=%u poisoned=%u pinned=%u received=%u total=%u type=%u version=%x digest_equal=%u capacity=%llu\n",b->phase,b->error,b->plan.phase,b->owns_pin,b->asset->ready,b->asset->poisoned,b->asset->pinned,b->asset->received,b->asset->policy.total,b->asset->policy.type,b->asset->policy.version,same(b->asset->policy.digest,qca_htt_container_digest,32),(unsigned long long)b->asset->capacity);
#endif
 /* firmware_chunks.c received is a chunk BITMASK, never a byte count. */
 if(!b||!b->asset||b->asset->policy.total!=751436||b->asset->policy.kind!=1||b->owns_pin!=1)return failed(__LINE__);
 unsigned chunks=(b->asset->policy.total+QCA_FW_CHUNK-1)/QCA_FW_CHUNK;
 uint32_t all=chunks==32?UINT32_MAX:(1u<<chunks)-1;
 if(b->phase!=5||b->error||b->plan.phase!=20||!b->owns_pin||b->asset->ready!=1||b->asset->poisoned||b->asset->pinned!=1||!b->asset->memory||b->asset->received!=all||b->asset->capacity<b->asset->policy.total||b->asset->policy.type!=8||b->asset->policy.version!=0x05020001||!same(b->asset->policy.digest,qca_htt_container_digest,32)||!apart(out,sizeof(*out),r,sizeof(*r))||!apart(out,sizeof(*out),b,sizeof(*b))||!apart(out,sizeof(*out),b->asset,sizeof(*b->asset))||!apart(out,sizeof(*out),b->asset->memory,b->asset->policy.total))return failed(__LINE__);
 if(!apart(out,sizeof(*out),r->startup,sizeof(*r->startup))||!apart(out,sizeof(*out),r->startup->operating,sizeof(*r->startup->operating)))return failed(__LINE__);
 for(unsigned j=0;j<47;j++){QcaDmaBuffer*map=j<14?&t->ce[j]:&t->extra[j-14];if(map->bytes>UINT32_MAX||!apart(out,sizeof(*out),map->host,(unsigned)map->bytes))return failed(__LINE__);}
 if(!sta_local_eligibility_live(g->station,r)||!g->station->gtk_index||g->station->peer_id!=p->peer_id||g->station->vdev!=p->vdev||!same(g->station->peer,p->peer,6)||!same(g->station->own_mac,p->own,6)||!key(ptk,g,p,0)||!key(gtk,g,p,g->station->gtk_index))return failed(__LINE__);
 unsigned slot=1023;uint32_t address=d->pending.paddr[d->pending_index];
 for(unsigned j=0;j<1023;j++)if(t->owners[j].paddr==address){slot=j;break;}
 if(slot==1023)return failed(__LINE__);QRxOwner*o=&t->owners[slot];QcaDmaBuffer*m=&t->extra[slot/32];
 if(o->state!=2||o->completion!=d->pending.completion||o->epoch!=g->epoch||o->map_identity!=(uintptr_t)m||!m->valid||!m->mapped||m->closing||!m->host||m->bytes!=65536||address!=m->address+2048*(slot%32)||!apart(out,sizeof(*out),m->host,(unsigned)m->bytes))return failed(__LINE__);
 uint8_t raw[2048];__atomic_thread_fence(__ATOMIC_SEQ_CST);
 const volatile uint8_t*actual=(const volatile uint8_t*)m->host+2048*(slot%32);
 for(unsigned j=0;j<2048;j++)raw[j]=actual[j];
 return qauth_raw_candidate(p,&d->pending,o,raw,sizeof raw,out);
}
int qauth_native_commit(QsgNative*g,const QsgKeyOp*ptk,const QsgKeyOp*gtk,QpnLedger*p,uint64_t now,QauthRawCandidate*out){
 if(!out||(uintptr_t)out>UINTPTR_MAX-sizeof(*out))return failed(__LINE__);
 const uint8_t*bytes=(const uint8_t*)out;
 for(unsigned j=0;j<sizeof(*out);j++)if(bytes[j])return failed(__LINE__);
 if(!qauth_native_candidate(g,ptk,gtk,p,now,out))return 0;
 /* candidate already checked all live source/key/owner joins and all output
  * aliases. Sole cooperative caller must not pump another callback here.
  * Retained output is complete before replay state advances; neither memory
  * assignment can fail. DMA/pending owner stays OWNED until separate refill. */
 *p=out->staged;return 1;
}
