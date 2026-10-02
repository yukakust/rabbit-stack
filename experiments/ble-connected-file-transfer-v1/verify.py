#!/usr/bin/env python3
"""Host ATT/file tests against the ACTUAL C world validator/renderer.

No Bluetooth traffic, USB, native payload execution or physical installation.
"""
import ctypes as C
import hashlib
import importlib.util
import random
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path
from prepare_transfer import ROOT,V3,compile_packet,bundle

NATIVE=ROOT.parent/'x86-64-uefi-runtime-supervisor-v1'
V1=ROOT.parent/'x86-64-uefi-god-runtime-v1'


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='rabbit-gatt-')
        d=Path(cls.temp.name)
        spec=importlib.util.spec_from_file_location('gatt_crypto_builder',V1/'build_image.py')
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.fetch_crypto(d)
        (d/'harness.c').write_text('''
#include <string.h>
#include "gatt_core.h"
#include "hci_link.h"
#include "runtime_core.c"
static RgServer server;
static uint32_t screen[480*270+2];
static unsigned commits;
static RlLink link;
static int apply(const uint8_t*p,uint32_t n,uint32_t*counter){
 int result=activate(p,n);if(result!=1)return 1;
 last_hash=fnv(active_package,active_length);*counter=last_counter;commits++;return 0;
}
void host_reset(void){memset(&server,0,sizeof(server));rg_init(&server,apply);
 active_length=object_count=last_counter=tick=commits=0;
 screen[0]=screen[480*270+1]=0xfeedface;
 framebuffer=screen+1;stride=width=480;height=270;pixel_format=1;ready=1;
}
size_t host_att(const uint8_t*p,size_t n,uint8_t*r){return rg_att(&server,p,n,r,247);}
unsigned host_counter(void){return last_counter;}
unsigned host_commits(void){return commits;}
unsigned host_hash(void){return fnv(active_package,active_length);}
unsigned host_tick(void){return rabbit_scene_tick(0)||screen[0]!=0xfeedface||screen[480*270+1]!=0xfeedface;}
void host_disconnect(void){rg_disconnected(&server);}
void host_link_init(void){rl_init(&link,apply);}
void host_event(const uint8_t*p,size_t n){rl_event(&link,p,n);}
void host_acl(const uint8_t*p,size_t n){rl_acl(&link,p,n);}
void host_bulk(const uint8_t*p,size_t n){rl_bulk(&link,p,n);}
size_t host_take(uint8_t*p,uint8_t*kind){return rl_take(&link,p,255,kind);}
unsigned host_link_state(void){return link.state;}
void host_elapsed(uint32_t ms){rl_elapsed(&link,ms);}
void host_stop(void){rl_stop(&link);}
''')
        subprocess.run(['cc','-std=c11','-O2','-shared','-fPIC','-Wall','-Wextra','-Werror','-Wno-attributes',
            '-I',str(ROOT),'-I',str(V3),'-I',str(NATIVE),'-I',str(d),str(d/'harness.c'),
            str(ROOT/'file_core.c'),str(ROOT/'gatt_core.c'),str(ROOT/'hci_link.c'),str(NATIVE/'sha256.c'),
            str(d/'monocypher.c'),str(d/'monocypher-ed25519.c'),'-o',str(d/'check.so')],check=True)
        cls.lib=C.CDLL(str(d/'check.so'))
        cls.lib.host_att.argtypes=[C.c_char_p,C.c_size_t,C.c_void_p];cls.lib.host_att.restype=C.c_size_t
        cls.cat=compile_packet(V3/'worlds/ginger-cat-walk-v1.json',2)
        cls.old=compile_packet(ROOT.parent/'x86-64-uefi-god-runtime-v2/worlds/cat-chases-mouse.json',1)

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def setUp(self):self.lib.host_reset();self.session=b'12345678'

    def att(self,p):
        guarded=C.create_string_buffer(249);guarded[0]=b'\xa5';guarded[248]=b'\x5a'
        n=self.lib.host_att(p,len(p),C.byref(guarded,1))
        self.assertLessEqual(n,247);self.assertEqual((guarded[0],guarded[248]),(b'\xa5',b'\x5a'))
        return guarded.raw[1:n+1]

    def write(self,handle,value):return self.att(b'\x12'+struct.pack('<H',handle)+value)

    def begin(self,p,session=None):
        nonce=self.session if session is None else session
        return self.write(3,b'\x01\x01\x01\x00'+nonce+struct.pack('<I',len(p)+32))

    def stream(self,p,start=0,chunk=16):
        data=hashlib.sha256(p).digest()+p
        for offset in range(start,len(data),chunk):
            self.assertEqual(self.write(5,struct.pack('<I',offset)+data[offset:offset+chunk]),b'\x13')
            self.assertEqual(self.lib.host_tick(),0)

    def commit(self):return self.write(3,b'\x02'+self.session)

    def status(self):
        result=self.att(b'\x0a\x07\x00')[1:]
        while len(result)<60:
            r=self.att(b'\x0c\x07\x00'+struct.pack('<H',len(result)))
            self.assertEqual(r[0],13);self.assertGreater(len(r),1);result+=r[1:]
        self.assertEqual(len(result),60);return result

    def deliver(self,p):self.assertEqual(self.begin(p),b'\x13');self.stream(p);self.assertEqual(self.commit(),b'\x13')

    def test_default_mtu_actual_cat_signature_health_commit(self):
        self.deliver(self.cat);s=self.status()
        self.assertEqual(s[:4],b'RFS\x01');self.assertEqual(s[20:22],b'\x02\x00')
        self.assertEqual(s[28:],hashlib.sha256(self.cat).digest());self.assertEqual(self.lib.host_counter(),2)
        for _ in range(240):self.assertEqual(self.lib.host_tick(),0)

    def test_lost_final_response_is_idempotent(self):
        self.deliver(self.cat)
        for _ in range(4):self.assertEqual(self.commit(),b'\x13')
        self.assertEqual(self.lib.host_commits(),1)
        self.assertEqual(self.begin(self.cat),b'\x13');self.assertEqual(self.status()[20],2)

    def test_disconnect_and_same_boot_resume_offset(self):
        self.assertEqual(self.begin(self.cat),b'\x13')
        data=hashlib.sha256(self.cat).digest()+self.cat
        self.assertEqual(self.write(5,struct.pack('<I',0)+data[:16]),b'\x13')
        self.lib.host_disconnect();self.assertEqual(self.begin(self.cat),b'\x13')
        self.assertEqual(struct.unpack_from('<I',self.status(),12)[0],16)
        self.stream(self.cat,start=16);self.commit();self.assertEqual(self.lib.host_counter(),2)

    def test_reorder_and_conflicting_duplicate_reject(self):
        self.begin(self.cat);data=hashlib.sha256(self.cat).digest()+self.cat
        self.assertEqual(self.write(5,struct.pack('<I',16)+data[16:32])[0],1)
        value=struct.pack('<I',0)+data[:16]
        self.assertEqual(self.write(5,value),b'\x13');self.assertEqual(self.write(5,value),b'\x13')
        self.assertEqual(self.write(5,value[:-1]+bytes([value[-1]^1]))[0],1)
        self.assertEqual(struct.unpack_from('<I',self.status(),12)[0],16)

    def test_signature_failure_keeps_exact_previous_world(self):
        self.deliver(self.old);old=self.lib.host_hash()
        self.session=b'abcdefgh';bad=self.cat[:-1]+bytes([self.cat[-1]^1]);self.deliver(bad)
        self.assertEqual(self.status()[20:22],b'\x03\x02')
        self.assertEqual(self.lib.host_hash(),old);self.assertEqual(self.lib.host_counter(),1)

    def test_sha_corruption_and_incomplete_commit_reject(self):
        self.begin(self.cat);self.assertEqual(self.commit()[0],1)
        data=bytes(32)+self.cat
        for offset in range(0,len(data),16):self.assertEqual(self.write(5,struct.pack('<I',offset)+data[offset:offset+16]),b'\x13')
        self.commit();self.assertEqual(self.status()[20:22],b'\x03\x01');self.assertEqual(self.lib.host_commits(),0)

    def test_authorized_health_failure_keeps_previous_world(self):
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        self.deliver(self.old);old=self.lib.host_hash();self.session=b'abcdefgh'
        body=bytearray(self.cat[:-64]);body[5]=1
        bad=bytes(body)+Ed25519PrivateKey.from_private_bytes(bytes(range(32))).sign(bytes(body))
        self.deliver(bad)
        self.assertEqual(self.status()[20:22],b'\x03\x02');self.assertEqual(self.lib.host_hash(),old)
        self.assertEqual(self.lib.host_counter(),1);self.assertEqual(self.lib.host_commits(),1)

    def test_mtu247_discovery_and_long_read(self):
        self.assertEqual(self.att(b'\x02\xf7\x00'),b'\x03\xf7\x00')
        self.assertEqual(self.att(bytes.fromhex('100100ffff0028'))[:2],b'\x11\x14')
        self.assertEqual(self.att(bytes.fromhex('080100ffff0328'))[:2],b'\x09\x15')
        self.begin(self.cat);self.stream(self.cat,chunk=240);self.commit()
        self.assertEqual(self.status()[20],2)

    def test_foreign_session_and_native_authority_reject(self):
        self.begin(self.cat)
        self.assertEqual(self.begin(self.old,b'abcdefgh')[0],1)
        self.assertEqual(self.write(3,b'\x02abcdefgh')[0],1)
        self.assertEqual(self.write(3,b'\x01\x01\x02\x00'+self.session+struct.pack('<I',256))[0],1)
        self.assertEqual(self.write(3,b'\x03'+self.session),b'\x13')
        self.assertEqual(self.begin(self.old,b'abcdefgh'),b'\x13')

    def test_reboot_has_no_hidden_persistence_and_replay_rejects(self):
        self.deliver(self.cat);self.session=b'abcdefgh';self.deliver(self.cat)
        self.assertEqual(self.lib.host_commits(),1);self.assertEqual(self.status()[20],3)
        self.lib.host_reset();self.assertEqual(self.status()[20],0)

    def test_malformed_att_bounded_and_no_false_apply(self):
        rng=random.Random(7)
        for _ in range(3000):
            n=rng.randrange(1,260);self.att(bytes(rng.randrange(256) for _ in range(n)))
        self.assertEqual(self.lib.host_commits(),0)

    def test_prepare_is_stable_with_explicit_session_and_no_radio(self):
        self.assertEqual(bundle(self.cat,2,self.session),bundle(self.cat,2,self.session))
        self.assertEqual(bundle(self.cat,2,self.session)['package_bytes'],33349)


if __name__=='__main__':unittest.main(verbosity=2)
