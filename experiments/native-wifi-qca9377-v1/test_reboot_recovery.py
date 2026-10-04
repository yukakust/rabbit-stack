"""Recovery state transitions with real fixture signatures, mocked radio/VM gates."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, PrivateFormat, NoEncryption
import reboot_recovery as r
flow = r.flow


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name); self.state = self.root / 'state.json'
        self.plan = self.root / 'plan'; self.checked = self.root / 'checked'; self.checked.mkdir()
        flow.save(self.checked / 'recovery-gate.json', {})
        self.key = Ed25519PrivateKey.from_private_bytes(bytes(range(32,64)))
        self.private = self.root / 'fixture.key'
        self.private.write_bytes(self.key.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption()))
        self.private.chmod(0o600)
        self.owner = self.key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
        self.private.with_suffix('.pub').write_bytes(self.owner)
        self.world = flow.city_module('city_world').initial_city()
        self.world.update(schema_version=5, actors=[flow.actors_module('scene5').models()['rabbit.actor.roof-cat-v1']])
        flow.save(self.root / 'world.json', self.world)
        packet = flow.compile_world(self.root / 'world.json', 12, flow.CREATOR)
        (self.root / 'world.rup').write_bytes(packet)
        flow.save(self.root / 'installed.json', {})
        self.installed = {'target_sha256':'11'*32,'module_hashes':{'1':'22'*32},'owner_public_sha256':flow.sha(self.owner)}
        pending = self.root / 'pending'; pending.mkdir()
        payload = b'FIXTURE-NATIVE-NOT-HARDWARE'
        native = r.engine.pack(payload, private=self.key, target=bytes.fromhex('11'*32),
            base_runtime=bytes.fromhex('33'*32), world=packet, counter=15)
        (pending / 'native.rrt').write_bytes(native); (pending / 'payload.efi').write_bytes(payload)
        flow.save(pending / 'session.json', flow.bundle(native,2,15))
        s = {'counter':12,'world':str(self.root/'world.json'),'package':str(self.root/'world.rup'),
            'world_sha256':flow.sha(flow.canonical(self.world)),'package_sha256':flow.sha(packet),
            'runtime_core_sha256':flow.sha((flow.V3/'runtime_core.c').read_bytes()),'pending':None,
            'native_pending':str(pending),'recovery_pending':None,'authority':'fixture-world',
            'engine':{'family':'reviewed-city-v2','native_counter':14,'payload_sha256':'33'*32,
                'city_core_sha256':flow.sha((flow.city_module('city_world').ROOT/'city_core.c').read_bytes()),
                'actor_core_sha256':r.profile.source_hashes()['city_core.c'],
                'installed_gate':str(self.root/'installed.json'),'installed_gate_sha256':flow.sha((self.root/'installed.json').read_bytes())}}
        flow.save(pending / 'report.json', {'kind':'native-read-only-pci','counter':15,
            'package_sha256':flow.sha(native),'session_sha256':flow.sha((pending/'session.json').read_bytes()),
            'base_runtime_sha256':'33'*32,'base_world_sha256':s['world_sha256'],'world_package_sha256':s['package_sha256']})
        flow.save(self.state, s); (self.root/'control').mkdir(); flow.save(self.root/'control/journal.json',{'active':None})
        restored = flow.compile_world(self.root/'world.json',13,flow.CREATOR)
        self.gate_report = {'restored_package_sha256':flow.sha(restored)}
        self.addCleanup(patch.stopall)
        patch.object(r.engine,'gate_check',return_value=self.installed).start()
        patch.object(r,'gate',return_value=(payload,self.gate_report)).start()
        self.original = self.state.read_bytes()
        self.old_files = r.hashes(pending, ('native.rrt','session.json','payload.efi','report.json'))
        self.old = pending

    def prepare(self):
        with patch.object(flow,'sender_step') as radio:
            p = r.prepare(self.state,self.checked,self.plan,self.private)
            radio.assert_not_called()
        self.assertEqual(self.state.read_bytes(),self.original)
        self.assertEqual(p['counter'],16); self.assertEqual(p['world_counter'],13)
        self.assertEqual(r.hashes(self.old,self.old_files),self.old_files)

    def test_prepare_is_offline_and_preserves_old_session(self):
        self.prepare()

    def test_owner_reboot_required_before_any_radio(self):
        self.prepare()
        with patch.object(flow,'sender_step') as radio:
            with self.assertRaisesRegex(ValueError,'explicitly confirm'):
                r.restore(self.state,self.plan,self.private)
            radio.assert_not_called()
        self.assertEqual(self.state.read_bytes(),self.original)

    def test_nonempty_receiver_does_not_retire_pending(self):
        self.prepare()
        with patch.object(flow,'sender_step',return_value=(0,'foreign')) as radio, patch.object(flow,'parse_status',return_value={'outcome':'foreign-final','raw_hex':'ff'}), patch.object(flow,'deliver_session') as write:
            with self.assertRaisesRegex(ValueError,'fresh empty'):
                r.restore(self.state,self.plan,self.private,True)
            self.assertEqual(radio.call_count,1); write.assert_not_called()
        self.assertEqual(self.state.read_bytes(),self.original)
        self.assertEqual(r.hashes(self.old,self.old_files),self.old_files)

    def test_changed_old_packet_blocks_radio(self):
        self.prepare(); (self.old/'native.rrt').write_bytes(b'changed')
        with patch.object(flow,'sender_step') as radio:
            with self.assertRaisesRegex(ValueError,'old pending evidence changed'):
                r.restore(self.state,self.plan,self.private,True)
            radio.assert_not_called()

    def activate(self):
        with patch.object(flow,'sender_step',return_value=(0,'zero')), patch.object(flow,'parse_status',return_value={'outcome':'idle','raw_hex':r.EMPTY}), patch.object(flow,'deliver_session',return_value=1):
            r.restore(self.state,self.plan,self.private,True)

    def test_timeout_retains_activation_and_exact_sessions(self):
        self.prepare(); self.activate()
        s = flow.read_json(self.state); self.assertIsNone(s['native_pending'])
        self.assertEqual(s['engine']['native_counter'],14); self.assertEqual(s['counter'],12)
        self.assertEqual(s['retired_native_sessions'][0]['files'],self.old_files)
        saved = (self.plan/'session.json').read_bytes()
        with patch.object(flow,'sender_step') as zero_query, patch.object(flow,'deliver_session',return_value=1):
            r.restore(self.state,self.plan,self.private)
            zero_query.assert_not_called()
        self.assertEqual((self.plan/'session.json').read_bytes(),saved)
        self.assertEqual(r.hashes(self.old,self.old_files),self.old_files)

    def test_native_receipt_then_world_resume_preserves_city(self):
        self.prepare(); self.activate()
        def applied(directory, report, session, callback):
            self.assertEqual(session['counter'],16 if session['kind']==2 else 13)
            return callback()
        calls = []
        def interrupted(directory, report, session, callback):
            calls.append(session['kind'])
            return applied(directory,report,session,callback) if session['kind']==2 else 1
        with patch.object(flow,'deliver_session',side_effect=interrupted):
            first = r.restore(self.state,self.plan,self.private)
        self.assertTrue(first['engine_done']); self.assertFalse(first['world_done'])
        world_session = (self.plan/'restored-world/session.json').read_bytes()
        with patch.object(flow,'deliver_session',side_effect=applied):
            final = r.restore(self.state,self.plan,self.private)
        self.assertEqual(final['status'],'APPLIED')
        s=flow.read_json(self.state); self.assertEqual(s['counter'],13); self.assertEqual(s['engine']['native_counter'],16)
        self.assertEqual(flow.current(s),self.world); self.assertIsNone(s['recovery_pending'])
        self.assertEqual((self.plan/'restored-world/session.json').read_bytes(),world_session)
        self.assertEqual(r.hashes(self.old,self.old_files),self.old_files)

    def test_prepared_packet_tamper_blocks_radio(self):
        self.prepare(); (self.plan/'native.rrt').write_bytes(b'changed')
        with patch.object(flow,'sender_step') as radio:
            with self.assertRaisesRegex(ValueError,'bytes changed'):
                r.restore(self.state,self.plan,self.private,True)
            radio.assert_not_called()


if __name__ == '__main__':
    unittest.main()
