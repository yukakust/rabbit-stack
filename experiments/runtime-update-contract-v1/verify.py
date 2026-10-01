#!/usr/bin/env python3
"""Offline reference tests. No candidate runtime or Bluetooth code is executed."""
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from update import (HEADER, MAX_BYTES, Policy, SupervisorModel,
                    UpdateError, WORLD_DEVELOPMENT_PUBLIC, digest, pack, verify)
from transport import decode, encode, frame


class UpdateTests(unittest.TestCase):
    def setUp(self):
        # Test-only key, never installed or offered as an owner credential.
        self.private = Ed25519PrivateKey.from_private_bytes(bytes(range(32, 64)))
        self.public = self.private.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
        self.policy = Policy(digest(b"test target"), self.public)
        self.old = b"opaque old runtime fixture; NOT executable"
        self.new = b"opaque reviewed candidate fixture; NOT executable"
        self.state = b"exact old world/state fixture"
        self.model = SupervisorModel(self.policy, self.old, self.state)
        self.package = self.make()

    def make(self, **overrides):
        args = dict(private=self.private, target=self.policy.target,
                    base_runtime=digest(self.old), state=self.state, counter=1)
        args.update(overrides)
        return pack(self.new, **args)

    def accept(self, data=None):
        return self.model.stage(self.package if data is None else data,
                                reviewed_payload_sha256=digest(self.new))

    def test_separate_key_and_signature_domain(self):
        with self.assertRaises(UpdateError):
            Policy(self.policy.target, WORLD_DEVELOPMENT_PUBLIC)
        development = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
        with self.assertRaises(UpdateError):
            self.make(private=development)
        data = self.package[:-64] + self.private.sign(self.package[:-64])
        with self.assertRaises(UpdateError):
            self.accept(data)  # Generic signed bytes are not an RRT1 signature.

    def test_tampering_truncation_and_other_owner(self):
        for offset in (0, 8, 30, HEADER.size, len(self.package)-1):
            bad = bytearray(self.package); bad[offset] ^= 1
            with self.assertRaises(UpdateError):
                self.accept(bytes(bad))
        for bad in (self.package[:-1], self.package + b"\0", b"", b"RUP2"):
            with self.assertRaises(UpdateError):
                self.accept(bad)
        unknown = Ed25519PrivateKey.from_private_bytes(b"X"*32)
        with self.assertRaises(UpdateError):
            self.accept(self.make(private=unknown))
        self.assertEqual((self.model.active, self.model.state, self.model.minimum_counter),
                         (self.old, self.state, 0))

    def test_exact_target_base_state_and_abi_bindings(self):
        for overrides in (dict(target=digest(b"other target")),
                          dict(base_runtime=digest(b"other runtime")),
                          dict(state=b"other world"), dict(supervisor_abi=2), dict(state_abi=2)):
            with self.assertRaises(UpdateError):
                self.accept(self.make(**overrides))
        with self.assertRaises(UpdateError):
            self.model.stage(self.package, reviewed_payload_sha256=digest(b"unreviewed"))
        self.assertEqual(self.model.minimum_counter, 0)

    def test_boolean_counter_and_budgets(self):
        for counter in (True, 0, -1, 2**64, 1.0):
            with self.assertRaises(UpdateError):
                self.make(counter=counter)
        with self.assertRaises(UpdateError):
            self.make(state_abi=True)
        with self.assertRaises(UpdateError):
            pack(b"x"*MAX_BYTES, private=self.private, target=self.policy.target,
                 base_runtime=digest(self.old), state=self.state, counter=1)
        with self.assertRaises(UpdateError):
            verify(self.package, self.policy, base_runtime=digest(self.old),
                   state=self.state, minimum_counter=True)

    def test_staging_does_not_activate_and_one_trial_only(self):
        candidate = self.accept()
        self.assertEqual((self.model.active, self.model.state), (self.old, self.state))
        with self.assertRaises(UpdateError):
            self.accept()
        for identity, health in ((digest(b"wrong"), True), (candidate.identity, 1)):
            with self.assertRaises(UpdateError):
                self.model.resolve(candidate_identity=identity, healthy=health)
        self.assertEqual(self.model.active, self.old)

    def test_success_retry_is_receipt_only(self):
        candidate = self.accept()
        receipt = self.model.resolve(candidate_identity=candidate.identity, healthy=True)
        self.assertEqual((receipt.status, self.model.active, self.model.state),
                         ("COMMITTED", self.new, self.state))
        self.assertFalse(receipt.authenticated)
        self.assertEqual(self.accept(), receipt)
        self.assertIsNone(self.model.pending)
        self.assertEqual(self.model.minimum_counter, 1)

    def test_unhealthy_retains_exact_old_state_and_consumes_counter(self):
        candidate = self.accept()
        receipt = self.model.resolve(candidate_identity=candidate.identity, healthy=False)
        self.assertEqual((receipt.status, self.model.active, self.model.state),
                         ("RETAINED-OLD", self.old, self.state))
        self.assertEqual(self.accept(), receipt)
        with self.assertRaises(UpdateError):
            self.accept(self.make(counter=1, state_abi=2))
        self.accept(self.make(counter=2))

    def test_chained_base_and_reboot_fallback(self):
        first = self.accept()
        self.model.resolve(candidate_identity=first.identity, healthy=True)
        with self.assertRaises(UpdateError):
            self.accept(self.make(counter=2))
        next_package = self.make(counter=2, base_runtime=digest(self.new))
        self.accept(next_package)
        self.model.reboot()
        self.assertEqual((self.model.active, self.model.state, self.model.pending,
                          self.model.receipt, self.model.minimum_counter),
                         (self.old, self.state, None, None, 0))
        # Cross-reboot replay is NOT claimed; volatile state intentionally resets.
        self.accept()

    def test_large_ordered_transfer_crosses_existing_length_limit(self):
        payload = bytes(range(256))*400
        data = pack(payload, private=self.private, target=self.policy.target,
                    base_runtime=digest(self.old), state=self.state, counter=2)
        frames = encode(data)
        self.assertGreater(len(data), 65535)
        self.assertEqual(decode(frames), data)
        accepted = verify(decode(frames), self.policy, base_runtime=digest(self.old),
                          state=self.state, minimum_counter=0)
        self.assertEqual(accepted.payload, payload)
        self.assertEqual(decode(encode(b"x"*MAX_BYTES)), b"x"*MAX_BYTES)

    def test_transfer_rejects_loss_reorder_substitution_corruption_padding(self):
        frames = encode(self.package)
        bad_sets = [frames[:-1], frames[:2]+frames[3:],
                    frames[:1]+[frames[2], frames[1]]+frames[3:]]
        bad = bytearray(frames[1]); bad[7] ^= 1
        bad_sets.append([frames[0], bytes(bad)] + frames[2:])
        # Correct checksum, wrong transfer id.
        transfer = frames[0][3]
        bad_sets.append([frames[0], frame(2, transfer % 255 + 1, 0, frames[1][6:12])] + frames[2:])
        for bad in bad_sets:
            with self.assertRaises(UpdateError):
                decode(bad)
        tiny = encode(b"a")
        tiny[1] = frame(2, tiny[0][3], 0, b"a\0\0\0\0x")
        with self.assertRaises(UpdateError):
            decode(tiny)


if __name__ == "__main__":
    unittest.main(verbosity=2)
