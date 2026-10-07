# Native54 observer v2: retained terminal observations

Preserves observer-v1 and its proof byte-for-byte. V1 incorrectly required a
retained raw beacon frequency to equal current `live_frequency`, which the frozen
coordinator clears on terminal events. V2 corrects that rejection and preserves
actual raw output before semantic decoding; it does not change any native54 code.

Implemented collectors only. During development **no Bluetooth manager/read/write,
device operation, secret load, signing, native C compilation or controller state
mutation** occurred. Mac Objective-C compilation/preflight and pure Python fixture
checks are the only executed operations in this branch.

Root controller interface:

```text
python3 experiments/native-wifi-qca9377-scan-observer-v2/collect.py --read
```

Default output stays in this branch's ignored `runs/control/scan54-capture.json`,
plus `.decoded.json` and `.log`. Without `--read`, compile/preflight only: the
preflight exits before constructing a Bluetooth manager. Do not launch a second
reader while the sole controller is working; all actual read execution belongs
to the root controller. This branch does not launch one itself.

## Before any read

The Python wrapper holds the same nonblocking `state.lock` used by the world/
asset controllers. It rejects pending world/native/recovery transports, requires
installed native54 and payload
`3eefea77fbab35bca609216e4a418c2abad695f1a8a83da8aa2ee147bbfefca3`,
the exact APPLIED54 saved session receipt `pci-native-1qq9s17x`, receiver-confirmed
application, and receipt binding to the actual checked candidate-report hash.
It checks the candidate's entire frozen source closure and pinned export decoder.
It rechecks exact receipt/state binding after capture and ensures its own source
bytes did not change during compilation/capture. It never loads private keys.

`hardware_trial_pending` is deliberately **not** required to be cleared: root's
final combined verdict owns that action. When present, the collector permits
only the exact54 full firmware-in-RAM report: all12 completed chunks, actual
receiver ready/bitmap4095/error0/known peer, matching generation/native payload,
firmware digest/type/version/owner/target and12 immutable generation54 manifests.
Incomplete asset transfer fails before the Bluetooth manager is started.
V2 additionally correlates the actual last receipt to the exact last manifest:
DONE4/state2/packet digest/length/received/floor30764. Before radio reads, it
checks every saved immutable packet's envelope/body/target/offset/generation,
public Ed25519 signature and the recombined whole firmware digest. Verification
uses the already public owner identity; no private key or signing operation.

The collector never clears pending state or edits `state.json`. Its lock uses
the actual flow's `state.lock`, append open and nonblocking exclusive flock;
static source comparison and a separate temporary contention test verify that
contract without touching the root's live lock. Root must combine
its actual54 QWBT/operating/startup/RX observations with this capture before any
owner-session verdict or subsequent native replacement.

## Known-peer read sequence

Objective-C retrieves only cached peer
`F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF`; no broad advertisement scan or fallback
discovery. It discovers exact service0x2A/characteristic0x2B and service0x2C/
characteristics0x40..0x67. These match the frozen GATT handle ranges32..34 and
35..115; forty export values are at handles37+2*page. No ATT writes,
notifications, ACK operations or custom characteristic mutation are used.

1. Read the complete416-byte QSCN0001 status.
2. Before requesting any export page, require54/13 generation/profile, exact
   policy/ruleset/location digests, reported actual owner release, zero actual
   mappings/DMA/PCI/wake/link/IRQ/pin/bus/access owners, adapter12/cleanup14 and
   bounded conserved credit ledger.
3. Read all40 pages in deterministic UUID order: four512-byte pages and one36-
   byte page per retained slot; then read status again.
4. Read all40 pages again, then status a third time. Every page and all three
   statuses must be byte-identical. Fail without an accepted capture on drift,
   wrong callback/UUID/length, missing characteristic, disconnect or timeout.

The helper has a180-second overall bound; wrapper has a190-second subprocess
bound. Run operationally through the root's background controller so this bound
does not prevent user-facing progress updates. Failure logs remain in ignored
runs; failure never authorizes state clearing or changes a native session.

Credits are software accounting, separate from actual DMA ownership: after a
fault, a conserved reservation may remain even when actual owners are released.
The collector records it rather than inventing a refund or treating it as DMA.
Conservation/16-bit bounds still must hold. This distinction follows frozen
`qca_tx_clear`, which does not refund the ledger.

## Pure decode and honest SSID evidence

