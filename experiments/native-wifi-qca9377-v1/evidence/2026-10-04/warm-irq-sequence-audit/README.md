# Warm ROM IRQ window audit — 2026-10-04

Pinned primary code: Linux6b5a2b7d9bc156e505f09e698d85d6a1547c1206,
drivers/net/wireless/ath/ath10k/pci.c. Read on Yukabox; no hardware writes.

ath10k_pci_warm_reset begins with ath10k_pci_irq_disable, before SI0/CPU reset.
ath10k_pci_wait_for_target_init reads FW_INDICATOR; while waiting in INTX mode
it enables firmware+CE mask7fc00. On EVERY exit it calls
ath10k_pci_disable_and_clear_intx_irq followed by ath10k_pci_irq_msi_fw_mask.
This happens after the first wait, BEFORE LF timer/CE reset/second CPU reset,
and after the second wait. Init pipes themselves do not start PCI DMA.

Our init_adapter/warm_read calls mapped_irq_poll before each FW indicator read,
but does not quiesce on successful first/second ready. The initial boot IRQ is
also still enabled when qca_warm_begin starts. Thus IRQ window boundaries differ
from upstream; first wait leaves7fc00 enabled across LF/CE/CPU reset. This is a
falsifiable timeout hypothesis, NOT proven physical causality.

Next change, after native29 terminal result: guarded mapped IRQ quiesce BEFORE
warm_begin and after each successful ready read, preserving all existing reset,
PCI/D0/wake/DMA ownership checks. Add an actual native fixture requiring IRQ
quiesced at CPU reset and between waits, with baseline demonstrating old behavior.
Do not change BME, target RAM/firmware, host IRQ handlers or bootstrap. Rebuild
all deterministic host/COFF/UEFI/source/current-world gates before signing.
