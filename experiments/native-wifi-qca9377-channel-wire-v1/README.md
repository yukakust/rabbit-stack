# Policy-bound SCAN_CHAN_LIST and PDEV_SET_REGDOMAIN wire codecs

Pure serializers, no RF publication/HTC/MMIO, default frequencies, ruleset, country
or authority decision. Caller supplies an independently authenticated and reviewed
policy with target/ruleset/location/review digests and actual hardware description.
Nonzero digest fields and alpha2 format are structural checks only: hashes do not
prove authenticity or give permission. The trusted caller must verify provenance,
actual board/country/ruleset intersection and policy approval before construction.
Host fixtures are synthetic and never constitute a production policy.

Narrow profile: selected rows only, passive legacy20MHz. DISABLED rows rejected,
NO_IR retained and all rows passive; RADAR remains passive/DFS on5GHz (rejected
on2GHz). No IBSS, active probes, HT/VHT/wide geometry or DFS-country override.
Explicit combined/per-band regdomain values must equal actual hardware domain;
alpha2 metadata does not override it. Capability bands restrict the approved
list but never generate channels or permission. Duplicate, malformed, unsupported,
out-of-band, wrong-target and missing-provenance inputs fail without output writes.
The syntax supports the same2.4/5GHz MHz range as current scan codec; a syntactically
valid centre still requires actual policy authorization and valid channel geometry.

Rows express powers in whole dBm and antenna in whole dB. Power converts to half-dBm
wire bytes as pinned ath10k_update_channel_list does; min_power/reg_classid remain
zero as its narrow legacy profile. Reject >127dBm, >255 antenna, max>regulatory max
and unsigned representations of negative/overflow values. Fractional mBm inputs
are not accepted by this API: the policy adapter must convert exactly or reject,
never silently round a regulatory limit upward. Zero fields must be explicitly
provided by the reviewed policy, not inferred as approval.

Complete WMI sizes: SCAN_CHAN_LIST16+28×count; PDEV_SET_REGDOMAIN32. Negotiated WMI
payload limit is explicit. At actual1784,63 rows fit and64 do not; no splitting,
implicit replacement or credit refund is implemented. Output may not overlap
input policy/hardware. Caller retains immutable policy while constructing/publishing.

verify_channel.py on isolated Yukabox extracts pinned Linux TLV enums/structs,
actual legacy channel assignments, actual power conversion and regdomain
assignments into an independent oracle. ASAN/UBSAN differential tests exercise
powers/antenna units, NO_IR/RADAR passive encoding, payload lengths, country/domain/
target/provenance rejection, DISABLED and active requests, duplicates/out-of-band,
overflow, overlapping buffers and mutation invariance. Freestanding COFF required.
These results establish wire compatibility and guards, not regulatory approval,
firmware acceptance or physical Wi-Fi. The actual CE3 publisher/owned RX/lifecycle
join, signed policy admission and hardware observation remain separate work.
