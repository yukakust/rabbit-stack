# Bounded pre-cleanup BMI exchange snapshot (QPD8)

QPD8 extends QPD7 from280 to356 bytes. The existing ATT diagnostic reader uses
Read/ReadBlob bounds; no write operation exists. This is application telemetry,
not device attestation, firmware compatibility or successful Wi-Fi association.

The BMI polling path remembers initial software seed indices and the last index
returned by each existing CE0-source/CE1-destination read. No new MMIO read/write,
reset, interrupt, DMA mapping, timeout or descriptor-publication behavior is added.
At the first shutdown of an initialized exchange, before any stop/unmap/free,
copy only bounded still-valid registered/mapped memory into76 static bytes. Retain
that immutable snapshot across cleanup retries and one-shot reattach. Descriptor
slot is the original seed, not the potentially advanced software read position.
A completed descriptor may already have its length cleared by normal consumption.
An acquire fence precedes observation; device memory may still change during a
failed exchange, so this is bounded evidence rather than a simultaneous snapshot.

All words are little-endian. Offsets below are absolute diagnostic byte offsets.

| Offset | Bytes | Meaning |
|---|---|---|
|280|4|flags: captured, TXdone, RXdone, valid request/response/TXdesc/RXdesc bits0..6|
|284|4|last hardware index observation-valid bits0TX/1RX|
|288|4|initial TX/RX ring indices, two16bit words|
|292|4|last observed TX/RX hardware indices, two16bit words|
|296|8|software TX read/write, RX read/write, four16bit words|
|304|16|mapped request/response DMA addresses, two64bit words|
|320|16|original posted TX/RX descriptor bytes, eight each|
|336|12|response bytes while mapped|
|348|4|request bytes while mapped (GET_TARGET_INFO=08000000)|
|352|4|completed received byte count|

Zero flags means capture never reached a registered exchange, not proof of
hardware inactivity. Missing observation-valid bits means unknown hardware index.
Decoder rejects unknown flags, indices outside8-entry rings, invalid/unavailable
DMA addresses, inconsistent absent captures and response size above12bytes.

Host production-code checks distinguish a complete reply, neither completion and
TX-only completion. Snapshots remain after all mappings are released and reattach
cannot change them. Actual host snapshots are decoded, and malformed flag/mask/
index/address fixtures must fail. Existing DMA lifetime/failed-cleanup tests and
normal+EMPTY actual UEFI city/Bluetooth/malformed-link/rejection gates remain.
Hardware diagnosis requires a new exact owner-signed native update and fresh
physical QPD8 read; mock indices and target identities must never become Dell facts.

## QPD9: CE configuration before the first halt

QPD9 retains bytes0..355 and extends the report to620bytes. After ROM-ready,
boot IRQ restoration, fresh PCI identity validation and CE access/bus initialization,
stage13 reads one engine per cooperative poll, before the first halt/zero write.
Bus mastering remains off; no DMA buffers have been allocated. Each engine's
registers are sequential observations, not an atomic snapshot or device attestation.
Raw descriptor addresses are never dereferenced, registered or reused.

| Offset | Bytes | Meaning |
|---|---|---|
|356|4|engine availability bits0..7: all eight reads succeeded and none were all-ones|
|360|4|engine failed/unavailable bits0..7: a read failed or returned all-ones|
|364+32*i|32|engine i source base/size, destination base/size, control, command, source-read and destination-read; eight little-endian32bit words|

CE registers use the existing validated QCA9377 allowlist at base34400 +400*i,
offsets0,4,8,c,10,18,44,48. A failed read's initialized zero is not evidence of an
empty queue. A missing engine bit means capture not reached, including cancellation.
Snapshots remain immutable after stop/zero/unmap/free and one-shot reattach.
The original all-eight quiescence, bus-master-off and DMA lifetime gates remain.

Production-code fixtures seed nonzero initial bases/sizes and verify that the
snapshot retains them after live queues are zeroed. Separate fixtures inject a
pre-halt read failure, all-ones and cancellation after engine0. Decoder rejects
unknown/overlapping masks, all-ones marked available and data marked uncaptured.
Actual UEFI normal+EMPTY gates read the620byte diagnostic in three ATT chunks,
reject offset621, and retain Bluetooth malformed-input and recovery checks.
