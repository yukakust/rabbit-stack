# Fixed read-only QCA9377 CE7 trial

This candidate reads exactly one32-bit target word: host_interest base400800 +
hi_interconnect_state offsetf8. Target Pack diag-target.json pins Linux source
hashes and the QCA9377/rev1 identity003821ff. This is an independent DMA/target
memory diagnostic before BMI, not early configuration or firmware activation.

Only CE7 is configured and run in the first exchange. Four registered coherent
pages remain under the existing bus lifetime: TX ring, RX ring, unused BMI request,
response. Both8-entry CE7 rings are seeded from hardware read indices. RX is posted
before TX, length4, metadata/flags0. The TX data address is the ONE fixed target
word translated using pinned qca6174_targ_cpu_to_ce_addr; no target write API exists.

CORE_CTRL is read through the claimed validated PCI IO handle at3a000. Translation
region `(core &7ff)<<21` must equal the freshly validated PCI BAR; the fixed target
window must fit the reported BAR extent. Active PCI Command must exactly match
owned bus command with Bus Master Enable. Unknown chip, failed/all-ones CORE_CTRL,
region mismatch, insufficient extent, wrong/unmapped/overlapping ring/response
memory or wrong callbacks fail before posting any target operation.

Poll cooperatively with a3second wait budget (reference busy-polls10ms); require both
completions, unchanged descriptor addresses/cookies and exact received length4.
Transient RX length0 is waited for. The observed target word remains raw data;
zero/all-ones/nonzero pointers do not grant any additional access or prove ABI.

Before first diagnostic shutdown, latch a96-byte snapshot. On success stop ALL
engines, verify Bus Master Enable off, close/flush both CE7 rings, then reinitialize
those same registered ring pages for the old CE0/CE1 BMI trial. On ambiguity,
cancellation or failure enter existing guarded teardown and retain uncertain
ownership; never free live DMA memory or skip stop/Flush/Unmap/Free. A failure of
CE7 suppresses BMI. No repeated allocation or target pointer chase is involved.

QPD11 retains QPD10 bytes0..699 and extends the read-only ATT report to716bytes:

|Offset|Bytes|Meaning|
|---|---|---|
|620|4|CE7 phase: idle0/wait1/done2/fault3|
|624|4|error: preflight1, command/core/region2, expose3, RXpost4, TXpost5, clock6, timeout7, lifecycle8, index9, descriptor10, completion11|
|628|4|flags: snapshot1, TXdone2, RXdone4, response bytes/address available8|
|632|4|fixed target CPU address4008f8|
|636|4|translated CE data address|
|640|4|CORE_CTRL read|
|644|2|active PCI Command|
|646|4|initial TX/RX indices, two16-bit words|
|650|4|last observed TX/RX indices, two16-bit words|
|654|2|observation-valid bits0TX/1RX|
|656|8|software TX read/write, RX read/write indices|
|664|8|mapped host response DMA address|
|672|16|original TX/RX descriptor slots, eight bytes each|
|688|4|host response word observed before cleanup|
|692|4|completed received byte count|
|696|4|reserved0|
|700|4|first poll elapsed microseconds, saturating32-bit|
|704|4|last poll elapsed microseconds, saturating32-bit|
|708|4|poll count, saturating32-bit|
|712|4|wait budget3000000microseconds|

Snapshot bytes persist across BMI overwriting the shared response page, cleanup,
retry and one-shot reattach. Descriptor nbytes may be cleared by completion. Data
is observational, not atomic or device attestation. Decoder retains old QPD formats,
bounds each snapshot separately and rejects malformed flags/masks/indices/address,
fixed-target/translation mismatch and inconsistent completed state. ATT ReadBlob
uses three chunks246/246/224bytes and rejects offset717.

Hardware completion is read before testing elapsed timeout. Delayed first polling
can observe an already completed read after the budget; this is reported explicitly
and does not prove when the device completed the operation. No polling frequency
is assumed. Clock reversal remains an error.

