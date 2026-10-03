# QCA9377 power/reset continuation contract

Goal: working secured Wi-Fi with DHCP and reconnect while city/Bluetooth remain
operational. This document describes the next probe, not completed association.
Native10 reached RTC ON, rejected zero chip-ID, cleared wake/restored PCI attrs/
closed exclusive PCI IO. Evidence is under evidence/2026-10-04/bringup.

## Baseline and discriminating test

Native11 read-only conventional PCI configuration256 and bounded capability list
will distinguish PM D0/D1/D2/D3 and capture PCIe Link Control. Missing/malformed
capabilities do not imply D0. No MMIO/PCI writes or reset in native11. Root and
world12 remain unchanged. The exact source, current-world, normal+EMPTY UEFI,
malformed capability, read-only ATT and owner/session gates precede delivery.
Physical state must be read through QPD3 rather than inferred from a mock.

## Next operational branches

If PMCSR is D3, implement an exclusive-claim D0 transition using the exact
capability address, preserving writable control bits and never writing a one to
PME-status (W1C). Wait the documented D3hot recovery interval cooperatively
before BAR access; re-read identity/PMCSR/command/BAR resources and fail closed
on loss. D3hot-to-D0 may internally reset PCI config when NO_SOFT_RESET is unset:
restore reviewed PCI resources before assuming the old BAR still applies. Mark
ownership before ambiguous writes. Shutdown clears wake, restores memory attrs,
restores the original PM control state, then closes PCI IO. Failed restoration
retains ownership. No bus-master enable is required for this identity probe.

If already D0, do not add a guessed power transition. Validate chip-only cold/
warm reset order against pinned pci.c/hw.c/hw.h. PCIe-local GLOBAL_RESET can
interrupt device accessibility; forbid reads during each reset settling window.
Implement assertion/deassertion as tracked cooperative stages, restoring reset
before release even after a write error. Observe FW indicator/SoC registers and
prove cleanup, timeouts, repeated detach, rejected-update rollback and city/BT
coexistence before physical signing. Do not mistake raw chip-ID zero for proof
of a supported revision. PCI revision0x31 is not a BMI/SoC version.

## Following requirements (still open)

CE/DMA must use bounded32-bit mapped buffers and stopped/verified engines before
unmapping/freeing. BMI get-target-info must bind target type/version before
firmware/board selection. Owner-signed hash-bound chunk assets must load firmware
in RAM within existing native/root limits. WMI/HTT ready, scan, local-only
credential entry, WPA handshake, packet interface, DHCP and measured reconnect/
loss behavior remain necessary. No password in chat/LLM/logs/Git. A physical
router scan/DHCP/two-way traffic test is required; host or OVMF tests alone cannot
prove final Wi-Fi operation.

Reference: pinned Linux6b5a2b7d9bc156e505f09e698d85d6a1547c1206 ath10k
pci.c:ath10k_pci_claim, ath10k_pci_qca6174_chip_reset,
ath10k_pci_cold_reset, ath10k_pci_warm_reset; core.c selects qca6174_regs for
QCA9377. Materials stay on Yukabox; owner secret stays on Mac.

Power reference: [pinned Linux PCI power transitions](https://raw.githubusercontent.com/torvalds/linux/6b5a2b7d9bc156e505f09e698d85d6a1547c1206/drivers/pci/pci.c), pci_set_full_power_state and pci_pm_reset.
