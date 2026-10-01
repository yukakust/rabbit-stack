#!/usr/bin/env python3
"""Synthetic HCI regression; never radios, executes attached PE, or rewrites EFI."""
import argparse
import ctypes as C
import platform
import subprocess
import tempfile
import unittest
import uuid
from pathlib import Path
from build_image import ROOT,NATIVE,assembly_source,digest
from send_runtime import advertising_bundle,encode_segments,runtime_transport
from send_progress import Progress

# Public transport bytes of the observed blocker, NOT executable module bytes.
BLOCKER='52503293-3F07-488D-5250-4881F9520AE8'
RELEASE=None

def report(frame):
    # Legacy advertising report: flags, Complete 128-bit Service UUID list.
    # CoreBluetooth advertises service UUID octets in little-endian order.
    ad=b'\x02\x01\x06\x11\x07'+frame[::-1]
    body=b'\x02\x01\x00\x01'+bytes.fromhex('112233445566')+bytes([len(ad)])+ad+b'\xc0'
    return b'\x3e'+bytes([len(body)])+body

def model_parse(event):
    # Independent transcription of the installed first-match scanner. Failure
    # exits the entire event, instead of continuing to the next UUID candidate.
    for offset in range(len(event)-15):
        window=event[offset:offset+16]
        if window[:2]==b'RP':candidate=window
        elif window[14:]==b'PR':candidate=window[::-1]
        else:continue
        if (candidate[:2]!=b'RP' or candidate[2]>>4 not in (2,3)
                or int.from_bytes(candidate[12:],'big')!=runtime_transport.fnv(candidate[:12])
                or candidate[2]&15 not in (1,2,3)):
            return None
        return candidate
    return None

