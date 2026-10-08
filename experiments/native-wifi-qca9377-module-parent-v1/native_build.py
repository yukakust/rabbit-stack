"""NEW unsigned parent projection. No key, BLE, native state or bootstrap edits."""
from pathlib import Path
import sys,os,importlib.util,shutil,hashlib,json,struct,tempfile,subprocess
assert sys.platform.startswith('linux'),'Native C only Yukabox'
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent
REPO=Path(os.environ.get('RABBIT_REFERENCE_REPO','/home/yuka/rabbit-world/parallel-filter64-native-v1/source'))
BASE=REPO/'experiments/native-wifi-qca9377-city-presentation-v1'
spec=importlib.util.spec_from_file_location('module_parent_base',BASE/'native_build.py');project=importlib.util.module_from_spec(spec);spec.loader.exec_module(project)
b=project.b;one=project.one
EPOCH=1 # Explicit UNSIGNED UNRESERVED model epoch; MUST NOT sign as actual native.
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def sources(out):
 baseline=json.loads((R/'base-freeze.json').read_text())
 for name,digest in baseline['source_sha256'].items():
  chosen=BASE/name if (BASE/name).is_file() else R/'reference-base-city'/name
  assert sha(chosen)==digest,name
 extras=project.sources(out)
 for name in ['artifact.c','artifact.h','loader.c','loader.h','module_abi.h','parent_glue.c','parent_glue.h','inventory.c','inventory.h','module_platform.c','module_platform.h']:
  shutil.copyfile(R/name,out/name)
 for name in ['artifact.c','loader.c','inventory.c','module_platform.c']:
  p=out/name;p.write_text('#pragma GCC diagnostic push\n#pragma GCC diagnostic ignored \"-Wmisleading-indentation\"\n'+p.read_text()+'\n#pragma GCC diagnostic pop\n')
 (out/'reference').mkdir(exist_ok=True)
 for p in (R/'reference').iterdir():shutil.copyfile(p,out/'reference'/p.name)
 extras.extend(out/name for name in ['artifact.c','loader.c','parent_glue.c','inventory.c','module_platform.c'])
 policy=json.loads((REPO/'experiments/native-wifi-qca9377-filter64-native-v1/receiver-policy.json').read_text())
 def array(n,data):return 'static const uint8_t '+n+'[32]={'+','.join(map(str,data))+'};\n'
 header=array('parent_owner',bytes.fromhex(policy['owner']))+array('parent_target',bytes.fromhex(policy['target']))+array('parent_cpu_source',bytes.fromhex(sha(R/'inventory.c')))+'#define PARENT_MODEL_EPOCH UINT64_C(1)\n'
 (out/'parent_policy.h').write_text(header)
 p=out/'driver.c';s=p.read_text();s=one(s,'#include "connected_abi.h"','#include "connected_abi.h"\n#include "parent_glue.h"\n#include "parent_policy.h"')
 s=one(s,'static int EFIAPI close_radio(void){','static int EFIAPI close_radio(void){\n if(!parent_module_close())return 1;')
 s=one(s,'if(radio_port.bound||qca_stop()','if(!parent_module_close()||!parent_module_released()||radio_port.bound||qca_stop()')
 s=one(s,' QcaHttPoolBoot city_boot;',' image->unload=connected_unload; if(!parent_module_bind(h,st,PARENT_MODEL_EPOCH,parent_owner,parent_target,parent_cpu_source))return EFI_ERROR(3);\n QcaHttPoolBoot city_boot;')
 # Typed public accessor is genuine native implementation; no secret output.
 s+='\nint module_parent_cpu_public(void*p,size_t n){return parent_cpu_export(p,n);}\n'
 p.write_text(s)
 cmd=['x86_64-w64-mingw32-gcc','-std=c11','-Os','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-fno-stack-protector','-mno-red-zone','-ffunction-sections','-fno-asynchronous-unwind-tables','-fno-unwind-tables','-I'+str(out),'-c',str(out/'rng_inventory_join.c'),'-o',str(out/'rng_inventory_join.provenance.obj')]
 completed=subprocess.run(cmd,text=True,capture_output=True);(out/'rng-object.log').write_text(json.dumps(cmd)+'\n'+completed.stdout+completed.stderr);assert not completed.returncode,completed.stderr
 extras=[out/'rng_inventory_join.provenance.obj' if p.name=='rng_inventory_join.c' else p for p in extras]
 p=out/'init_probe.c';s=p.read_text();digest=sha(out/'rng_inventory_join.provenance.obj');old='static const uint8_t inventory_code[32]={'+','.join(['0']*32)+'};';new=array('inventory_code',bytes.fromhex(digest)).strip();s=one(s,old,new);p.write_text(s)
 return extras

