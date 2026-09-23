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
