# Pure WMI TLV INIT envelope and memory description

Independent from the frozen, currently installed native43 driver. No device,
allocation, mapping, credentials or transmit permission. No memory/vector policy
is approved by this serializer. The caller must supply an independently approved
44-word resource vector in the exact upstream struct order (176bytes) and prove
actual DMA mappings/retention/exclusion of every control buffer before sending.
Only vector vdev/peer counts are checked here against the memory-plan resources;
the remaining resource fields are opaque and MUST NOT be treated as approved.
Active-peer resource mode is not represented by this fixed struct and is rejected.

The complete WMI command id1 and TLVs INIT74,RESOURCE75,ARRAY18,MEMORY76 follow
pinned Linux ath10k wmi-tlv.c/.h at commit6b5a2b7d9bc156e505f09e698d85d6a1547c1206.
ABI1.0/namespaces and minor53 come from that exact implementation. A command is
220+20*chunks bytes. One unsplit mapped chunk per SERVICE_READY request, at most16.
The existing checked memory planner is recomputed: ids/byte sizes/counts must
match. Require nonzero,4-byte-aligned32-bit addresses, bounded extents, no overlap.
This is not proof those addresses belong to the adapter. No64-bit addresses or
splitting one request across multiple chunks is supported. Output may not alias
inputs, and every rejection leaves it untouched.

`verify_init.py` extracts actual structs, tag enum, command id and ABI definitions
from hash-pinned primary source into an independent host oracle.1,691,012 wire,
capacity, plan/address/extent/overlap and rejection checks pass ASAN/UBSAN plus
COFF on Yukabox. Initial oracle checks caught and corrected a wrong resource
struct size and an inverted memory-planner return-code check before any device
integration. No test/COFF/native compilation runs on Mac.

wmi-tlv.c SHA02309cad56513a1ef0975c9d73e568e343c874d35124f39111ddd26d8a75c5bb;
wmi-tlv.h SHA16c6b984177dd8c0f80dbc4df52597a6def435d8892fb55381091bdb88a258c9.
Reference files: /home/yuka/rabbit-world/wmi-init-next/reference. Public proof in
evidence/2026-10-05. This module is NOT included in signed native43, its411 frozen
inputs or the active firmware-ram-5yo48w3h session. Next: actual service requests,
reviewed station resource vector, separately owned DMA memory lifecycle, then
integration/admission/transmission and a genuine WMI READY response. No Wi-Fi
scan, association, encrypted data or IP is claimed.
