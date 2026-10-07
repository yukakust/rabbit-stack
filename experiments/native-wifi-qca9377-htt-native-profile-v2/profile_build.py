"""Unsigned provisional56: production version-only loop, authenticated IE6."""
import importlib.util,sys,struct,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent;NATIVE=ROOT.parent/'native-wifi-qca9377-htt-native-v1';PRIOR=ROOT.parent/'native-wifi-qca9377-persistent-profile-v1';SCAN=ROOT.parent/'native-wifi-qca9377-scan-native-profile-v1'
sys.path.insert(0,str(NATIVE));import htt_build as native
checked=native.prior.checked;one=native.one
spec=importlib.util.spec_from_file_location('checked_profile53',PRIOR/'profile_build.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
spec=importlib.util.spec_from_file_location('checked_normalizer',SCAN/'scan_build.py');normal=importlib.util.module_from_spec(spec);spec.loader.exec_module(normal)
def policy():
 d=json.loads((ROOT/'receiver-policy.json').read_text())
 if d!={**native.prior.checked.policy(),'generation':56}:raise ValueError('exact inherited owner/target/firmware plus provisional56 required')
 expected='#ifndef QCA_HTT_AUTHENTICATED_POLICY_H\n#define QCA_HTT_AUTHENTICATED_POLICY_H\n#include <stdint.h>\nstatic const uint8_t qca_htt_container_digest[32]={'+','.join(str(n) for n in bytes.fromhex(d['digest']))+'};\n#endif\n'
 if (ROOT/'firmware_policy.h').read_text()!=expected:raise ValueError('compiled firmware digest binding differs')
 return d
def sources(d):
 native.sources(d)
 for n in ('firmware_op.c','firmware_op.h','firmware_policy.h','profile_gatt.c'):(d/n).write_bytes((ROOT/n).read_bytes())
 for name in ('htt_native.c','version.c','firmware_op.c','profile_gatt.c','rx.c'):
  p=d/name;p.write_text(normal.statement_lines(p.read_text()))
 p=d/'init_probe.c';s=p.read_text();s=one(s,'.generation=52ull','.generation=56ull')
 s=one(s,'#include "persistent.h"','#include "persistent.h"\n#include "htt_native.h"\n#include "firmware_op.h"')
 s=one(s,'static QcaPersistentNative persistent;','static QcaPersistentNative persistent;\nstatic QcaHttNative htt_query;static QcaHttFirmwareProof htt_proof;static unsigned htt_attempted;static QcaRxEvent htt_export_scratch;')
 s=one(s,' qca_hardware_poll(ms);',' qca_hardware_poll(ms);\n qca_htt_profile_step(ms*1000);')
 s=one(s,'void qca_poll(uint64_t ms){','static void qca_htt_profile_step(uint64_t);\nvoid qca_poll(uint64_t ms){')
 s+='''
static unsigned htt_actual_released(void){
 return persistent.life.phase&&qca_init_adapter_released(&adapter)&&!port.claimed&&!port.dma_users
 &&!adapter.access.count&&!boot.owns_pin&&!ram.asset.pinned&&!irq.owned&&!link.owned&&!wake.owned;
}
static void qca_htt_profile_step(uint64_t now){
 if(!htt_attempted&&qca_radio_accepts_work(&persistent.life)){
  htt_attempted=1;
  if(!qca_htt_firmware_proof(&htt_proof,&boot)||!qca_htt_native_begin(&htt_query,&persistent,htt_proof.htt_op,now)){
   if(!htt_query.error)htt_query.error=30;
   htt_query.phase=QCA_HTTN_FAULT;htt_query.stop_requested=1;
   (void)qca_persistent_quiesce(&persistent,now);(void)qca_stop();
  }
 }
 if(htt_query.phase&&(!htt_query.stop_requested||htt_actual_released()))(void)qca_htt_native_poll(&htt_query,now);
}
const QcaHttNative*qca_htt_native_view(void){return &htt_query;}
const QcaHttFirmwareProof*qca_htt_firmware_view(void){return &htt_proof;}
void qca_htt_status(uint8_t out[320]){
 for(unsigned j=0;j<320;j++)out[j]=0;
 const uint8_t magic[8]={'Q','H','T','T','0','0','0','1'};for(unsigned j=0;j<8;j++)out[j]=magic[j];
 uint32_t held=0;for(unsigned j=0;j<14;j++)if(adapter.channels.buffers[j].allocated||adapter.channels.buffers[j].mapped||adapter.channels.buffers[j].allocation_uncertain)held++;
 const QcaHttNative*s=&htt_query;const QcaPersistentRx*r=&persistent.rx;
 uint32_t f[56]={s->phase,s->error,s->stop_requested,htt_attempted,htt_actual_released(),
 s->attempted,s->dma_completed,s->version_seen,s->version.major,s->version.minor,s->binding.endpoint,s->binding.max_bytes,s->binding.op_version,
 s->watermark,s->consumed,s->archive_count,htt_proof.valid,htt_proof.error,htt_proof.htt_op,htt_proof.wmi_op,htt_proof.htt_offset,htt_proof.main_offset,htt_proof.main_bytes,
 (uint32_t)htt_proof.generation,(uint32_t)(htt_proof.generation>>32),r->phase,r->error,r->completed,r->posted_count,r->count,r->backpressure,
 operating.control.credit.available,operating.control.credit.outstanding,operating.control.credit.reserved,operating.control.credit.total,
 held,port.dma_users,port.claimed,wake.owned,link.owned,irq.owned,boot.owns_pin,adapter.bus.owned,adapter.access.count,
 adapter.phase,adapter.channels.cleanup_slot,persistent.life.phase,persistent.life.error,persistent.error,persistent.polls,
 startup.transaction.ready_seen,startup.transaction.tx_complete,(uint32_t)s->epoch,(uint32_t)(s->epoch>>32),56,persistent.stop_latched};
 for(unsigned j=0;j<56;j++)for(unsigned k=0;k<4;k++)out[8+4*j+k]=(uint8_t)(f[j]>>(8*k));
 for(unsigned j=0;j<32;j++){out[232+j]=htt_proof.digest[j];out[264+j]=htt_proof.main_digest[j];}
}
unsigned qca_htt_profile_export(unsigned page,uint8_t*out,unsigned cap){
 if(!out||cap<512||page>=30)return 0;
 unsigned slot=page/5,offset=(page%5)*512,length=2104-offset;if(length>512)length=512;
 unsigned present=qca_htt_native_export(&htt_query,slot,&htt_export_scratch,sizeof(htt_export_scratch));
 const QcaRxEvent*e=&htt_export_scratch;
 uint32_t f[12]={slot,present,present&&slot!=5,present?e->completion:0,(uint32_t)htt_query.epoch,(uint32_t)(htt_query.epoch>>32),
 present?e->endpoint:0,present?e->pipe:0,present?e->bytes:0,present?e->raw_bytes:0,present?e->event:0,slot==5?persistent.rx.error:0};
 const uint8_t magic[8]={'Q','H','T','X','0','0','0','1'};
 for(unsigned j=0;j<length;j++){
  unsigned at=offset+j;uint8_t v=0;
  if(at<8)v=magic[at];else if(at<56)v=(uint8_t)(f[(at-8)/4]>>(8*((at-8)&3)));
  else if(present&&at-56<e->raw_bytes)v=e->raw[at-56];out[j]=v;
 }
 return length;
}
'''
 p.write_text(normal.statement_lines(s))
 p=d/'diagnostic_gatt.c';s=p.read_text();s=one(s,'size_t qca_wmi_att(uint16_t,const uint8_t*,size_t,uint8_t*,size_t);','size_t qca_wmi_att(uint16_t,const uint8_t*,size_t,uint8_t*,size_t);\nsize_t qca_htt_profile_att(uint16_t,const uint8_t*,size_t,uint8_t*,size_t);')
 s=one(s,'if(s){size_t init=qca_wmi_att','if(s){size_t hp=qca_htt_profile_att(s->mtu,p,n,r,capacity);if(hp!=SIZE_MAX)return hp;}\n if(s){size_t init=qca_wmi_att');p.write_text(s)
def compile_driver(d,crypto):
 sources(d)
 saved=old.sources;compiler=checked.prior.actors.compile_efi
 def compile_more(directory,name,files,**kwargs):
  # Existing53 compile list's trial/profile modules are irrelevant here.
  files=[p for p in files if Path(p).name not in ('trial.c','profile_gatt.c')]
  extra=[d/n for n in ('htt_native.c','version.c','firmware_op.c','profile_gatt.c')]
  return compiler(directory,'htt-native-profile',files+extra,**kwargs)
 try:
  old.sources=lambda _:None;checked.prior.actors.compile_efi=compile_more
  return old.compile_driver(d,crypto)
 finally:old.sources=saved;checked.prior.actors.compile_efi=compiler
