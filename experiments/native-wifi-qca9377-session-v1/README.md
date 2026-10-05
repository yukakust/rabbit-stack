# QCA9377 operating-firmware session

Prepared independently while the native38 RAM upload is pending. Nothing here
changes that immutable receiver or signs/sends a new native package.

`htc_wire` is a bounded, freestanding PCI HTC wire codec. It separates payload
from validated trailers, aggregates credit reports transactionally, checks
READY/service responses, and constructs endpoint-zero WMI/HTT service requests
and unbundled PCI setup-complete. It has no MMIO, DMA, radio or network access.
Unknown records and bundles fail closed. READY credits above 255 are outside
this initial profile (the service credit allocation wire field is eight bits).

Run `python3 verify_htc.py` on Yukabox. The checker hashes the pinned Linux
`htc.h`, extracts its packed wire structs as an independent layout oracle,
compares transmitted bytes, checks malformed frames with ASAN/UBSAN, and
compiles the codec to freestanding x86-64 COFF. These are host checks only.

`wmi_scan` constructs a WMI-TLV passive VDEV0 scan over supplied frequencies
and decodes scan events only when scan/request IDs match. It does not send
anything. Caller must first initialize firmware, create VDEV0, and validate the
frequencies against the firmware's regulatory information. The initial TLV
iterator accepts four-byte-aligned records only. No password, SSID, probe
request IE or BSSID filter is included in the passive scan command.

Run `python3 verify_scan.py` on Yukabox. This checker also pins `wmi.h` and
`wmi-tlv.h`, compares the scan bytes to their extracted packed structs/enums,
tests malformed/truncated/duplicate/uncorrelated scan events, and builds COFF.
The TLV reference header is the exact pinned download at the earlier
experiment's `runs/wmi-reference/wmi-tlv.h`; its hash is checked before use.

`htc_session` adds the bounded READY → WMI connect → HTT connect → PCI setup
handshake. It checks transport completion, service IDs and unique assigned
endpoints. It has no DMA, deadline, operational credit ledger or WMI dispatch;
those remain obligations of the future native transport. Its injected-message
sequence tests are included in `verify_htc.py`.

`beacon_info` extracts SSID/BSSID, advertised DS/HT channel, privacy flag and
opaque RSN bytes from one bounded ordinary beacon/probe response. Hidden SSIDs
do not match the requested network. Malformed frames, duplicate key elements,
inconsistent channels and fragments preserve caller output. RX must validate
firmware framing and strip any FCS before calling it. Advertisements are
untrusted; an SSID match or privacy flag does not authenticate an access point.
Opaque RSN bytes still need a separate security validator before association.

Run `python3 verify_beacon.py` on Yukabox with the pinned Linux `ieee80211.h`
saved under `runs/reference`. It checks the header hash, derives an independent
layout/constant oracle, checks9117 assertion groups with ASAN/UBSAN, and builds
freestanding COFF. This parser is not integrated into native41 or a real scan.

`wmi_boot_info` validates the pinned WMI-TLV ABI and extracts bounded service
bitmaps, regulatory band limits, memory requests and READY/MAC information.
Malformed, duplicate and inconsistent events preserve the caller output. It
only describes requirements; it neither allocates memory nor authorizes radio
frequencies. The verifier pins the ABI macros in `wmi-tlv.c` as well as structs
and includes injected-event tests with sanitizers.

Still required: physical firmware startup; retained CE receive/transmit queues;
native HTC service/credit state; WMI TLV init and physical scan; HTT data receive/transmit;
protected local credential delivery; router authentication; DHCP/IP; actual
traffic to Yukabox. Firmware READY is not a Wi-Fi connection.

Protocol reference: Linux commit
`6b5a2b7d9bc156e505f09e698d85d6a1547c1206`, ath10k `htc.h` and `htc.c`.


## Operating control prerequisites (host-only)

`htc_credit.h/.c`: single-owner WMI credit ledger, fixed negotiated endpoint;
accounting preserves available + reserved + outstanding = negotiated credits.
Reservations include the eight-byte HTC header. Commit before DMA publication;
only unposted reservations may be cancelled. DMA completion alone never restores
credits. Caller must retain unknown DMA ownership and consume each RX completion
once. Arbitrary repeated incremental firmware reports cannot be detected here.
No hardware, dynamic allocation, automatic cleanup or HTT credit-flow support.
`verify_credit.py` uses the exact pinned Linux cost expression as its oracle;
100,487,721 size/boundary/state/rejection checks pass ASAN/UBSAN and COFF on Yukabox.

`htc_control.h/.c`: endpoint-zero READY/WMI/HTT/setup coordinator. A response
arriving before the corresponding validated TX completion is checked against the
prospective state and copied once; no phase advances before completion. All six
WMI/HTT endpoint assignments within the observed four-endpoint limit and both
response/completion orders pass (1,418 checks), ASAN/UBSAN and COFF on Yukabox.
Actual CE ownership, deadlines, quiesce and early WMI service events remain outside
this module. Neither module is installed or proves a router connection.
