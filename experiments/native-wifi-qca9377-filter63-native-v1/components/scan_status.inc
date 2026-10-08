const QcaNativeScan*qca_scan_native_view(void){return &native_scan;}
unsigned qca_scan_export(unsigned page,uint8_t*out,unsigned cap){return qca_native_scan_export(&native_scan,page,out,cap);}
void qca_scan_status(uint8_t out[416]){
 for(unsigned j=0;j<416;j++)out[j]=0;
 const uint8_t magic[8]={'Q','S','C','N','0','0','0','1'};for(unsigned j=0;j<8;j++)out[j]=magic[j];
 const QcaNativeScan*s=&native_scan;const QcaScanCoordinator*c=&s->scan;const QcaPersistentTx*t=&s->tx;const QcaPersistentRx*r=&persistent.rx;
 uint32_t held=0;for(unsigned j=0;j<14;j++)if(adapter.channels.buffers[j].allocated||adapter.channels.buffers[j].mapped||adapter.channels.buffers[j].allocation_uncertain)held++;
 uint32_t f[64]={s->phase,s->error,s->stop_requested,s->quiesce_requested,actual_released(),
 c->phase,c->error,c->stage,c->request,t->phase,t->error,t->request,t->attempted,t->completed,
 c->pending.phase,c->pending.result,c->pending.started,c->pending.last_event.type,c->pending.last_event.reason,
 c->pending.last_event.frequency,c->pending.last_event.request_id,c->pending.last_event.scan_id,c->pending.last_rx,
 c->start_floor,c->live_frequency,c->stop.stop.phase,c->stop.stop.terminal_seen,c->stop.stop.tx_complete,
 c->stop.terminal_completion,c->ssid_seen,c->has_observation,(c->has_orphan||r->rejected.raw_bytes),c->dispatch.count,s->archive_count,
 r->phase,r->error,r->completed,r->posted_count,r->count,r->backpressure,
 operating.control.credit.available,operating.control.credit.outstanding,operating.control.credit.reserved,operating.control.credit.total,
 held,port.dma_users,port.claimed,wake.owned,link.owned,irq.owned,boot.owns_pin,adapter.bus.owned,adapter.access.count,
 adapter.phase,adapter.channels.cleanup_slot,persistent.life.phase,persistent.life.error,persistent.error,
 startup.transaction.ready_seen,startup.transaction.tx_complete,63,13,0,0};
 for(unsigned j=0;j<64;j++)for(unsigned k=0;k<4;k++)out[8+4*j+k]=(uint8_t)(f[j]>>(8*k));
 for(unsigned j=0;j<32;j++){out[264+j]=scan_policy.reviewed_digest[j];out[296+j]=scan_policy.ruleset_digest[j];out[328+j]=scan_policy.location_digest[j];}
 if(c->has_observation){const QcaBeaconInfo*b=&c->observation.parsed.bss;out[360]=(uint8_t)b->ssid_bytes;
  for(unsigned j=0;j<32;j++)out[364+j]=j<b->ssid_bytes?b->ssid[j]:0;
  for(unsigned j=0;j<6;j++)out[396+j]=b->bssid[j];
 }
}
