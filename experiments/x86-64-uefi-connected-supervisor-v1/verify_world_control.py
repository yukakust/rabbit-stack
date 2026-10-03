#!/usr/bin/env python3
"""Planner composition, journal, sequencing and shared voice/text policy checks."""
import copy
import json
import tempfile
import unittest
import uuid
import threading
import urllib.request
import urllib.error
from pathlib import Path
from unittest.mock import patch
import ask_connected_world as flow
import world_planner as planner
from world_control import Controller


class Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='world-controller-check-')
        self.root = Path(self.temp.name)
        self.base = flow.read_json(flow.V3 / 'worlds/ginger-cat-red-hat-walk-v1.json', 2 * 1024 * 1024)
        world = self.root / 'base.json'; flow.save(world, self.base)
        package = self.root / 'base.rup'; package.write_bytes(flow.compile_world(world, 3, flow.CREATOR))
        gate = self.root / 'gate.json'
        flow.save(gate, {'status': 'OWNER-OBSERVED-EXACT-MAC-QEMU-NO-DEVICE', 'source_hashes': {
            'experiments/x86-64-uefi-god-runtime-v3/runtime_core.c': flow.sha((flow.V3 / 'runtime_core.c').read_bytes())}})
        self.path = self.root / 'state.json'
        state = flow.initialize(self.path, world, package, gate)
        state['engine'] = {'background': '121826', 'native_counter': 3, 'payload_sha256': '1' * 64}
        state['native_pending'] = None; flow.save(self.path, state)
        self.controller = Controller(self.path, self.root / 'unused-owner-key')

    def tearDown(self): self.temp.cleanup()

    def plan(self, speed=2):
        state = flow.read_json(self.path); base = flow.current(state)
        objects = copy.deepcopy(base['objects']); objects[0]['vx'] = speed
        return {'status': 'ready', 'explanation': 'Кот быстрее', 'base_world_sha256': state['world_sha256'],
                'objects': objects, 'programs': base['programs'], 'inventory_assets': [], 'created_sprites': [],
                'background': None, 'restore_version': None, 'missing_capabilities': []}

    def applied(self, path, state):
        directory = Path(state['pending']); report = flow.read_json(directory / 'report.json')
        return flow.advance(path, state, directory, report, flow.read_json(directory / 'session.json'))

    def test_sequential_requests_keep_hat_assets_and_history_restores_with_new_counter(self):
        with patch.object(flow, 'check_world', return_value={'test_fixture': True}), patch.object(flow, 'deliver', side_effect=self.applied):
            first = self.controller.execute('кот быстрее', plan=self.plan(2))
            self.assertEqual(first['status'], 'APPLIED')
            second = self.controller.execute('ещё быстрее', plan=self.plan(3))
            self.assertEqual(second['status'], 'APPLIED')
            restored = self.controller.execute('верни исходный мир', restore='initial')
        state = flow.read_json(self.path)
        self.assertEqual(restored['status'], 'APPLIED'); self.assertEqual(state['counter'], 6)
        self.assertEqual(flow.current(state), self.base)
        status = self.controller.status(); self.assertEqual(len(status['versions']), 4)
        self.assertIsNone(status['active'])

    def test_text_and_voice_share_identical_candidate_gates_and_delivery(self):
        calls = []
        def deliver(path, state):
            calls.append(flow.read_json(Path(state['pending']) / 'world.json', 2 * 1024 * 1024))
            return self.applied(path, state)
        with patch.object(flow, 'check_world', return_value={'test_fixture': True}), patch.object(flow, 'deliver', side_effect=deliver):
            result = self.controller.execute('кот быстрее', source='voice', plan=self.plan(2))
        self.assertEqual(result['source'], 'voice'); self.assertEqual(result['status'], 'APPLIED')
        self.assertEqual(calls[0]['objects'][0]['vx'], 2)
        self.assertEqual(calls[0]['sprites'], self.base['sprites'])

    def test_idempotent_client_retry_and_uncertain_pending_block_fresh_request(self):
        identity = uuid.uuid4().hex
        with patch.object(flow, 'check_world', return_value={}), patch.object(flow, 'deliver', return_value=1) as radio:
            first = self.controller.execute('кот быстрее', identity=identity, plan=self.plan(2))
            again = self.controller.execute('кот быстрее', identity=identity, plan=self.plan(2))
            self.assertEqual(first, again); self.assertEqual(radio.call_count, 1)
            with self.assertRaisesRegex(ValueError, 'finish the saved'):
                self.controller.execute('новая просьба', plan=self.plan(3))
        session = Path(flow.read_json(self.path)['pending']) / 'session.json'; before = session.read_bytes()
        with patch.object(flow, 'check_world', return_value={}), patch.object(flow, 'deliver', side_effect=self.applied):
            final = self.controller.execute(resume=True)
        self.assertEqual(final['status'], 'APPLIED'); self.assertEqual(session.read_bytes(), before)

    def test_invalid_data_rejects_before_native_preparation_or_radio(self):
        plan = self.plan(); plan['background'] = '203050'; plan['objects'][0]['sprite'] = 250
        with patch('world_control.native.prepare_engine') as native, patch.object(flow, 'deliver') as radio:
            result = self.controller.execute('кандидат с неверной ссылкой', plan=plan)
        self.assertEqual(result['status'], 'FAILED'); native.assert_not_called(); radio.assert_not_called()
        self.assertEqual(flow.read_json(self.path)['engine']['native_counter'], 3)

    def test_background_selects_native_route_without_faking_world_field(self):
        plan = self.plan(); plan.update(objects=None, programs=None, background='203050')
        calls = []
        def prepare(path, state, color, private): calls.append(('prepare', color))
        def deliver(path, state, private):
            state['engine'].update(background='203050', native_counter=4)
            flow.save(path, state); calls.append(('deliver', 4)); return 0
        with patch.object(flow, 'check_world', return_value={}), patch('world_control.native.prepare_engine', side_effect=prepare), \
             patch('world_control.native.deliver_engine', side_effect=deliver), patch.object(flow, 'deliver') as world_sender:
            result = self.controller.execute('тёмно-синий фон', plan=plan)
        self.assertEqual(result['status'], 'APPLIED'); self.assertEqual(calls, [('prepare', '203050'), ('deliver', 4)])
        self.assertEqual(flow.read_json(self.path)['counter'], 3); world_sender.assert_not_called()

    def test_unsupported_request_and_stale_plan_do_not_touch_radio(self):
        plan = self.plan(); plan.update(status='unsupported', objects=None, programs=None, missing_capabilities=['3d'])
        with patch.object(flow, 'deliver') as radio, patch('world_control.native.prepare_engine') as native:
            result = self.controller.execute('трёхмерный мир', plan=plan)
            self.assertEqual(result['status'], 'UNSUPPORTED')
            stale = self.plan(); stale['base_world_sha256'] = '0' * 64
            result = self.controller.execute('устаревший план', plan=stale)
            self.assertEqual(result['status'], 'FAILED'); radio.assert_not_called(); native.assert_not_called()
        self.assertIsNone(self.controller.status()['active'])

    def test_resume_after_native_receipt_before_journal_flag_does_not_rebuild_or_resign(self):
        plan = self.plan(); plan.update(objects=None, programs=None, background='203050')
        def delivered_then_interrupted(path, state, private):
            state['engine'].update(background='203050', native_counter=4)
            flow.save(path, state)
            raise RuntimeError('crash after exact receipt and state advance')
        with patch.object(flow, 'check_world', return_value={}), patch('world_control.native.prepare_engine'), \
             patch('world_control.native.deliver_engine', side_effect=delivered_then_interrupted):
            first = self.controller.execute('новый фон', plan=plan)
        self.assertEqual(first['status'], 'PENDING')
        with patch('world_control.native.prepare_engine') as prepare, patch('world_control.native.deliver_engine') as radio:
            result = self.controller.execute(resume=True)
        self.assertEqual(result['status'], 'APPLIED'); self.assertEqual(result['native_counter'], 4)
        prepare.assert_not_called(); radio.assert_not_called()
        self.assertEqual(len(self.controller.status()['versions']), 2)

    def test_inventory_mouse_preserves_existing_render_colors_and_passes_actual_c(self):
        state = flow.read_json(self.path); plan = self.plan()
        plan['inventory_assets'] = [{'component_id': 'rabbit.asset.toon-mouse-pixel', 'sprite_id': 2,
                                    'display_width': 16, 'display_height': 16}]
        plan['objects'].append({'id': 2, 'sprite': 2, 'program': 2, 'x': 110, 'y': 40, 'vx': 1, 'vy': 0, 'target': 1})
        plan['programs'].append({'id': 2, 'name': 'mouse-walk', 'code': [1, 2, 5, 3, 0]})
        world, _, provenance = planner.compose(state, plan)
        self.assertEqual(world['sprites'][0], self.base['sprites'][0])
        for index in set(bytes.fromhex(''.join(self.base['sprites'][0]['frames']))):
            self.assertEqual(world['palette'][index], self.base['palette'][index])
        world_path = self.root / 'mouse.json'; flow.save(world_path, world)
        packet = self.root / 'mouse.rup'; packet.write_bytes(flow.compile_world(world_path, 4, flow.CREATOR))
        self.assertEqual(flow.check_world(packet, self.root / 'host-check')['host_ticks'], 240)
        self.assertEqual(provenance[0]['license']['spdx'], 'CC0-1.0')

    def test_novel_pixel_art_is_checked_and_cannot_replace_existing_sprite_or_inject_code(self):
        state = flow.read_json(self.path); plan = self.plan()
        plan['created_sprites'] = [{'id': 2, 'name': 'original-star', 'width': 2, 'height': 2,
            'display_width': 4, 'display_height': 4, 'palette': ['00000000', 'ffeeddff'], 'frames': ['00010100']}]
        world, _, provenance = planner.compose(state, plan)
        self.assertEqual(world['sprites'][1]['name'], 'original-star')
        self.assertEqual(provenance[0]['license'], 'NOT-ASSIGNED')
        plan['created_sprites'][0]['id'] = 1
        with self.assertRaisesRegex(ValueError, 'replaces existing'): planner.compose(state, plan)
        plan['native_code'] = 'execute me'
        with self.assertRaises(ValueError): planner.parse_plan(json.dumps(plan))

    def test_existing_high_resolution_variant_switch_keeps_exact_render_colors_in_budget(self):
        state = flow.read_json(self.path); plan = self.plan()
        plan['objects'][0]['sprite'] = 2
        plan['inventory_assets'] = [{'component_id': 'rabbit.asset.ginger-cat-walk', 'sprite_id': 2,
                                    'display_width': 64, 'display_height': 43}]
        world, _, provenance = planner.compose(state, plan)
        self.assertEqual(len(world['sprites']), 1)
        original = flow.read_json(flow.V3 / 'worlds/ginger-cat-walk-v1.json', 2 * 1024 * 1024)
        for actual, expected in zip(world['sprites'][0]['frames'], original['sprites'][0]['frames']):
            actual_colors = [world['palette'][i] for i in bytes.fromhex(actual)]
            expected_colors = [original['palette'][i] for i in bytes.fromhex(expected)]
            self.assertEqual(actual_colors, expected_colors)
        path = self.root / 'variant.json'; flow.save(path, world)
        self.assertLess(len(flow.compile_world(path, 4, flow.CREATOR)), 65535)
        self.assertEqual(provenance[0]['license']['spdx'], 'LicenseRef-Not-Assigned')

    def test_unchanged_request_is_explicit_and_does_not_create_a_version_or_send(self):
        plan = self.plan(1)
        with patch.object(flow, 'deliver') as sender, patch('world_control.native.prepare_engine') as native:
            result = self.controller.execute('ничего не меняй', plan=plan)
        self.assertEqual(result['status'], 'UNCHANGED'); sender.assert_not_called(); native.assert_not_called()
        self.assertEqual(len(self.controller.status()['versions']), 1)

    def test_loopback_server_auth_and_voice_use_same_execute_endpoint(self):
        from world_control_server import Server
        calls = []; finished = threading.Event()
        class Fake:
            def status(self): return {'active': None, 'requests': [], 'versions': []}
            def request_path(self, identity): return self.controller.request_path(identity)
            def execute(self, *args, **kwargs): calls.append((args, kwargs)); finished.set()
        fake = Fake(); fake.controller = self.controller
        server = Server(fake, self.root / 'connection.json')
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        base = f'http://127.0.0.1:{server.server_port}'
        try:
            with self.assertRaises(urllib.error.HTTPError) as denied:
                urllib.request.urlopen(base + '/status', timeout=2)
            self.assertEqual(denied.exception.code, 403)
            body = json.dumps({'id': uuid.uuid4().hex, 'intent': 'кот быстрее', 'source': 'voice'}).encode()
            request = urllib.request.Request(base + '/request', data=body,
                headers={'Authorization': 'Bearer ' + server.token, 'Content-Type': 'application/json'})
            with urllib.request.urlopen(request, timeout=2) as response: self.assertEqual(response.status, 202)
            self.assertTrue(finished.wait(2)); self.assertEqual(calls[0][0][1], 'voice')
            self.assertEqual(calls[0][0][0], 'кот быстрее')
            self.assertEqual((self.root / 'connection.json').stat().st_mode & 0o777, 0o600)
        finally:
            server.shutdown(); server.server_close(); thread.join(2)


if __name__ == '__main__': unittest.main(verbosity=2)
