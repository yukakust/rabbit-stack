# Owned WMI BSS selection, stage 2

Offline CPU component; no native deployment, DMA allocation, RF command,
association, credentials or IP. `selection.h` imports exact frozen64 production
`QcaRxEvent`/persistent/READY headers, not an invented model ABI. Copied parser
bytes come from the mature BSS-security/hostap 2.11 extraction and HTC/beacon
parsers; `frozen-inputs.json` pins their originals. Frozen64 is unchanged.

The target is exactly ten bytes `iPhone (9)`. Eight bounded entries retain an
owned raw HTC image plus copied parsed metadata. Offer re-decodes the full HTC
image, verifies actual WMI pipe2/negotiated endpoint/event/body-length joins and
validates the MGMT_RX TLV/frame, source=BSSID, channel/live-frequency, privacy,
RSN framing, suites, PMF and supported/basic legacy rates. Only pure WPA2-PSK /
CCMP group+pairwise and optional PMF are eligible. PMF-required, mixed suite
advertisements, RSNX, unsupported basic rates and unknown native capabilities
are rejected; there is no fallback to open/TKIP/SAE or automatic downgrade.
Mixed WPA2/WPA3 advertisements require a separately reviewed policy extension.

`qca_selection_begin` requires a zero-initialized table and immutable binding.
`qca_selection_offer_live` joins real persistent ACTIVE/owner/epoch/READY MAC/
HTC endpoint/RX completion observations before the pure offer. Caller invokes
it only after successful `qca_rx_take`; it never consumes a queue or touches
DMA. Unknown/non-target/malformed/stale input leaves the table unchanged, and
the dispatcher must retain/archive the original raw record. Repeated or below-
floor completions fail. Same BSSID replaces its previous snapshot only with a
newer accepted completion; expired entries can be reused, otherwise a full
table rejects rather than silently evicting a live candidate.

Freshness is CPU observation time, not TSF or claimed firmware arrival time.
Caller supplies a monotonic microsecond clock and explicit TTL (1..30,000,000
microseconds; this maximum is a local profile bound, not a vendor requirement).
Selection rechecks ACTIVE/current epoch/unchanged policy+native capability
provenance, and excludes expired entries. Highest firmware MGMT_RX **SNR** wins;
ties choose newest CPU observation, then lexicographically smallest BSSID.
The separately labeled estimated signal is SNR−95, following pinned ath10k's
default noise floor; no calibrated RSSI or measured per-channel noise is claimed.
Raw four-chain RSSI values remain in the parsed snapshot. Integer values that
cannot be represented as positive signed SNR are unsupported, not wrapped.

Primary source: Linux commit `6b5a2b7d9bc156e505f09e698d85d6a1547c1206`,
[`wmi.c`](https://raw.githubusercontent.com/torvalds/linux/6b5a2b7d9bc156e505f09e698d85d6a1547c1206/drivers/net/wireless/ath/ath10k/wmi.c)
MGMT_RX signal conversion, and
[`core.h`](https://raw.githubusercontent.com/torvalds/linux/6b5a2b7d9bc156e505f09e698d85d6a1547c1206/drivers/net/wireless/ath/ath10k/core.h)
default noise floor −95 / invalid chain RSSI128. Ranking uses SNR ordering under
that fixed-noise convention; it does not establish physical strongest RSSI when
actual channel noise differs.

Run `verify.py` only on Yukabox in isolated TMPDIR. It compiles actual imported
production types, exercises positive/negative lifecycle joins and single-byte
raw mutations under ASAN/UBSAN, then COFF-compiles every production C component.
All fixtures are synthetic. No physical Wi-Fi result is asserted.
