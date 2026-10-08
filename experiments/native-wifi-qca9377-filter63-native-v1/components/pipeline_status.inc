void qca_filter63_status(uint8_t out[448]){
 for(unsigned i=0;i<448;i++)out[i]=0;
 const uint8_t magic[8]={'Q','F','6','3','0','0','0','1'};for(unsigned i=0;i<8;i++)out[i]=magic[i];
 const QcaPersistentTx*t=&native_scan.tx;uint32_t held=0;
 for(unsigned i=0;i<14;i++)if(adapter.channels.buffers[i].allocated||adapter.channels.buffers[i].mapped||adapter.channels.buffers[i].allocation_uncertain)held++;
 uint32_t f[64]={pipeline_phase,pipeline_error,filter_attempted,filter.phase,filter.error,filter.step,
 filter.tx_count,filter.tx_completed,filter.echo_seen,filter.initial_floor,filter.echo_floor,filter.last_rx,filter.raw_completion,filter.raw_bytes,filter.raw_pipe,filter.raw_endpoint,
 filter.tx_request,filter.last_request,filter.credit_serial,filter.echo_arg,t->phase,t->error,t->serial,t->request,t->attempted,t->completed,
 htt_query.phase,htt_query.error,htt_query.attempted,htt_query.dma_completed,htt_query.version_seen,htt_query.version.major,htt_query.version.minor,htt_query.watermark,htt_query.response_completion,htt_query.binding.endpoint,htt_query.binding.max_bytes,htt_query.binding.op_version,
 htt_proof.valid,htt_proof.error,(uint32_t)htt_proof.generation,(uint32_t)(htt_proof.generation>>32),(uint32_t)persistent.epoch,(uint32_t)(persistent.epoch>>32),actual_released(),held,port.dma_users,adapter.access.count,port.claimed,adapter.bus.owned,
 wake.owned,link.owned,irq.owned,boot.owns_pin,ram.asset.pinned,adapter.phase,adapter.channels.cleanup_slot,persistent.life.phase,persistent.life.error,63,operating.service.service_count,persistent.rx.error,persistent.rx.completed,persistent.error};
 for(unsigned i=0;i<64;i++)for(unsigned k=0;k<4;k++)out[8+4*i+k]=(uint8_t)(f[i]>>(8*k));
 for(unsigned i=0;i<32&&i<operating.service.service_count;i++)for(unsigned k=0;k<4;k++)out[264+4*i+k]=(uint8_t)(operating.service.service_words[i]>>(8*k));
 for(unsigned i=0;i<6;i++)out[392+i]=filter.mac[i];
 out[398]=10;
 const uint8_t requested[10]={'i','P','h','o','n','e',' ','(','9',')'};for(unsigned i=0;i<10;i++)out[400+i]=requested[i];
 uint32_t echo_slot=UINT32_MAX,version_slot=UINT32_MAX;
 for(unsigned i=0;i<native_scan.archive_count;i++){if(native_scan.archive[i].completion==filter.raw_completion)echo_slot=i;if(native_scan.archive[i].completion==htt_query.response_completion)version_slot=i;}
 for(unsigned k=0;k<4;k++){out[432+k]=(uint8_t)(echo_slot>>(8*k));out[436+k]=(uint8_t)(version_slot>>(8*k));}
 out[440]=1; /* Explicit PARTIAL startup: no RX_RING_CFG or aggregation. */
}
