"""Unsigned provisional63 partial filter/version/passive experiment, no device/key."""
from pathlib import Path
import importlib.util,json,hashlib,struct
ROOT=Path(__file__).resolve().parent;E=ROOT.parent;COMPONENTS=ROOT/'components';FULLBOOT=E/'native-wifi-qca9377-fullboot60-native-v1'
spec=importlib.util.spec_from_file_location('filter63_frozen_fullboot60',FULLBOOT/'fullboot_build.py');prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
base_sources=prior.sources;checked=prior.checked;BASE=prior.BASE;CHECKED=prior.CHECKED;one=prior.one
SKIP={'prefix_gatt.c','profile_gatt.c'}
FILES=tuple(n for n in prior.FILES if n not in SKIP)+tuple(n for n in json.loads((ROOT/'component-inputs.json').read_text())['components_sha256'] if n.endswith('.c') and n not in prior.FILES and n not in SKIP)
def policy():
 p=json.loads((ROOT/'receiver-policy.json').read_text())
 if p!=dict(prior.policy(),generation=63):raise ValueError('exact authenticated policy, provisional63')
 return p
def sources(d):
 base_sources(d)
 m=json.loads((ROOT/'component-inputs.json').read_text())
 for n,h in m['components_sha256'].items():
  p=COMPONENTS/n
  if hashlib.sha256(p.read_bytes()).hexdigest()!=h:raise ValueError('component changed '+n)
  if n.endswith(('.c','.h')):(d/n).write_bytes(p.read_bytes())
 # Preserve exact frozen component bytes inside a diagnostic-only wrapper.
 # GCC's indentation heuristic disagrees with the component's validated style;
 # all other warning classes remain errors. No production token changes.
 p=d/'filter_barrier.c';raw=p.read_bytes()
 p.write_bytes(b'#pragma GCC diagnostic push\n#pragma GCC diagnostic ignored "-Wmisleading-indentation"\n'+raw+b'\n#pragma GCC diagnostic pop\n')
 p=d/'startup.h';p.write_text(one(p.read_text(),'frame_bytes,prefix_bytes,','ready_frame_bytes,frame_bytes,prefix_bytes,'))
 p=d/'startup.c';t=p.read_text()
 t=one(t,'for(unsigned j=0;j<128;j++)s->prefix[j]=j<n?p[j]:0;','if(!s->transaction.ready_seen)for(unsigned j=0;j<128;j++)s->prefix[j]=j<n?p[j]:0;')
 t=one(t,'s->rx_count++;return 0;','if(s->transaction.ready_seen&&!s->ready_frame_bytes)s->ready_frame_bytes=n;\n s->rx_count++;return 0;')
 p.write_text(t)
 p=d/'init_probe.c';s=p.read_text();s=one(s,'.generation=60ull','.generation=63ull');s=one(s,'f[58]={60,','f[58]={63,')
 s=one(s,'#include "prefix.h"','#include "prefix.h"\n#include "persistent.h"\n#include "htt_native.h"\n#include "firmware_op.h"\n#include "scan_native.h"\n#include "scan_policy.h"\n#include "filter_barrier.h"\n#include "query_handover.h"')
 s=one(s,'static QcaPrefix prefix;','static QcaPrefix prefix;\nstatic QcaPersistentNative persistent;\nstatic QcaHttNative htt_query;static QcaHttFirmwareProof htt_proof;static unsigned htt_attempted;\nstatic QcaNativeScan native_scan;')
 s=one(s,'else rc=qca_wmi_startup_poll(&startup,now);','''else rc=qca_wmi_startup_poll(&startup,now);
         if(rc==1){if(!persistent.life.phase)rc=qca_persistent_begin(&persistent,&startup,1,now);else rc=qca_persistent_poll(&persistent,now);if(rc==1)rc=0;}''')
 s=one(s,'else if(rc<0&&startup.phase==1)(void)qca_wmi_startup_poll(&startup,now);','''else if(rc<0&&startup.phase==1)(void)qca_wmi_startup_poll(&startup,now);
        if(rc<0&&persistent.life.phase)(void)qca_persistent_poll(&persistent,now);''')
 s=one(s,'int qca_stop(void){','int qca_stop(void){\n (void)qca_persistent_quiesce(&persistent,last_now);')
 s=one(s,'void qca_poll(uint64_t ms){','static void qca_filter63_step(uint64_t);\nvoid qca_poll(uint64_t ms){')
 s=one(s,' qca_hardware_poll(ms);',' qca_hardware_poll(ms);\n qca_filter63_step(ms*1000);')
 s=one(s,'if(ram_closing){if(boot_round&&qca_boot_native_close(&boot))return;(void)qca_fwp_close(&ram);return;}','''if(ram_closing){if(boot_round&&qca_boot_native_close(&boot)){(void)qca_persistent_poll(&persistent,ms*1000);return;}(void)qca_persistent_poll(&persistent,ms*1000);(void)qca_fwp_close(&ram);return;}''')
 s=one(s,'if(qca_init_adapter_released(&adapter)&&!port.claimed)(void)qca_boot_native_close(&boot);','''if(qca_init_adapter_released(&adapter)&&!port.claimed)(void)qca_boot_native_close(&boot);
  if(persistent.life.phase&&persistent.life.phase!=QCA_RADIO_ACTIVE)(void)qca_persistent_poll(&persistent,ms*1000);''')
 s+='\nconst QcaPersistentNative*qca_persistent_view(void){return &persistent;}\n'+(COMPONENTS/'pipeline.inc').read_text()+'\n'+(COMPONENTS/'scan_status.inc').read_text()+'\n'+(COMPONENTS/'pipeline_status.inc').read_text();p.write_text(s)
 p=d/'prefix.c';p.write_text(one(p.read_text(),'v[14]={60,','v[14]={63,'));p=d/'overlay.h';p.write_text(one(p.read_text(),'FULLBOOT 60 FRAME ','FILTER 63 FRAME '))
 p=d/'diagnostic_gatt.c';s=p.read_text().replace('qca_prefix_att','qca_filter63_att');p.write_text(s)
def driver_sources(d):
 saved=prior.sources
 try:prior.sources=sources;prior.driver_sources(d)
 finally:prior.sources=saved
def compile_driver(d,crypto):
 driver_sources(d);a=checked.prior.actors
 payload=a.compile_efi(d,'filter-scan63',[d/'driver.c',d/'city_core.c',d/'pci_collect.c',d/'pci_identity.c',*[d/n for n in FILES],d/'usb_port.c',d/'bt_event_stream.c',d/'ble_recovery_link.c',d/'diagnostic_gatt.c',a.LINK/'file_core.c',a.NATIVE/'sha256.c',*crypto],driver=True,definitions=('SCENE_REVISION=1','QCA_CONFIG_SETUP=1','QCA_FC_BASE=13'))
 pe=struct.unpack_from('<I',payload,60)[0]
 if len(payload)>262144 or struct.unpack_from('<I',payload,pe+80)[0]>4194304:raise ValueError('unchanged whole EFI file/mapped caps')
 return payload
