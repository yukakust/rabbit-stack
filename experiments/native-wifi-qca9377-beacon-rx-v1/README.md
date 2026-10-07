# Pinned TLV WMI management RX → copied beacon/probe BSS information

Offline pure-parser slice. No RF scan, native candidate, device read/write,
credentials, signing, state mutation or frozen-source edit occurred here.
The SSID in fixtures is synthetic input, not a received physical observation.

## Mature path and minimal supported profile

Pinned Linux commit `6b5a2b7d9bc156e505f09e698d85d6a1547c1206`:

* `ath10k_wmi_tlv_op_rx` strips `wmi_cmd_hdr` and dispatches
  `WMI_TLV_MGMT_RX_EVENTID` to `ath10k_wmi_event_mgmt_rx`.
* `ath10k_wmi_tlv_op_pull_mgmt_rx_ev` finds `STRUCT_MGMT_RX_HDR` and
  `ARRAY_BYTE`, reports channel/SNR/rate/PHY mode/frame length/status/four RSSIs,
  bounds the frame and passes exactly its declared bytes onward.
* `ath10k_wmi_event_mgmt_rx` explicitly documents that essential management
  frames arrive via WMI; extra copies can arrive via HTT. This supplies a mature
  WMI path for potential beacon discovery without guessing the HTT descriptor
  format. It does not prove this physical firmware has already delivered a frame.

The constants and struct are independently compiled from the actual pinned
header in the host oracle:

| Field | Pinned wire definition |
|---|---|
| WMI event | 0x7001; low24 bits of cmd_id, high8 platform-private bits |
| Management header | TLV tag44; known struct40 bytes |
| Frame array | TLV tag17 (ARRAY_BYTE) |
| Header offsets | channel0, SNR4, rate8, PHY mode12, buf_len16, status20, RSSI24..39 |

`qca_wmi_beacon_rx` takes the WMI payload including its four-byte event header,
after the caller has validated/removed HTC framing and its trailers. Its own
bounded TLV walk follows Linux's byte lengths. The existing SESSION
`qca_wmi_tlv` enforces every TLV length divisible by4, whereas Linux's iterator
does not; therefore that helper is intentionally not reused for unaligned
ARRAY_BYTE frame lengths. The new parser accepts an exact byte array or at most
three zero bytes of padding to the next4-byte boundary. Frame bytes must fit
their own ARRAY_BYTE TLV, never borrow a following TLV. Duplicated required TLVs,
truncation, oversized declarations and nonzero padding fail deterministically.
The total envelope is locally bounded to4096 bytes.

The first profile accepts only exact40-byte headers, status0 and received
channel1..13. Unknown header extensions/extra TLVs, extension-status0x40,
CRC/decrypt/MIC/key-cache errors, another management subtype or an unsupported
channel remain unaccepted. The strict status0 policy is narrower than Linux's
general handler, which may forward MIC-error frames with an error flag.
Larger headers require actual format evidence and a reviewed extension; no
common-prefix guess is silently applied here.

Both beacon and probe-response frames pass through the **unchanged** existing
`beacon_info.c/.h`, whose own bounded 802.11 validation checks addresses,
infrastructure capabilities, SSID/RSN/DS/HT elements and their consistency.
The adapter additionally requires any advertised DS/HT channel to match the RX
channel. Cross-channel advertisements may consequently be excluded by this
narrow profile. If no channel IE exists, it stays absent (`bss.channel=0`);
`channel`/`frequency_mhz` separately describe the validated RX metadata, not an
invented advertised BSS channel. Hidden SSIDs stay hidden and cannot match the
requested SSID. RSN is copied as opaque bytes; security selection/authentication
are not implemented here.

SNR/rate/PHY/RSSI fields are preserved as raw32-bit firmware metadata. No noise
floor, signal-strength or rate validity is invented. Linux divides rate by100
for its bitrate lookup, and warns PHY mode alone is unreliable for band
selection; this adapter uses the explicitly supported received-channel range.
No signed-RSSI reinterpretation or dBm assertion is made from these raw fields.

No heuristic FCS removal occurs. The supported framing mirrors the pinned WMI
path, which passes the declared management-frame bytes onward without trimming
an assumed4-byte FCS. The existing helper expects an ordinary no-FCS frame;
an observed firmware variant with appended FCS or extension data needs a
separately proven extractor before acceptance. The first physical event must
confirm this profile, not be coerced into it by dropping arbitrary trailing data.

