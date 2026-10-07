# Serialized WMI CE3 publisher boundary

Host-only transport work. No new native candidate/counter, firmware admission,
station command policy, RF permission, key access or hardware send is provided.
The model uses an explicit dummy command header and never fabricates a firmware
response. Production callers must supply independently validated command bytes.

The startup INIT API cannot be reused: it requires no outstanding credits and
expects a READY event. This module instead borrows the actual persistent radio,
CE3 ring, descriptor/data mappings6/7 and **the same** HTC credit ledger as RX.
There is one publisher and one outstanding request. Caller serializes all APIs
with radio polling, RX dispatch and stop; it must not create competing publishers.

## Ordering and ownership

`submit` validates the minimal WMI envelope, limits/deadline and fresh owners,
then makes an immutable owned copy. It does not validate a command's semantics
or grant RF permission. Frames that cannot fit the entire negotiated credit pool
are rejected rather than waiting forever. Temporary credit shortage is bounded.

`poll` advances at most one TX transition:

1. WAIT_CREDIT reserves a ticket from the shared ledger when actual credits exist.
2. RESERVED copies data to the existing retained buffer, commits credits and marks
   POSTED **before** any descriptor/doorbell write. Ambiguous publication faults.
3. POSTED observes the actual CE3 completion index and validates exact software
   cookie, address, capacity and descriptor length. Only then becomes DMA_DONE.

DMA_DONE means the transfer completed, allowing command ordering. It is not a
regulatory, VDEV_CREATE, scan or other firmware ACK. Completion does not refund
credits. Only the validated RX trailer does so. Repeated DONE polls do not count
another completion or return any credit. A matching `retire` orders the next
request with a new monotonic cookie and HTC sequence.

Explicit cancel refunds only an unpublished WAIT/RESERVED request with fresh
active owner/ring proof and the exact owned ticket. Committed publication cannot
cancel/refund. Starvation/deadline/clock/owner/descriptor/index/read failures retain
the ticket or committed credits and actual mappings until checked stop. Clearing
the publisher requires the same acquisition's all-owner-release proof and never
returns credits to an old ledger. Radio faults can leave the lifecycle RETAINED;
independent checked recovery remains a separate gate.

## Scan-plan integration contract

Follow `native-wifi-qca9377-scan-native-plan-v1`: reviewed channel/policy artifact
first; pinned SCAN_CHAN_LIST then PDEV_SET_REGDOMAIN ordering; constructor and
pending-command binding before publication; VDEV_CREATE yields CREATE_ORDERED
after actual DMA, without an invented ACK; only real matching SCAN_STARTED/terminal
events establish scan acceptance/end. RX owns early/unknown events and returns
credits once. A command registry/dispatcher must join those events to requests.

No approved selected-frequency artifact exists merely because SERVICE_READY gives
capability bands or regdomain108. A scan event also does not establish discovery
of the requested SSID; management/HTT beacon collection is still required.

## Verification

Run `verify_native.py` only on Yukabox in the unique
`/home/yuka/rabbit-world/parallel-persistent-tx-v1` mirror. It links the actual
native entrypoints, persistent RX and this CE3 owner under ASAN/UBSAN, then builds
freestanding COFF. The fixed test signing owner is not the real owner key.

Sixteen model cases exercise sequential ordering, DMA without credit refund,
actual RX credit return restoring a starved publisher, unposted cancel, starvation,
deadline, rollback, publish ambiguity, cookie/address/length/index/read errors,
quiesce and lost route/mapping ownership. Rejected malformed/alias/oversized/
unfundable requests preserve publisher and ledger. Actual all14 release is checked.
These are hardware models, not Dell command/RF results or full EFI/QEMU admission.

Remaining: reviewed RF/channel serializers/policy, pending registry/event dispatcher,
station/scan/owned STOP joins, future bounded whole EFI profile/source/admission
checks and physical observation. No firmware success should be inferred from this
transport's DMA completion.
