# Owned station/scan event dispatcher (host only)

Adapts the station-scan coordinator to `QcaRxEvent` owned payloads returned by the
reviewed persistent RX pump. The pump validates HTC/trailers and applies firmware
credits exactly once before creating an event. This dispatcher does not decode
HTC or call the credit ledger. It publishes only validated station event state.

Completion IDs must increase but can have gaps: the pump counts credit-only and
other completions even when no WMI payload is emitted. FIFO offer detects repeated
or out-of-order IDs. The copied type is exactly the reviewed rx.h QcaRxEvent ABI.
Pending scan/request IDs and negotiated endpoint are bound at begin; subsequent
mutation is rejected. Current checked profile is VDEV0, not arbitrary VDEV support.
Begin precedes runtime events (`station.last_rx == 0`); no migration of a partially
consumed old/raw stream is fabricated.

A two-slot owned FIFO permits explicit backpressure. Unknown HTC control, unrelated
WMI, foreign scan/request/VDEV events and known scan messages with unsupported TLV
extensions remain UNMATCHED and retained. Caller can explicitly transfer the FIFO
head to another owner using `take`; the output must be retained, not dropped.
Malformed/duplicate/invalid-order matching scan events remain owned and return an
explicit error for caller fault/recovery. There is no ACK for unknown commands.

STA-create still uses the existing checked prepare/credit/post/complete TX methods.
Exact CREATE TX completion means CREATE_ORDERED only. Matching SCAN_STARTED proves
this scan was accepted, not that station is associated or has IP. Matching terminal
scan events are retained in station.last_event, with early RX result held in
SCAN_POSTED until actual scan-command TX completion. Foreign-channel indications
must reference a selected policy-approved frequency; this is no country/channel
approval and no RF operation is performed by the dispatcher.

Native handoff: peek RX FIFO before `take`; ensure the dispatcher has room, take to
an owned local event and `offer`. If offer rejects unexpectedly, retain that local
copy for recovery. Route all events through this new owner; do NOT pass the same
raw frame into old qca_station_scan_receive or qca_scan_stop_receive, as that would
apply credits a second time and enforce invalid contiguous IDs. TX preparation may
still reserve/commit the common ledger under the same serialized owner. STOP_SCAN
needs a corresponding owned-event adapter; the earlier raw STOP wrapper is not
silently treated as compatible. Unknown events can block the head until another
router handles them, deliberately preserving bounded ownership.

Required next integration: actual persistent pump/native command publisher,
exclusive owner and pending registry lifecycle, bounded timeout/fault handling,
STOP adapter, reviewed regulatory/device configuration, scan/beacon collection,
authentication and packet networking. No firmware CREATE ACK, legal channel list,
SSID discovery, association or physical Wi-Fi result is claimed.

verify_dispatch.py uses pinned Linux scan enum/struct oracles, exact extracted
reviewed owned-event ABI, ASAN/UBSAN and freestanding COFF on an isolated Yukabox
mirror. Tests include a previously applied incremental credit with no second
ledger mutation, real completion ID gaps, early RX/DMA ordering, replayed and
foreign events, control ownership, FIFO-full backpressure and malformed mutation
invariance. This is a pure dispatcher contract test, not a new MMIO/RX-pump model.
