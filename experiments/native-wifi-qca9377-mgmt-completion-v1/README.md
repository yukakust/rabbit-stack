# WMI management transmission completion preparation

Pure strict wire decoder and atomic outstanding-ID matching plan. Needed before
admitting the Linux resource candidate's host_capab bit9 into a native management
transmitter. This is not an installed native dispatcher or a DMA owner lifecycle.
No descriptors, firmware commands, credits, keys, radio operations, allocation,
unmapping or frees occur here. Not part of frozen native47.

Pinned Linux ath10k wmi-tlv.h/.c define single event28678/tag423 (20-byte struct)
and bundle event28679/tag552 (count followed by positional UINT32 arrays tag16:
descriptor IDs, statuses, optional PPDU IDs, optional ACK RSSI). Independent
fixtures compile actual Linux enums and the single-event struct. Bundle array
semantics are pinned to the real ath10k callback/pull implementation.

Admitted envelope is at most2048 bytes and32 reports (our bounded queue policy,
not a claim of firmware maximum). Arrays must match the declared count exactly,
IDs must be unique, all TLVs aligned/bounded, and only known tags are admitted.
ACK RSSI remains opaque wire data and is exposed only when the caller's validated
service policy explicitly enables it; current resource candidate does not enable
extended ACK RSSI. Even ignored optional arrays must have exact valid lengths.
Unknown extensions reject before output mutation; a physical response may require
a separately documented extension after actual capture. Firmware status is opaque:
a failed transmission is still a completion, not a successful association.

The whole report is matched against unique currently outstanding IDs before a
mask is returned. If any ID is unknown/duplicate, no partial output is published.
The mask authorizes no release. A future native dispatcher must also prove the
retained descriptor generation, actual TX DMA completion, current owning scope,
and all-owner cleanup. Descriptor reuse/replay safety is not solved by matching
payload IDs. Credit reports use the separate checked HTC ledger; this decoder
never refunds credits.

`verify_completion.py` runs on Yukabox with ASAN/UBSAN and freestanding x86-64
COFF. Pins Linux commit6b5a2b7d9bc156e505f09e698d85d6a1547c1206 and exact header/
source hashes under `/home/yuka/rabbit-world/wmi-init-next/reference`. Tests cover
all0..32 report counts,2..4 array layouts, ACK enabled/disabled, every truncation
except valid optional-array boundaries, mismatched lengths, duplicate/unknown
IDs, oversized counts, extra arrays, bad tags/alignment, output aliasing, opaque
failure statuses and atomic whole-batch rejection.33502 checks pass. Evidence
explicitly records no native integration, physical verification, owner release,
station admission, router connection or IP claim.
