# ath10k scan event prefix correction

Pinned Linux6b5a2b7d9bc156e505f09e698d85d6a1547c1206 wmi-tlv.c
sets SCAN_EVENT minimum length sizeof(wmi_scan_event)=24 and copies only six
prefix words. Additional bounded aligned bytes inside tag36 stay opaque.
wmi.c STARTED/FOREIGN handlers do not interpret reason. This codec retains
reason uint32 unchanged; caller treats any nonzero terminal reason as failure.

No old source changed. One reusable prefix parser feeds match/dispatch; duplicate
known TLVs, truncated/unaligned/out-of-bound lengths, unknown type bits,
invalid encoded ids and aliases fail closed. Unknown additional TLVs return2
for owned archival, never semantic application. Original full frame/suffix is
retained by the native FIFO/archive; parser exposes no pointers into freed DMA.

Independent oracle extracts actual upstream packed struct and verifies minimum
policy. ASAN/UBSAN+COFF on Yukabox only. Tests include the exact captured
physical54 STARTED/FOREIGN28-byte values/reason6, all nine known types with
opaque reason variations and suffixes0..128, malformed sizes and aliases.
This is host evidence, not a new physical scan/SSID/connection result.
