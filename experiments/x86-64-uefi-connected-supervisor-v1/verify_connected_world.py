#!/usr/bin/env python3
"""Host-only V3 intent, C health, custody and uncertain-delivery checks."""
import copy
import base64
import json
import os
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import ask_connected_world as flow


class WorldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='connected-intent-check-')
        cls.root = Path(cls.temp.name)
        cls.base = flow.read_json(flow.V3 / 'worlds/ginger-cat-walk-v1.json', 2 * 1024 * 1024)
        cls.world = cls.root / 'base.json'; flow.save(cls.world, cls.base)
        cls.packet = cls.root / 'base.rup'; cls.packet.write_bytes(flow.compile_world(cls.world, 2, flow.CREATOR))
        cls.gate = cls.root / 'gate.json'
        flow.save(cls.gate, {'status': 'OWNER-OBSERVED-EXACT-MAC-QEMU-NO-DEVICE', 'source_hashes': {
            'experiments/x86-64-uefi-god-runtime-v3/runtime_core.c': flow.sha((flow.V3 / 'runtime_core.c').read_bytes())}})

    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    def state(self):
        directory = Path(tempfile.mkdtemp(dir=self.root))
        path = directory / 'state.json'
        return path, flow.initialize(path, self.world, self.packet, self.gate)

    def proposal(self):
        objects = copy.deepcopy(self.base['objects']); objects[0]['vx'] = 2
        return {'status': 'ready', 'explanation': 'Кот быстрее',
                'base_world_sha256': flow.sha(flow.canonical(self.base)),
                'objects': objects, 'programs': copy.deepcopy(self.base['programs'])}

    def test_edit_preserves_four_pose_assets_and_rejects_stale_or_extra_fields(self):
        result = flow.apply_edit(self.base, self.proposal())
        self.assertEqual(result['sprites'], self.base['sprites'])
        self.assertEqual(result['palette'], self.base['palette'])
        self.assertEqual(result['objects'][0]['vx'], 2)
        for proposal in [dict(self.proposal(), base_world_sha256='0' * 64),
                         dict(self.proposal(), native_code='arbitrary')]:
            with self.assertRaises(ValueError): flow.apply_edit(self.base, proposal)
        bad = self.proposal(); bad['objects'][0]['vx'] = True
        with self.assertRaises(ValueError): flow.parse_edit(json.dumps(bad))

    def test_complete_asset_candidate_cannot_smuggle_native_fields_or_legacy_world(self):
        for world in [dict(self.base, native_code='not data'), dict(self.base, schema_version=2)]:
            path, state = self.state()
            with self.assertRaises(ValueError):
                flow.prepare_world(path, state, 'asset fixture', world, {'kind': 'asset-fixture'})
            self.assertIsNone(flow.read_json(path)['pending'])
            self.assertEqual(flow.read_json(path)['counter'], 2)

    def test_actual_resident_c_accepts_speed_edit_and_rejects_unsafe_first_tick(self):
        path, state = self.state()
        directory, report = flow.prepare(path, state, 'кот быстрее', self.proposal())
        self.assertEqual(report['host_checks']['host_ticks'], 240)
        self.assertFalse(report['physical_execution_verified'])
        self.assertEqual(flow.read_json(path)['counter'], 2)
        self.assertEqual(flow.read_json(directory / 'session.json')['counter'], 3)
        path, state = self.state()
        bad = self.proposal(); bad['objects'][0].update(x=159, vx=8)
        bad['programs'][0]['code'] = [1, 0]  # MOVE without a boundary handler.
        with self.assertRaisesRegex(ValueError, 'resident C world checks failed'):
            flow.prepare(path, state, 'unsafe fixture', bad)
        self.assertIsNone(flow.read_json(path)['pending'])
        self.assertEqual(flow.read_json(path)['counter'], 2)

    def prepared(self):
        path, state = self.state()
        with patch.object(flow, 'check_world', return_value={'host_ticks': 240, 'test_fixture': True}):
            directory, _ = flow.prepare(path, state, 'host-only transport fixture', self.proposal())
        return path, state, directory

    def receipt(self, directory, state=0, received=0, foreign=False):
        session = flow.read_json(directory / 'session.json')
        stream = base64.b64decode(session['stream_base64'])
        nonce = base64.b64decode(session['session_base64'])
        raw = bytearray(60); raw[:4] = b'RFS\1'; raw[4:12] = b'foreign!' if foreign else nonce
        struct.pack_into('<II', raw, 12, received, len(stream) if state else 0)
        raw[20] = state; raw[21] = 2 if state == 3 else 0
        if state in (2, 3):
            struct.pack_into('<I', raw, 24, session['counter']); raw[28:60] = stream[:32]
        return subprocess.CompletedProcess([], 0, 'RFS STATUS HEX=' + raw.hex() + '\n')

    def runs(self, outcomes):
        responses = iter(outcomes)
        def run(command, **kwargs):
            response = next(responses)
            kwargs['stdout'].write(response.stdout)
            return response
        return run

    def staged(self, directory):
        length = len(base64.b64decode(flow.read_json(directory / 'session.json')['stream_base64']))
        return subprocess.CompletedProcess([], 0, f'STAGING CHECKPOINT={length}/{length}\nSTAGED-NOT-APPLIED: stop\n')

    def test_failure_retains_counter_and_same_nonce_then_exact_receipt_advances(self):
        path, state, directory = self.prepared()
        session_before = (directory / 'session.json').read_bytes()
        outcomes = [self.receipt(directory), subprocess.CompletedProcess([], 1, 'timeout'),
                    self.receipt(directory, 1, 1000), subprocess.CompletedProcess([], 1, 'timeout')]
        with patch.object(flow, 'check_world', return_value={}), patch.object(flow.subprocess, 'run', side_effect=self.runs(outcomes)):
            self.assertEqual(flow.deliver(path, state), 1)
        state = flow.read_json(path); self.assertEqual(state['counter'], 2)
        with self.assertRaisesRegex(ValueError, 'pending delivery'):
            flow.prepare(path, state, 'new request', self.proposal())
        applied = 'FILE APPLIED RECEIPT (NOT ATTESTATION): exact SHA256/session/counter matched'
        outcomes = [self.receipt(directory, 1, 1000), self.staged(directory), subprocess.CompletedProcess([], 0, applied)]
        with patch.object(flow, 'check_world', return_value={}), patch.object(flow.subprocess, 'run', side_effect=self.runs(outcomes)) as sender:
            self.assertEqual(flow.deliver(path, state), 0)
            first = sender.call_args_list[1].args[0]
            self.assertIn('--data-delay-ms', first)
            self.assertIn(str(len(self.packet.read_bytes()) + 31), first)
        self.assertEqual((directory / 'session.json').read_bytes(), session_before)
        state = flow.read_json(path); self.assertEqual(state['counter'], 3); self.assertIsNone(state['pending'])
        self.assertEqual(flow.current(state)['objects'][0]['vx'], 2)

    def test_exit_zero_without_exact_receipt_cannot_advance_current_world(self):
        path, state, directory = self.prepared()
        outcomes = [self.receipt(directory), subprocess.CompletedProcess([], 0, 'no receipt'),
                    self.receipt(directory, 1, 0), subprocess.CompletedProcess([], 0, 'no receipt')]
        with patch.object(flow, 'check_world', return_value={}), patch.object(flow.subprocess, 'run', side_effect=self.runs(outcomes)):
            self.assertEqual(flow.deliver(path, state), 1)
        self.assertEqual(flow.read_json(path)['counter'], 2)
        self.assertIsNotNone(flow.read_json(path)['pending'])

    def test_discard_only_never_sent_draft_keeps_current_and_blocks_uncertain_discard(self):
        path, state, directory = self.prepared()
        with patch.object(flow.sys, 'argv', ['ask_connected_world.py', '--state', str(path), '--discard']):
            self.assertEqual(flow.main(), 0)
        self.assertEqual(flow.read_json(path)['counter'], 2)
        self.assertIsNone(flow.read_json(path)['pending'])
        self.assertEqual(flow.read_json(directory / 'report.json')['status'], 'DISCARDED-NEVER-SENT')
        path, state, directory = self.prepared()
        outcomes = [self.receipt(directory), subprocess.CompletedProcess([], 1, 'timeout'), subprocess.CompletedProcess([], 1, 'query timeout')]
        with patch.object(flow, 'check_world', return_value={}), patch.object(flow.subprocess, 'run', side_effect=self.runs(outcomes)):
            self.assertEqual(flow.deliver(path, state), 1)
        with patch.object(flow.sys, 'argv', ['ask_connected_world.py', '--state', str(path), '--discard']):
            with self.assertRaisesRegex(ValueError, 'delivery may have started'):
                flow.main()
        self.assertEqual(flow.read_json(path)['pending'], str(directory))

    def test_saved_session_or_package_substitution_stops_before_radio(self):
        for artifact in ('session.json', 'world.rup'):
            path, state, directory = self.prepared()
            p = directory / artifact; p.write_bytes(p.read_bytes() + b' ')
            with patch.object(flow.subprocess, 'run') as radio:
                with self.assertRaises(ValueError): flow.deliver(path, state)
                radio.assert_not_called()

    def test_lost_commit_response_reconciles_exact_receipt_without_resending(self):
        path, state, directory = self.prepared()
        length = len(base64.b64decode(flow.read_json(directory / 'session.json')['stream_base64']))
        outcomes = [self.receipt(directory), self.staged(directory),
                    subprocess.CompletedProcess([], 1, 'lost COMMIT response'), self.receipt(directory, 2, length)]
        with patch.object(flow, 'check_world', return_value={}), patch.object(flow.subprocess, 'run', side_effect=self.runs(outcomes)) as sender:
            self.assertEqual(flow.deliver(path, state), 0)
            self.assertEqual(sum('--send' in c.args[0] for c in sender.call_args_list), 2)
        self.assertEqual(flow.read_json(path)['counter'], 3)
        self.assertEqual(flow.read_json(directory / 'report.json')['last_receiver_status']['outcome'], 'applied')

    def test_saved_partial_log_survives_process_crash_and_blocks_prefix_regression(self):
        for receiver_state, received in [(1, 499), (0, 0), (2, 0)]:
            path, state, directory = self.prepared()
            log = directory / 'crashed-stage.log'
            length = len(base64.b64decode(flow.read_json(directory / 'session.json')['stream_base64']))
            log.write_text(f'STAGING CHECKPOINT=500/{length}\n')
            report = flow.read_json(directory / 'report.json')
            report['sender_steps'].append({'name': 'paced-stage', 'log': str(log), 'exit_code': None})
            flow.save(directory / 'report.json', report)
            # A foreign old final receipt also cannot justify replay after a possibly reset receiver.
            if receiver_state == 2: received = length
            outcomes = [self.receipt(directory, receiver_state, received, foreign=receiver_state == 2)]
            with patch.object(flow, 'check_world', return_value={}), patch.object(flow.subprocess, 'run', side_effect=self.runs(outcomes)) as sender:
                self.assertEqual(flow.deliver(path, state), 1)
                self.assertEqual(sender.call_count, 1)
                self.assertIn('--query-only', sender.call_args.args[0])
            self.assertEqual(flow.read_json(directory / 'report.json')['status'], 'RECOVERY-REQUIRED-RECEIVER-LOSS')
            self.assertEqual(flow.read_json(path)['counter'], 2)

    def test_foreign_active_pending_and_exact_rejection_never_send(self):
        for receiver_state, foreign, expected in [(1, True, 1), (4, True, 1), (4, False, 1), (3, False, 2)]:
            path, state, directory = self.prepared()
            length = len(base64.b64decode(flow.read_json(directory / 'session.json')['stream_base64']))
            outcomes = [self.receipt(directory, receiver_state, length, foreign)]
            with patch.object(flow, 'check_world', return_value={}), patch.object(flow.subprocess, 'run', side_effect=self.runs(outcomes)) as sender:
                self.assertEqual(flow.deliver(path, state), expected)
                self.assertEqual(sender.call_count, 1)
            self.assertEqual(flow.read_json(path)['counter'], 2)
            self.assertIsNotNone(flow.read_json(path)['pending'])

    def test_preflight_floor_is_passed_to_actual_sender_to_close_reset_race(self):
        path, state, directory = self.prepared()
        outcomes = [self.receipt(directory, 1, 500),
                    subprocess.CompletedProcess([], 1, 'RECEIVER STAGING REGRESSED: previously confirmed=500 now=0')]
        with patch.object(flow, 'check_world', return_value={}), patch.object(flow.subprocess, 'run', side_effect=self.runs(outcomes)) as sender:
            self.assertEqual(flow.deliver(path, state), 1)
            command = sender.call_args.args[0]
            self.assertEqual(command[command.index('--minimum-received') + 1], '500')
        with patch.object(flow, 'check_world', return_value={}), patch.object(flow.subprocess, 'run') as sender:
            self.assertEqual(flow.deliver(path, flow.read_json(path)), 1)
            sender.assert_not_called()

    def test_timeout_archives_partial_output_and_preserves_pending(self):
        path, state, directory = self.prepared()
        count = 0
        def run(command, **kwargs):
            nonlocal count
            count += 1
            if count == 1:
                kwargs['stdout'].write(self.receipt(directory).stdout)
                return subprocess.CompletedProcess([], 0)
            if count == 2:
                length = len(base64.b64decode(flow.read_json(directory / 'session.json')['stream_base64']))
                kwargs['stdout'].write(f'STAGING CHECKPOINT=700/{length}\n')
                raise subprocess.TimeoutExpired(command, 380)
            kwargs['stdout'].write('query failed')
            return subprocess.CompletedProcess([], 1)
        with patch.object(flow, 'check_world', return_value={}), patch.object(flow.subprocess, 'run', side_effect=run):
            self.assertEqual(flow.deliver(path, state), 1)
        report = flow.read_json(directory / 'report.json')
        self.assertEqual(report['confirmed_received'], 700)
        self.assertIn('ORCHESTRATOR TIMEOUT', Path(report['sender_steps'][1]['log']).read_text())
        self.assertIsNotNone(flow.read_json(path)['pending'])

    def test_status_is_local_by_default_and_receipt_parser_rejects_ambiguous_output(self):
        path, state, directory = self.prepared()
        with patch.object(flow.subprocess, 'run') as radio:
            view = flow.status_view(path, state)
            radio.assert_not_called()
        self.assertEqual(view['current_world']['counter'], 2)
        self.assertEqual(view['pending']['counter'], 3)
        session = flow.read_json(directory / 'session.json')
        text = self.receipt(directory).stdout
        for invalid in [text + text, 'RFS STATUS HEX=abcd\n', text.replace('52465301', '52465300')]:
            with self.assertRaises(ValueError): flow.parse_status(invalid, session)

    def test_status_query_does_not_promote_pending_world(self):
        path, state, directory = self.prepared()
        before = path.read_bytes()
        length = len(base64.b64decode(flow.read_json(directory / 'session.json')['stream_base64']))
        with patch.object(flow.subprocess, 'run', side_effect=self.runs([self.receipt(directory, 2, length)])):
            view = flow.status_view(path, state, query=True)
        self.assertEqual(view['receiver']['outcome'], 'applied')
        self.assertEqual(path.read_bytes(), before)
        self.assertIsNotNone(flow.read_json(path)['pending'])

    def test_durable_receipt_finishes_local_crash_without_radio(self):
        path, state, directory = self.prepared()
        report = flow.read_json(directory / 'report.json')
        report.update(status='EXACT-APPLIED-RECEIPT', receiver_reported_applied=True)
        flow.save(directory / 'report.json', report)
        with patch.object(flow, 'check_world', return_value={}), patch.object(flow.subprocess, 'run') as sender:
            self.assertEqual(flow.deliver(path, state), 0)
            sender.assert_not_called()
        self.assertEqual(flow.read_json(path)['counter'], 3)

    def test_sender_child_keeps_lock_after_controller_exits_critical_section(self):
        from send_file import inherited_lock_fds
        path, _, _ = self.prepared()
        child = None
        try:
            with flow.state_lock(path):
                env = os.environ.copy(); env['RABBIT_CONNECTED_LOCK_FD'] = str(flow.LOCK_FD)
                with patch.dict(os.environ, {'RABBIT_CONNECTED_LOCK_FD': str(flow.LOCK_FD)}):
                    held = inherited_lock_fds()
                child = subprocess.Popen([flow.sys.executable, '-u', '-c',
                    'import sys; print("held",flush=True); sys.stdin.readline()'],
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, env=env, pass_fds=held)
                self.assertEqual(child.stdout.readline().strip(), 'held')
            with self.assertRaisesRegex(ValueError, 'still holds'):
                with flow.state_lock(path): pass
        finally:
            if child:
                child.communicate('\n', timeout=5)
        with flow.state_lock(path): pass


if __name__ == '__main__': unittest.main(verbosity=2)
