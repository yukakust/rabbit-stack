static QcaHttWarmStop stop_model;
int stop_model_active(void){return stop_started!=0;}
int stop_model_retained(QcaChannels*c){if(!stop_started||c!=&stop_model.adapter->channels)return 0;return stop_model.phase==QSTOP_PROVEN?qstop_remaining_inventory(&stop_model):qca_htt_runtime_inventory(stop_model.data->runtime);}
int stop_model_dma_guard(QcaHttRuntime*r){return stop_started&&r==stop_model.data->runtime?qstop_release_guard(&stop_model):-1;}
void stop_model_tick(uint64_t now){
 QcaHttRuntime*r=stop_model.data->runtime;
 if(stop_model.phase!=QSTOP_PROVEN){
  int rc=qstop_poll(&stop_model,now);
  if(rc<0){assert(stop_fault&&r->port->dma_users==47&&r->cleanup==0&&r->callback_owners==1&&stop_model.data->phase==QDP_QUARANTINED&&!qca_radio_accepts_work(&stop_model.data->radio->life)&&qstop_release_guard(&stop_model)<0);puts("ACTUAL WARM STOP FAULT RETAINS47 NO RELEASE PASS SYNTHETIC");exit(0);}
  if(!rc)return;
  assert((!stop_fault||stop_fault>=7)&&stop_model.clear_readbacks==2&&stop_model.cpu_writes==2&&stop_model.warm.cpu_resets==2&&stop_model.warm.pipe_inits==2&&stop_model.warm.indicator==2&&stop_model.completion&&r->port->dma_users==47&&!r->callback_owners&&!r->rx_copy_owners&&!r->tx_owners&&!stop_model.data->radio->htt_owner&&!stop_model.data->rx.owners);
 }
 int rc=qstop_close_extra_one(&stop_model);
 if(rc<0){assert((stop_fault==7||stop_fault==8)&&stop_model.phase==QSTOP_PROVEN&&r->cleanup==0&&r->port->dma_users==47&&!r->callback_owners&&!r->rx_copy_owners&&!r->tx_owners&&r->extra[0].allocated&&r->ring.released_maps==0);if(stop_fault==7)assert(r->extra[0].mapped);else assert(!r->extra[0].mapped&&r->extra[0].host);puts("ACTUAL TARGET STOP PROVEN BUT FAILED UNMAP/FREE RETAINS EXACT ALLOCATION47 PASS SYNTHETIC");exit(0);}
 assert(r->port->dma_users==47-r->cleanup&&r->ring.released_maps==r->cleanup);
 if(rc==1){assert(r->cleanup==33&&r->ring.phase==Q_RING_CLOSED&&r->port->dma_users==14&&qca_htt_runtime_detachable(r));puts("ACTUAL WARM RESET+FW CLEAR READBACK+FRESH ROM2+CE IRQ BME FLUSH+REAL47 TO14/33 EXTRA FREE PASS; CE14 RETAINED; SYNTHETIC");exit(0);}
}
