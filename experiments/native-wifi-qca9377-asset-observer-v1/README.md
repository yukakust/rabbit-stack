# Asset sender observation (Mac host only)

Optional telemetry in the existing firmware sender connection: exact RFCS0001
receipt → unchanged QFS decision/floor → durable original checkpoint → public
240-byte QPFX0001 read on the same peer → durable JSONL → existing next action.
Status service UUID suffix40/characteristic41; generation must match the signed
packet's generation. No second connection or diagnostic controller is created.

`python3 observer.py` only compiles the host sender. `python3 verify_host.py`
compiles and runs fake Objective-C callback peers, a pure Python status decoder,
and unsigned dummy-layout `--preflight`. Neither command creates a Bluetooth
manager. Results: 41 host callback/sequence checks and 260 Python checks in
`evidence/host-proof.json`. Real device behavior remains untested.

Root's separately reviewed production route may invoke the resulting executable:

```
runs/control/sender SIGNED_PACKET CHECKPOINT --send --prefix-log DIAGNOSTIC_JSONL
```

That invocation requires explicit known `RABBIT_ASSET_PEER`, exclusive controller
ownership, public packet/signature/admission verification and current exact
native generation. The executable itself only checks packet layout/checkpoint;
it does not verify the owner signature or provide production admission. Existing
city58 has no prefix service, so it must not be used for this observation trial.
`--query-only` performs zero ATT writes; `--preflight` is entirely offline and
writes only the local checkpoint. The Python wrapper exposes no send/query mode.

The original firmware_sender_core.c/h and SHA256 sources are imported unchanged.
The existing send/query timeout intervals240/60 seconds,50ms pacing,4096-byte
checkpoint cadence and QFS decisions remain unchanged. The instrumentation adds
one serialized status read and fsync per checkpoint, therefore changes host ATT
traffic and timing; it is observation, not evidence of a firmware/timer fix.
No native HCI/USB/watchdog/driver source is included or modified.

Full public status bytes, receipt bytes, timestamp, stage and NSError domain/code
are saved before continuing. Connection failure/disconnection/expiry are logged
before stopping; no automatic reconnect, replay, ABORT, re-signing or floor advance
is performed. Missing/error/malformed/mismatched status and crossed callbacks stop.
A failed diagnostic append also stops. Diagnostic paths cannot alias packet or
checkpoint (normalized path and inode checks); logs are appended and fsynced.

`decode_prefix.py RAW --generation GEN` maps all58 little-endian status words
using frozen prefix57 layout. These public bytes are telemetry, not recipient
attestation, entropy proof or proof that hardware owners released. Raw bytes with
NSError are retained even if CoreBluetooth's value could be cached; they must not
be interpreted as a successful fresh read.
