# Prefix57 read-only observer

Isolated preparation, **no actual Bluetooth operations executed**. Mac Objective-C
helper compiled with Apple SDK and ran only `--preflight`; this path returns before
constructing CBCentralManager. No native C is compiled on Mac. No writeValue,
notifications, discovery scan, state reads/writes, signatures or key loads.

Default `python3 collect.py` compiles/preflights without a radio manager. Only ROOT,
under its existing sole-controller operation lock and after57 admission, may use:

```
python3 collect.py --read --context /absolute/public-context.json --output /absolute/fresh-observer-directory
```

The output directory must not already exist. No stale decoded positive can be reused.
The helper journals each received callback atomically before validation, including
unexpected/error callbacks (bounded512-byte copy with explicit truncation marker).
It reads status,10 raw characteristics,status,10 raw characteristics,status: **23 reads**.
Stall limit90s, total600s, outer process620s. Monotonic system uptime bounds the stall;
clock rollback fails closed. Failure/timeout retains journal/log and rejected marker.
Never clears controller ownership or state. ROOT must hold its existing lock externally.

## Contract (coordinate final source hashes before physical use)

Peer F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF is an OS cached identifier, **not identity authentication**.
UUIDs: `52414242-4954-4649-8000-%012X`, service40, status41, raw50..59.
Status240 = QPFX0001 +58u32LE. Three snapshots must individually show native57,
phase3, genuine actual release1, CLOSED12, cleanup14, all owner indicators22..32 zero.
Compare only frozen fields0..32,48/49,54..57: BLE33..39, USB40..47 and
frames/max timings51..53 intentionally remain live. Healthy positive decoding also
requires USBfault50 zero. A fault capture remains saved even when decoding rejects it.

Raw4672 = QPHCI001 +14u32header +16×288 records. Ten pages9×512+64,
two complete byte-identical passes. Protected slots0..3 contain first four critical
events; slots4..15 contain chronological latest twelve routine events. Explicit
critical overflow and routine overwrite counters mean this is **bounded history**.
Partial ring head equals routine count; full ring head0..11. Frozen raw correlates
phase/gen/count/overflow/start/last with status. Unused records and tails must be zero.
HCI lengths and critical predicates checked against native contract. Time rollback
reason2 preserves raw times; no fabricated time correction or complete-history claim.
This proves only exported host-owner-release and stable bounded bytes, not chip
quiescence, device attestation, firmware READY, Wi-Fi association or connection.

## Explicit public context

`format: PREFIX57-PUBLIC-CONTEXT-1`, `inputs` exact seven names below, each
`{"path":"/absolute/path", "sha256":"expected immutable file digest"}`:

- native_report: delivered native_route report.json for57.
- candidate_report: checked-candidate/report.json for57.
- policy: receiver-policy.json, exact generation57 public RAM policy.
- asset_report: full12 firmware-ram session/report.json.
- world_report: actual world18 EXACT-APPLIED-RECEIPT report.json.
- world_session: saved session.json (or world-session.json) for world18.
- world_packet: immutable world.rup for18.

No defaults or current-state access. Native public Ed25519 RRT3 signature/body,
saved stream/session, candidate source hash closure, report/gate/policy/world hashes,
world18 RUP5 signature/session/actual commit log and **all12** firmware signatures,
whole digest751436 bytes, generation/type/version/kind, actual successful correlated
DONE packet receipts in saved sender logs, final bitmap4095/ready1 checked.
Before and after reading context verification must be identical. These saved reports
are exact receiver-reported evidence, **not cryptographic device attestation**.

## Verified and still pending

Host fixtures only: 65 independent struct-oracle critical/routine population cases,
malformed/partial/duplicate/length/owner/changed-frozen rejection, permitted live
telemetry changes;9 unittest methods across parser/context suites. Context session
models do not sign anything. No real57 public applied artifacts exist yet, so **full
positive context verification and actual CoreBluetooth reads are still untested**.
Final sibling contract/source hashes and ROOT review required before any `--read`.
No new firmware candidate, counter, native publication or physical admission here.
