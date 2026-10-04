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
