# Bounded WMI host-memory plan

This pure component plans sizes from already validated service-ready requests.
It allocates no memory and performs no DMA, PCI, radio or credential operation.
It is not integrated into the installed Dell driver.

A fixed future resource profile supplies virtual-device, peer, active-peer and
byte-budget counts. The planner uses the pinned Linux order (active peers,
peers, then virtual devices), includes the extra self unit, falls back to peer
count when active count is zero, and aligns each unit to four bytes. Unknown
flags, duplicate request IDs, zero literal units, size-rounding overflow and
budget overflow reject the entire plan without modifying output.

The component's conservative ceiling is 16 virtual devices, 2048 peers and 16 MiB.
These are parser limits, not a selected or physically supported Dell profile.
Actual operating integration still needs observed service-ready bytes, a checked
station resource configuration, actual coherent allocations/mappings, 32-bit
physical-address validation, WMI INIT encoding and retained-owner cleanup tests.
No physical connection is implied by these calculations.

`verify_memory.py` extracts the count-selection branch and allocation-size
expression from pinned Linux commit 6b5a2b7d9bc156e505f09e698d85d6a1547c1206.
4,605,536 source-oracle/overflow/budget/duplicate cases pass ASAN/UBSAN and
freestanding native COFF on Yukabox. Source and log hashes are in
`evidence/2026-10-05/memory-plan/report.json`. Build only on Yukabox.