`decode_scan.py` names all64 u32 fields directly from frozen `scan_build.py`.
It validates exact416-byte/magic/generation/reserved regions, policy hashes,
booleans, enum/owner/queue bounds, credit conservation, actual owner-release
coherence and SSID padding. Released status with nonzero actual owners is rejected.

It uses the **hash-pinned frozen** `decode_exports.py` unchanged to reconstruct
eight2084-byte slots from forty pages, checks slot indices/epoch/payload bounds,
zero unused bytes, owner-graph counts and nonduplicate completion ownership.
QSCN has no epoch field: epoch comes from QEXP slots and must agree across all
eight; no epoch is invented from status or packet counters. Gaps in genuine
completion IDs are allowed.

No SSID claim follows merely from SCAN_STARTED. A positive requested-SSID result
needs actual `pending_started`, `ssid_seen`/`has_observation`, retained slot2 with
owned WMI pipe2/endpoint1/completion beyond the start floor, independently parsed
supported raw MGMT0x7001 envelope and beacon/probe, and exact SSID/BSSID/RX
identity agreement with status, and raw frequency inside the exact13-channel
reviewed policy. When `live_frequency` is nonzero, equality is still required.
When it is zero in a quiesced/released snapshot, the retained observation is
validated through STARTED, owned raw completion beyond the start fence and a
positive consistent acquisition epoch. Its frequency remains a separate raw
beacon field; the decoded `live_frequency=0` is preserved rather than invented.
The Python raw parser follows the frozen narrow
beacon adapter: header40, bounded byte array/padding, status0, channels1..13,
ordinary infrastructure frame/address/IE consistency, hidden SSID not matched,
opaque RSN only. It does not fabricate vdev/scan IDs absent from MGMT headers.

The complete stdout and parsed raw capture are saved **before** semantic decode.
A previous decoded file is archived by digest before a pending marker replaces
it, so stale positive evidence cannot remain current after a failed new decode.
A rejected decode additionally records an error with raw-file digest and
`state_cleared=false`; raw bytes are retained for inspection, not promoted to a
successful verdict. The pure decoder always leaves `physical_ssid_discovered=false`; it cannot turn
a cached JSON fixture into physical evidence. Only the guarded actual `--read`
path marks `physical_read_performed` and conditionally records the physical SSID
observation after all bindings pass. Known peer/GATT receipts are not cryptographic
device attestation. `wifi_connected=false` remains unconditional: discovery is
neither association/security nor an IP/Yukabox connection.

## Verification performed

**2749** static cases passed: released and retained-observation synthetic
fixtures; every status truncation; magic/policy/reserved corruption; held owners,
bad credits/enums/counts; each byte of one complete2084-byte empty export slot
corrupted in both otherwise stable passes; each changed second-pass page;
status drift, false SSID/STARTED/observation relations; state/pending/receipt/
candidate gates and incomplete/wrong-generation/wrong-policy asset reports.
New cases model actual frozen coordinator terminal semantics (SSID retained,
terminal event and `live_frequency=0`), reject wrong-policy channel14, reject
nonzero active-frequency disagreement and reject missing quiesce context.
An explicitly labelled parser test double separately exercises membership in
the exact policy set without widening the real channels1..13 parser. Final packet
receipt action/state/hash/floor/length and manifest-order corruption are rejected.
The installed mature public-verification library also passes [RFC8032 section7.1](https://www.rfc-editor.org/rfc/rfc8032#section-7.1)'s
public key/signature test vector and rejects its altered signature; no private
seed/key or signing function is involved. This is a library verification check,
not a claim that synthetic asset manifests are genuine signed packets.
The Mac helper compiles with ARC/Wall/Wextra/Werror and preflight confirms no
manager/secret/radio operation.

The uninitialized status fixture is explicitly a **reconstruction of the frozen
real-QEMU ATT assertion contract**, not a captured full416-byte/40-page dump.
The existing QEMU verifier proves absent-radio runtime fields zero, generation54,
policy_count13, exact policy suffix and bounded read-only service/blob behavior.
The reconstructed fixture decodes only with `require_release=False`; the actual
collector rejects it before exports because there is no actual release proof.
Synthetic released/SSID fixtures are separately labelled nonphysical. No claim
of a physical scan or a complete QEMU export snapshot is made.

Public evidence hashes bind this branch's sources, the frozen export decoder,
frozen QEMU verifier and actual QEMU report. Native54 frozen files were not edited.
Re-run with `python3 .../scan-observer-v2/verify_observer.py`; this verifier never
passes `--read` and cannot perform Bluetooth observation.