Host fixtures use the physical Dell's2MiB extent and chip identity; the old port
fixtures remain unchanged. Cases cover success, no completion, TX-only, invalid RX
length, CORE_CTRL read error/all-ones/region mismatch, cancellation, transient RX
zero, reversed time and insufficient1MiB extent. Additional cases cover delayed
first polling at200ms and3.5s, genuine no-completion after3.5s, and cancellation
after partial completion. They assert exact read-only
TX/RX descriptors and successful CE7 teardown before BMI publication. Existing
DMA failure retention, cached-MemoryEnable and Bluetooth recovery gates remain.

Physical authorization remains exact source/world gates -> local owner signature
-> Bluetooth saved session -> exact receipt -> fresh QPD11 -> owner scene check.
Firmware upload, early-config writes and Wi-Fi association are subsequent work.


## Bounded initialization reads after physical native23

Native23 proved fixed4008f8 read completed with response401ee0. New candidate
permits exactly three further read-only locations only after a completed HI read
with that exact value, both completion bits and mask3,4receivedbytes, same owned
bus/rings/response lifetime and fresh command/CORE/BAR validation for each read:
1. Fixed401ee0,36bytes: pinned pci.h pcie_state,9LE32words.
2. Fixed400900,4bytes: hi_early_alloc.
3. Fixed4008cc,4bytes: hi_option_flag2.

These addresses are finite Target Pack constants. A different returned HI pointer
fails before any configuration read. No arbitrary pointer chase or write API.
The structure's pipe/service pointers remain data; they are not adopted as
authorized read/write destinations. Read completion does not prove config ABI.

Reuse CE7 rings for all three reads, then the existing all-eight shutdown/flush
before CE0/1 BMI. Four existing coherent pages only. Copy each successful response
into owned telemetry before the next exchange overwrites it; preserve it during
cleanup and reattach. Failure/cancellation suppresses BMI and uses guarded teardown.

QPD12 retains QPD11 bytes0..715, appends84bytes, total800. New offsets:
716phase idle0/state1/early2/option3/done4/fault5;720error;724readmask;728fixed
state address;732last target;736completed length;740..775state9words;776early
allocation;780optionflag2;784firstpollus;788lastpollus;792pollcount;796reserved0.
Four ATT chunks246/246/246/62; offset801 rejected. Decoder rejects out-of-pack
addresses/lengths, impossible masks, unavailable data and missing completed-HI
authority. First HI snapshot still describes4bytes; later36byte read is separate.

Target initialization writes/commit marker/CPU wake/firmware upload remain disabled
until these physical fields, destination spans, exact target tables and reset
sequence are validated in a separately gated candidate.


## Physical long-read boundary and QPD13 transport

Native24 exact applied, but physical CoreBluetooth returned738 of800bytes with
no NSError. Envelope rejected; missing bytes were never padded or accepted.
This establishes the observed transport boundary, not its underlying cause.

QPD13 keeps the same800byte logical report, version13. Distinct diagnostic service
UUID suffix8 advertises handles8..12; file service1..7 stays unchanged. Read-only
characteristic UUID6/handle10 returns bytes0..715(716bytes, three ATT chunks).
UUID7/handle12 returns120bytes: QIC1 header4, SHA256 of primary716bytes32,
configuration bytes716..799(84bytes). No writes/notify/subscription are needed.

Reader accepts a split prefix only when main probe stage5/6/7 is terminal. It
checks extension exact length/header and prefix hash before assembling800bytes.
A hash mismatch, active probe or missing extension fails without accepting data.
Decoder's independent combiner checks the same framing; host tests reject partial
parts, invalid header/hash and a correctly hashed active probe. Native UEFI tests
read actual primary and extension via ATT, verify hash/bounds and reject out-of-range
offsets. A hash binds the two reads; it is not device attestation.
