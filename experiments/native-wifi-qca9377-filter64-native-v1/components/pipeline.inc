static unsigned actual_released(void){return persistent.life.phase==QCA_RADIO_CLOSED&&prefix_released();}
static uint32_t pipeline_phase,pipeline_error,filter_attempted;
static QcaFilterBarrier filter;
int qca_filter64_archive_take(QcaPersistentRx*r,uint32_t completion){
 if(r!=&persistent.rx||native_scan.epoch!=persistent.epoch||native_scan.archive_count>=16)return 0;
 if(!qca_rx_take(r,completion,&native_scan.archive[native_scan.archive_count],sizeof(QcaRxEvent)))return 0;
 native_scan.archive_count++;return 1;
}
static int archive_owned(const QcaRxEvent*e){
 if(!e||!e->completion||native_scan.archive_count>=16||native_scan.epoch!=persistent.epoch)return 0;
 for(unsigned i=0;i<native_scan.archive_count;i++)if(native_scan.archive[i].completion==e->completion)return 0;
 native_scan.archive[native_scan.archive_count++]=*e;return 1;
}
static void pipeline_fault(unsigned error,uint64_t now){
 if(!pipeline_error)pipeline_error=error;
 pipeline_phase=5;native_scan.error=error;native_scan.phase=QCA_NATIVE_SCAN_FAULT;native_scan.quiesce_requested=1;
 qca_prefix_request(&prefix,3,boot.plan.offset,boot.plan.submitted,boot.plan.completed,boot.plan.phase,boot.io.wire.phase);
 (void)qca_persistent_quiesce(&persistent,now);(void)qca_stop();
}
static void qca_filter64_step(uint64_t now){
 if(!pipeline_phase&&qca_radio_accepts_work(&persistent.life)){
  filter_attempted=1;native_scan.radio=&persistent;native_scan.epoch=persistent.epoch;
  QcaHtcFrame ready={0};
  if(!startup.transaction.ready_seen||!startup.transaction.tx_complete||!startup.ready_frame_bytes||startup.ready_frame_bytes>128||!qca_htc_decode(startup.prefix,startup.ready_frame_bytes,&ready)
    ||!qca_tx_begin(&native_scan.tx,&persistent,now)
    ||!qca_filter_begin(&filter,&operating.control.credit,ready.payload,ready.payload_bytes,persistent.epoch,persistent.rx.completed,0x64000001u,now)){pipeline_fault(101,now);return;}
  pipeline_phase=1;
 }
 if(pipeline_phase==1){
  if(qca_filter_poll(&filter,persistent.epoch,now)<0){pipeline_fault(102,now);return;}
  QcaPersistentTx*t=&native_scan.tx;
  if((filter.phase==QCA_FILTER_READY||filter.phase==QCA_FILTER_ORDERED)&&t->phase==QCA_TX_IDLE){
   uint32_t id=0;if(!qca_filter_prepare(&filter,persistent.epoch,now)||!qca_tx_submit(t,filter.frame,filter.frame_bytes,now,2000000,&id)||!qca_filter_submitted(&filter,persistent.epoch,id,now)){pipeline_fault(103,now);return;}
  }
  if(t->phase!=QCA_TX_IDLE){
   int rc=qca_tx_poll(t,now);if(rc<0){pipeline_fault(104,now);return;}
   /* Immediately after actual POSTED transition, before another RX pump. */
   if(t->phase==QCA_TX_POSTED&&filter.phase==QCA_FILTER_SUBMITTED&&!qca_filter_post(&filter,persistent.epoch,t->request,persistent.rx.completed,t->frame,t->bytes,now)){pipeline_fault(105,now);return;}
   if(rc==1){if(!qca_filter_tx_complete(&filter,persistent.epoch,t->request,t->bytes,now)||!qca_tx_retire(t,t->request)){pipeline_fault(106,now);return;}}
  }
  for(unsigned i=0;i<2&&persistent.rx.count;i++){
   QcaRxEvent e;
   uint32_t id=persistent.rx.events[persistent.rx.head].completion;
   if(native_scan.archive_count>=16||!qca_rx_take(&persistent.rx,id,&e,sizeof(e))){pipeline_fault(107,now);return;}
   int rc=qca_filter_receive(&filter,persistent.epoch,e.completion,e.pipe,e.raw,e.raw_bytes,now);
   if(!archive_owned(&e)){pipeline_fault(108,now);return;}
   if(rc<0){pipeline_fault(109,now);return;}
  }
  if(qca_filter_passed(&filter)){
   if(native_scan.tx.phase!=QCA_TX_IDLE||native_scan.tx.request!=filter.last_request||native_scan.tx.completed!=3||native_scan.tx.attempted!=3){pipeline_fault(110,now);return;}
   htt_attempted=1;
   if(native_scan.archive_count>13||!qca_htt_firmware_proof(&htt_proof,&boot)||!qca_htt_native_begin(&htt_query,&persistent,htt_proof.htt_op,now,&native_scan.archive[13],3)){pipeline_fault(111,now);return;}
   pipeline_phase=2;
  }
 }
 if(pipeline_phase==2){
  int rc=qca_htt_native_poll(&htt_query,now);
  /* Preserve taken HTT bytes on both success and failure, before fault export. */
  if(rc){
   if(!qca63_query_handover(&native_scan,&htt_query)){pipeline_fault(114,now);return;}
  }
  if(rc<0){pipeline_fault(112,now);return;}
  if(rc==1){
   if(htt_query.phase!=QCA_HTTN_READY||!htt_query.version_seen||!htt_query.dma_completed||htt_query.stop_requested||htt_query.version.major!=3||htt_query.version.minor!=56||htt_query.epoch!=persistent.epoch){pipeline_fault(113,now);return;}
   if(!htt_query.response_completion||!qca_native_scan_begin(&native_scan,&persistent,now)){pipeline_fault(115,now);return;}
   pipeline_phase=3;
  }
 }
 if(pipeline_phase==3&&!native_scan.quiesce_requested&&qca_native_scan_poll(&native_scan,now)){
  qca_prefix_request(&prefix,native_scan.error?3:0,boot.plan.offset,boot.plan.submitted,boot.plan.completed,boot.plan.phase,boot.io.wire.phase);(void)qca_stop();
 }
 if(native_scan.quiesce_requested&&actual_released()){
  if(!pipeline_error&&!native_scan.error&&qca_filter_passed(&filter)&&htt_query.phase==QCA_HTTN_READY){native_scan.phase=QCA_NATIVE_SCAN_RELEASED;pipeline_phase=4;}
  else pipeline_phase=5;
 }
}
