"""NEW unsigned city arena projection over the retained47 prototype.
This is compile feasibility, not hardware admission or a reserved generation.
"""
from pathlib import Path
import importlib.util,sys,os,tempfile,shutil,struct,json,hashlib
assert sys.platform.startswith('linux'),'Native compile only Yukabox'
R=Path(__file__).resolve().parent
P=R.parent/'native-wifi-qca9377-htt-persistent-runtime-v1'
spec=importlib.util.spec_from_file_location('city_base47',P/'runtime_native_prototype.py');rt=importlib.util.module_from_spec(spec);spec.loader.exec_module(rt)
b=rt.b
def one(s,old,new):
 assert s.count(old)==1,old
 return s.replace(old,new)
def sources(out):
 extras=rt.sources(out)
 for name in ['city_arena.c','city_arena.h']:shutil.copyfile(R/name,out/name)
 extras.append(out/'city_arena.c')
 # A QCA-absent startup owns the phase pool but never acquires a DMA runtime.
 # Admit retirement only for its canonical untouched zero ledger, or CLOSED
 # actual owners. This does not reinterpret a failed/acquired runtime as empty.
 p=out/'init_probe.c';s=p.read_text()
 s=one(s,'int runtime_phase_retire(void){','static int runtime_city_retirable(const QcaHttRuntime*r){if(r->phase)return qca_htt_runtime_detachable(r);const uint8_t*p=(const uint8_t*)r;for(size_t i=0;i<sizeof(*r);i++)if(p[i])return 0;return 1;}\nint runtime_phase_retire(void){')
 s=one(s,'!qca_htt_runtime_detachable(&runtime_phase.arena->runtime)||!qca_htt_public_rng_cleanup','!runtime_city_retirable(&runtime_phase.arena->runtime)||!qca_htt_public_rng_cleanup');p.write_text(s)
 p=out/'city_core.c';s=p.read_text();s=one(s,'static uint32_t depth[CITY_W*CITY_H];','static uint32_t *depth;\nuint32_t **city_depth_holder(void){return &depth;}\nextern int city_pool_enter(void);extern void city_pool_leave(void);')
 # Only the public renderer wrapper changes; the rasterizer body remains exact.
 s=one(s,'void city_render(','static void city_render_owned(')
 s+='\nvoid city_render(const City*c,uint32_t*p,uint32_t ms){if(!city_pool_enter())return;city_render_owned(c,p,ms);city_pool_leave();}\n';p.write_text(s)
 p=out/'city_display.c';s=p.read_text();s=one(s,'static uint32_t city_picture[480*270];','static uint32_t *city_picture;\nextern int city_pool_enter(void);extern void city_pool_leave(void);')
 s=one(s,' if(!city_physical)return;',' if(!city_physical||!city_pool_enter())return;')
 # No projection or pixel formula changes.
 assert s.rstrip().endswith('}');s=s.rstrip()[:-1]+' city_pool_leave();\n}\n';p.write_text(s)
 p=out/'driver.c';s=p.read_text();s=one(s,'#include "city_display.c"','#include "city_arena.h"\n#include "runtime_pool.h"\n#include "city_display.c"\nstatic CityArena city_pool;\nextern uint32_t **city_depth_holder(void);\nint city_pool_enter(void){return city_arena_enter(&city_pool,1);}\nvoid city_pool_leave(void){(void)city_arena_leave(&city_pool,1);}\nstatic int city_pool_retire(void){if(city_pool.depth_slot&&!city_arena_detach(&city_pool,1))return 0;return city_arena_close(&city_pool,1);}')
 s=one(s,'if(radio_port.bound||qca_stop()||!runtime_phase_retire())return EFI_ERROR(6);return 0;','if(radio_port.bound||qca_stop()||!runtime_phase_retire()||!city_pool_retire())return EFI_ERROR(6);return 0;')
 s=one(s,' r->init=driver_init;', ''' QcaHttPoolBoot city_boot;
 if(!qca_htt_pool_boot(st,&city_boot)||!city_arena_open(&city_pool,(CityAllocate)city_boot.allocate,(CityFree)city_boot.release,1))return EFI_ERROR(9);
 if(!city_arena_attach(&city_pool,1,city_depth_holder(),&city_picture)){(void)city_arena_close(&city_pool,1);return EFI_ERROR(9);}
 r->init=driver_init;''')
 p.write_text(s)
 return extras
def main():
 out=R/'runs/native-projection';out.mkdir(parents=True,exist_ok=True);tmp=out/'tmp';tmp.mkdir(exist_ok=True);os.environ['TMPDIR']=str(tmp);tempfile.tempdir=str(tmp)
 a=b.checked.prior.actors;_,_,crypto=a.engine.prepare(out,bytes.fromhex('29acbae141bccaf0b22e1a94d34d0bc7361e526d0bfe12c89794bc9322966dd7'));extras=sources(out)
 files=[out/'driver.c',out/'city_core.c',out/'pci_collect.c',out/'pci_identity.c',*[out/n for n in b.FILES],out/'usb_port.c',out/'bt_event_stream.c',out/'ble_recovery_link.c',out/'diagnostic_gatt.c',a.LINK/'file_core.c',a.NATIVE/'sha256.c',*crypto,*extras,P/'chkstk_bridge.S']
 payload=a.compile_efi(out,'city-arena-projection',files,driver=True,definitions=('SCENE_REVISION=1','QCA_CONFIG_SETUP=1','QCA_FC_BASE=13'));(out/'payload.efi').write_bytes(payload)
 pe=struct.unpack_from('<I',payload,60)[0];mapped=struct.unpack_from('<I',payload,pe+80)[0]
 sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 report={'status':'UNSIGNED-CITY-ARENA-47-PROJECTION-COMPILE-ONLY','build_host':'yukabox','file_bytes':len(payload),'mapped_bytes':mapped,'payload_sha256':hashlib.sha256(payload).hexdigest(),'fits':len(payload)<=262144 and mapped<=4194304,'city_pool_bytes':1958415,'removed_static_bytes':1958400,'generation_reserved':False,'signing_admitted':False,'physical_proved':False,'world_QEMU_proved':False,'source_sha256':{str(p.relative_to(R)):sha(p) for p in [R/'native_projection.py',R/'city_arena.c',R/'city_arena.h']},'base_generator_sha256':sha(P/'runtime_native_prototype.py'),'generated_source_sha256':{p.name:sha(p) for p in out.iterdir() if p.suffix in ['.c','.h','.S']}}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if not isinstance(v,dict)}))
if __name__=='__main__':main()