## Ownership and evidence boundary

With a distinct nonaliasing output object, the function never changes/releases caller RX storage or touches credits,
completion IDs, timers, radio, queues or state. An accepted result contains
copied metadata/BSS/SSID/opaque RSN, so no borrowed frame pointer outlives RX.
For every other return the output remains untouched and caller retains input:

* ACCEPTED1: supported envelope and beacon/probe BSS parsed;
* OTHER_EVENT0: another WMI event;
* MALFORMED−1: bad envelope or frame;
* UNSUPPORTED−2: unknown extension/status/channel/type/advertised-channel mismatch.

These are parse results, not instructions to consume/free a queue entry.
The dispatcher retains unknown frames/events or applies its separately reviewed
bounded diagnostic/backpressure handling. In particular an authentication frame
belongs to a later management consumer, not the beacon collector.

This WMI header contains **no vdev, request ID or scan ID**. The parser cannot
honestly invent correlation to START_SCAN. The future caller must bind actual
RX ownership/completion, current boot/native/radio epoch and reviewed frequency
policy; reset collection/deferred inputs appropriately at a new epoch, and avoid
attributing a stale/pre-scan frame to a later accepted scan. SCAN_STARTED alone
does not prove reception or SSID discovery. An accepted syntactic frame alone
does not authenticate an AP or prove it came from physical Dell.

To claim physical `SILK_56E35E_Plus` discovery, preserve a real bounded owned WMI
RX observation with native/epoch/CE completion and policy bindings, parse the
actual supported envelope and beacon/probe payload, and show the exact nonhidden
SSID bytes/BSSID/RX frequency from that observation. Record actual format/status
and parsing result; no synthetic fixture or scan-event substitution. An untrusted
AP can advertise this SSID, so discovery still does not establish WPA security,
association, an IP address or Yukabox connectivity.

No separate MGMT_RX service-bit gate was identified in the pinned TLV service
enum; its MGMT_TX_HTT/MGMT_TX_WMI entries describe TX, not RX. Static receive
dispatch and the mature code comment support implementing this parser, but real
delivery still requires the physical persistent radio, registered scan/vdev
setup, actual event/CE2 pump and accepted format. If firmware delivers only an
unknown variant or an HTT-only frame, retain/report it; this branch does not
invent its layout or claim the RX path works physically.

## Verification

**459252** pinned-layout adapter checks passed under ASAN/UBSAN on Yukabox:
every16-bit header length, array length, declared frame length, status, channel,
event ID and frame-control value; all truncation boundaries; both byte-array
orders and unaligned/padded forms; duplicates/unknown extensions; padding,
overflow, nulls, exact-size heap inputs at every truncation for ASAN redzones,
unchanged rejection output, platform-private bits; raw metadata
extremes, hidden SSID, opaque RSN and missing/contradicting channel IEs.
The original unchanged beacon helper's **9117** tests were independently rerun
against the pinned 802.11 layout oracle. Both parser/helper compile to
freestanding x86-64 COFF. Native binaries and downloaded reference source stay
out of Git; public evidence binds source/oracle/reference/log hashes.

Reproduce on Yukabox with `verify_beacon_rx.py --reference <pinned-reference>
--session <unchanged-beacon-helper-snapshot> --clang <reviewed-clang>
--output <ignored-runs-directory>`. The isolated remote directory is
`/home/yuka/rabbit-world/parallel-beacon-rx-v1`.

Primary sources:
[pinned wmi-tlv.c](https://github.com/torvalds/linux/blob/6b5a2b7d9bc156e505f09e698d85d6a1547c1206/drivers/net/wireless/ath/ath10k/wmi-tlv.c),
[wmi-tlv.h](https://github.com/torvalds/linux/blob/6b5a2b7d9bc156e505f09e698d85d6a1547c1206/drivers/net/wireless/ath/ath10k/wmi-tlv.h),
[wmi.c](https://github.com/torvalds/linux/blob/6b5a2b7d9bc156e505f09e698d85d6a1547c1206/drivers/net/wireless/ath/ath10k/wmi.c),
[wmi.h](https://github.com/torvalds/linux/blob/6b5a2b7d9bc156e505f09e698d85d6a1547c1206/drivers/net/wireless/ath/ath10k/wmi.h),
[ieee80211.h](https://github.com/torvalds/linux/blob/6b5a2b7d9bc156e505f09e698d85d6a1547c1206/include/linux/ieee80211.h).
