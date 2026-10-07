# Owned-event STOP and bounded cancellation (host-only)

Joins the checked STOP prepare/post/complete methods with the owned station event
dispatcher. Reuses immutable scan-stop-v1 wire/credit/DMA-ordering code but never
calls its raw receive or station_scan_receive. The persistent RX pump alone applies
HTC credits; dispatcher and this wrapper process owned payloads without replaying
those credits. Preparation/commit still use the one exclusive common ledger.

Zero-initialize each wrapper before begin.

Route all accepted station event handling through owned_scan_stop_head. It captures
the actual FIFO head completion ID, calls dispatcher_head and recognizes terminal
only after dispatcher returns SCAN, the station's last_rx equals that completion,
and pending scan/request/VDEV binding still matches. Unknown/control/foreign events
stay owned/UNMATCHED; malformed/duplicate matching head stays owned and faults.
Completion IDs may have gaps. No new firmware acknowledgment is synthesized.

A genuine matching COMPLETED/DEQUEUED/START_FAILED can establish scan termination.
If STOP was published, both that event and exact STOP TX completion are necessary;
early terminal is held until TX completes. A genuine natural terminal before
publication cancels only an unposted STOP reservation. No other automatic cancel
or refund exists. ENDED does not prove a distinct STOP ACK or actual CE stop/DMA
owner release; initial scan TX may also still be in flight in an early-event case.

Scan timeout requests STOP. REQUESTED/RESERVED has a separate bounded credit-wait
deadline; repeated requests do not extend it. This also bounds initial scan TX
ordering wait. Posted STOP has its own bounded terminal/TX deadline. Caller supplies
monotonic milliseconds and must tick on every scheduler iteration. Rollback,
deadline expiry, binding mutation and malformed matching event fault closed,
retaining committed credits, reserved ticket if any, and all external owners.
A reservation retained on timeout is not silently cancelled: actual quiesce/owner
release and explicit reviewed recovery are required. Timing out never means scan
or radio stopped, and never grants unload or admission.

Caller must serialize dispatcher, STOP, command publisher and ledger; enforce the
persistent lifecycle/epoch and retain any event rejected while taking from RX.
Do not call the old raw STOP receive wrapper after the pump. Outbound CE3 publication,
actual descriptor-completion identity, clocks, adapter quiesce and all-owner-release
remain native integration responsibilities. No RF transmission, country/channel
permission, credentials, association or usable IP is claimed by this module.

Yukabox-only verify_owned_stop.py pins the reviewed RX ABI and upstream scan enums/
structs, runs ASAN/UBSAN and COFF. Tests cover early terminal/TX permutations,
completion gaps, natural terminal before publication, once-applied firmware credit,
no DMA refund, posted/credit-starvation deadlines, rollback, malformed/foreign/
duplicate ownership and event mutation invariance. This is an offline coordinator
contract test, not a new physical or MMIO test.
