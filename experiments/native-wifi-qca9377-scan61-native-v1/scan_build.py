"""Unsigned GEN61: frozen60 boot + frozen55 corrected passive scan components."""
import importlib.util,json,hashlib,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parent;E=ROOT.parent;COMPONENTS=ROOT/'components';FULLBOOT=E/'native-wifi-qca9377-fullboot60-native-v1'
spec=importlib.util.spec_from_file_location('frozen_fullboot60_build',FULLBOOT/'fullboot_build.py');prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
base_sources=prior.sources
checked=prior.checked;BASE=prior.BASE;CHECKED=prior.CHECKED;one=prior.one
FILES=tuple(n for n in prior.FILES if n!='prefix_gatt.c')+tuple(n for n in json.loads((ROOT/'component-inputs.json').read_text())['components_sha256'] if n.endswith('.c') and n not in prior.FILES)
def component_bytes(name):
 b=(COMPONENTS/name).read_bytes()
 if name=='scan_gatt.c':
  text=b.decode();text=one(text,'if(h<32)return SIZE_MAX;','''if(h>=29&&h<32&&(op==0x10||op==8||op==4)){
  if(n!=(op==4?5u:7u))return error(out,op,h,4);
  if(h>half(p+3))return error(out,op,h,1);
  if(half(p+3)<32)return error(out,op,h,10);
  h=32; /* Explicit29..31 hole: next service/info is32, declaration33. */
 }
 if(h<32)return SIZE_MAX;''');b=text.encode()
 return b
def policy():
 p=json.loads((ROOT/'receiver-policy.json').read_text())
 if p!=dict(prior.policy(),generation=61):raise ValueError('exact60 public policy with61 required')
 return p
