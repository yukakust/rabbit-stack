"""Explicit reviewed city native profile; immutable installed sources untouched."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
CONNECTED=ROOT.parent/'x86-64-uefi-connected-supervisor-v1'
sys.path.insert(0,str(CONNECTED))
import engine_route as engine
from build_image import OLD,LINK,NATIVE,V3,compile_efi

def one(source,old,new):
 if source.count(old)!=1:raise ValueError("reviewed city source anchor differs: "+old[:80])
 return source.replace(old,new,1)

def sources(directory):
 runtime=(V3/'runtime_core.c').read_text()
 runtime=one(runtime,'#include "monocypher-ed25519.h"','#include "monocypher-ed25519.h"\n#include "city_core.h"\nstatic City city_scene;')
 old='static void draw_scene(const uint8_t *p,struct object_state *state,uint8_t count){'
 runtime=one(runtime,old,old+'if(p[4]==4){if(city_scene.counter!=le32(p+8)&&city_decode(p,le16(p+6),0,&city_scene))return;city_render(&city_scene,framebuffer);return;}')
 old='static int validate_package(const uint8_t *p,uint32_t length,uint32_t minimum_counter,struct object_state *state,uint8_t *count){'
 runtime=one(runtime,old,old+'if(p&&length>=96&&p[4]==4){City checked;if(city_decode(p,length,minimum_counter,&checked))return 1;*count=0;return 0;}')
 old='static int step_scene(const uint8_t *p,struct object_state *state,uint8_t count,uint32_t now){'
 if old not in runtime:raise ValueError('step_scene source anchor differs')
 runtime=one(runtime,old,old+'if(p[4]==4)return 0;')
 (directory/'runtime_core.c').write_text(runtime)
 scene=(OLD/'scene_module.c').read_text()
 scene=one(scene,'#include "scene_abi.h"','#include "scene_abi.h"\nstatic int city_display_bind(SystemTable*);\nstatic void city_present(Surface*);')
 scene=one(scene,' return result;',' if(!result)city_present(s);\n return result;')
 (directory/'scene_module.c').write_text(scene)
 driver=one((CONNECTED/'driver.c').read_text(),'#undef module_entry','#undef module_entry\n#include "city_display.c"')
 driver=one(driver,' diagnostic_system=st;',' diagnostic_system=st;\n if(city_display_bind(st))return 1;')
 driver=one(driver,'static void diagnostic(const char*text){','static void diagnostic(const char*text){\n if(active_length&&active_package[4]==4)return;')
 (directory/'driver.c').write_text(driver)
 for name in ('city_core.h','city_core.c','city_display.c'):(directory/name).write_bytes((ROOT/name).read_bytes())

def compile_city_driver(directory,crypto):
 sources(directory)
 return compile_efi(directory,'city-driver',[directory/'driver.c',directory/'city_core.c',LINK/'usb_port.c',LINK/'hci_link.c',
  LINK/'gatt_core.c',LINK/'file_core.c',NATIVE/'sha256.c',*crypto],driver=True,definitions=('SCENE_REVISION=1',))