def parser_harness():
    source=assembly_source()
    start=source.index('    mov rcx, [rsp + 0x98]\n    sub rcx, 15')
    end=source.index('\nscan_frame_begin:',start)
    # SysV wrapper around UNCHANGED actual scanner instructions; fake firmware
    # labels return accepted frame or rejection. No privileged/radio operations.
    return '''.intel_syntax noprefix
.text
.globl host_parse
.type host_parse,@function
host_parse:
    cmp rsi, 20
    jb parse_early_fail
    cmp rsi, 80
    ja parse_early_fail
    mov r10, rdi
    mov r11, rdx
    sub rsp, 0x708
    mov [rsp + 0x98], rsi
    mov rcx, rsi
    mov rsi, r10
    lea rdi, [rsp + 0xa0]
    rep movsb
'''+source[start:end]+'''
scan_frame_begin:
scan_frame_chunk:
scan_frame_commit:
    lea rsi, [rsp + 0x430]
    mov rdi, r11
    mov ecx, 16
    rep movsb
    xor eax, eax
    add rsp, 0x708
    ret
scan_scan_event_loop:
    mov eax, 1
    add rsp, 0x708
    ret
parse_early_fail:
    mov eax, 1
    ret
.section .note.GNU-stack,"",@progbits
'''

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (ROOT/'runs').mkdir(exist_ok=True)
        cls.temp=tempfile.TemporaryDirectory(prefix='uuid-test-',dir=ROOT/'runs')
        cls.directory=Path(cls.temp.name);cls.native=None
        if platform.system()=='Linux' and platform.machine().lower() in ('x86_64','amd64'):
            source=cls.directory/'parser.S';source.write_text(parser_harness())
            library=cls.directory/'parser.so'
            subprocess.run(['cc','-shared','-fPIC','-o',str(library),str(source)],check=True)
            cls.native=C.CDLL(str(library))
            cls.native.host_parse.argtypes=[C.c_char_p,C.c_size_t,C.c_void_p]

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def parse(self,event):
        model=model_parse(event)
        if self.native:
            output=C.create_string_buffer(16)
            result=self.native.host_parse(event,len(event),output)
            self.assertEqual(None if result else output.raw,model)
        return model

    def test_observed_frame_rejects_standard_and_accepts_reversed(self):
        frame=uuid.UUID(BLOCKER).bytes
        self.assertEqual(runtime_transport.fnv(frame[:12]),int.from_bytes(frame[12:],'big'))
        self.assertIsNone(self.parse(report(frame)))
        self.assertEqual(self.parse(report(frame[::-1])),frame)

    def test_conversion_is_involution_and_does_not_change_hashes_or_config(self):
        data=bytes((i*17)%256 for i in range(1200));bundle=encode_segments(data)
        bundle.update(start_block=2,probe=True,frame_ms=450,max_attempts=3)
        converted=advertising_bundle(bundle,'reversed')
        self.assertEqual(advertising_bundle(converted,'reversed')['segments'],bundle['segments'])
        self.assertEqual(advertising_bundle(bundle,'standard')['segments'],bundle['segments'])
        for field in ('hashes','start_block','probe','frame_ms','max_attempts'):
            self.assertEqual(converted[field],bundle[field])
        with self.assertRaises(ValueError):advertising_bundle(bundle,'unknown')

    def test_mode_change_keeps_existing_resume_journal_binding(self):
        bundle=encode_segments(bytes((i*17)%256 for i in range(1200)))
        path=self.directory/'resume.json';identity={'release':'fixture','hashes':bundle['hashes']}
        journal=Progress(path,identity,bundle['hashes'])
        journal.accept('NATIVE CHECKPOINT block=1 hash='+bundle['hashes'][0]+' family=22')
        resumed=Progress(path,identity,bundle['hashes'],resume=True)
        resumed.configure(bundle,450,3)
        changed=advertising_bundle(bundle,'reversed')
        self.assertEqual(changed['start_block'],1);self.assertTrue(changed['probe'])

    def test_exact_owner_release_synthetic_hci_before_and_after(self):
        if RELEASE is None:self.skipTest('optional exact owner release supplied via --release')
        data=RELEASE.read_bytes();bundle=encode_segments(data)
        self.assertEqual(digest(data).hex(),'d16b740da692ab45e680cb0a91304ffd9559e129026865889a0c76b6c33b01db')
        failures=[];accepted=[]
        converted=advertising_bundle(bundle,'reversed')
        for bi,block in enumerate(bundle['segments']):
            for fi,value in enumerate(block):
                frame=uuid.UUID(value).bytes
                if self.parse(report(frame))!=frame:failures.append((bi+1,fi+1,value))
                wire_value=uuid.UUID(converted['segments'][bi][fi]).bytes
                self.assertEqual(self.parse(report(wire_value)),frame)
                accepted.append(frame)
        self.assertEqual(failures,[(58,32,BLOCKER)])
        library=self.directory/'rx.so'
        subprocess.run(['cc','-shared','-fPIC','-O2','-I',str(NATIVE),str(NATIVE/'transport_core.c'),'-o',str(library)],check=True)
        receiver=C.CDLL(str(library));receiver.rabbit_rx_data.restype=C.c_void_p;receiver.rabbit_rx_length.restype=C.c_size_t
        receiver.rabbit_rx_reset()
        # Reproduce the old parser's partial block 58, then the exact same-boot
        # checkpoint probe and block replay with changed CBUUID representation.
        for bi,block in enumerate(bundle['segments'][:58]):
            for value in block:
                parsed=self.parse(report(uuid.UUID(value).bytes))
                if parsed is not None:result=receiver.rabbit_rx_frame(parsed)
            self.assertEqual(result,1 if bi==57 else 3)
        self.assertEqual(receiver.rabbit_rx_length(),1855*6)
        checkpoint=self.parse(report(uuid.UUID(converted['segments'][57][-1]).bytes))
        self.assertEqual(receiver.rabbit_rx_frame(checkpoint),1)
        for value in converted['segments'][57]:
            result=receiver.rabbit_rx_frame(self.parse(report(uuid.UUID(value).bytes)))
        self.assertEqual(result,3)
        self.assertEqual(receiver.rabbit_rx_length(),11136)
        self.assertEqual(C.string_at(receiver.rabbit_rx_data(),11136),data[:11136])
        receiver.rabbit_rx_reset()
        for frame in accepted:result=receiver.rabbit_rx_frame(frame)
        self.assertEqual(result,2)
        self.assertEqual(C.string_at(receiver.rabbit_rx_data(),receiver.rabbit_rx_length()),data)
        print(f'EXACT RELEASE: {len(accepted)} synthetic HCI frames; original rejects block 58/frame 32; reversed accepts all')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--release',type=Path)
    args=parser.parse_args();RELEASE=args.release
    unittest.main(argv=[__file__],verbosity=2)
