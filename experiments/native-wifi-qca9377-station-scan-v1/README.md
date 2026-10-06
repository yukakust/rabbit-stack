# STA creation and passive scan coordinator (host-only)

This is a pure, bounded next-stage coordinator, not a working Dell Wi-Fi driver.
It uses the existing independently checked VDEV/scan serializers and HTC credit
ledger. A fresh actual WMI READY payload supplies the MAC; no synthetic MAC is
accepted as a production prerequisite. STA is fixed to VDEV0.

Flow: READY → reserve STA-create → commit credit → publish CE3 externally →
actual TX completion → reserve passive scan → commit → publish CE3 externally →
SCAN_STARTED / SCAN_COMPLETED, with early events held until actual TX completion.
`CREATE_ORDERED` means only that command DMA completed. It is deliberately not
called `CREATED`: no fabricated VDEV_CREATE acknowledgment is awaited or assumed.
SCAN_STARTED proves firmware accepted this scan, not association or usable IP.
The single-threaded caller exclusively owns the borrowed credit ledger. Firmware
incremental credit trailers alone return outstanding credits; DMA completion,
timeout, fault and terminal scan events do not refund them. Reservations can be
cancelled only before publication. Ambiguous publication must fault and retain
external DMA owners until an actual stop.

Every consumed RX completion gets its next monotonic ID from the actual descriptor
consumer, shared by all events/credit records in this coordinator. Payload hashes
are not completion IDs. This is API duplicate-consumption protection, not security
against firmware replay. Unknown events must be routed by a native dispatcher,
which is not implemented here; do not discard RX and pretend the IDs are contiguous.

Regulatory prerequisites remain external and mandatory. Frequencies passed to
`begin` must be authorized by a reviewed country/channel policy and that policy
must already be configured on the device. Hardware SERVICE_READY band endpoints
and the codec's syntactic frequency range are NOT permission to scan. This module
cannot attest the provenance of a caller-supplied frequency array. No country or
legal channel list was invented, and no RF commands were sent.

Remaining native integration: successful WMI INIT/READY; persistent CE3 TX and WMI
RX rings, owner lifetime and actual stop; device regulatory configuration;
validated START_SCAN dispatch/deadline and stop-scan cleanup; actual management or
HTT receive frames feeding the existing beacon parser; deduplicated BSS collection
and SSID `SILK_56E35E_Plus` comparison. This coordinator neither receives beacons nor
claims to have found that network. Credentials, authentication/key installation,
association, packet transport and DHCP are separate later stages.

`verify_station_scan.py` runs on Yukabox only in an isolated mirror. It derives
Linux enums/structs from pinned ath10k headers, checks create bytes against the
upstream struct, validates scan event values, and exercises early events, TX-only
ordering, credit starvation/refund, duplicates, malformed/foreign events,
truncation/mutation invariance, unapproved selected-frequency rejection, fault
ownership and cancellation under ASAN/UBSAN. A freestanding COFF build is also
required. Evidence explicitly says physical_verified/native_integrated/scan_sent
and wifi_connected are false.
