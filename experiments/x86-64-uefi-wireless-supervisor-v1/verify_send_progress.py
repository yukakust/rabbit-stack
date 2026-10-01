#!/usr/bin/env python3
"""Offline regressions: journal, Mac-source adapter and installed RPv3 receiver."""
import ctypes as C
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import uuid
from pathlib import Path
from send_progress import Progress, run_logged
from build_image import NATIVE
from send_runtime import ROOT, encode_segments, sender_source


class Tests(unittest.TestCase):
    def setUp(self):
        (ROOT/'runs').mkdir(exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=ROOT/'runs',prefix='progress-test-')
        self.directory=Path(self.temp.name)
        self.path=self.directory/'progress.json'
        self.identity={'release':'exact-release','world':'exact-world','owner':'exact-owner'}
        self.hashes=['12345678','87654321','ABCDEF00']

    def tearDown(self): self.temp.cleanup()
    def journal(self,**kw):return Progress(self.path,self.identity,self.hashes,**kw)
    def event(self,block):return f'NATIVE CHECKPOINT block={block} hash={self.hashes[block-1]} family={"21" if block==3 else "22"}'

    def test_atomic_confirmed_progress_and_resume(self):
        journal=self.journal();journal.accept(self.event(1))
        saved=self.journal(resume=True)
        self.assertEqual(saved.confirmed,1)
        bundle={};saved.configure(bundle,900,8)
        self.assertEqual(bundle,dict(start_block=1,probe=True,frame_ms=900,max_attempts=8))
        self.assertEqual(self.path.stat().st_mode&0o777,0o600)
        self.assertFalse(json.loads(self.path.read_text())['receipt_authenticated'])

    def test_wrong_world_release_key_transport_and_counter_reject(self):
        self.journal()
        for field in ('release','world','owner','transport','counter','base','target'):
            other=dict(self.identity);other[field]='changed'
            for restart in (False,True):
                with self.assertRaises(ValueError):Progress(self.path,other,self.hashes,resume=not restart,restart=restart)

    def test_fresh_launch_never_silently_discards_progress(self):
        self.journal().accept(self.event(1))
        with self.assertRaises(ValueError):self.journal()
        self.assertEqual(self.journal(restart=True).confirmed,0)

    def test_no_state_resume_and_bad_state_reject(self):
        with self.assertRaises(ValueError):self.journal(resume=True)
        self.journal();data=json.loads(self.path.read_text());data['confirmed']=True
        self.path.write_text(json.dumps(data))
        with self.assertRaises(ValueError):self.journal(resume=True)

    def test_atomic_write_failure_retains_old_file(self):
        journal=self.journal();before=self.path.read_bytes()
        with patch('send_progress.os.replace',side_effect=OSError('disk full')):
            with self.assertRaises(OSError):journal.accept(self.event(1))
        self.assertEqual(self.path.read_bytes(),before)
        self.assertEqual(self.journal(resume=True).confirmed,0)

    def test_ctrl_c_stops_child_and_preserves_progress(self):
        pid_path=self.directory/'child.pid'
        child='import os,time; from pathlib import Path; Path('+repr(str(pid_path))+').write_text(str(os.getpid())); print('+repr(self.event(1))+',flush=True); time.sleep(20)'
        parent='''import os,signal,sys,threading
from send_progress import Progress,run_logged
p=Progress(sys.argv[1],{"release":"exact-release","world":"exact-world","owner":"exact-owner"},["12345678","87654321","ABCDEF00"])
threading.Timer(.5,lambda:os.kill(os.getpid(),signal.SIGINT)).start()
raise SystemExit(run_logged([sys.executable,"-c",sys.argv[2]],p,10))
'''
        result=subprocess.run([sys.executable,'-c',parent,str(self.path),child],cwd=ROOT,capture_output=True,text=True,timeout=5)
        self.assertEqual(result.returncode,130,result.stderr)
        self.assertEqual(self.journal(resume=True).confirmed,1)
        with self.assertRaises(ProcessLookupError):os.kill(int(pid_path.read_text()),0)

    def test_receipt_identity_sequence_family_and_completion(self):
        journal=self.journal()
        for line in (self.event(2),self.event(3),self.event(1).replace('12345678','99999999'),self.event(1).replace('22','21')):
            with self.assertRaises(ValueError):journal.accept(line)
        self.assertFalse(journal.accept('SEEN 128-BIT UUID=52412200-1234-5678-0000-000000000000'))
        journal.accept(self.event(1));journal.accept(self.event(1))
        journal.accept(self.event(2));journal.accept(self.event(3))
        self.assertTrue(self.journal(resume=True).complete)

    def test_process_log_and_final_receipt_required(self):
        journal=self.journal()
        program='\n'.join('print('+repr(self.event(i))+',flush=True)' for i in range(1,4))
        self.assertEqual(run_logged([sys.executable,'-c',program],journal,3),0)
        self.assertTrue(journal.complete)
        self.assertIn(b'NATIVE CHECKPOINT block=3',self.path.with_suffix('.log').read_bytes())
        other=Progress(self.directory/'other.json',self.identity,self.hashes)
        with self.assertRaises(ValueError):run_logged([sys.executable,'-c','print("done")'],other,3)

    def test_timeout_partial_line_preserves_checkpoint_and_stops_child(self):
        journal=self.journal()
        code='import time; print('+repr(self.event(1))+',flush=True); print("partial",end="",flush=True); time.sleep(10)'
        self.assertEqual(run_logged([sys.executable,'-c',code],journal,.3),4)
        self.assertEqual(self.journal(resume=True).confirmed,1)

    def test_sender_probe_replay_bounded_retries_and_diagnostics(self):
        source=sender_source()
        for marker in ('RESUME PROBE','RESUME REPLAY','startBlock','sender.probing=probe',
                       'self.attempts>self.maximumAttempts','ACK IGNORED','NATIVE CHECKPOINT',
                       'finalBlock ? 0x21 : 0x22','self.frameSeconds'):
            self.assertIn(marker,source)
        self.assertNotIn('[self scheduleAdvanceAfter:0.45]',source)
        self.assertIn('self.probing=NO; self.attempts=0; self.segment++',source)

    def test_installed_receiver_partial_block_lost_ack_resume_and_reboot(self):
        library=self.directory/'rx.so'
        subprocess.run(['cc','-shared','-fPIC','-O2','-I',str(NATIVE),str(NATIVE/'transport_core.c'),'-o',str(library)],check=True)
        receiver=C.CDLL(str(library));receiver.rabbit_rx_data.restype=C.c_void_p;receiver.rabbit_rx_length.restype=C.c_size_t
        data=bytes((i*17)%256 for i in range(1200));bundle=encode_segments(data)
        segments=[[uuid.UUID(f).bytes for f in block] for block in bundle['segments']]
        def send(block):return [receiver.rabbit_rx_frame(f) for f in block][-1]
        receiver.rabbit_rx_reset()
        self.assertEqual(send(segments[0]),3)
        # Partial next block: stale prior checkpoint is no longer acknowledged.
        send(segments[1][:9])
        self.assertEqual(receiver.rabbit_rx_frame(segments[0][-1]),1)
        self.assertEqual(receiver.rabbit_rx_frame(segments[1][-1]),1)
        self.assertEqual(send(segments[1]),3) # duplicate prefix + missing tail
        self.assertEqual(receiver.rabbit_rx_frame(segments[1][-1]),3) # lost ACK probe
        # One lost ordered frame: retry reconstructs, not an engine change.
        self.assertEqual(send(segments[2][:12]+segments[2][13:]),1)
        self.assertEqual(send(segments[2]),3)
        for block in segments[3:]:result=send(block)
        self.assertEqual(result,2)
        self.assertEqual(receiver.rabbit_rx_frame(segments[-1][-1]),2)
        self.assertEqual(C.string_at(receiver.rabbit_rx_data(),receiver.rabbit_rx_length()),data)
        receiver.rabbit_rx_reset()
        self.assertEqual(send(segments[1]),1) # no BEGIN: lost RAM cannot fake receipt

if __name__=='__main__':unittest.main(verbosity=2)
