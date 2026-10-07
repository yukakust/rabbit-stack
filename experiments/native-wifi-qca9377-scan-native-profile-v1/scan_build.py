"""Offline provisional54 actual passive coordinator profile; no admission."""
import sys,json,importlib.util,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parent;E=ROOT.parent
PROFILE=E/'native-wifi-qca9377-persistent-profile-v1'
sys.path.insert(0,str(PROFILE));import profile_build as prior
one=prior.one;checked=prior.checked
MODULES={'coordinator':'native-wifi-qca9377-scan-coordinator-v1','tx':'native-wifi-qca9377-persistent-tx-v1','channel_wire':'native-wifi-qca9377-channel-wire-v1','vdev_wire':'native-wifi-qca9377-vdev-wire-v1','station_scan':'native-wifi-qca9377-station-scan-v1','dispatch':'native-wifi-qca9377-station-dispatch-v1','scan_stop':'native-wifi-qca9377-scan-stop-v1','owned_stop':'native-wifi-qca9377-owned-scan-stop-v1','beacon_rx':'native-wifi-qca9377-beacon-rx-v1'}
def policy():return json.loads((ROOT/'receiver-policy.json').read_text())
def statement_lines(text):
 # Whitespace-only portability fix for strict GCC's misleading-indentation
 # warning. Never split for headers, quoted strings/chars or comments.
 out=[];depth=0;quote=None;escaped=False;comment=None;i=0
 while i<len(text):
  c=text[i];nextchar=text[i+1] if i+1<len(text) else ''
  out.append(c)
  if comment=='line':
   if c=='\n':comment=None
  elif comment=='block':
   if c=='*' and nextchar=='/':out.append('/');i+=1;comment=None
  elif quote:
   if escaped:escaped=False
   elif c=='\\':escaped=True
   elif c==quote:quote=None
  elif c=='/' and nextchar in ('/','*'):out.append(nextchar);i+=1;comment='line' if nextchar=='/' else 'block'
  elif c in ('"',"'"):quote=c
  elif c=='(':depth+=1
  elif c==')':depth-=1
  elif c==';' and not depth:out.append('\n ')
  i+=1
 return ''.join(out)
def sources(d):
 prior.sources(d)
 for m,folder in MODULES.items():
  for ext in ('c','h'):(d/(m+'.'+ext)).write_bytes((E/folder/(m+'.'+ext)).read_bytes())
 for n in ('scan_native.c','scan_native.h','scan_policy.h','scan_gatt.c'):(d/n).write_bytes((ROOT/n).read_bytes())
 for n in ('beacon_info.c','beacon_info.h'):(d/n).write_bytes((checked.SESSION/n).read_bytes())
 for n in [m+'.c' for m in MODULES]+['scan_native.c','scan_gatt.c']:
  p=d/n;p.write_text(statement_lines(p.read_text()))
 p=d/'init_probe.c';s=p.read_text()
 s=one(s,'.generation=53ull','.generation=54ull')
 s=one(s,'#include "trial.h"','#include "trial.h"\n#include "scan_native.h"')
 s=one(s,'static QcaBoundedTrial trial;','static QcaBoundedTrial trial;\nstatic QcaNativeScan native_scan;')
 s=one(s,'static void qca_profile_step(uint64_t now){\n if(qca_trial_tick(&trial,qca_radio_accepts_work(&persistent.life),actual_released(),now))(void)qca_stop();\n}', '''static void qca_profile_step(uint64_t now){
 if(!native_scan.phase&&qca_radio_accepts_work(&persistent.life)){
  if(!qca_native_scan_begin(&native_scan,&persistent,now)){native_scan.quiesce_requested=1;(void)qca_stop();}
 }
 if(native_scan.phase&&!native_scan.quiesce_requested&&qca_native_scan_poll(&native_scan,now))(void)qca_stop();
 if(native_scan.quiesce_requested&&actual_released()&&!native_scan.error)native_scan.phase=QCA_NATIVE_SCAN_RELEASED;
}''')
 s=one(s,'p->stop_latched,53,0','p->stop_latched,54,0')
 s+='''
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
 c->stop.terminal_completion,c->ssid_seen,c->has_observation,c->has_orphan,c->dispatch.count,s->archive_count,
 r->phase,r->error,r->completed,r->posted_count,r->count,r->backpressure,
 operating.control.credit.available,operating.control.credit.outstanding,operating.control.credit.reserved,operating.control.credit.total,
 held,port.dma_users,port.claimed,wake.owned,link.owned,irq.owned,boot.owns_pin,adapter.bus.owned,adapter.access.count,
 adapter.phase,adapter.channels.cleanup_slot,persistent.life.phase,persistent.life.error,persistent.error,
 startup.transaction.ready_seen,startup.transaction.tx_complete,54,13,0,0};
 for(unsigned j=0;j<64;j++)for(unsigned k=0;k<4;k++)out[8+4*j+k]=(uint8_t)(f[j]>>(8*k));
 for(unsigned j=0;j<32;j++){out[264+j]=scan_policy.reviewed_digest[j];out[296+j]=scan_policy.ruleset_digest[j];out[328+j]=scan_policy.location_digest[j];}
 if(c->has_observation){const QcaBeaconInfo*b=&c->observation.parsed.bss;out[360]=(uint8_t)b->ssid_bytes;
  for(unsigned j=0;j<32;j++)out[364+j]=j<b->ssid_bytes?b->ssid[j]:0;
  for(unsigned j=0;j<6;j++)out[396+j]=b->bssid[j];
 }
}
'''
 s=one(s,'#include "scan_native.h"','#include "scan_native.h"\n#include "scan_policy.h"');p.write_text(s)
 p=d/'diagnostic_gatt.c';s=p.read_text()
 s=one(s,'size_t qca_profile_att(uint16_t,const uint8_t*,size_t,uint8_t*,size_t);','size_t qca_profile_att(uint16_t,const uint8_t*,size_t,uint8_t*,size_t);\nsize_t qca_scan_att(uint16_t,const uint8_t*,size_t,uint8_t*,size_t);')
 s=one(s,'if(s){size_t prof=qca_profile_att','if(s){size_t sc=qca_scan_att(s->mtu,p,n,r,capacity);if(sc!=SIZE_MAX)return sc;}\n if(s){size_t prof=qca_profile_att');p.write_text(s)
def compile_driver(d,crypto):
 # Reuse exact53 full codegen but substitute prepared54 sources and append new
 # compiler units at the same checked compile_efi boundary; no shared file edits.
 sources(d)
 saved=prior.sources;compile_saved=checked.prior.actors.compile_efi
 def compile_more(directory,name,files,**kwargs):
  extra=[d/(m+'.c') for m in MODULES]+[d/'beacon_info.c',d/'scan_native.c',d/'scan_gatt.c']
  existing={Path(p).name for p in files};return compile_saved(directory,name,files+[p for p in extra if p.name not in existing],**kwargs)
 try:
  prior.sources=lambda _d:None;checked.prior.actors.compile_efi=compile_more
  return prior.compile_driver(d,crypto)
 finally:prior.sources=saved;checked.prior.actors.compile_efi=compile_saved
