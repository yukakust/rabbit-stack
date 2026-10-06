# Passive scan deadline and STOP_ONE (host-only)

Pinned Linux ath10k STOP_SCAN serializer plus a pure bounded-state coordinator.
No actual radio command, credentials, driver MMIO or Dell state modification.
Only STOP_ONE for the current scan/request pair is implemented. Linux writes the
raw scan ID through the union's `vdev_id` member and the prefixed scan ID separately:
the ignored field for STOP_ONE is preserved exactly, rather than invented as zero.

The wrapper borrows the station-scan coordinator and its exclusive credit ledger.
Route every actual consumed RX completion through this wrapper, numbered once in
the same sequence. Monotonic caller milliseconds establish a scan deadline; crossing
it requests STOP. Manual cancellation requests the same STOP path. Preparation
waits for initial scan-command DMA completion and sufficient actual credits.
Commit credits before CE3 descriptor publication; TX completion never refunds.
Cancel an unposted reservation only, allowing a later retry.

Firmware terminal scan events (COMPLETED, DEQUEUED, START_FAILED) confirm that this
matching scan ended. STARTED, channel events, DMA completion and a timeout alone do
not. If STOP is posted, a terminal event can arrive early, but ENDED additionally
requires exact STOP TX completion. This does not establish a distinct STOP command
acknowledgment: no such acknowledgment is fabricated. A scan may finish naturally
before the cancellation command is sent; the unposted STOP reservation is then
cancelled safely. Terminal reason remains in the underlying scan's last_event.

After STOP publication, its separate bounded deadline faults if no complete
terminal exchange arrives. Committed credits and external DMA owners remain
retained on fault. If credits are starved before publication, REQUESTED waits for
validated incremental firmware credits; the native caller must apply its existing
bounded RX/credit starvation watchdog and explicitly fault, rather than spin
forever or refund scan credits. Monotonic tick rollback is rejected. External DMA
teardown needs actual adapter stop and owner release even after ENDED. `fault`
never cancels an unposted reservation implicitly: call cancel_unposted before
faulting when a reservation exists.

Native prerequisites: INIT/READY, permanent CE3/control receive ownership, reviewed
country/channel configuration, actual scan transmission, per-completion RX router,
monotonic clock, STOP descriptor publication and bounded watchdogs. The station
coordinator itself remains host-only; no network has been found or joined here.

verify_stop.py extracts pinned structs/enums and the actual upstream STOP command
assignments, compares all scan IDs with representative request IDs, and tests
credit starvation, natural termination before publication, early completion,
manual cancellation, monotonic deadline/timeout, truncation/mutation rejection and
fault retention under Yukabox ASAN/UBSAN and freestanding COFF.
