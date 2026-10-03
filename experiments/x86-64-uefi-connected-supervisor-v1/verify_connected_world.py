#!/usr/bin/env python3
"""Host-only V3 intent, C health, custody and uncertain-delivery checks."""
import copy
import json
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

    def test_failure_retains_counter_and_same_nonce_then_exact_receipt_advances(self):
        path, state, directory = self.prepared()
        session_before = (directory / 'session.json').read_bytes()
        with patch.object(flow, 'check_world', return_value={}), patch.object(flow.subprocess, 'run', return_value=subprocess.CompletedProcess([], 1, 'timeout')):
            self.assertEqual(flow.deliver(path, state), 1)
        state = flow.read_json(path); self.assertEqual(state['counter'], 2)
        with self.assertRaisesRegex(ValueError, 'pending delivery'):
            flow.prepare(path, state, 'new request', self.proposal())
        applied = 'FILE APPLIED RECEIPT (NOT ATTESTATION): exact SHA256/session/counter matched'
        outcomes = [subprocess.CompletedProcess([], 0, 'STAGED-NOT-APPLIED'), subprocess.CompletedProcess([], 0, applied)]
        with patch.object(flow, 'check_world', return_value={}), patch.object(flow.subprocess, 'run', side_effect=outcomes) as sender:
            self.assertEqual(flow.deliver(path, state), 0)
            first = sender.call_args_list[0].args[0]
            self.assertIn('--data-delay-ms', first)
            self.assertIn(str(len(self.packet.read_bytes()) + 31), first)
        self.assertEqual((directory / 'session.json').read_bytes(), session_before)
        state = flow.read_json(path); self.assertEqual(state['counter'], 3); self.assertIsNone(state['pending'])
        self.assertEqual(flow.current(state)['objects'][0]['vx'], 2)

    def test_exit_zero_without_exact_receipt_cannot_advance_current_world(self):
        path, state, _ = self.prepared()
        with patch.object(flow, 'check_world', return_value={}), patch.object(flow.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, 'no receipt')):
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
        with patch.object(flow, 'check_world', return_value={}), patch.object(flow.subprocess, 'run', return_value=subprocess.CompletedProcess([], 1, 'timeout')):
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


if __name__ == '__main__': unittest.main(verbosity=2)
