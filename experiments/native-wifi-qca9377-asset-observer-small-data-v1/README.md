# Host DATA100 observation experiment

A new isolated derivative of frozen asset-observer-v1. The production sender diff
is exactly one substitution: `if(count>240)count=240;` becomes
`if(count>100)count=100;`. This is100 payload bytes plus unchanged4-byte offset,
so the ATT value is at most104 bytes. The existing244-byte stack buffer is unchanged.
No native/HCI/USB/watchdog/firmware/resident code or timer changes.

50ms pacing,240second send/60second query bounds,4096-byte checkpoint cadence,
whole immutable packet/checkpoint/QFS/owner signature semantics, serial240byte
QPFX/fsync/known-peer diagnostics and generation-from-packet remain unchanged.
`sequence.h`, `observer.py`, `decode_prefix.py` are byte-identical clones. Original
sources are hashed against the frozen v1 proof before/after the offline test.

Run `python3 verify_host.py` for fake host callbacks and offline layout preflight.
65 host checks pass: the original41 failure/sequencing cases plus DATA100 exact
wire offsets/body bytes, resume floor18480, subsequent offset18580, final37-byte
payload, exact100-byte final payload, ACK/cursor scheduling cannot raise floor,
and only a matching synthetic RFCS raises/saves floor18680. Packet bytes remain
unchanged. No Bluetooth manager, real owner key/credential, state or native C
compilation was used. These are host fixtures, not successful physical delivery.

`python3 observer.py` by default ONLY compiles. Optional `--preflight` uses a local
checkpoint and never creates a manager. It does not verify an owner signature;
Root's outer production admission remains required. Root alone may invoke the
compiled `runs/control/sender SIGNED_PACKET CHECKPOINT --send --prefix-log PATH`
after a fresh known-peer GEN60/actual saved asset context check, controller lock,
exact byte/source/executable/signature binding and explicit single hardware-trial
admission. No automatic experiment/replay/re-sign/ABORT or fallback is provided.

Public proof/log: `evidence/host-proof.json`, `evidence/host.log`. This experiment
changes host DATA size only; it does not establish the reason for the observed
No-Sync/NACK/linkloss or promise that100-byte writes will solve it.
