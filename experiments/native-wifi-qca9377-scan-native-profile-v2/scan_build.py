"""Private GEN55 derivative: one checked prefix codec, archive16,110pages."""
import importlib.util,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent;E=ROOT.parent;PREVIOUS=E/'native-wifi-qca9377-scan-native-profile-v1';EVENT=E/'native-wifi-qca9377-scan-event-v2'
spec=importlib.util.spec_from_file_location('frozen_scan54_build',PREVIOUS/'scan_build.py');prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
one=prior.one;checked=prior.checked;PROFILE=prior.PROFILE;MODULES=prior.MODULES
statement_lines=prior.statement_lines
def policy():
 d=json.loads((ROOT/'receiver-policy.json').read_text())
 if d!={**prior.policy(),'generation':55}:raise ValueError('exact54 public target/owner/firmware +55 required')
 return d
def sources(d):
 prior.sources(d)
 (d/'scan_policy.h').write_bytes((ROOT/'scan_policy.h').read_bytes())
 for name in ['scan_event_v2.c','scan_event_v2.h']:(d/name).write_bytes((EVENT/name).read_bytes())
 p=d/'wmi_scan.c';s=p.read_text();start=s.index('int qca_wmi_scan_event(');end=s.index('static int frequency(',start)
 s=s[:start]+'''int qca_wmi_scan_event(const uint8_t*p,unsigned n,unsigned scan,unsigned request,QcaWmiScanEvent*out){return qca_scan_event_v2_match(p,n,scan,request,out);}
'''+s[end:];s=one(s,'static uint32_t le32(const uint8_t*p){return le16(p)|((uint32_t)le16(p+2)<<16);}\n','')
 s=one(s,'#include "wmi_scan.h"','#include "wmi_scan.h"\n#include "scan_event_v2.h"');p.write_text(s)
 p=d/'dispatch.c';s=p.read_text();start=s.index('static int scan_event(');end=s.index('int qca_station_dispatch_head(',start)
 s=s[:start]+'''static int scan_event(const QcaRxEvent*e,QcaWmiScanEvent*out){return qca_scan_event_v2(e->payload,e->bytes,out);}
'''+s[end:];s=s.replace('if(started||v.reason)','if(started)');s=one(s,'#include "dispatch.h"','#include "dispatch.h"\n#include "scan_event_v2.h"');p.write_text(s)
 p=d/'station_scan.c';s=p.read_text();s=one(s,'if(started||event.reason)','if(started)');p.write_text(s)
 p=d/'coordinator.c';s=p.read_text();s=one(s,'if(s->has_observation)return 0;','if(s->has_observation||!qca_beacon_ssid_matches(&b.bss,s->ssid,s->ssid_bytes))return 0;');p.write_text(statement_lines(s))
 p=d/'scan_native.h';s=p.read_text();s=one(s,'archive[2]','archive[16]');s=s.replace('8 retained slots ×5 pages.','22 retained slots ×5 pages.');p.write_text(s)
 p=d/'scan_native.c';s=p.read_text();s=one(s,'#include "scan_policy.h"','#include "scan_policy.h"\n#include "scan_event_v2.h"');s=s.replace('archive_count==2','archive_count==16')
 s=s.replace('t.bytes==24','t.bytes>=24')
 s=one(s,'(rc==QCA_BEACON_RX_ACCEPTED&&b.frequency_mhz!=c->live_frequency)', '(rc==QCA_BEACON_RX_ACCEPTED&&(b.frequency_mhz!=c->live_frequency||c->has_observation||!qca_beacon_ssid_matches(&b.bss,c->ssid,c->ssid_bytes)))')
 # Explicitly own structurally valid future unknown TLVs rather than blocking
 # every later matching event behind an unhandled payload at dispatcher head.
 needle='unmatched=scan&&request&&qca_wmi_scan_event(e->payload,e->bytes,scan,request,&parsed);'
 s=one(s,needle,needle+'\n if(qca_scan_event_v2(e->payload,e->bytes,&parsed)==2)unmatched=1;')
 s=one(s,'(void)archive_head(s);','for(unsigned j=0;j<2;j++){if(!archive_head(s))break;}')
 s=one(s,'s->scan.ssid_seen||s->archive_count==16||s->radio->rx.backpressure','s->scan.ssid_seen||s->archive_count==16')
 start=s.index('static const QcaRxEvent*event(');end=s.index('unsigned qca_native_scan_export(',start)
 s=s[:start]+'''static const QcaRxEvent*event(const QcaNativeScan*s,unsigned slot){
 if(!s||!s->phase)return 0;
 if(slot<16)return slot<s->archive_count?&s->archive[slot]:0;
 if(slot==16)return s->scan.has_observation?&s->scan.observation.raw:0;
 if(slot==17)return s->scan.has_orphan?&s->scan.orphan:0;
 if(slot<20){unsigned n=slot-18;return n<s->scan.dispatch.count?&s->scan.dispatch.owned[(s->scan.dispatch.head+n)&1]:0;}
 if(slot<22&&s->radio){unsigned n=slot-20;return n<s->radio->rx.count?&s->radio->rx.events[(s->radio->rx.head+n)&1]:0;}
 return 0;
}
'''+s[end:];s=s.replace('page>=40','page>=110');p.write_text(statement_lines(s))
 p=d/'scan_gatt.c';s=p.read_text();s=s.replace('115','255').replace('114','254').replace('0x40+','0x80+');p.write_text(s)
 p=d/'init_probe.c';s=p.read_text();s=one(s,'.generation=54ull','.generation=55ull');s=one(s,'p->stop_latched,54,0','p->stop_latched,55,0');s=one(s,'startup.transaction.tx_complete,54,13','startup.transaction.tx_complete,55,13');p.write_text(s)
 for name in ('dispatch.c','station_scan.c','scan_event_v2.c','scan_gatt.c'):
  p=d/name;p.write_text(statement_lines(p.read_text()))
def compile_driver(d,crypto):
 sources(d);saved=prior.sources;compiler=checked.prior.actors.compile_efi
 def extra(directory,name,files,**kwargs):return compiler(directory,'scan-native-v2',files+[d/'scan_event_v2.c'],**kwargs)
 try:
  prior.sources=lambda _:None;checked.prior.actors.compile_efi=extra
  return prior.compile_driver(d,crypto)
 finally:prior.sources=saved;checked.prior.actors.compile_efi=compiler
