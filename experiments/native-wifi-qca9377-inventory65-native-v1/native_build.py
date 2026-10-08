from pathlib import Path
import sys,os,subprocess,importlib.util,hashlib,json,struct,shutil,tempfile
assert sys.platform.startswith('linux'),'C/COFF/QEMU only Yukabox'
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent;REPO=Path('/home/yuka/rabbit-world/parallel-filter64-native-v1/source');BASE=REPO/'experiments/native-wifi-qca9377-filter64-native-v1'
spec=importlib.util.spec_from_file_location('inventory65_original64',BASE/'filter64_build.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
one=b.one;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def cb(name,v):return 'static const uint8_t '+name+'[32]={'+','.join(map(str,v))+'};\n'
def sources(out):
 b.driver_sources(out)
 original=json.loads((BASE/'runs/checked-candidate/report.json').read_text())
 baseline={name:sha(out/name) for name in original['generated_compiler_sources_sha256'] if '/' not in name and (out/name).is_file()}
 (out/'base64-generated.json').write_text(json.dumps(baseline,sort_keys=True,indent=2)+'\n')
 for name in ['inventory.c','inventory.h','platform.c','platform.h','rng_port.c','rng_port.h','probe65.c','probe65.h','city_arena.c','city_arena.h']:
  shutil.copyfile(R/name,out/name)
  if name.endswith('.c'):
   p=out/name;p.write_text('#pragma GCC diagnostic push\n#pragma GCC diagnostic ignored "-Wmisleading-indentation"\n'+p.read_text()+'\n#pragma GCC diagnostic pop\n')
 # Probe-independent compiled code provenance has no selfhash cycle.
 cmd=['x86_64-w64-mingw32-gcc','-std=c11','-Os','-ffreestanding','-fno-builtin','-fno-stack-protector','-mno-red-zone','-ffunction-sections','-I'+str(out),'-c',str(out/'rng_port.c'),'-o',str(out/'rng65-provenance.obj')];x=subprocess.run(cmd,text=True,capture_output=True);assert not x.returncode,x.stderr;(out/'rng65-object.log').write_text(json.dumps(cmd)+'\n'+x.stderr)
 (out/'inventory65_hashes.h').write_text(cb('probe65_code_sha256',bytes.fromhex(sha(out/'rng65-provenance.obj')))+cb('cpuid65_source_sha256',bytes.fromhex(sha(R/'inventory.c'))))
 # Proven owned city pool, renderer expressions unchanged.
 p=out/'city_core.c';s=one(p.read_text(),'static uint32_t depth[CITY_W*CITY_H];','static uint32_t *depth;\nuint32_t **city_depth_holder(void){return &depth;}\nextern int city_pool_enter(void);extern void city_pool_leave(void);');s=one(s,'void city_render(','static void city_render_owned(');s+='\nvoid city_render(const City*c,uint32_t*p,uint32_t ms){if(!city_pool_enter())return;city_render_owned(c,p,ms);city_pool_leave();}\n';p.write_text(s)
 p=out/'city_display.c';s=one(p.read_text(),'static uint32_t city_picture[480*270];','static uint32_t *city_picture;\nextern int city_pool_enter(void);extern void city_pool_leave(void);');s=one(s,' if(!city_physical)return;',' if(!city_physical||!city_pool_enter())return;');assert s.rstrip().endswith('}');s=s.rstrip()[:-1]+' city_pool_leave();\n}\n';p.write_text(s)
 p=out/'driver.c';s=p.read_text();s=one(s,'#include "city_display.c"','#include "city_arena.h"\n#include "probe65.h"\n#include "city_display.c"\nstatic CityArena city_pool;\nextern uint32_t **city_depth_holder(void);\nint city_pool_enter(void){return city_arena_enter(&city_pool,65);}\nvoid city_pool_leave(void){(void)city_arena_leave(&city_pool,65);}\nstatic int city_pool_retire(void){if(city_pool.depth_slot&&!city_arena_detach(&city_pool,65))return 0;return !city_pool.epoch||city_arena_close(&city_pool,65);}')
 s=one(s,' qca_collect(st);qca_start(st,city_clock_ms());',' /* Diagnostic only: no PCI collect, WLAN startup, RF or firmware assets. */')
 s=one(s,' qca_poll(began/1000);',' /* WLAN poll deliberately absent in this diagnostic profile. */')
 s=s.replace('(void)qca_stop();','/* no WLAN owner acquired */').replace(' if(qca_stop())return 1;',' if(!inventory65_close())return 1;')
 s=one(s,'return radio_port.bound||qca_stop()?EFI_ERROR(6):0;','return radio_port.bound||!inventory65_close()||!city_pool_retire()?EFI_ERROR(6):0;')
 s=one(s,' r->init=driver_init;', ''' image->unload=connected_unload;
 if(!inventory65_begin(st))return EFI_ERROR(3);
 CityAllocate allocate=(CityAllocate)service(st,64);CityFree release=(CityFree)service(st,72);
 if(!city_arena_open(&city_pool,allocate,release,65)||!city_arena_attach(&city_pool,65,city_depth_holder(),&city_picture))return EFI_ERROR(9);
 r->init=driver_init;''');p.write_text(s)
 # Keep exactly the existing 0D/06/07 read route, with standards-bounded values.
 p=out/'diagnostic_gatt.c';s=p.read_text();start=s.index(' if(s){size_t diag=');end=s.index(' if(!s||',start);s=s[:start]+s[end:]
 s=one(s,'for(unsigned i=0;i<716;i++)value[i]=qca_diagnostic[i];length=716;','for(unsigned i=0;i<512;i++)value[i]=qca_diagnostic[i];length=512;')
 s=one(s,"value[3]=1;rabbit_sha256(value+4,qca_diagnostic,716);for(unsigned i=0;i<208;i++)value[36+i]=qca_diagnostic[716+i];length=244;", "value[3]=2;rabbit_sha256(value+4,qca_diagnostic,512);for(unsigned i=0;i<412;i++)value[36+i]=qca_diagnostic[512+i];length=448;")
 p.write_text(s)
 return [out/n for n in ['inventory.c','platform.c','probe65.c','city_arena.c']]+[out/'rng65-provenance.obj']
def main():
 out=R/'runs/checked-candidate';out.mkdir(parents=True,exist_ok=True);tmp=out/'tmp';tmp.mkdir(exist_ok=True);os.environ['TMPDIR']=str(tmp);tempfile.tempdir=str(tmp);a=b.checked.prior.actors;_,_,crypto=a.engine.prepare(out,bytes.fromhex('29acbae141bccaf0b22e1a94d34d0bc7361e526d0bfe12c89794bc9322966dd7'));extra=sources(out)
 files=[out/'driver.c',out/'city_core.c',out/'pci_collect.c',out/'pci_identity.c',*[out/n for n in b.FILES],out/'usb_port.c',out/'bt_event_stream.c',out/'ble_recovery_link.c',out/'diagnostic_gatt.c',a.LINK/'file_core.c',a.NATIVE/'sha256.c',*crypto,*extra]
 payload=a.compile_efi(out,'inventory65',files,driver=True,definitions=('SCENE_REVISION=1','QCA_CONFIG_SETUP=1','QCA_FC_BASE=13'));(out/'payload.efi').write_bytes(payload);pe=struct.unpack_from('<I',payload,60)[0];mapped=struct.unpack_from('<I',payload,pe+80)[0];assert len(payload)<=262144 and mapped<=4194304
 report={'status':'UNSIGNED-INVENTORY65-CPU-GETINFO-NORF-NATIVE-PROJECTION','native_counter':65,'generation_reserved':False,'physical_admission':False,'entropy_approved':False,'GetRNG_RDSEED_MSR_calls':0,'payload_sha256':hashlib.sha256(payload).hexdigest(),'payload_bytes':len(payload),'mapped_bytes':mapped,'world_package_sha256':'89ffda340552cf33a4c732597388f4fea358d47b0850f7720bdce51a2b3968b7','source_sha256':{str(p.relative_to(R)):sha(p) for p in R.rglob('*') if p.is_file() and 'runs' not in p.parts and 'evidence' not in p.parts and '__pycache__' not in p.parts},'generated_sources_sha256':{str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file() and p.suffix in ('.c','.h','.S')},'compiled_inputs_sha256':{str(p):sha(p) for p in files},'rng_code_object_sha256':sha(out/'rng65-provenance.obj'),'base64_report_sha256':sha(BASE/'runs/checked-candidate/report.json'),'base64_generated_sha256':json.loads((out/'base64-generated.json').read_text())};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],len(payload),mapped,report['payload_sha256'])
if __name__=='__main__':main()
