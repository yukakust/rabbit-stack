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

Still required: physical firmware startup; retained CE receive/transmit queues;
HTC service/credit state; WMI TLV init and physical scan; HTT data receive/transmit;
protected local credential delivery; router authentication; DHCP/IP; actual
traffic to Yukabox. Firmware READY is not a Wi-Fi connection.

Protocol reference: Linux commit
`6b5a2b7d9bc156e505f09e698d85d6a1547c1206`, ath10k `htc.h` and `htc.c`.