def main():
 out=R/'runs/native-projection';out.mkdir(parents=True,exist_ok=True);tmp=out/'tmp';tmp.mkdir(exist_ok=True);os.environ['TMPDIR']=str(tmp);tempfile.tempdir=str(tmp)
 a=b.checked.prior.actors;_,_,crypto=a.engine.prepare(out,bytes.fromhex('29acbae141bccaf0b22e1a94d34d0bc7361e526d0bfe12c89794bc9322966dd7'));extra=sources(out)
 files=[out/'driver.c',out/'city_core.c',out/'pci_collect.c',out/'pci_identity.c',*[out/n for n in b.FILES],out/'usb_port.c',out/'bt_event_stream.c',out/'ble_recovery_link.c',out/'diagnostic_gatt.c',a.LINK/'file_core.c',a.NATIVE/'sha256.c',*crypto,*extra,project.city.P/'chkstk_bridge.S']
 payload=a.compile_efi(out,'module-parent',files,driver=True,definitions=('SCENE_REVISION=1','QCA_CONFIG_SETUP=1','QCA_FC_BASE=13'));(out/'payload.efi').write_bytes(payload)
 pe=struct.unpack_from('<I',payload,60)[0];mapped=struct.unpack_from('<I',payload,pe+80)[0]
 child=json.loads((R/'child-report.json').read_text());report={'status':'UNSIGNED-NATIVE-PARENT-MODULE-INVENTORY-PROJECTION','build_host':'yukabox','file_bytes':len(payload),'mapped_bytes':mapped,'payload_sha256':hashlib.sha256(payload).hexdigest(),'fits':len(payload)<=262144 and mapped+child['mapped_bytes']<=4194304,'child_payload_sha256':child['payload_sha256'],'child_mapped_bytes':child['mapped_bytes'],'aggregate_mapped_bytes':mapped+child['mapped_bytes'],'known_external_pool_max_bytes':1958415+262144+131072,'known_mapped_plus_external_max_bytes':mapped+child['mapped_bytes']+1958415+262144+131072,'total_runtime_4MiB_fit':mapped+child['mapped_bytes']+1958415+262144+131072<=4194304,'global_external_pool_budget_not_implemented':True,'parent_module_epoch':EPOCH,'epoch_unreserved':True,'physical_admission':False,'entropy_approved':False,'GetRNG_calls':0,'rng_provenance_object_sha256':sha(out/'rng_inventory_join.provenance.obj'),'owner_parent_hash_binding':'OWNER-SIGNED-ASSERTION-NOT-RELOCATED-SELFHASH','module_transport_integrated':False,'source_sha256':{str(p.relative_to(R)):sha(p) for p in R.rglob('*') if p.is_file() and 'runs' not in p.parts and 'evidence' not in p.parts and '__pycache__' not in p.parts},'base_freeze_sha256':sha(R/'base-freeze.json'),'compiled_source_sha256':{str(p):sha(p) for p in files},'generated_source_sha256':{str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file() and p.suffix in ('.c','.h','.S')}}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');assert report['fits'];print(json.dumps({k:v for k,v in report.items() if not isinstance(v,dict)}))
if __name__=='__main__':main()
