# Offline GEN61 scan snapshot observer

This scope prepares host-only collection/validation, not an admitted physical61
controller. No actual Bluetooth manager/read, signer/key, state write, native
compile or device operation was used.495 fake host callback cases and794 pure
Python decoder/binding checks passed. `python3 verify_host.py` only compiles Mac
host Objective-C, executes fake callbacks and `--preflight`, and tests synthetic
fixtures. Proof/log/source/compiler/executable digests are in `evidence/`.

Layout contract from the producer: no prefix ATT29..51; QSCN416 at32..34
(UUID2a/2b), raw service35..255 (UUID2c,110values UUID80..ed/handles37+2page).
The internal QPFX/overlay remain native producer concerns; this reader never
tries prefix ATT. QWBT20..22/QWOP23..25/QWIN26..28 remain separate boot telemetry.

One cached exact known peer, one CBCentralManager/connection. Discover status
service2a/one value2b first, then raw service2c/exact110 read values. Require exact
service instance/characteristic identity, not a matching UUID from a different
callback. No scan, reconnect, alternate peer, writes or mutable ACK. Any callback
error/missing/duplicate/malformed value stops. Each full public raw callback,
NSError domain/code, timestamp/stage/page is appended+fsynced BEFORE the next
read. Log failure stops. Known cached values on NSError are marked accordingly.

Snapshot order: status →110pages →same status →110pages →same status.416bytes,
GEN61/policy13/bound digests/all14owner release/adapter closed before ANY page;
all three statuses and both110page passes must be byte-identical.600seconds
collection bound,90seconds stalled progress. A partial capture/error is not a
positive verdict. Raw JSONL is durable even if final capture validation fails.
Only the parent Root may invoke the compiled binary's future actual mode after
separate complete admission and sole-controller ownership:

```
runs/control/read-scan61 --root-authorized-read --log /ABS/NEW_JSONL
```

That argument is an invocation guard, not authorization/attestation. The default
proof helper NEVER invokes it. There is deliberately no automatic actual `--read`
wrapper while the candidate/actual APPLIED61 gate is pending.

`decode_scan.py` derives the frozen v3 parser with only generation61/context text
changed; it uses the exact pinned unchanged55 QEXP reconstruction codec
(b794cf27...20441b), which defines the same22slot/110page format. It preserves
terminal live_frequency0 instead of inventing a channel. A retained beacon must
bind matching STARTED, actual export epoch, RXcompletion>start_floor, reviewed
policy frequency, WMI endpoint/pipe, supported MGMT framing, exact status/BSSID and
nonhidden16byte SSID `SILK_56E35E_Plus`. Unknown/unsupported variants are not
interpreted as that SSID. A pure fixture always has physical_ssid_discoveredfalse;
actual Root must establish source/session/device provenance separately.

`bindings.py` is only a partial pure admission boundary: Root's future frozen
report/payload/status/native61 pins + exact saved source closure; exact current
world19 package89ffda...3968b7/public creator signature; exact native61 APPLIED
report/candidate correlation; and public RRT61 target/owner/body/domain signature
checks with explicit trusted runtime identity. It never loads a signer. Missing
pins fail. The real61 positive public/APPLIED proofs are still pending, not
substituted by host fixtures. It always returns physical_admissionfalse.

Root still must validate complete candidate/generated/native/QEMU/policy closure,
actual saved native session/last_release path and whole public native signature,
current immutable world19 source/reproduction, all12 firmware packets/public
signatures/body digest and correlated final RFS receipt, exact state.lock and all
transport owners, source/executable pins before and after reads, then preserve
raw before decode. No state or hardware_pending is cleared here. The final
physical SSID claim must rely on actual accepted MGMT bytes from Dell, not solely
SCAN_STARTED or a status flag. Discovery is not WPA/association/IP/connectivity.

During firmware staging QSCN phase0 is expected; it cannot pass all-owner-release
snapshot admission. Full boot progress needs the separate QWBT collector: this
snapshot reader does not poll/reconnect while boot runs. Candidate report/status/
payload hashes have not been invented. New61 route must supply the actual frozen
contract later; do not reuse native55 receipts, gen55 collector pins or world17.
