#!/usr/bin/env python3
"""Owner C/Python authority and root-owned deferred-file checks; no radio."""
import ctypes as C
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
from build_image import ROOT,NATIVE,LINK,old,prepare,digest,build,verifier_source
from release import pack,verify,UpdateError

class Policy(C.Structure):
    _fields_=[('target',C.c_ubyte*32),('owner',C.c_ubyte*32),('base',C.c_ubyte*32),('state',C.c_ubyte*32),('counter',C.c_uint64)]

class Tests(unittest.TestCase):
    def test_qemu_log_hash_and_archive_use_one_immutable_snapshot(self):
        source=(ROOT/'run_qemu.py').read_text()
        self.assertEqual(source.count('observed_log=log.read_bytes()'),3)
        self.assertEqual(source.count('digest(observed_log).hex()'),3)
        self.assertEqual(source.count('.write_bytes(observed_log)'),3)
        self.assertNotIn('digest(log.read_bytes())',source)
        self.assertNotIn('.write_bytes(log.read_bytes())',source)

    def test_mac_digest_property_does_not_override_NSObject_hash(self):
        source=(LINK/'mac_file_sender.m').read_text()
        self.assertIn('NSData *stream,*nonce,*expectedDigest;',source)
        self.assertNotIn('self.hash',source)
        self.assertNotIn('s.hash=',source)
        self.assertIn('self.expectedDigest.bytes',source)
        for marker in ('DISCOVERED:', 'CONNECTED:', 'SERVICE DISCOVERY:',
                       'CHARACTERISTIC DISCOVERY:', 'BEGIN:', 'CONTROL ACK:',
                       'DISCONNECTED: phase=', 'setvbuf(stdout,NULL,_IONBF,0)'):
            self.assertIn(marker,source)
        compiler=(ROOT/'send_file.py').read_text()
        self.assertIn('-Werror=incompatible-property-type',compiler)
        self.assertIn('-Werror=objc-property-synthesis',compiler)
        for marker in ('rs_status(', 'STAGING CHECKPOINT=', 'RECEIVER STAGING REGRESSED:',
                       'STAGED-NOT-APPLIED:', 'self.status==waitingStatus'):
            self.assertIn(marker,source)
        self.assertIn("command.append(str(a.stage_only_bytes))",compiler)
        # Deliberate staging stop must exit before scheduling the next DATA/COMMIT.
        pause=source.index('if(self.pauseAfter&&received>=self.pauseAfter)')
        self.assertLess(source.index('exit(0);',pause),source.index('[self scheduleNext];',pause))

    @classmethod
    def setUpClass(cls):
        ROOT.joinpath('runs').mkdir(exist_ok=True)
        cls.temp=tempfile.TemporaryDirectory(prefix='host-',dir=ROOT/'runs');d=Path(cls.temp.name)
        cls.key=Ed25519PrivateKey.from_private_bytes(bytes(range(32,64)))
        cls.owner=cls.key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
        cls.target,cls.modules,crypto=prepare(d,cls.owner);cls.base=digest(cls.modules[1])
        (d/'host.c').write_text('''
#include "file_core.h"
#include "gatt_core.h"
#include "sender_status.h"
static RfFile file;static RgServer driver;static unsigned calls;
static int dispatch(uint8_t kind,const uint8_t*p,uint32_t n,uint32_t*counter){(void)p;(void)n;(void)counter;calls++;return kind==2?2:1;}
void host_init(int owner){if(owner)rf_init_owner(&file,dispatch);else rf_init(&file,0);calls=0;rg_init_shared(&driver,&file);}
int host_control(const uint8_t*p,unsigned n){return rf_control(&file,p,n);}
int host_data(const uint8_t*p,unsigned n){return rf_data(&file,p,n);}
int host_finish(int failed,unsigned counter){return rf_finish(&file,failed,counter);}
unsigned host_state(void){return file.state;}
unsigned host_calls(void){return calls;}
void host_swap(void){rg_init_shared(&driver,&file);}
unsigned host_status(uint8_t*out){return rg_att(&driver,(const uint8_t*)"\\x0a\\x07\\x00",3,out,247);}
unsigned host_status_full(uint8_t*out){
 rg_att(&driver,(const uint8_t*)"\\x02\\xf7\\x00",3,out,247);return host_status(out);
}
int host_status_check(const uint8_t*p,unsigned n,const uint8_t*nonce,const uint8_t*digest,unsigned counter,unsigned length){
 uint32_t received;return rs_status(p,n,nonce,digest,counter,length,&received);
}
''')
        lib=d/'host.so'
        subprocess.run(['cc','-std=c11','-O2','-shared','-fPIC','-Wall','-Wextra','-Werror',
            '-I',str(d),'-I',str(NATIVE),'-I',str(LINK),str(d/'host.c'),str(d/'native_verify.c'),
            str(LINK/'file_core.c'),str(LINK/'gatt_core.c'),str(NATIVE/'sha256.c'),*map(str,crypto),'-o',str(lib)],check=True)
        cls.lib=C.CDLL(str(lib));cls.lib.rabbit_update_verify.argtypes=[C.c_char_p,C.c_size_t,C.POINTER(Policy)]
        cls.lib.rabbit_module_pe.argtypes=[C.c_char_p,C.c_size_t]
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()
    def setUp(self):self.lib.host_init(1)
    def policy(self,counter=0):
        p=Policy();p.target[:]=self.target;p.owner[:]=self.owner;p.base[:]=self.base;p.state[:]=digest(b'world');p.counter=counter;return p
    def release(self):return pack(self.modules[2],private=self.key,target=self.target,base_runtime=self.base,world=b'world',counter=1)
    def begin(self,kind=2,length=33,session=b'12345678'):
        p=bytes([1,1,kind,0])+session+struct.pack('<I',length)
        return self.lib.host_control(p,len(p))
    def stage(self):
        data=digest(b'x')+b'x';self.assertEqual(self.begin(),0)
        p=bytes(4)+data;self.assertEqual(self.lib.host_data(p,len(p)),0)
        self.assertEqual(self.lib.host_control(b'\x0212345678',9),0)
    def test_rrt3_same_C_and_python_signature_authority(self):
        data=self.release();self.assertEqual(self.lib.rabbit_update_verify(data,len(data),C.byref(self.policy())),0)
        self.assertEqual(verify(data,target=self.target,owner=self.owner,base_runtime=self.base,world=b'world',counter=0).payload,self.modules[2])
        for offset in (0,16,32,64,96,128,160,len(data)-1):
            bad=bytearray(data);bad[offset]^=1
            self.assertNotEqual(self.lib.rabbit_update_verify(bytes(bad),len(bad),C.byref(self.policy())),0)
            with self.assertRaises(UpdateError):verify(bytes(bad),target=self.target,owner=self.owner,base_runtime=self.base,world=b'world',counter=0)
    def test_world_development_key_cannot_authorize_native(self):
        with self.assertRaises(UpdateError):pack(self.modules[2],private=Ed25519PrivateKey.from_private_bytes(bytes(range(32))),target=self.target,base_runtime=self.base,world=b'world',counter=1)
        self.lib.host_init(0);self.assertEqual(self.begin(kind=2),1)
    def test_stale_profile_and_counter_rejected(self):
        data=self.release();self.assertNotEqual(self.lib.rabbit_update_verify(data,len(data),C.byref(self.policy(1))),0)
        previous=old.load('connected_previous_release',ROOT.parent/'x86-64-uefi-wireless-supervisor-v1/release.py')
        rrt2=previous.pack(self.modules[2],private=self.key,target=self.target,base_runtime=self.base,world=b'world',counter=1)
        self.assertNotEqual(self.lib.rabbit_update_verify(rrt2,len(rrt2),C.byref(self.policy())),0)
    def test_modules_have_restricted_driver_PE_profile(self):
        for module in self.modules.values():self.assertEqual(self.lib.rabbit_module_pe(module,len(module)),0)
        with self.assertRaises(ValueError):build(old.TEST_OWNER)
    def test_receipt_waits_until_callback_return_and_explicit_finish(self):
        self.stage();self.assertEqual(self.lib.host_state(),4);self.assertEqual(self.lib.host_calls(),1)
        self.assertEqual(self.lib.host_control(b'\x0212345678',9),0);self.assertEqual(self.lib.host_calls(),1)
        self.assertEqual(self.lib.host_finish(0,9),0);self.assertEqual(self.lib.host_state(),2)
        self.assertEqual(self.lib.host_finish(0,9),1)
    def test_whole_stream_staging_remains_unapplied_until_explicit_commit(self):
        data=digest(b'x')+b'x';self.assertEqual(self.begin(kind=1,length=len(data)),0)
        packet=bytes(4)+data;self.assertEqual(self.lib.host_data(packet,len(packet)),0)
        self.assertEqual(self.lib.host_state(),1);self.assertEqual(self.lib.host_calls(),0)
        self.lib.host_status_check.argtypes=[C.c_char_p,C.c_uint,C.c_char_p,C.c_char_p,C.c_uint,C.c_uint]
        out=C.create_string_buffer(247);n=self.lib.host_status_full(out)
        self.assertEqual(n,61)
        self.assertEqual(self.lib.host_status_check(out.raw[1:n],60,b'12345678',digest(b'x'),1,len(data)),1)
        self.lib.host_swap();self.assertEqual(self.begin(kind=1,length=len(data)),0)
        self.assertEqual(self.lib.host_calls(),0)
        self.assertEqual(self.lib.host_control(b'\x0212345678',9),0)
        self.assertEqual(self.lib.host_calls(),1)
    def test_no_abort_substitution_or_data_while_native_pending(self):
        self.stage()
        self.assertEqual(self.lib.host_control(b'\x0312345678',9),1)
        self.assertEqual(self.begin(session=b'87654321'),1)
        self.assertEqual(self.begin(kind=1),1)
        self.assertEqual(self.lib.host_data(bytes(4)+b'x',5),1)
        self.assertEqual(self.lib.host_finish(1,3),0);self.assertEqual(self.lib.host_state(),3)
    def test_root_owned_receipt_survives_driver_reinitialization(self):
        self.stage();self.lib.host_finish(0,2)
        a=C.create_string_buffer(247);b=C.create_string_buffer(247)
        n=self.lib.host_status(a);self.lib.host_swap();m=self.lib.host_status(b)
        self.assertEqual(n,m);self.assertEqual(a.raw[:n],b.raw[:m]);self.assertEqual(self.lib.host_state(),2)

    def test_exact_consumed_counter_rejection_is_distinct_from_application(self):
        self.stage();self.assertEqual(self.lib.host_finish(1,1),0)
        out=C.create_string_buffer(247);n=self.lib.host_status_full(out)
        self.assertEqual(n,61);self.assertEqual(out.raw[0],0x0b)
        status=out.raw[1:n];data=b'x'
        self.lib.host_status_check.argtypes=[C.c_char_p,C.c_uint,C.c_char_p,C.c_char_p,C.c_uint,C.c_uint]
        def check(s):return self.lib.host_status_check(s,len(s),b'12345678',digest(data),1,len(data)+32)
        self.assertEqual(check(status),4)
        self.lib.host_swap();self.lib.host_status_full(out)
        self.assertEqual(check(out.raw[1:n]),4)
        self.assertEqual(check(status[:-1]),0)
        for index in (4,12,16,20,21,22,23,24,28,59):
            bad=bytearray(status);bad[index]^=1
            self.assertEqual(check(bytes(bad)),0,index)
        applied=bytearray(status);applied[20]=2;applied[21]=0
        self.assertEqual(check(bytes(applied)),2)
    def test_kind_limits_and_partial_commit(self):
        self.assertEqual(self.begin(1,65568),1);self.assertEqual(self.begin(2,262177),1)
        self.assertEqual(self.begin(2,262176),0)
        self.assertEqual(self.lib.host_control(b'\x0212345678',9),1)
        self.assertEqual(self.lib.host_finish(0,1),1)

    def test_saved_file_session_rejects_counter_or_digest_substitution(self):
        from prepare_file import bundle
        from send_file import validate
        import base64
        good=bundle(self.release(),2,1,b'12345678')
        self.assertEqual(validate(good),good)
        with self.assertRaises(ValueError):bundle(self.release(),2,2)
        wrong=dict(good);wrong['counter']=2
        with self.assertRaises(ValueError):validate(wrong)
        wrong=dict(good);raw=bytearray(base64.b64decode(wrong['stream_base64']));raw[-1]^=1
        wrong['stream_base64']=base64.b64encode(raw).decode()
        with self.assertRaises(ValueError):validate(wrong)

    def test_stage_stop_cli_rejects_invalid_limits_before_mac_or_radio(self):
        import json,sys
        from prepare_file import bundle
        path=Path(self.temp.name)/'stage-check.json'
        path.write_text(json.dumps(bundle(self.release(),2,1,b'12345678')))
        for args in (['--stage-only-bytes','1'],
                     [str(path),'--send','--stage-only-bytes','0'],
                     [str(path),'--send','--stage-only-bytes','-1'],
                     [str(path),'--send','--stage-only-bytes','999999']):
            result=subprocess.run([sys.executable,str(ROOT/'send_file.py'),*args],capture_output=True,text=True)
            self.assertEqual(result.returncode,2,result.stderr)
            self.assertIn('--stage-only-bytes',result.stderr)
            self.assertNotIn('MAC SENDER COMPILED',result.stdout)

    def test_native_trial_exact_gate_plan_and_owner_signing(self):
        import json,os,sys
        from prepare_native_trial import prepare_plan,sign_plan,checked_inputs
        from send_file import validate
        key=Ed25519PrivateKey.from_private_bytes(bytes(range(64,96)))
        owner=key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
        image,report,modules=build(owner)
        # Synthetic gate for helper validation, NOT an owner/QEMU observation.
        report.update(status='OWNER-OBSERVED-EXACT-MAC-QEMU-NO-DEVICE',qemu_verified=True,mac_sender_compile_verified=True)
        d=Path(self.temp.name)/'trial';d.mkdir()
        installed=d/'report.json';installed.write_text(json.dumps(report))
        (d/'connected-supervisor.img').write_bytes(image)
        payload=d/'driver-revision-2.efi';payload.write_bytes(modules[2])
        public=d/'owner.pub';public.write_bytes(owner)
        from build_image import V3
        sys.path.insert(0,str(V3))
        compiler=old.load('trial_world_compiler',V3/'compile_world.py')
        world=d/'world.rup';world.write_bytes(compiler.compile_world(V3/'worlds/ginger-cat-walk-v1.json',2,Ed25519PrivateKey.from_private_bytes(bytes(range(32)))))
        world_sha=digest(world.read_bytes()).hex();plan_path=d/'plan.json'
        plan=prepare_plan(installed,world,world_sha,public,plan_path)
        self.assertEqual(plan['native_counter'],1)
        with tempfile.TemporaryDirectory(prefix='rabbit-fixture-key-') as external:
            private=Path(external)/'owner.key';private.write_bytes(bytes(range(64,96)));os.chmod(private,0o600)
            with self.assertRaises(UpdateError):sign_plan(plan_path,private,'00'*32)
            self.assertFalse(plan_path.with_suffix('.rrt').exists())
            sign_plan(plan_path,private,digest(plan_path.read_bytes()).hex())
            validate(json.loads(plan_path.with_suffix('.session.json').read_text()))
            with self.assertRaises(UpdateError):sign_plan(plan_path,private,digest(plan_path.read_bytes()).hex())
        with self.assertRaises(UpdateError):checked_inputs(installed,world,'00'*32,public)
        payload.write_bytes(modules[1])
        with self.assertRaises(UpdateError):checked_inputs(installed,world,world_sha,public)
        payload.write_bytes(modules[2]);public.write_bytes(self.owner)
        with self.assertRaises(UpdateError):checked_inputs(installed,world,world_sha,public)

if __name__=='__main__':unittest.main(verbosity=2)
