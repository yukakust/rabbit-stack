"""Unsigned62: frozen60 boot + frozen56 version-only components; no scan/RFdata."""
import importlib.util,json,hashlib,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parent;E=ROOT.parent;COMPONENTS=ROOT/'components';FULLBOOT=E/'native-wifi-qca9377-fullboot60-native-v1'
spec=importlib.util.spec_from_file_location('frozen_fullboot60_build',FULLBOOT/'fullboot_build.py');prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
base_sources=prior.sources;checked=prior.checked;BASE=prior.BASE;CHECKED=prior.CHECKED;one=prior.one
FILES=tuple(n for n in prior.FILES if n!='prefix_gatt.c')+tuple(n for n in json.loads((ROOT/'component-inputs.json').read_text())['components_sha256'] if n.endswith('.c') and n not in prior.FILES)
def policy():
 p=json.loads((ROOT/'receiver-policy.json').read_text())
 if p!=dict(prior.policy(),generation=62):raise ValueError('exact60 public policy with provisional62 required')
 return p
def sources(d):
 base_sources(d)
 for n,h in json.loads((ROOT/'component-inputs.json').read_text())['components_sha256'].items():
  p=COMPONENTS/n
  if hashlib.sha256(p.read_bytes()).hexdigest()!=h:raise ValueError('frozen HTT component '+n)
  if n.endswith(('.c','.h')):(d/n).write_bytes(p.read_bytes())
 p=d/'init_probe.c';s=p.read_text();s=one(s,'.generation=60ull','.generation=62ull');s=one(s,'f[58]={60,','f[58]={62,')
 s=one(s,'#include "prefix.h"','#include "prefix.h"\n#include "persistent.h"\n#include "htt_native.h"\n#include "firmware_op.h"')
 s=one(s,'static QcaPrefix prefix;','static QcaPrefix prefix;\nstatic QcaPersistentNative persistent;\nstatic QcaHttNative htt_query;static QcaHttFirmwareProof htt_proof;static unsigned htt_attempted;static QcaRxEvent htt_export_scratch;')
 s=one(s,'else rc=qca_wmi_startup_poll(&startup,now);','''else rc=qca_wmi_startup_poll(&startup,now);
         if(rc==1){
          if(!persistent.life.phase)rc=qca_persistent_begin(&persistent,&startup,1,now);
          else rc=qca_persistent_poll(&persistent,now);
          if(rc==1)rc=0; /* Adopt before60 diagnostic teardown. */
         }''')
 s=one(s,'else if(rc<0&&startup.phase==1)(void)qca_wmi_startup_poll(&startup,now);','''else if(rc<0&&startup.phase==1)(void)qca_wmi_startup_poll(&startup,now);
        if(rc<0&&persistent.life.phase)(void)qca_persistent_poll(&persistent,now);''')
 s=one(s,'int qca_stop(void){','int qca_stop(void){\n (void)qca_persistent_quiesce(&persistent,last_now);')
 s=one(s,'void qca_poll(uint64_t ms){','static void qca_htt_profile_step(uint64_t);\nvoid qca_poll(uint64_t ms){')
 s=one(s,' qca_hardware_poll(ms);',' qca_hardware_poll(ms);\n qca_htt_profile_step(ms*1000);')
 s=one(s,'if(ram_closing){if(boot_round&&qca_boot_native_close(&boot))return;(void)qca_fwp_close(&ram);return;}','''if(ram_closing){
  if(boot_round&&qca_boot_native_close(&boot)){(void)qca_persistent_poll(&persistent,ms*1000);return;}
  (void)qca_persistent_poll(&persistent,ms*1000);(void)qca_fwp_close(&ram);return;
 }''')
 s=one(s,'if(qca_init_adapter_released(&adapter)&&!port.claimed)(void)qca_boot_native_close(&boot);','''if(qca_init_adapter_released(&adapter)&&!port.claimed)(void)qca_boot_native_close(&boot);
  if(persistent.life.phase&&persistent.life.phase!=QCA_RADIO_ACTIVE)(void)qca_persistent_poll(&persistent,ms*1000);''')
 s+='\nconst QcaPersistentNative*qca_persistent_view(void){return &persistent;}\n'+(COMPONENTS/'htt_profile.inc').read_text()
 start=s.index(' return persistent.life.phase&&',s.index('static unsigned htt_actual_released'));end=s.index('\n}',start)
 s=s[:start]+' return persistent.life.phase==QCA_RADIO_CLOSED&&prefix_released();'+s[end:]
 p.write_text(s)
 p=d/'prefix.c';p.write_text(one(p.read_text(),'v[14]={60,','v[14]={62,'))
 p=d/'overlay.h';p.write_text(one(p.read_text(),'FULLBOOT 60 FRAME ','HTT 62 FRAME '))
 p=d/'diagnostic_gatt.c';s=p.read_text();s=s.replace('qca_prefix_att','qca_htt_profile_att');p.write_text(s)
def driver_sources(d):
 saved=prior.sources
 try:prior.sources=sources;prior.driver_sources(d)
 finally:prior.sources=saved
def compile_driver(d,crypto):
 driver_sources(d);a=checked.prior.actors
 payload=a.compile_efi(d,'htt-version62',[d/'driver.c',d/'city_core.c',d/'pci_collect.c',d/'pci_identity.c',*[d/n for n in FILES],d/'usb_port.c',d/'bt_event_stream.c',d/'ble_recovery_link.c',d/'diagnostic_gatt.c',a.LINK/'file_core.c',a.NATIVE/'sha256.c',*crypto],driver=True,definitions=('SCENE_REVISION=1','QCA_CONFIG_SETUP=1','QCA_FC_BASE=13'))
 off=struct.unpack_from('<I',payload,60)[0]
 if len(payload)>262144 or struct.unpack_from('<I',payload,off+80)[0]>4194304:raise ValueError('immutable file/mapped cap')
 return payload
