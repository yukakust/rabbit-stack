# Bounded native WMI INIT candidate (generation48)

Not physically admitted, signed or delivered. Derives isolated outputs from
unchanged native47. Firmware trial47 is still active on Dell. No physical
SERVICE_READY memory result is assumed; no scan, association, IP or WAN claim.

After actual HTC setup + validated SERVICE_READY, borrow the operating scope's
existing14 mapped buffers, CE0/1/2 rings, adapter and exact firmware pin. Reuse
the actual native47 retained-owner guard on every poll. Only zero host memory
requests are supported. Any request or unsupported base bitmap rejects before
INIT publication; no allocation while PCI bus mastering is active. A separate
live DMA owner design is required if physical firmware requests memory.

Use the pinned Linux PCI resource candidate and existing checked serializer/
transaction ledger. Reserve credits when building; commit BEFORE publishing
CE0 INIT228-byte frame, using negotiated WMI endpoint as transfer metadata.
Existing control TX buffer is reused only after previous DMA consumption and
empty-ring proof. Post fresh bounded CE1/2 receive buffers before transmitting.
Each actual consumed RX completion gets a monotonically increasing coordinator
ID. Firmware READY may arrive before TX completion; success requires both.
Credits return only via valid firmware reports, never via host DMA completion.
Reported minor53 or574 does not bypass strict ABI major/namespaces/status/MAC.

20-second bounded lifetime. Cancellation refunds only an unposted reservation;
ambiguous publication retains committed ledger state and all physical owners.
Errors from the shared operating guard propagate into startup diagnostics.
The existing outer probe owns ALL-engine stop/flush/unmap/free and pin release
on every success/error/cancel path. This is an INIT diagnostic, not a persistent
operating radio. The Linux host_capab management-bundle flag is reference data;
no management transmission is generated in this trial. Native management
completion dispatch/retained descriptor generations are still required before
station traffic and profile admission.

New read-only GATT UUID26/27 handles26..28 exposes QWIN0001/96 bytes:12 u32
phase/error/transaction/TX/RX/READY/minor/credit/memory fields, MAC at56, eight
last RX diagnostic words at64. Existing QWOP0003/488 and QWBT observations are
preserved. A physical success needs correlated native identity, INIT phase2,
valid READY/MAC, actual TX completion and all-owner QWBT release; receipt/QEMU
alone cannot establish that.

`verify_startup.py` runs actual generated entrypoints, real CE and checked
protocol code under ASAN/UBSAN on Yukabox, with an explicit mock target and
fixture-only owner override.22 scenarios: normal and early READY, missing READY,
missing TX completion, bad major/namespace/status/MAC/endpoint, wrong DMA cookie,
ambiguous TX/RX publication, cancellation before/after publication, nonzero
memory requests, unsupported bitmap, excessive credit reports, duplicate READY,
minor53 and574, clock reversal, poisoned pin and outer resident-stop callback.
Every scenario checks actual all14 mapping releases and firmware unpinning;
read-only GATT telemetry/read bounds/write rejection are checked too. No fixture
is claimed as a physical radio observation. `verify_initial.py` retains all65
initial entrypoint/resource rejection cases. Full EFI/QEMU/current-world proof
and fresh physical47 result are required before any signing gate is added.