def sources(d):
 base_sources(d) # Only frozen60 bootstrap; NEVER55.sources over61.
 manifest=json.loads((ROOT/'component-inputs.json').read_text())
 for n,h in manifest['components_sha256'].items():
  p=COMPONENTS/n
  if hashlib.sha256(p.read_bytes()).hexdigest()!=h:raise ValueError('frozen scan component '+n)
  if n.endswith(('.c','.h')):(d/n).write_bytes(component_bytes(n))
 p=d/'init_probe.c';s=p.read_text();s=one(s,'.generation=60ull','.generation=61ull');s=one(s,'f[58]={60,','f[58]={61,')
 s=one(s,'#include "prefix.h"','#include "prefix.h"\n#include "persistent.h"\n#include "scan_native.h"\n#include "scan_policy.h"')
 s=one(s,'static QcaPrefix prefix;','static QcaPrefix prefix;\nstatic QcaPersistentNative persistent;\nstatic QcaNativeScan native_scan;')
 s=one(s,'else rc=qca_wmi_startup_poll(&startup,now);','''else rc=qca_wmi_startup_poll(&startup,now);
         if(rc==1){
          if(!persistent.life.phase)rc=qca_persistent_begin(&persistent,&startup,1,now);
          else rc=qca_persistent_poll(&persistent,now);
          if(rc==1)rc=0; /* Adopt before60 success teardown. */
         }''')
 s=one(s,'else if(rc<0&&startup.phase==1)(void)qca_wmi_startup_poll(&startup,now);','''else if(rc<0&&startup.phase==1)(void)qca_wmi_startup_poll(&startup,now);
        if(rc<0&&persistent.life.phase)(void)qca_persistent_poll(&persistent,now);''')
 s=one(s,'int qca_stop(void){','int qca_stop(void){\n (void)qca_persistent_quiesce(&persistent,last_now);')
 s=one(s,'void qca_poll(uint64_t ms){','static void qca_profile_step(uint64_t);\nvoid qca_poll(uint64_t ms){')
 s=one(s,' qca_hardware_poll(ms);',' qca_hardware_poll(ms);\n qca_profile_step(ms*1000);')
 s=one(s,'if(ram_closing){if(boot_round&&qca_boot_native_close(&boot))return;(void)qca_fwp_close(&ram);return;}','''if(ram_closing){
  if(boot_round&&qca_boot_native_close(&boot)){
   (void)qca_persistent_poll(&persistent,ms*1000);return;
  }
  (void)qca_persistent_poll(&persistent,ms*1000);
  (void)qca_fwp_close(&ram);return;
 }''')
 s=one(s,'if(qca_init_adapter_released(&adapter)&&!port.claimed)(void)qca_boot_native_close(&boot);','''if(qca_init_adapter_released(&adapter)&&!port.claimed)(void)qca_boot_native_close(&boot);
  if(persistent.life.phase&&persistent.life.phase!=QCA_RADIO_ACTIVE)(void)qca_persistent_poll(&persistent,ms*1000);''')
 s+='''
const QcaPersistentNative*qca_persistent_view(void){return &persistent;}
static unsigned actual_released(void){return persistent.life.phase==QCA_RADIO_CLOSED&&prefix_released();}
static void qca_profile_step(uint64_t now){
 if(!native_scan.phase&&qca_radio_accepts_work(&persistent.life)){
  if(!qca_native_scan_begin(&native_scan,&persistent,now)){
   native_scan.quiesce_requested=1;qca_prefix_request(&prefix,3,boot.plan.offset,boot.plan.submitted,boot.plan.completed,boot.plan.phase,boot.io.wire.phase);(void)qca_stop();
  }
 }
 if(native_scan.phase&&!native_scan.quiesce_requested&&qca_native_scan_poll(&native_scan,now)){
  qca_prefix_request(&prefix,native_scan.error?3:0,boot.plan.offset,boot.plan.submitted,boot.plan.completed,boot.plan.phase,boot.io.wire.phase);(void)qca_stop();
 }
 if(native_scan.quiesce_requested&&actual_released()&&!native_scan.error)native_scan.phase=QCA_NATIVE_SCAN_RELEASED;
}
'''+(COMPONENTS/'scan_status.inc').read_text()
 p.write_text(s)
 p=d/'prefix.c';s=p.read_text();s=one(s,'v[14]={60,','v[14]={61,');p.write_text(s)
 p=d/'overlay.h';s=p.read_text();s=one(s,'FULLBOOT 60 FRAME ','PASSIVE 61 FRAME ');p.write_text(s)
 p=d/'diagnostic_gatt.c';s=p.read_text()
 s=one(s,'size_t qca_prefix_att(uint16_t,const uint8_t*,size_t,uint8_t*,size_t);','size_t qca_scan_att(uint16_t,const uint8_t*,size_t,uint8_t*,size_t);')
 s=one(s,'size_t diag=qca_prefix_att(s->mtu,p,n,r,capacity)','size_t diag=qca_scan_att(s->mtu,p,n,r,capacity)');p.write_text(s)
def driver_sources(d):
 # Reuse60 driver generation verbatim, then replace only61 target modules.
 saved=prior.sources
 try:
  prior.sources=sources;prior.driver_sources(d)
 finally:prior.sources=saved
def compile_driver(d,crypto):
 driver_sources(d);a=checked.prior.actors
 payload=a.compile_efi(d,'passive-scan61',[d/'driver.c',d/'city_core.c',d/'pci_collect.c',d/'pci_identity.c',*[d/n for n in FILES],d/'usb_port.c',d/'bt_event_stream.c',d/'ble_recovery_link.c',d/'diagnostic_gatt.c',a.LINK/'file_core.c',a.NATIVE/'sha256.c',*crypto],driver=True,definitions=('SCENE_REVISION=1','QCA_CONFIG_SETUP=1','QCA_FC_BASE=13'))
 off=struct.unpack_from('<I',payload,60)[0]
 if len(payload)>262144 or struct.unpack_from('<I',payload,off+80)[0]>4194304:raise ValueError('whole file/mapped immutable cap')
 return payload
