# Actual native HTT version adapter: host-only proof

This folder derives isolated native52/persistent RX copies; frozen sources are
unchanged. No candidate/counter, signing, hardware, RF, credentials or state.
Build/run native C, ASAN/UBSAN and COFF exclusively on Yukabox.

## Exact owner boundary

The generated rx.c replaces the existing CE1 endpoint policy, not the owner.
The same QcaPersistentRx instance exclusively completes/reposts CE1 and CE2,
retaining startup descriptors/cookies, DMA maps and bounded FIFO2. CE1 permits
HTC endpoint0 and actual negotiated HTT endpoint; CE2 remains actual WMI.
Every frame/trailer is checked before committing shared WMI credit changes.
HTT credit reports and every unsupported endpoint report fault; actual WMI
trailer returns on HTT/control/WMI frames are applied once. No HTT request
reserves, commits or refunds WMI credits. Firmware HTT op3 is the exact pinned
scope; codec validates actual retained RUNNING service metadata. Future
admission must bind that op value to accepted firmware and target provenance.

A private persistent-radio owner token binds the first query instance and
rejects rival instances even after DMA completion; it stays retained through
stop and evidence export. No retry instance can reuse the same acquisition.

QcaHttNative exclusively borrows CE4 ring4/descriptors8/payload9. It constructs
four-byte VERSION_REQ inside HTC endpoint from existing connection, transfer
metadata endpoint, no credit request, fresh cookie, immutable12-byte frame.
No additional DMA or duplicate CONNECT. Persistent guard validates actual
PCI/CE/register bases/maps, ring/cookie/address/capacity/index and same radio
lifetime/epoch. Publication sets request/watermark before doorbell; ambiguity
never becomes success and prevents resubmission. The source ring DMA matching
completion and actual newer current-endpoint VERSION_CONF are both required.
Response may be copied before DMA completion; query success waits for both.

A response already queued by the prepublication guard is rejected by actual RX
completion watermark. This is completion ordering, not an invented firmware
nonce or proof of air arrival timestamp. VERSION_REQ is issued once after INIT;
no association/station/data traffic is enabled.

The wrapper copies VERSION_CONF into response slot and unrelated control/WMI/
HTT payloads into archive2; no discard. If archive is full, the next FIFO head
stays owned and stop is requested. Export slots0=response,1/2=archive,
3/4=retained FIFO head/next,5=rejected frame after validated completion.
Private event copies include full bounded HTC frame/trailer; credit-only
frames also enter the owned FIFO. Malformed decoded frames are retained in
the rejected slot, and terminal RX fault prevents overwriting them. Read-only exact-copy export rejects short/aliased
output; payload bounds remain2040; raw HTC bounds2048. Copies survive stop and all-owner release.
No GATT/export framing is added here; a future whole profile must expose and
persist exact bytes/hash before native unload admission.

Deadline3seconds, clock rollback/guard/codec error/backpressure requests the
existing checked qca_stop once after explicit quiesce at checked current
timestamp (native loop last_now can lag wrapper servicing). Its return is busy-state, not success/ACK.
The native loop must continue ticking actual cleanup. RELEASED query status
requires unchanged persistent lifecycle's actual all-owner closure/unload-safe
proof. Hardware ownership faults remain lifecycle RETAINED even if separate
adapter cleanup later proves maps physically gone; no reset bypass. Error and
raw evidence stay accessible and no automatic query retry occurs.

## Actual entrypoint model

verify_native.py uses original native PCI/config/MMIO/CE/DMA and firmware startup
entrypoints, full public firmware bytes and a fixed public fixture owner only.
It injects actual descriptor completions/HTC bytes via the hardware simulator,
not a fake callback returning VERSION_CONF. Cases exercise healthy response,
DMA stall, ambiguous doorbell, cookie/address/length/index corruption,
unsupported major/reserved/endpoint, genuine WMI trailer on HTT response,
unsupported HTT credit report, stale response, control+WMI+HTT interleaving,
archive/backpressure, missing response, mapping loss, epoch/session change
and clock rollback.
Reports bind source and exact compiled native fixture copies. Host model
all14 release is not physical Dell proof. No wholeEFI/QEMU was attempted.

The reusable adapter is called explicitly by native fixture begin/poll; a
production whole-profile loop still needs integration, read-only status/raw
exports, exact accepted firmware op proof, repeatedEFI/QEMU/world17 closure,
and root-controlled admission/physical trial. HTT version success still does
not establish RX data ring, fragment banks, HTT TX/RX packet formats, peer-map,
RSN, AP association, key installation, DHCP or internet connectivity.
