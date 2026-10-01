#!/usr/bin/env python3
"""Host checks for Scene ABI, RRT2 authority and RPv3 checkpoint adapter."""
import ctypes as C
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
from build_image import ROOT,NATIVE,V3,prepare,digest,assembly_source,verifier_source,load,build,TEST_OWNER
from release import pack,verify,UpdateError
from send_runtime import encode_segments,sender_source,runtime_transport

class Policy(C.Structure):
    _fields_=[('target',C.c_ubyte*32),('owner',C.c_ubyte*32),('base',C.c_ubyte*32),('state',C.c_ubyte*32),('counter',C.c_uint64)]

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ROOT.joinpath('runs').mkdir(exist_ok=True)
        cls.temp=tempfile.TemporaryDirectory(prefix='host-',dir=ROOT/'runs');cls.directory=Path(cls.temp.name)
        cls.key=Ed25519PrivateKey.from_private_bytes(bytes(range(32,64)))
        cls.owner=cls.key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
        cls.target,cls.modules,cls.crypto=prepare(cls.directory,cls.owner)
        cls.base=digest(cls.modules[1])
        lib=cls.directory/'verify.so'
        subprocess.run(['cc','-shared','-fPIC','-O2','-I',str(NATIVE),'-I',str(cls.directory),str(cls.directory/'native_verify.c'),
                        str(NATIVE/'sha256.c'),str(NATIVE/'transport_core.c'),*map(str,cls.crypto),'-o',str(lib)],check=True)
        cls.native=C.CDLL(str(lib));cls.native.rabbit_update_verify.argtypes=[C.c_char_p,C.c_size_t,C.POINTER(Policy)]
        cls.native.rabbit_rx_data.restype=C.c_void_p;cls.native.rabbit_rx_length.restype=C.c_size_t
        # Wrappers bridge host SysV tests to reviewed EFI ms_abi callbacks.
        wrapper=cls.directory/'wrapper.c'
        wrapper.write_text('''#include "scene_module.c"
static uint32_t guarded[SURFACE_PIXELS+2];
static Surface test_surface={guarded+1,480,270,480,1};
int host_init(const uint8_t*p,uint32_t n){guarded[0]=0x12345678;guarded[SURFACE_PIXELS+1]=0x87654321;return scene_init(p,n,&test_surface);}
int host_tick(void){return scene_tick(&test_surface);}
int host_frame(const uint8_t*p){return scene_frame(p,&test_surface);}
int host_snapshot(uint8_t*p,uint32_t*n){return scene_export(p,SNAPSHOT_MAX,n);}
int host_canaries(void){return guarded[0]==0x12345678&&guarded[SURFACE_PIXELS+1]==0x87654321;}
''')
        cls.scenes=[]
        for mode in (1,2,3):
            path=cls.directory/f'scene-{mode}.so'
            subprocess.run(['cc','-shared','-fPIC','-O2','-D'+f'SCENE_REVISION={mode}','-I',str(ROOT),'-I',str(NATIVE),'-I',str(V3),'-I',str(cls.directory),
                            str(wrapper),*map(str,cls.crypto),'-o',str(path)],check=True)
            scene=C.CDLL(str(path));scene.host_init.argtypes=[C.c_char_p,C.c_uint32];scene.host_frame.argtypes=[C.c_char_p]
            cls.scenes.append(scene)
        import sys
        sys.path.insert(0,str(V3))
        compiler=load('wireless_test_world_compiler',V3/'compile_world.py')
        cls.world=compiler.compile_world(ROOT.parent/'x86-64-uefi-god-runtime-v2/worlds/cat-chases-mouse.json',1,
                                        Ed25519PrivateKey.from_private_bytes(bytes(range(32))))
        cls.world_transport=load('wireless_test_world_transport',V3/'transport.py')

    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()
    def policy(self,world=b'',counter=0):
        p=Policy();p.target[:]=self.target;p.owner[:]=self.owner;p.base[:]=self.base;p.state[:]=digest(world);p.counter=counter;return p
    def release(self,world=b'',counter=1):
        return pack(self.modules[2],private=self.key,target=self.target,base_runtime=self.base,world=world,counter=counter)
    def snapshot(self,scene):
        out=C.create_string_buffer(65823);n=C.c_uint32()
        self.assertEqual(scene.host_snapshot(out,C.byref(n)),0);return out.raw[:n.value]
    def init_world(self,scene):
        empty=b'RSS2'+struct.pack('<I',32)+bytes(24)
        self.assertEqual(scene.host_init(empty,len(empty)),0)
        results=[scene.host_frame(f) for f in self.world_transport.encode_transfer(self.world)]
        self.assertEqual(results[-1],1)

    def test_rrt2_c_python_authority_and_profile(self):
        data=self.release(self.world);policy=self.policy(self.world)
        self.assertEqual(self.native.rabbit_update_verify(data,len(data),C.byref(policy)),0)
        self.assertEqual(verify(data,target=self.target,owner=self.owner,base_runtime=self.base,world=self.world,counter=0).payload,self.modules[2])
        for offset in (0,16,32,64,96,128,160,len(data)-1):
            bad=bytearray(data);bad[offset]^=1
            self.assertNotEqual(self.native.rabbit_update_verify(bytes(bad),len(bad),C.byref(policy)),0)
            with self.assertRaises(UpdateError):verify(bytes(bad),target=self.target,owner=self.owner,base_runtime=self.base,world=self.world,counter=0)
        policy.state[:]=digest(b'other-world')
        self.assertNotEqual(self.native.rabbit_update_verify(data,len(data),C.byref(policy)),0)
        with self.assertRaises(UpdateError):pack(self.modules[1],private=Ed25519PrivateKey.from_private_bytes(bytes(range(32))),target=self.target,base_runtime=self.base,world=b'',counter=1)
        for pe in self.modules.values():self.assertEqual(self.native.rabbit_module_pe(pe,len(pe)),0)
        with self.assertRaises(ValueError):build(TEST_OWNER)

    def test_stale_counter_and_rrt1_are_not_silently_reinterpreted(self):
        data=self.release();policy=self.policy(counter=1)
        self.assertNotEqual(self.native.rabbit_update_verify(data,len(data),C.byref(policy)),0)
        from update import pack as old_pack
        old=old_pack(self.modules[2],private=self.key,target=self.target,base_runtime=self.base,state=b'',counter=1,supervisor_abi=2,state_abi=2)
        self.assertNotEqual(self.native.rabbit_update_verify(old,len(old),C.byref(self.policy())),0)
        with self.assertRaises(UpdateError):verify(old,target=self.target,owner=self.owner,base_runtime=self.base,world=b'',counter=0)

    def test_rgba_world_roundtrips_live_snapshot(self):
        import sys
        sys.path.insert(0,str(V3));compiler=load('wireless_graphics_test_compiler',V3/'compile_world.py')
        package=compiler.compile_world(V3/'worlds/cat-chases-smooth-mouse.json',2,Ed25519PrivateKey.from_private_bytes(bytes(range(32))))
        a,b,_=self.scenes;empty=b'RSS2'+struct.pack('<I',32)+bytes(24)
        self.assertEqual(a.host_init(empty,len(empty)),0)
        self.assertEqual([a.host_frame(f) for f in self.world_transport.encode_transfer(package)][-1],1)
        for _ in range(240):self.assertEqual(a.host_tick(),0)
        state=self.snapshot(a);self.assertEqual(b.host_init(state,len(state)),0);self.assertEqual(self.snapshot(b),state)
        self.assertEqual(a.host_canaries(),1);self.assertEqual(b.host_canaries(),1)

    def test_live_scene_snapshot_survives_engine_swap(self):
        a,b,_=self.scenes;self.init_world(a)
        for _ in range(120):self.assertEqual(a.host_tick(),0)
        state=self.snapshot(a);self.assertEqual(b.host_init(state,len(state)),0);self.assertEqual(self.snapshot(b),state)
        for _ in range(120):
            self.assertEqual(a.host_tick(),0);self.assertEqual(b.host_tick(),0)
            self.assertEqual(self.snapshot(a),self.snapshot(b))
        self.assertEqual(a.host_canaries(),1);self.assertEqual(b.host_canaries(),1)
        self.assertEqual(b.host_frame(self.world_transport.encode_transfer(self.world)[-1]),5)

    def test_bad_snapshot_and_unhealthy_trial_preserve_old_scene(self):
        a,_,bad=self.scenes;self.init_world(a);state=self.snapshot(a)
        self.assertEqual(bad.host_init(state,len(state)),1);self.assertEqual(self.snapshot(a),state)
        for offset in (0,4,16,21,32,32+len(self.world)):
            changed=bytearray(state);changed[offset]^=1
            self.assertEqual(self.scenes[1].host_init(bytes(changed),len(changed)),1)
        self.assertEqual(self.snapshot(a),state)

    def test_transport_checkpoint_loss_retry_and_final(self):
        data=self.release();segments=encode_segments(data);self.native.rabbit_rx_reset()
        import uuid
        for i,segment in enumerate(segments['segments']):
            frames=[uuid.UUID(value).bytes for value in segment]
            for f in frames:result=self.native.rabbit_rx_frame(f)
            self.assertEqual(result,2 if i==len(segments['segments'])-1 else 3)
            # A dropped receipt causes only exact already-buffered chunk retries.
            for f in frames:result=self.native.rabbit_rx_frame(f)
            self.assertEqual(result,2 if i==len(segments['segments'])-1 else 3)
        self.assertEqual(C.string_at(self.native.rabbit_rx_data(),self.native.rabbit_rx_length()),data)

    def test_sender_and_hardware_ownership_contract(self):
        source=sender_source();assembly=assembly_source()
        self.assertIn('finalBlock ? 0x21 : 0x22',source);self.assertIn('bytes[2]==0x23',source)
        self.assertNotIn('bytes[2] != 0x11',source);self.assertIn('call rabbit_receipt_write',assembly)
        self.assertIn('cmp r9d, 3',assembly);self.assertIn('call rabbit_scene_shutdown',assembly)
        self.assertIn('call scan_radio_cleanup_best_effort',assembly)
        self.assertIn('RRT2',verifier_source());self.assertIn('SCENE_REVISION', (ROOT/'scene_module.c').read_text())

    def test_new_signer_and_sender_are_explicit_and_create_only(self):
        from owner_key import create
        with tempfile.TemporaryDirectory(prefix='rabbit-owner-test-',dir=ROOT.parents[2]) as temporary:
            directory=Path(temporary);private=directory/'private';public=directory/'public';create(private,public)
            payload=directory/'scene.efi';payload.write_bytes(self.modules[2]);world=directory/'world.rup';world.write_bytes(self.world)
            output=directory/'release.rrt'
            command=[sys.executable,str(ROOT/'sign_runtime.py'),'--private',str(private),'--payload',str(payload),
                     '--world-package',str(world),'--output',str(output),'--target-sha256',self.target.hex(),
                     '--base-runtime-sha256',self.base.hex(),'--reviewed-payload-sha256',digest(self.modules[2]).hex(),'--counter','1']
            self.assertEqual(subprocess.run(command,capture_output=True).returncode,0)
            saved=output.read_bytes();self.assertNotEqual(subprocess.run(command,capture_output=True).returncode,0);self.assertEqual(output.read_bytes(),saved)
            command=[sys.executable,str(ROOT/'send_runtime.py'),str(output),'--owner-public',str(public),'--world-package',str(world),
                     '--target-sha256',self.target.hex(),'--base-runtime-sha256',self.base.hex(),'--minimum-counter','0']
            result=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr);self.assertIn('VERIFIED-NOT-SENT',result.stdout)
            world.write_bytes(b'other-world');self.assertNotEqual(subprocess.run(command,capture_output=True).returncode,0)

if __name__=='__main__':unittest.main(verbosity=2)
