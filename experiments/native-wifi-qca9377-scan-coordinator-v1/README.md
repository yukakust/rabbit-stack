# Host-only bounded passive scan coordinator join

Not admitted for native/RF deployment. Full EFI/candidate work waits for root review.
Joins immutable channel/vdev/scan/stop body codecs with the actual persistent TX/RX
APIs and the owned event dispatcher. The only reserve/commit/cancel owner is
persistent-tx. Old station/STOP TX prepare/post methods are never called. Stage
ordering: channel list → regdomain → STA create → passive start → bounded stop.

Pending station POSTED/frame bytes are projected only from the exact outstanding
TX request and the publisher's real POSTED/DMA_DONE state. Actual matching DMA_DONE
permits ordering, not a firmware ACK. CREATE_ORDERED stays distinct from scan
acceptance. Scan STARTED must be a validated matching owned event newer than the
RX completion watermark recorded at publication; no earlier matching packet can
be reused as acceptance. Actual v5 validated startup READY supplies MAC, including
physical52 extended prefix; old strict36 station constructor is not used.

The policy is explicitly provided, copied immutably and structurally checked with
channel-wire. Hardware capability fields must equal actual SERVICE_READY data.
Policy authentication/approval and target identity provenance remain external
trusted admission prerequisites, not decisions made by this coordinator.

RX pump applies firmware trailers once. Owned scan/STOP handles events with ID
gaps and retains unmatched/control/foreign/unsupported payloads. Before progressing
an unposted TX, already available owned terminal events are serviced. Genuine
natural termination may cancel ONLY persistent TX WAIT/RESERVED, then retires its
exact ID. No old STOP reservation is projected or cancelled. STOP publication is
projected into event/deadline state only, and ended after actual terminal+DMA_DONE.
Starvation/deadline/rollback/epoch/request mismatch fault with retained owners.
Native clock is microseconds; owned STOP milliseconds are derived only after
checking microsecond rollback. ENDED is never DMA-unload permission.

Beacon parsing alone cannot prove SSID discovery. Accepted observation additionally
requires this epoch, matching SCAN_STARTED, active matching FOREIGN_CHANNEL,
selected reviewed channel and completion newer than publication watermark. The
full owned raw event plus parsed BSS/epoch is retained in one observation slot;
full slot backpressures MGMT processing. Unknown/wrong-channel/unsupported data
stay owned. Caller explicitly transfers unmatched events/observations and must
retain them; records do not authenticate an AP or establish association.

The test joins actual persistent tx.c/rx.c, real CE ring bookkeeping, lifecycle,
v5 READY parser and codecs in one bounded C model. Lower operating/PCI/DMA owners,
CE hardware index/MMIO and device firmware are explicit backend models, not actual
native platform entrypoints or physical results. Healthy/fault cases check that
clear/unload is denied before same-epoch stop plus exact14 releases. An epoch-change
case remains retained with14 resources; it is not fabricated into release.

Remaining before EFI: independent root review, actual native backend join and
fresh observation/stop policy; authenticated policy admission; more actual-adapter
failure/recovery coverage; immutable full-source closure/repeated builds/QEMU/
current-world admission. No real source authority, fixture country/frequencies,
key, native counter, candidate, signing or RF permission is manufactured here.
