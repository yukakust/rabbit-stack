"""Unsigned additive link projection only, not a runtime-connected producer."""
from pathlib import Path
import importlib.util,sys,os,tempfile,struct,json,hashlib,shutil
ROOT=Path(__file__).resolve().parent
if not sys.platform.startswith('linux'):raise SystemExit('Yukabox C/EFI only')
BASE=ROOT.parent/'native-wifi-qca9377-filter64-native-v1';spec=importlib.util.spec_from_file_location('runtime_projection_frozen64',BASE/'filter64_build.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
out=ROOT/'runs/native-fit';out.mkdir(parents=True,exist_ok=True);tmp=out/'tmp';tmp.mkdir(exist_ok=True);os.environ['TMPDIR']=str(tmp);tempfile.tempdir=str(tmp);a=b.checked.prior.actors;_,_,crypto=a.engine.prepare(out,bytes.fromhex('29acbae141bccaf0b22e1a94d34d0bc7361e526d0bfe12c89794bc9322966dd7'));b.driver_sources(out)
extra=[]
for p in [ROOT/'dma_runtime.c',ROOT/'runtime_pool.c',ROOT/'guarded_dma.c',ROOT/'guarded_dma.h',ROOT/'dma_runtime.h',ROOT/'runtime_pool.h',ROOT/'dependencies/ring.c',ROOT/'dependencies/ring.h',ROOT/'dependencies/rx_decode.c',ROOT/'dependencies/rx_decode.h']:
 shutil.copyfile(p,out/p.name)
 if p.suffix=='.c':extra.append(out/p.name)
# Diagnostic-only wrappers around frozen inherited C style/prototype spelling;
# bytes embedded unchanged, all other warnings remain errors.
for name in ['ring.c','rx_decode.c']:
 p=out/name;raw=p.read_bytes();p.write_bytes(b'#pragma GCC diagnostic push\n#pragma GCC diagnostic ignored "-Wmisleading-indentation"\n#pragma GCC diagnostic ignored "-Warray-parameter"\n'+raw+b'\n#pragma GCC diagnostic pop\n')
# Force relocations reachable from EFI entry so --gc-sections cannot hide
# unused runtime code in a misleading identical-payload fit result.
p=out/'driver.c';driver=p.read_text();table='#include "runtime_pool.h"\nstatic volatile uintptr_t runtime_projection_keep[]={ (uintptr_t)qca_htt_pool_acquire,(uintptr_t)qca_htt_pool_attach,(uintptr_t)qca_htt_pool_release,(uintptr_t)qca_htt_pool_boot,(uintptr_t)qca_htt_runtime_allocate_one,(uintptr_t)qca_htt_runtime_bind_ring,(uintptr_t)qca_htt_runtime_refill_one,(uintptr_t)qca_htt_runtime_close_one,(uintptr_t)qrx_indication,(uintptr_t)qrx_claim,(uintptr_t)qrx_frame};\n'
driver=table+driver;needle='Status EFIAPI module_entry(void*h,SystemTable*st){';assert driver.count(needle)==1;driver=driver.replace(needle,needle+'\n for(unsigned keep=0;keep<11;keep++){volatile uintptr_t address=runtime_projection_keep[keep];(void)address;}');p.write_text(driver)
files=[out/'driver.c',out/'city_core.c',out/'pci_collect.c',out/'pci_identity.c',*[out/n for n in b.FILES],out/'usb_port.c',out/'bt_event_stream.c',out/'ble_recovery_link.c',out/'diagnostic_gatt.c',a.LINK/'file_core.c',a.NATIVE/'sha256.c',*crypto,*extra,ROOT/'chkstk_bridge.S']
payload=a.compile_efi(out,'runtime-additive-projection',files,driver=True,definitions=('SCENE_REVISION=1','QCA_CONFIG_SETUP=1','QCA_FC_BASE=13'));(out/'payload.efi').write_bytes(payload);offset=struct.unpack_from('<I',payload,60)[0];mapped=struct.unpack_from('<I',payload,offset+80)[0]
report={'status':'UNSIGNED-RUNTIME-ADDITIVE-LINK-PROJECTION-NOT-INTEGRATED','file_bytes':len(payload),'mapped_bytes':mapped,'file_cap':262144,'mapped_cap':4194304,'fits':len(payload)<=262144 and mapped<=4194304,'payload_sha256':hashlib.sha256(payload).hexdigest(),'runtime_functions_not_called':True,'linker_gc_prevented_by_EFI_entry_references':True,'physical':False,'signing_admitted':False,'device_operations':0};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
