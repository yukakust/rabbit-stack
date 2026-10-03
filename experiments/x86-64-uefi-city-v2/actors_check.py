"""Actual portable C city decode/render gate; never claims physical execution."""
import hashlib
import subprocess
from pathlib import Path
import scene5
ROOT = Path(__file__).resolve().parent
HARNESS = r'''
#include <stdio.h>
#include "city_core.h"
static uint32_t pixels[CITY_W*CITY_H+2];
static uint32_t image_hash(void){uint32_t h=2166136261u;for(unsigned i=1;i<=CITY_W*CITY_H;i++)h=(h^pixels[i])*16777619u;return h;}
int main(int argc,char**argv){
 if(argc!=3)return 9;
 uint8_t bytes[6817];FILE*f=fopen(argv[1],"rb");if(!f)return 9;
 unsigned n=fread(bytes,1,sizeof(bytes),f);fclose(f);City city;
 if(city_decode(bytes,n,0,&city))return 2;
 if(!city_decode(bytes,n,city.counter,&city))return 3;
 pixels[0]=pixels[CITY_W*CITY_H+1]=0xdeadbeef;
 if(city.actor_count){
  City stable=city;for(unsigned i=0;i<stable.part_count;i++)stable.parts[i].motion=(CityVec){0,0,0};
  city_render(&stable,pixels+1,9999);uint32_t neutral=image_hash();
  city_render(&stable,pixels+1,10000);uint32_t smile=image_hash();
  if(neutral==smile)return 7;
  city_render(&stable,pixels+1,10999);if(image_hash()!=smile)return 7;
  city_render(&stable,pixels+1,11000);if(image_hash()!=neutral)return 7;
  city_render(&stable,pixels+1,20000);if(image_hash()!=smile)return 7;
  city_render(&city,pixels+1,250);uint32_t tail=image_hash();
  city_render(&city,pixels+1,850);if(image_hash()==tail)return 8;
 }
 for(unsigned i=0;i<120;i++)city_render(&city,pixels+1,i*100);
 if(pixels[0]!=0xdeadbeef||pixels[CITY_W*CITY_H+1]!=0xdeadbeef)return 4;
 f=fopen(argv[2],"wb");if(!f)return 9;fprintf(f,"P6\n%d %d\n255\n",CITY_W,CITY_H);
 for(unsigned i=1;i<=CITY_W*CITY_H;i++){fputc(pixels[i]>>16,f);fputc(pixels[i]>>8,f);fputc(pixels[i],f);}fclose(f);
 /* Exercise near-plane clipping and maximum geometry/camera bounds. */
 for(unsigned i=city.count;i<CITY_MAX;i++)city.buildings[i]=city.buildings[i%city.count];
 city.count=CITY_MAX;
 for(unsigned i=0;i<CITY_MAX;i++){
  city.buildings[i].w=city.buildings[i].h=city.buildings[i].d=3000;
  city.buildings[i].position=(CityVec){i&1?20000:-20000,i&2?3000:0,i&4?20000:-20000};
 }
 for(unsigned i=0;i<16;i++){
  city.camera=(CityVec){i&1?20000:-20000,i&2?3000:50,i&4?20000:-20000};city.yaw=(uint8_t)(i*16);
  city_render(&city,pixels+1,i*100);
 }
 if(pixels[0]!=0xdeadbeef||pixels[CITY_W*CITY_H+1]!=0xdeadbeef)return 6;
 bytes[n-1]^=1;if(!city_decode(bytes,n,0,&city))return 5;
 return 0;
}
'''

def check_city(package_path, cache, sanitizers=False, roof_cat_timing=False):
    packet = Path(package_path).read_bytes()
    scene5.decode_scene(packet) if packet[:5]==b'RUP5\x05' else scene5.city_world.decode_city(packet)
    cache = Path(cache); cache.mkdir(parents=True, exist_ok=True)
    # Reuse the pinned, independently verified crypto source fetcher.
    from actors_build import engine
    old = engine.old
    old.load('city_check_crypto',old.V1/'build_image.py').fetch_crypto(cache)
    harness=HARNESS if roof_cat_timing else HARNESS.replace('if(city.actor_count){','if(0){',1)
    source = cache/'city-check.c'; source.write_text(harness)
    executable = cache/'city-check'
    command = ['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',str(ROOT),'-I',str(cache),
               str(source),str(ROOT/'city_core.c'),str(cache/'monocypher.c'),str(cache/'monocypher-ed25519.c'),'-o',str(executable)]
    if sanitizers: command[1:1]=['-fsanitize=address,undefined','-fno-sanitize-recover=all']
    built = subprocess.run(command,capture_output=True,text=True,timeout=180)
    if built.returncode: raise ValueError('city C compile failed: '+built.stderr)
    subprocess.run([str(executable),str(Path(package_path).resolve()),str(cache/'preview.ppm')],check=True,timeout=30)
    return {'city_core_sha256':hashlib.sha256((ROOT/'city_core.c').read_bytes()).hexdigest(),
            'harness_sha256':hashlib.sha256(harness.encode()).hexdigest(), 'host_ticks':120,'roof_cat_timing':roof_cat_timing,
            'adversarial_camera_frames':16,'sanitizers':sanitizers,'physical_execution_verified':False}
