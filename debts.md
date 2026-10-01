# Rabbit Stack technical debts

## Authenticate wireless Rabbit programs

Current BLE program frames use FNV-1a only as an accidental-corruption check. FNV has
no secret, so it cannot prove that a frame came from the owner's Mac. A nearby sender
that knows the public frame format can construct another checksum-valid program.

Before treating the wireless loader as an authority boundary:

- provision an explicit owner key or reviewed public key;
- authenticate the complete canonical program and its protocol version;
- bind a monotonic counter or nonce to each accepted program;
- reject replayed, stale, substituted, truncated, and reordered transfers;
- define key provisioning, rotation, loss, and recovery without hidden persistence;
- keep authentication distinct from encryption and document whether program contents
  remain visible over the air;
- add deterministic positive/negative vectors and physical evidence;
- never describe FNV, transport UUIDs, Bluetooth proximity, or device ownership as
  authentication.

This debt is intentionally separate from the first Dell-to-Mac acknowledgement. An ACK
lets the current Mac process correlate a receipt with the program it sent, but without
authentication it does not prove that the receipt came from this Dell or from the
authorized owner.

God Runtime v2 now authenticates each complete Universal Package with Ed25519 and binds
an in-boot monotonic counter. The remaining parts of this debt are production key
provisioning/rotation, authenticated receipts, cross-reboot replay state, and optional
confidentiality; the deterministic development key is not a production secret.

## Make acknowledgements retryable without repeating effects

The first exact Dell-to-Mac acknowledgement proved that the physical round trip works,
but an acknowledgement can still be lost over the air. If Mac sends the same transfer
again because it did not hear the receipt, Dell must not apply the program a second time.

In child-sized terms: Mac gives Dell instruction card `38`; Dell performs it and says
"done." If Mac does not hear "done," it may show card `38` again. Dell must remember that
this exact card was already completed, avoid doing the work twice, and repeat only the
receipt.

Before treating the transport as reliable:

- give every accepted transfer an unambiguous identity;
- retain enough bounded runtime state to recognize the latest completed transfers;
- make duplicate `BEGIN`, `CHUNK`, and `COMMIT` frames safe;
- re-advertise the exact prior acknowledgement for an exact duplicate;
- never increment the applied counter or repeat the physical effect for that duplicate;
- define bounded expiry and behavior after reboot, where volatile duplicate history is
  lost;
- test lost frames, lost acknowledgements, reordered frames, repeated commits, and Mac
  restart;
- keep delivery reliability distinct from authentication and anti-replay security.

This matters little when the effect is merely repainting an already-blue square, but it
is mandatory before Rabbit can safely trigger non-idempotent effects such as opening a
lock, dispensing material, starting a motor, or deleting data.

## Implement transactional world and runtime patches

Rabbit can already replace a small VM program atomically after the complete program has
validated. The wider system still needs the same discipline for modules, runtime code,
drivers, state schemas, and whole worlds.

A transactional patch must proceed through explicit phases:

1. prepare and stage the candidate without disturbing the active world;
2. validate identity, authority, resources, compatibility, and migration requirements;
3. commit through one well-defined atomic boundary;
4. run bounded health and observable-contract checks;
5. keep the new revision only after those checks pass;
6. otherwise restore the exact previous revision and compatible state automatically.

Cold, warm, and hot updates must be distinguished. Unsupported live transitions must be
rejected rather than guessed. Recovery after power loss, partial transport, failed state
migration, driver failure, or an unhealthy new module must be deterministic and tested.
Rollback identity and evidence must bind the old world, patch, resulting world, target,
runtime, state migration, and observed outcome.

God Runtime v2 implements this transaction for data-only worlds: separate staging RAM,
signature and graph/budget validation, one provisional health step, commit-or-retain,
and a correlated ACK. Runtime/driver/native-code updates and crash/power-loss recovery
remain outside that hot-world transaction and continue to be debt.

## Detailed graphics transport and resource-reference editing

Graphics v3 has a 256-RGBA/128x128 data path and host-tested block receipts. These
receipts and idempotent final ACK still need Mac/Dell physical conformance; they do
not close the older general retry/security debt by themselves. The current smooth
mouse is about 9KB and needs roughly 13 minutes at 6 bytes/450ms per advertisement.
Replace or safely optimize this correctness-first transport only with a reviewed
Target Pack, measured throughput/loss behavior and an unchanged signing/staging/rollback
boundary. Do not silently enable connections, active scan or arbitrary radio effects.

Add immutable asset references to LLM world edits, so the model changes palette/state/
behavior without regenerating large pixel arrays. Extend trusted Inventory schemas to
high-resolution assets and decide publishing licenses explicitly. Add genuinely authored
animation poses, frame/tick raster tests, full-frame buffering where useful, and visible
health checks. Existing text builder still emits v2 worlds and cannot preserve a v3
asset automatically. Runtime/driver/ABI upgrades still require a reviewed image update;
only data changes within that ABI can avoid USB movement.

## Wireless runtime supervisor (prioritized before graphics v3 installation)

The owner requested updating the runtime over Bluetooth before another graphics-only
USB upgrade. `runtime-update-contract-v1` tests a separately authorized signed envelope,
256KiB ordered framing and NON-EXECUTING transaction model. It does not close this debt.

The owner chose privileged owner-reviewed native modules on 2026-10-01.
Provision an owner-local update key distinct from the public world development key.
Implement supervisor/module ABI, QCA ownership, state export, real trial/health/recovery,
streaming receipts and measured throughput. Signed native code can still corrupt memory
or access firmware/storage; signature and RAM backup do not enforce isolation or recover
a hang. Observe the actual fault/fallback boundary before physical installation.

No updater image is ready or installed. Installed v2 has no update entry point; adding
one needs a separately gated bootstrap installation. Initial updates are RAM-only.
Persistent removable-media slots and cross-reboot counters need separate authorization.

Native execution is now QEMU-observed in `x86-64-uefi-runtime-supervisor-v1`: independent
C signature/PE checks, two signed driver swaps, ordinary health-failure retention,
receipt-only retry and watchdog reset from a marked interrupts-enabled infinite init
loop. Owner-local key generation/reviewed signing is implemented, but no real owner key
is provisioned. This is a public-test-key, physical-installation-forbidden probe, not
a Bluetooth updater. Actual Mac/QCA handover, Scene/Anima ABI/state export, physical
watchdog conformance and bootstrap installation remain open. Signature/PE/backup do
not isolate native corruption; key encryption/rotation and authenticated receipts remain
debt. No embedded per-payload release allowlist is needed in the native loader.
