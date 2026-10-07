# Full boot 60 — unsigned offline candidate

The exact public target/owner/751436-byte firmware container policy is inherited
from59 with generation60. This candidate restores the validated WMI-v5 path:
full MAIN727128 bytes including padding → BMI_DONE → HTC READY/control setup →
SERVICE_AVAILABLE/SERVICE_READY → one CE3 WMI INIT → INIT TX complete + WMI READY.
Nonzero firmware host-memory requests still fail closed; new DMA allocation is
unsupported. Scan, association, credentials and IP are not integrated here.

QPFX0001 remains240 bytes/58words, read-only service29..51, ten raw HCI pages.
Generation and raw generation become60. Phase0 means not armed,1 fullboot active,
2 teardown requested,3 verified actual host resource release + frozen raw history.
Reason0 now requires actual WMI INIT completion and parsed READY, not prefix limit.
Reasons1 deadline,2 clock rollback,3 boot/operating/startup fault,4 invalid boot
phase,5 critical HCI overflow,6 USB fault,7 explicit cancel retain their diagnostics.
QWBT/QWOP/QWIN remain the inherited bounded full boot/operating/startup statuses;
QPFX alone is not proof of network scan, an IP address, or chip future ROM readiness.

The32KiB stop is removed. Physical59 measured312descriptors/255.354s (~0.818s each).
Full MAIN needs about2932descriptors plus helper/board/control work, suggesting
roughly45–50min. The overall watcher is bounded at5400s (90min), approximately a
2x allowance. Individual BMI/HTC/WMI and all USB/HCI/resident timers are unchanged.
Boundary tests prove no stop one microsecond before5400s and stop exactly at5400s.
The model also crosses32KiB and all valid boot phases without a prefix stop.

On success the inherited checked adapter cleanup is allowed to finish, then RAM
is released. An early unconditional qca_stop would mark successful cleanup as
cancelled;60 avoids that while fault/cancel paths still initiate checked teardown.
Phase3 requires the real all14 unmap/free/close, no bus/pin/pool/PCI/IRQ/link/reset
owners, rather than inventing release from a model counter. Resident-fatal USB
boundary explicitly reports incomplete/unfrozen cleanup; it is not called success.

Only Yukabox Linux performs C/ASAN/UBSAN/COFF/whole EFI/QEMU checks, in independent
parallel-fullboot60-native-v1/source and its own TMPDIR. Fixed public model keys
are used only in fixtures. Native59/signed artifacts and the rejected HCI timer
preparation are untouched. Root must review before admission/signing/hardware.

```
python3 verify_native.py
python3 prove_fullboot.py --world runs/world19.rup --world-json runs/world19.json --tmpdir /home/yuka/rabbit-world/parallel-fullboot60-native-v1/tmp
python3 verify_production_diff.py --baseline /home/yuka/rabbit-world/parallel-observation59-native-v1/source/experiments/native-wifi-qca9377-transport-observation59-native-v1/runs/checked-candidate --candidate runs/checked-candidate
```
