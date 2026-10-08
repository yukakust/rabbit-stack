static unsigned htt_actual_released(void){
 return persistent.life.phase&&qca_init_adapter_released(&adapter)&&!port.claimed&&!port.dma_users
 &&!adapter.access.count&&!boot.owns_pin&&!ram.asset.pinned&&!irq.owned&&!link.owned&&!wake.owned;
 
}
static void qca_htt_profile_step(uint64_t now){
 if(!htt_attempted&&qca_radio_accepts_work(&persistent.life)){
  htt_attempted=1;
 
  if(!qca_htt_firmware_proof(&htt_proof,&boot)||!qca_htt_native_begin(&htt_query,&persistent,htt_proof.htt_op,now)){
   if(!htt_query.error)htt_query.error=30;
 
   htt_query.phase=QCA_HTTN_FAULT;
 htt_query.stop_requested=1;
 
   (void)qca_persistent_quiesce(&persistent,now);
 (void)qca_stop();
 
  }
 }
 if(htt_query.phase&&(!htt_query.stop_requested||htt_actual_released()))(void)qca_htt_native_poll(&htt_query,now);
 
}
const QcaHttNative*qca_htt_native_view(void){return &htt_query;
 }
const QcaHttFirmwareProof*qca_htt_firmware_view(void){return &htt_proof;
 }
void qca_htt_status(uint8_t out[320]){
 for(unsigned j=0;j<320;j++)out[j]=0;
 
 const uint8_t magic[8]={'Q','H','T','T','0','0','0','1'};
 for(unsigned j=0;j<8;j++)out[j]=magic[j];
 
 uint32_t held=0;
 for(unsigned j=0;j<14;j++)if(adapter.channels.buffers[j].allocated||adapter.channels.buffers[j].mapped||adapter.channels.buffers[j].allocation_uncertain)held++;
 
 const QcaHttNative*s=&htt_query;
 const QcaPersistentRx*r=&persistent.rx;
 
 uint32_t f[56]={s->phase,s->error,s->stop_requested,htt_attempted,htt_actual_released(),
 s->attempted,s->dma_completed,s->version_seen,s->version.major,s->version.minor,s->binding.endpoint,s->binding.max_bytes,s->binding.op_version,
 s->watermark,s->consumed,s->archive_count,htt_proof.valid,htt_proof.error,htt_proof.htt_op,htt_proof.wmi_op,htt_proof.htt_offset,htt_proof.main_offset,htt_proof.main_bytes,
 (uint32_t)htt_proof.generation,(uint32_t)(htt_proof.generation>>32),r->phase,r->error,r->completed,r->posted_count,r->count,r->backpressure,
 operating.control.credit.available,operating.control.credit.outstanding,operating.control.credit.reserved,operating.control.credit.total,
 held,port.dma_users,port.claimed,wake.owned,link.owned,irq.owned,boot.owns_pin,adapter.bus.owned,adapter.access.count,
 adapter.phase,adapter.channels.cleanup_slot,persistent.life.phase,persistent.life.error,persistent.error,persistent.polls,
 startup.transaction.ready_seen,startup.transaction.tx_complete,(uint32_t)s->epoch,(uint32_t)(s->epoch>>32),62,persistent.stop_latched};
 
 for(unsigned j=0;j<56;j++)for(unsigned k=0;k<4;k++)out[8+4*j+k]=(uint8_t)(f[j]>>(8*k));
 
 for(unsigned j=0;j<32;j++){out[232+j]=htt_proof.digest[j];
 out[264+j]=htt_proof.main_digest[j];
 }
}
unsigned qca_htt_profile_export(unsigned page,uint8_t*out,unsigned cap){
 if(!out||cap<512||page>=30)return 0;
 
 unsigned slot=page/5,offset=(page%5)*512,length=2104-offset;
 if(length>512)length=512;
 
 unsigned present=qca_htt_native_export(&htt_query,slot,&htt_export_scratch,sizeof(htt_export_scratch));
 
 const QcaRxEvent*e=&htt_export_scratch;
 
 uint32_t f[12]={slot,present,present&&slot!=5,present?e->completion:0,(uint32_t)htt_query.epoch,(uint32_t)(htt_query.epoch>>32),
 present?e->endpoint:0,present?e->pipe:0,present?e->bytes:0,present?e->raw_bytes:0,present?e->event:0,slot==5?persistent.rx.error:0};
 
 const uint8_t magic[8]={'Q','H','T','X','0','0','0','1'};
 
 for(unsigned j=0;j<length;j++){
  unsigned at=offset+j;
 uint8_t v=0;
 
  if(at<8)v=magic[at];
 else if(at<56)v=(uint8_t)(f[(at-8)/4]>>(8*((at-8)&3)));
 
  else if(present&&at-56<e->raw_bytes)v=e->raw[at-56];
 out[j]=v;
 
 }
 return length;
 
}
