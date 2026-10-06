# QCA9377 PCI TLV resource reference candidate

Pure preparation for WMI INIT. No native integration, DMA allocation, radio
command, scan, credentials, association or IP. Native47 and its491 frozen
inputs remain unchanged while physical firmware delivery is active.

Instead of treating the old opaque `{1,2,...}` fixture as a station policy,
construct all44 resource words from pinned Linux ath10k QCA9377 PCI defaults:
4 vdevs,33 peers,66 TIDs, two peer keys, AST skid16, WDS32, native-WiFi decap1,
1056 pending MSDU descriptors,22 WoW patterns, remaining exact reference values.
The original Linux chain masks7 are preserved; actual physical SERVICE_READY
reported one chain. This candidate does not establish radio/channel permission
or decide any later per-device chain-mask command.

The base bitmap is exactly32 u32 words representing128 services; only four
low bits per word are used. RX_FULL_REORDER65 is word16/bit1. Its offload counts
are4 when advertised,0 otherwise. Upper bits confer no capability. Extended
TX_DATA_MGMT_ACK_RSSI174 is not validated; host TX_ACK_RSSI bit18 stays unset.
No capability is inferred from the truncated physical native46 capture.

The Linux reference host_capab bit9 (management completion bundles) is512.
Before native admission the dispatcher must implement that response contract,
or a separately justified and tested alternate host capability policy must be
chosen. The resource counts also feed the existing pure memory planner and INIT
serializer. Tests exercise0..16 synthetic memory requests; synthetic addresses
are not actual DMA owners. Retained mappings and non-overlap with live control
buffers remain required for native use. Memory planning budget is16 MiB.

`verify_resources.py` runs only on Yukabox. It pins the exact Linux commit
6b5a2b7d9bc156e505f09e698d85d6a1547c1206 and hashes of core.c,hw.h,wmi.h,
wmi-tlv.c/.h under `/home/yuka/rabbit-world/wmi-init-next/reference`.
The independent C oracle compiles resource assignments extracted from the real
Linux INIT function, the real packed resource struct, QCA9377 hardware defaults,
TLV constants and the actual WMI_SERVICE_IS_ENABLED macro. ASAN/UBSAN tests
compare8192 random bitmap/vector cases, reject unsupported lengths, invalid
chains and aliases, distinguish conventional32-bit packing and ignored high
bits, and exercise the full memory-plan/INIT serializer connection. The same
candidate compiles freestanding x86-64 COFF. Evidence records source/reference
hashes, derived oracle identity and explicit non-physical/non-admitted status.
