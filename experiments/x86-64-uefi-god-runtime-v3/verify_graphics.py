#!/usr/bin/env python3
"""Independent Python/C graphics, bounds, legacy, signature and transport tests."""
import copy
import hashlib
import json
import os
import shutil
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from build_image import ROOT, V1, load_module
from compile_world import compile_world
from package import PackageError, decode_package, rle_decode, v2, LEGACY
from transport import encode_transfer, decode_transfer, encode_segments, TransportError


class GraphicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.private=Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
        cls.public=cls.private.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
        cls.world=ROOT/"worlds/cat-chases-smooth-mouse.json"
        cls.package=compile_world(cls.world,1,cls.private)
        cls.tmp=tempfile.TemporaryDirectory(prefix="rabbit-v3-check-",dir=os.environ.get("RABBIT_TMPDIR",str(ROOT)))
        cls.directory=Path(cls.tmp.name)
        load_module("v3_test_crypto",V1/"build_image.py").fetch_crypto(cls.directory)
        cls.harness=cls.directory/"harness.c"
        cls.harness.write_text('''
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "runtime_core.c"
static uint32_t guarded[480*270+2];
int main(int argc,char**argv){
 uint8_t b[65536];FILE*f=fopen(argv[1],"rb");if(!f)return 9;
 size_t n=fread(b,1,sizeof(b),f);fclose(f);
 if(!strcmp(argv[2],"frames")){
  framebuffer=guarded+1;stride=width=480;height=270;pixel_format=1;ready=1;
  unsigned commits=0,blocks=0,repeats=0;
  for(size_t i=0;i+16<=n;i+=16){unsigned oldhash=fnv(active_package,active_length),oldcounter=last_counter,oldlength=active_length;
   int result=rabbit_package_frame(b+i,0);
   if((result==2||result==3)&&(oldhash!=fnv(active_package,active_length)||oldcounter!=last_counter||oldlength!=active_length))return 6;
   commits+=result==1;blocks+=result==4;repeats+=result==5;}
  printf("%u %u %u %u\\n",commits,blocks,repeats,last_counter);return 0;
 }
 if(argc<4)return rabbit_package_verify_only(b,(uint32_t)n,(uint32_t)strtoul(argv[2],0,10));
 guarded[0]=0xdeadbeef;guarded[480*270+1]=0xdeadbeef;
 framebuffer=guarded+1;stride=width=480;height=270;pixel_format=1;ready=1;
 if(activate(b,(uint32_t)n)!=1)return 2;
 for(unsigned i=0;i<240;i++)if(rabbit_scene_tick(0))return 3;
 if(guarded[0]!=0xdeadbeef||guarded[480*270+1]!=0xdeadbeef)return 4;
 f=fopen(argv[3],"wb");if(!f)return 9;fprintf(f,"P6\\n480 270\\n255\\n");
 for(unsigned i=0;i<480*270;i++){unsigned c=framebuffer[i];fputc((c>>16)&255,f);fputc((c>>8)&255,f);fputc(c&255,f);}fclose(f);
 unsigned counter=last_counter;
 if(activate(b,(uint32_t)n)!=3||counter!=last_counter)return 5;
 return 0;
}
''')
        cls.check=cls.directory/"check"
        command=[shutil.which("cc"),"-std=c11","-O2","-Wall","-Wextra","-Werror","-Wno-attributes","-I",str(ROOT),"-I",str(cls.directory),str(cls.harness),str(cls.directory/"monocypher.c"),str(cls.directory/"monocypher-ed25519.c"),"-o",str(cls.check)]
        subprocess.run(command,check=True,capture_output=True,text=True)

    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()

    def c_accepts(self,data,minimum=0,render=None):
        path=self.directory/"package.bin";path.write_bytes(data)
        args=[str(self.check),str(path),str(minimum)]
        if render:args.append(str(render))
        return subprocess.run(args,check=False).returncode==0

    def sign(self,data):return bytes(data[:-64])+self.private.sign(bytes(data[:-64]))

    def reject_both(self,data):
        with self.assertRaises(PackageError):decode_package(data,self.public)
        self.assertFalse(self.c_accepts(data))

    def test_rgba256_rle128_and_exact_transport(self):
        decoded=decode_package(self.package,self.public)
        mouse=decoded["sprites"][1]
        self.assertEqual(len(decoded["palette"]),256)
        self.assertEqual((mouse["width"],mouse["height"]),(128,128))
        self.assertTrue(any(0<c[3]<255 for c in decoded["palette"]))
        self.assertGreater(len(self.package),4096)
        frames=encode_transfer(self.package)
        self.assertEqual(decode_transfer(frames),self.package)
        self.assertTrue(self.c_accepts(self.package))
        print(f"GRAPHICS: {len(self.package)} bytes, {len(frames)} frames, minimum {len(frames)*.45:.1f}s/burst")

    def test_v2_package_is_unchanged_and_accepted(self):
        legacy=compile_world(LEGACY/"worlds/cat-chases-mouse.json",1,self.private)
        self.assertEqual(hashlib.sha256(legacy).hexdigest(),"ccd9a10ad43e96c2bddcc58a3b2c2ce1643e250d944df241ece3aefa9ec210bb")
        decode_package(legacy,self.public);self.assertTrue(self.c_accepts(legacy))

    def test_c_scene_240_ticks_stays_in_framebuffer_and_rejects_replay(self):
        output=ROOT/"runs"/"mouse-c-frame.ppm";output.parent.mkdir(exist_ok=True)
        self.assertTrue(self.c_accepts(self.package,render=output))
        self.assertTrue(output.read_bytes().startswith(b"P6\n480 270\n255\n"))

    def test_c_alpha_blend_matches_independent_integer_reference(self):
        world={"schema_version":3,"world_id":"alpha-test","palette":["00000000","ff000080","0000ffff"],
               "sprites":[{"id":1,"name":"alpha","width":2,"height":1,"display_width":2,"display_height":1,"frames":["0102"]}],
               "objects":[{"id":1,"sprite":1,"program":1,"x":0,"y":0,"vx":0,"vy":0,"target":255}],
               "programs":[{"id":1,"name":"still","code":[0]}]}
        path=self.directory/"alpha.json";path.write_text(json.dumps(world))
        package=compile_world(path,1,self.private);image=self.directory/"alpha.ppm"
        self.assertTrue(self.c_accepts(package,render=image))
        raster=image.read_bytes().split(b"\n",3)[3]
        expected=bytes((foreground*128+background*127+127)//255
                       for foreground,background in zip((255,0,0),(18,24,38)))
        self.assertEqual(raster[:3],expected)
        self.assertEqual(raster[3*3:3*3+3],bytes((0,0,255)))

    def test_signature_counter_and_untrusted_creator(self):
        bad=bytearray(self.package);bad[80]^=1;self.reject_both(bytes(bad))
        self.assertFalse(self.c_accepts(self.package,1))
        with self.assertRaises(PackageError):decode_package(self.package,self.public,1)
        self.reject_both(self.package[:-64]+Ed25519PrivateKey.from_private_bytes(b"z"*32).sign(self.package[:-64]))

    def test_resigned_malformed_records_reject_in_both_decoders(self):
        base=bytearray(self.package);so=struct.unpack_from("<H",base,18)[0];oo=struct.unpack_from("<H",base,20)[0];po=struct.unpack_from("<H",base,22)[0]
        for label,offset,value in [("zero-rle",so+8,0),("size",so+1,129),("display",so+6,0),("zero-object",oo,0),("velocity",oo+8,127),("opcode",po+2,127),("transparent",35,255)]:
            with self.subTest(label=label):
                data=bytearray(base);data[offset]=value;self.reject_both(self.sign(data))

    def test_rle_bomb_and_missing_reordered_frames_reject(self):
        for data,expected in [(b"\xff\x01",8),(b"\x00\x01",8),(b"\x08",8),(b"\x07\x01",8),(b"\x08\xff",8)]:
            with self.assertRaises(PackageError):rle_decode(data,expected,2)
        frames=encode_transfer(self.package)
        for broken in [frames[:-2]+frames[-1:],frames[:1]+frames[2:3]+frames[1:2]+frames[3:]]:
            with self.assertRaises(TransportError):decode_transfer(broken)
        huge=bytes(65535);self.assertEqual(decode_transfer(encode_transfer(huge)),huge)
        with self.assertRaises(TransportError):encode_transfer(bytes(65536))

    def test_bad_json_and_native_effects_rejected_before_build(self):
        world=json.loads(self.world.read_text())
        for mutate in [lambda w:w.update(shell="bad"),lambda w:w["sprites"][1].update(width=True),lambda w:w["objects"][0].update(x=True),lambda w:w["sprites"][1].update(frames=["ff"]),lambda w:w["programs"][0].update(code=[1]*16+[0])]:
            candidate=copy.deepcopy(world);mutate(candidate)
            path=self.directory/"bad.json";path.write_text(json.dumps(candidate))
            with self.assertRaises((PackageError,ValueError)):compile_world(path,2,self.private)

    def test_checkpoint_loss_retry_and_final_receipt_are_idempotent(self):
        bundle=encode_segments(self.package)
        blocks=[[bytes.fromhex(uuid.replace("-","")) for uuid in group] for group in bundle["segments"]]
        sequence=blocks[0]+blocks[0]+[f for group in blocks[1:] for f in group]+blocks[-1]
        path=self.directory/"frames.bin";path.write_bytes(b"".join(sequence))
        result=subprocess.run([str(self.check),str(path),"frames"],capture_output=True,text=True,check=True)
        self.assertEqual(result.stdout.strip(),f"1 {len(blocks)} 1 1")
        # A missing chunk must not acknowledge staging or commit a world.
        path.write_bytes(b"".join(blocks[0][:3]+blocks[0][4:]))
        result=subprocess.run([str(self.check),str(path),"frames"],capture_output=True,text=True,check=True)
        self.assertEqual(result.stdout.strip(),"0 0 0 0")

    def test_failed_health_or_signature_keeps_previous_world(self):
        for health in (False,True):
            failed=bytearray(self.package);struct.pack_into("<I",failed,8,2)
            if health:failed[5]=1;failed=bytearray(self.sign(failed))
            # Otherwise the changed counter invalidates the signature.
            frames=encode_transfer(self.package)+encode_transfer(bytes(failed))
            path=self.directory/"frames.bin";path.write_bytes(b"".join(frames))
            result=subprocess.run([str(self.check),str(path),"frames"],capture_output=True,text=True,check=True)
            self.assertEqual(result.stdout.strip(),"1 0 0 1")


if __name__=="__main__":unittest.main(verbosity=2)
