# Bounded native persistent RX pump

Offline derivation of immutable `wmi-native-v5` (native52/min-prefix READY) and
the reviewed `persistent-native-v1` ownership bridge. Only this new folder is
edited. No assigned next generation, hardware admission, signing, credentials,
station/RF command or physical write exists here.

## What runs

After actual INIT TX completion and validated READY, the bridge adopts the
startup's posted CE1 and CE2 descriptors, including their exact cookies. It
services these queues while the persistent lifecycle remains active. This
fills the concrete gap where `startup.phase==2` returned before receiving.

Each poll validates fresh mapping/PCI/IRQ/operating guards, ring ownership,
address, capacity, expected cookie and hardware index. It consumes at most one
completion per pipe. A zero RX length after an advanced hardware index waits
for actual length publication without consuming or returning credits.

Complete HTC frame validation precedes publication. The shared ledger receives
only validated incremental trailers; DMA completion never refunds credit.
Malformed endpoint/payload/trailer/length, excess credit and startup events
arriving again as runtime confirmations fault and revoke persistent admission.
There is no synthesized READY or ACK. CE1 payloads must be HTC endpoint zero;
CE2 payloads must use the negotiated WMI endpoint. Credit-only frames may use
endpoint zero or WMI on either control pipe. This narrow profile is explicit;
other routing is not guessed into support.

Unknown control/WMI payloads become bounded owned copies in a two-event FIFO,
including pipe, endpoint, raw WMI event word and actual completion ID. A later
dispatcher must interpret them. The pump does not discard or acknowledge them.
When full, it stops consuming/reposting; already posted descriptors remain
owned and bounded. Taking the correct FIFO-head ID returns a copy. Repeated or
wrong IDs and short/overlapping destinations leave the queue unchanged.

The lifecycle address and acquisition epoch bind the pump to one radio owner.
Quiesce blocks RX access/reposts; actual CE stop and existing cleanup retain
all mappings/pin until verified release. Queue reset/discard requires the same
lifecycle's real all-owner-release proof, never a timeout or another owner's
closed status. Runtime faults stay retained; independent recovery remains a
separate reviewed gate. The caller must zero-initialize each pump and serialize
the shared credit ledger, startup, ring and lifecycle operations.

## Evidence and remaining work

`verify_native.py` runs actual derived native entrypoints with an explicit PCI/
DMA/firmware model on Yukabox, using the existing pinned compiler, ASAN/UBSAN
and freestanding COFF. The fixed signing seed is only the public test owner;
the real owner key is never read. The unique mirror lives under
`/home/yuka/rabbit-world/parallel-persistent-rx-v1` and borrows Monocypher sources
read-only. Host-model results do not prove Dell behavior.

The suite covers all23 startup outcomes (including extended READY), five
persistent-owner failures and13 runtime RX cases: queued unknown WMI/control,
real incremental credit return, bad HTC length/endpoint/credit/READY/cookie/
address/size/index, delayed descriptor-length publication, full-FIFO
backpressure and ambiguous repost. Healthy cases retain200 ticks then prove
all14 releases. Runtime-negative cases also check that rejected frames never
alter the credit ledger or create owned events. Repeated idle polls after a
credit return prove the same completion cannot return credits twice.

Still needed: a validated event dispatcher and pending command registry,
station/VDEV command completion integration, regulatory/scan/association/WPA,
HTT data queues, DHCP/IP, confidential credential provisioning, persistent
read-only telemetry, reviewed recovery/unload state handling, full EFI repeated
builds/QEMU/current-world gates and a newly assigned/admitted physical packet.
This derivation retains native52 identity only as an offline reference and
must not be signed or deployed as counter52.
