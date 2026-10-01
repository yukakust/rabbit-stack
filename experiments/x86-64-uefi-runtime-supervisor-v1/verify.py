#!/usr/bin/env python3
"""Host C/Python signature/PE/SHA differential checks and local key lifecycle."""
import ctypes
import hashlib
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest

from build_image import ROOT, REPO, CONTRACT, prepare_fixtures, crypto
from update import DOMAIN, HEADER, Policy, UpdateError, digest, verify, WORLD_DEVELOPMENT_PUBLIC
from owner_key import create, load_private
from transport import encode, frame, fnv
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat


class CPolicy(ctypes.Structure):
    _fields_ = [(name, ctypes.c_ubyte*32) for name in ("target", "owner", "base", "state")] + [("counter", ctypes.c_uint64)]


class NativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ROOT.joinpath("runs").mkdir(exist_ok=True)
        cls.temp = tempfile.TemporaryDirectory(prefix="verify-", dir=ROOT / "runs")
        cls.directory = Path(cls.temp.name)
        cls.fixtures = prepare_fixtures(cls.directory)
        cls.private = Ed25519PrivateKey.from_private_bytes(bytes(range(32, 64)))
        lib = cls.directory / "verify.so"
        subprocess.run(["cc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
                        "-I", str(ROOT), "-I", str(cls.directory), str(ROOT / "verify_core.c"), str(ROOT / "transport_core.c"),
                        str(ROOT / "sha256.c"), *map(str, crypto(cls.directory)), "-o", str(lib)], check=True)
        cls.c = ctypes.CDLL(str(lib))
        cls.c.rabbit_update_verify.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(CPolicy)]
        cls.c.rabbit_module_pe.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        cls.c.rabbit_sha256.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]
        cls.c.rabbit_rx_frame.argtypes = [ctypes.c_void_p]
        cls.c.rabbit_rx_data.restype = ctypes.c_void_p
        cls.c.rabbit_rx_length.restype = ctypes.c_size_t

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def policy(self, *, owner=None, counter=0):
        f = self.fixtures
        values = [f["identity"], f["public"] if owner is None else owner, f["base"], digest(f["states"][0])]
        return CPolicy(*( (ctypes.c_ubyte*32).from_buffer_copy(value) for value in values), counter)

    def c_accepts(self, data, policy=None):
        buffer = ctypes.create_string_buffer(data)
        return self.c.rabbit_update_verify(buffer, len(data), ctypes.byref(policy or self.policy())) == 0

    def resign(self, data):
        return data[:-64] + self.private.sign(DOMAIN + data[:-64])

    def test_sha256_matches_hashlib_padding_and_large_inputs(self):
        for n in (0, 1, 3, 55, 56, 63, 64, 65, 119, 120, 127, 128, 255, 4096, 262144):
            data = bytes((i*37+5) % 256 for i in range(n))
            output = ctypes.create_string_buffer(32)
            self.c.rabbit_sha256(output, ctypes.create_string_buffer(data), len(data))
            self.assertEqual(output.raw, hashlib.sha256(data).digest())

    def test_actual_signed_native_module_accepted_by_python_and_c(self):
        f = self.fixtures; data = f["updates"]["a"]
        policy = Policy(f["identity"], f["public"])
        accepted = verify(data, policy, base_runtime=f["base"], state=f["states"][0], minimum_counter=0)
        self.assertEqual(accepted.payload, f["modules"][1])
        self.assertTrue(self.c_accepts(data))
        for module in f["modules"].values():
            self.assertEqual(self.c.rabbit_module_pe(ctypes.create_string_buffer(module), len(module)), 0)

    def test_header_signature_payload_and_policy_rejection(self):
        data = self.fixtures["updates"]["a"]
        f = self.fixtures; policy = Policy(f["identity"], f["public"])
        for offset in (0,4,6,8,12,16,20,24,32,64,96,128,160,192,len(data)-1):
            changed = bytearray(data); changed[offset] ^= 1
            values = (bytes(changed),) if offset == len(data)-1 else (bytes(changed), self.resign(bytes(changed)))
            for value in values:
                with self.assertRaises(UpdateError):
                    verify(value, policy, base_runtime=f["base"], state=f["states"][0], minimum_counter=0)
                self.assertFalse(self.c_accepts(value))
        for bad in (b"", data[:-1], data+b"x"):
            self.assertFalse(self.c_accepts(bad))
        self.assertFalse(self.c_accepts(data, self.policy(counter=1)))

    def test_known_development_world_key_rejected_even_if_pinned(self):
        data = bytearray(self.fixtures["updates"]["a"])
        data[160:192] = WORLD_DEVELOPMENT_PUBLIC
        world_key = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
        data[-64:] = world_key.sign(DOMAIN + bytes(data[:-64]))
        self.assertFalse(self.c_accepts(bytes(data), self.policy(owner=WORLD_DEVELOPMENT_PUBLIC)))

    def test_pe_rejects_wrong_machine_subsystem_imports_and_writable_code(self):
        module = self.fixtures["modules"][1]
        pe = struct.unpack_from("<I", module, 60)[0]; opt = pe+24
        cases = []
        for offset, value, fmt in ((pe+4, 0xaa64, "<H"), (opt+68,10,"<H"),
                                   (opt+56,8*1024*1024,"<I"), (opt+112+9*8,1,"<I")):
            data = bytearray(module); struct.pack_into(fmt,data,offset,value); cases.append(data)
        section = opt+240
        data = bytearray(module); struct.pack_into("<I",data,section+36,0xe0000020); cases.append(data)
        imports = struct.unpack_from("<I",module,opt+120)[0]
        count = struct.unpack_from("<H",module,pe+6)[0]
        for i in range(count):
            record=section+i*40
            rva,raw,offset=struct.unpack_from("<III",module,record+12)
            if rva<=imports<rva+raw:
                data=bytearray(module);data[offset+imports-rva]=1;cases.append(data)
        for bad in [b"", module[:100], *cases]:
            self.assertNotEqual(self.c.rabbit_module_pe(ctypes.create_string_buffer(bytes(bad)),len(bad)),0)

    def test_owner_key_generate_permissions_no_overwrite_and_no_repo_secret(self):
        # Disposable test credential outside the repository; never provisioned.
        with tempfile.TemporaryDirectory(prefix="rabbit-key-test-", dir=os.environ.get("RABBIT_TMPDIR", str(REPO.parent))) as directory:
            private = Path(directory)/"owner.key"; public = Path(directory)/"owner.pub"
            fingerprint = create(private, public)
            key = load_private(private)
            self.assertEqual(key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw),public.read_bytes())
            self.assertEqual(fingerprint, digest(public.read_bytes()).hex())
            self.assertEqual(private.stat().st_mode & 0o777,0o600)
            original = private.read_bytes()
            with self.assertRaises((UpdateError,FileExistsError)):
                create(private, public)
            self.assertEqual(private.read_bytes(),original)
            private.chmod(0o644)
            with self.assertRaises(UpdateError):
                load_private(private)
        with self.assertRaises(UpdateError):
            create(ROOT/"runs/never-create.key",ROOT/"runs/never-create.pub")

    def test_c_stream_missing_chunk_checkpoint_and_retry(self):
        data=self.fixtures["updates"]["a"]; frames=encode(data)
        self.c.rabbit_rx_reset()
        feed=lambda f:self.c.rabbit_rx_frame(ctypes.create_string_buffer(f))
        for f in frames[:33]: self.assertEqual(feed(f),0)
        prefix=data[:32*6]; transfer=frames[0][3]
        checkpoint=frame(3,transfer,32,fnv(prefix).to_bytes(4,"big")+b"\0\0")
        self.assertEqual(feed(checkpoint),3)
        self.assertEqual(feed(checkpoint),3) # Lost checkpoint receipt.
        self.assertEqual(feed(frames[0]),0) # Same BEGIN preserves partial staging.
        self.assertEqual(feed(frames[1]),0) # Exact stale chunk safe.
        self.assertEqual(feed(frames[34]),1) # Chunk 32 missing; no advancement.
        self.assertEqual(feed(frames[33]),0)
        for f in frames[34:-1]: self.assertEqual(feed(f),0)
        self.assertEqual(feed(frames[-1]),2)
        self.assertEqual(feed(frames[-1]),2) # Supervisor must repeat receipt only.
        self.assertEqual(self.c.rabbit_rx_length(),len(data))
        self.assertEqual(ctypes.string_at(self.c.rabbit_rx_data(),len(data)),data)

    def test_c_stream_budget_version_corruption_reorder_and_large_roundtrip(self):
        self.c.rabbit_rx_reset()
        feed=lambda f:self.c.rabbit_rx_frame(ctypes.create_string_buffer(f))
        frames=encode(b"a"*100003)
        self.assertEqual(feed(frames[0]),0)
        self.assertEqual(feed(frames[2]),1)
        corrupt=bytearray(frames[1]);corrupt[9]^=1
        self.assertEqual(feed(bytes(corrupt)),1)
        for f in frames[1:-1]:self.assertEqual(feed(f),0)
        self.assertEqual(feed(frames[-1]),2)
        self.assertEqual(ctypes.string_at(self.c.rabbit_rx_data(),100003),b"a"*100003)
        self.assertEqual(feed(frame(1,1,0,(262145).to_bytes(4,"little")+b"\0\0")),1)
        old=bytearray(frames[0]);old[2]=0x21
        old[12:]=fnv(old[:12]).to_bytes(4,"big")
        self.assertEqual(feed(bytes(old)),1)

    def test_owner_sign_cli_requires_exact_review_and_never_sends(self):
        with tempfile.TemporaryDirectory(prefix="rabbit-sign-test-",dir=str(REPO.parent)) as directory:
            folder=Path(directory);secret=folder/"owner.key";public=folder/"owner.pub"
            create(secret,public)
            payload=folder/"module.efi";payload.write_bytes(self.fixtures["modules"][1])
            snapshot=folder/"state.bin";snapshot.write_bytes(self.fixtures["states"][0])
            output=folder/"update.rrt"
            command=[sys.executable,str(CONTRACT/"owner_key.py"),"sign",
                     "--private",str(secret),"--payload",str(payload),"--state",str(snapshot),
                     "--output",str(output),"--target-sha256",self.fixtures["identity"].hex(),
                     "--base-runtime-sha256",self.fixtures["base"].hex(),"--counter","1",
                     "--reviewed-payload-sha256","0"*64]
            rejected=subprocess.run(command,capture_output=True,text=True)
            self.assertNotEqual(rejected.returncode,0)
            self.assertFalse(output.exists())
            command[-1]=digest(payload.read_bytes()).hex()
            accepted=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(accepted.returncode,0,accepted.stderr)
            self.assertIn("SIGNED-NOT-SENT",accepted.stdout)
            result=verify(output.read_bytes(),Policy(self.fixtures["identity"],public.read_bytes()),
                          base_runtime=self.fixtures["base"],state=snapshot.read_bytes(),minimum_counter=0)
            self.assertEqual(result.payload,payload.read_bytes())
            original=output.read_bytes()
            repeated=subprocess.run(command,capture_output=True,text=True)
            self.assertNotEqual(repeated.returncode,0)
            self.assertEqual(output.read_bytes(),original)


if __name__ == "__main__":
    unittest.main(verbosity=2)
