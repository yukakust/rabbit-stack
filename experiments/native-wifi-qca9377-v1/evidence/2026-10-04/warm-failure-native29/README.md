# Physical native29 cached warm failure

Exact APPLIED runtime29/world14 preserved, session pci-native-aqp0dyyt,
payload11a9df2059578ca8f2b6c7046a61e211672ddda3f5ab065660038fb99190db3e.
Host prerequisites: ../warm-failure-qpd15-host. No replay/signature regeneration.
Fresh known Dell QPD15 hash-bound split, zero reader writes. Failed stage6,
adapter CLOSED12/channels CLOSED6,14 buffers released, cold recovery verified,
ROM2 and IRQ/link/PCI restored; no retained DMA ownership, BME off.

Warm failure phase11 (second ROM wait), last indicator0, phase elapsed1175000us,
first ROM polls4, second ROM polls2, last reset read33000800. This is LESS than
per-wait3s. Core source has only phase3s and global7s TIMEOUT paths; absent a
cancellation, this establishes GLOBAL deadline exhausted before second phase
budget. Do not claim device exhausted its3s ready window. Native cooperative
polls/guarded PCI/MMIO and configuration consume wall-clock time as well.

Next falsifiable change: increase only global bound to20s, preserve3s per wait,
all I/O order/IRQ/DMA guards; add600ms cooperative native fixture, run old7s
baseline and verify success with new bound. Separate IRQ-window discrepancy
remains a hypothesis and should NOT be mixed into this deadline comparison.
Physical cause of ROM delay still unproved. No firmware/association/DHCP/video.
No user reboot, USB/bootstrap write or owner key export. City/tail after29 unobserved.
