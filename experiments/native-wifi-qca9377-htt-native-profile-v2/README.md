# Unsigned native56: bounded production HTT version profile

New derivative of frozen HTT profile-v1; old source/evidence remain untouched.

No hardware, admission, signing, RF/peer/association/DHCP claim. Counter56 is
provisional only. Frozen native52/53/54/55 and host-only modules are untouched;
only generated private copies receive composition/whitespace normalization.
Native C/ASAN/COFF/wholeEFI/QEMU execute on Yukabox exclusively.

## Firmware provenance and production entrypoint

Before VERSION_REQ, qca_htt_profile_step verifies the actual retained boot.asset:
owner-signed chunks marked ready, immutable pin held by boot, no poison,
physical type/version/kind/size matching existing boot prerequisites. It
rehashes actual full RAM container against BOTH authenticated policy digest and
reviewed receiver-policy digest. It parses bounded unique ath10k IEs, obtains
HTT op from IE6's actual4-byte payload, validates WMI IE5=4 and exact main/helper
pointer+length agreement with the already executed boot plan. Main digest,
container digest, IE offset, op values and signed generation are saved before
checked stop clears the asset. The production query receives parsed htt_op;
no literal3 is passed by this production entrypoint. Existing narrow codec
then accepts only mature ath10k TLV mapping3 and actual VERSION_CONF major2/3.
RX's private codec policy is narrow TLV3, but it cannot authorize query without
this authenticated container proof. Ready/pinned metadata is trusted internal
state produced by the existing signature checker, not network-provided booleans.

qca_poll's actual production loop calls the profile after hardware startup/RX
servicing. It creates exactly one query after validated INIT, polls combined
single CE1/CE2 owner and CE4 request, deadline3seconds, explicit once-quiesce/
checked stop. Existing fourteen DMA owners remain until actual bus/IRQ stop;
query RELEASED requires lifecycle all-owner closure. Hardware/epoch faults
remain lifecycle retained even when separate physical-owner inventory is zero.

## Read-only observations

QHTT0001 status320bytes, service UUID2e/char2f, handles29..31:
56u32 fields bind query phase/error/once-stop, actual release, submitted/DMA/
version fields, endpoint/max-message/op, watermark/consumption/archive counts,
firmware proof/error/IEs/offsets/generation, RX/error/posts/FIFO/backpressure,
WMI ledger, all actual owner counts, adapter cleanup, lifecycle/errors/polls,
INIT proof, epoch, provisional counter56 and actual stop latch. Full container/main SHA256 are at
232/264. No status implies association or working packet data plane.

QHTX0001 raw records2104bytes = header8 +12u32 +raw2048:
slot,present,HTC-validated,completion,epochlow/high,endpoint,pipe,payloadbytes,
rawbytes,event,RX-error-for-rejected-slot. Six slots are response/archive2/
retainedFIFO2/rejected frame. Unsupported VERSION_CONF remains exact raw bytes;
rejected HTC frame is explicitly not validated. Payload is recoverable from
raw HTC/trailer bytes; none is rewritten as a guessed ACK.

Thirty fixed page characteristics expose five pages per slot: first4pages512,
last56. Service UUID30 handles32..92; values34+2*page, UUID80+page. Standard
READ_BLOB offset supports the MTU247 limit; every write denied, no mutable ACK,
credential path or arbitrary memory reader. After quiesce, static owned copies
remain stable; root must persist all exact pages and hashes before later unload.
Status counts alone are insufficient evidence. No radio still exposes explicit
empty slot records and counter56 without reporting readiness or owners.

## Verification contract and remaining gates

Actual-entrypoint model invokes the production qca_poll composition, actual
PCI/CE/DMA simulator and signed public fixture firmware; it never directly
calls begin to fabricate a production result. Cases include both supported
majors, malformed/stale/wrong responses, DMA faults/order/stall, real WMI
trailer once, unsupported credits, control/WMI/HTT preservation/backpressure,
epoch/session/mapping loss, rollback, and authenticated-container corruption/
boot pointer disagreement before query. ATT/export checks cover all30pages,
READ_BLOB reconstruction, bounds, writes and byte stability after all14release.

WholeEFI proof requires repeated equal builds, actual supervisor normal and
empty-boot QEMU, exact frozen world17 package/semantic hashes, ASAN120ticks/
16camera checks, full imported/generated source closure and native-model proof.
Only root may admit/sign the candidate, after physical55 result and all its
retained raw exports have been captured. A successful version-only physical
trial still precedes HTT RX-ring/fragment-bank/packet setup, peer-map, protected
RSN credentials, real AP association, key installation and IP.

## Offline admission boundary

admission_gate.py checks exact GEN56 public owner/target/asset identity, all
source/generated/compiled fixtures, actual-native24 proof/log, bounded single
owner/credit scope, both real-supervisor QEMU logs and frozen world17 checks.
It imports no key/state/signing/Bluetooth provider and always returns physical
admission=false. Negative gate fixtures are host data, never actual55 evidence.
Root must independently bind real55 receipt, both complete110-page captures
and genuine all14/lifecycle release before future56 signing/hardware.
