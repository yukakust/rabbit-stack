"""NEW unsigned cached-presentation/cooperative QCA-only service projection."""
from pathlib import Path
import sys,importlib.util,os,tempfile,shutil,hashlib,json,struct
assert sys.platform.startswith('linux'),'Native compile only Yukabox'
R=Path(__file__).resolve().parent
BASE=R.parent/'native-wifi-qca9377-city-arena-v1'
spec=importlib.util.spec_from_file_location('presentation_owned_city',BASE/'native_projection.py');city=importlib.util.module_from_spec(spec);spec.loader.exec_module(city)
b=city.b;one=city.one
SERVICE=r'''
void qca_poll(uint64_t);
static unsigned city_net_live,city_net_busy;
static uint32_t city_net_last;
void city_network_slice(void){
 if(!city_net_live||city_net_busy)return;
 uint32_t now=prefix_clock_ms();
 /* A rollback/wrap disables extra frame-service, not ownership/normal poll.
  * No readiness or entropy authority is inferred from this clock. */
 if(now<city_net_last){city_net_live=0;return;}
 if(now-city_net_last<4)return;
 city_net_last=now;city_net_busy=1;qca_poll(now);city_net_busy=0;
}
static void city_present_service(void*context){(void)context;city_network_slice();}
'''
def sources(out):
 extras=city.sources(out)
 for n in ['presentation.c','presentation.h']:shutil.copyfile(R/n,out/n)
 extras.append(out/'presentation.c')
 p=out/'driver.c';s=p.read_text()
 s=one(s,'#include "city_display.c"','#include "presentation.h"\nvoid city_network_slice(void);\nstatic void city_present_service(void*);\n#include "city_display.c"')
 s=one(s,'static RlLink radio_link;',SERVICE+'\nstatic RlLink radio_link;')
 s=one(s,'rl_init(&radio_link,0);rg_init_shared(&radio_link.gatt,file);return 0;','rl_init(&radio_link,0);rg_init_shared(&radio_link.gatt,file);city_net_last=prefix_clock_ms();city_net_live=1;return 0;')
 s=one(s,'static int EFIAPI close_radio(void){','static int EFIAPI close_radio(void){\n city_net_live=0;')
 s=one(s,'!runtime_phase_retire()||!city_pool_retire()','!runtime_phase_retire()||!city_presentation_close(&city_presentation)||!city_pool_retire()');p.write_text(s)
 p=out/'city_display.c';s=p.read_text();s=one(s,'static uint32_t *city_physical;','static CityPresentation city_presentation;\nstatic uint32_t *city_physical;')
 s=one(s,' return 0;\n}', ' if(!city_presentation_bind(&city_presentation,city_width,city_height,city_stride,city_format)){city_physical=0;return 1;}\n return 0;\n}')
 marker='static void city_present(Surface*s){';assert s.count(marker)==1;s=s[:s.index(marker)]+r'''
static void city_present(Surface*s){
 if(!city_physical||!city_pool_enter())return;
 unsigned detailed=active_length&&(active_package[4]==4||active_package[4]==5);
 const uint32_t*picture=city_frame;
 if(!detailed){for(unsigned i=0;i<480*270;i++)city_picture[i]=s->pixels[i];picture=city_picture;}
 (void)city_presentation_draw(&city_presentation,city_physical,(size_t)city_stride*city_height*4,s->pixels,picture,detailed,city_present_service,0);
 city_pool_leave();
}
''';p.write_text(s)
 p=out/'city_core.c';s=p.read_text();s=one(s,'static uint32_t *depth;','extern void city_network_slice(void);\nstatic uint32_t *depth;')
 s=one(s,'for(int y=miny;y<=maxy;y++)for(int x=minx;x<=maxx;x++){','for(int y=miny;y<=maxy;y++)for(int x=minx;x<=maxx;x++){\n  if(x==minx&&!(y&15))city_network_slice();')
 s=one(s,'for(int y=0;y<CITY_H;y++)for(int x=0;x<CITY_W;x++){','for(int y=0;y<CITY_H;y++)for(int x=0;x<CITY_W;x++){\n  if(!x&&!(y&15))city_network_slice();');p.write_text(s)
 return extras
def main():
 out=R/'runs/native-projection';out.mkdir(parents=True,exist_ok=True);tmp=out/'tmp';tmp.mkdir(exist_ok=True);os.environ['TMPDIR']=str(tmp);tempfile.tempdir=str(tmp)
 a=b.checked.prior.actors;_,_,crypto=a.engine.prepare(out,bytes.fromhex('29acbae141bccaf0b22e1a94d34d0bc7361e526d0bfe12c89794bc9322966dd7'));extra=sources(out)
 files=[out/'driver.c',out/'city_core.c',out/'pci_collect.c',out/'pci_identity.c',*[out/n for n in b.FILES],out/'usb_port.c',out/'bt_event_stream.c',out/'ble_recovery_link.c',out/'diagnostic_gatt.c',a.LINK/'file_core.c',a.NATIVE/'sha256.c',*crypto,*extra,city.P/'chkstk_bridge.S']
 payload=a.compile_efi(out,'presentation-service-projection',files,driver=True,definitions=('SCENE_REVISION=1','QCA_CONFIG_SETUP=1','QCA_FC_BASE=13'));(out/'payload.efi').write_bytes(payload)
 pe=struct.unpack_from('<I',payload,60)[0];mapped=struct.unpack_from('<I',payload,pe+80)[0];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 report={'status':'UNSIGNED-CACHED-PRESENTATION-QCA-SERVICE-COMPILE-ONLY','build_host':'yukabox','file_bytes':len(payload),'mapped_bytes':mapped,'payload_sha256':hashlib.sha256(payload).hexdigest(),'fits':len(payload)<=262144 and mapped<=4194304,'physical_proved':False,'signing_admitted':False,'generation_reserved':False,'render_service_calls_Bluetooth':False,'service_period_ms':4,'source_sha256':{p.name:sha(p) for p in [R/'native_build.py',R/'presentation.c',R/'presentation.h']},'base_generator_sha256':sha(BASE/'native_projection.py'),'generated_source_sha256':{p.name:sha(p) for p in out.iterdir() if p.suffix in ['.c','.h','.S']}}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if not isinstance(v,dict)}))
if __name__=='__main__':main()
