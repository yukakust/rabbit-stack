# Source-supported next target-stop adapter

Pinned ath10k `pci.c` at 6b5a2b7d9bc156e505f09e698d85d6a1547c1206, `ath10k_pci_hif_stop` (2073) resets the chip before buffer cleanup because a configured HTT ring can otherwise still access host memory. `ath10k_pci_safe_chip_reset` (2668) calls the per-device soft reset; QCA9377's table selects `ath10k_pci_warm_reset`. `hif_power_down` (2880) performs no additional reset because stop already did it. This is a Wi-Fi-chip operation, not a Dell reboot, flash/OTP or USB operation.

The existing checked `QcaWarm` machine has the required finite QCA9377 register allowlist (0x800, 0x850, 0x3a028), two CPU reset writes, 10ms SI/CE settle windows and two bounded ROM polls. Its native adapter uses fresh PCI/identity/D0/wake/IRQ guards, retained CE mappings, real CE stop and reconfiguration without BME/start. `qca_mapped_irq_guard` joins through `qca_channels_retained`; the completed47 wrapper already measures the actual47 object inventory rather than substituting fourteen.

A NEW adapter can therefore proceed after actual radio work revocation and CE halt/BME-off, while all47 mappings remain allocated:

1. Revoke the data publisher and future callbacks for the current epoch. Preserve unknown TX outcomes and raw/pending RX, never mark them successful. Establish synchronous callback depth/readers are zero before reset. No current borrowed descriptor may be erased or freed.
2. Reuse the immutable warm machine in a separately owned stop object. Every read/write must use the checked actual adapter, maintain BME-off and preserve all47 mappings. Require a fresh observed indicator clear after the actual 0 write before each CPU-reset sequence; an old READY2 value cannot certify a reset.
3. The pipes callbacks perform real CE stop/reconfiguration on the retained CE14, with the extra33 maps still held; a no-op pipes callback is insufficient. Do not enable bus mastering or reload firmware.
4. After both CPU resets and bounded fresh ROM initialization, stop the reconfigured CEs again. Disable/clear/read back device boot IRQ, keep host INTx/MSI/MSI-X isolation, verify actual BME-off and invoke the actual PCI Flush.
5. Only that completed adapter may construct the ring quiescence proof. Bind it to the original owner epoch and real reset/completion serial. Epoch revocation means normal TX DMA/HTT join was cancelled, not an AP ACK. Clear borrowed pointers/registered callbacks only through this checked retirement.
6. Close the extra33 maps using the original real DMA stop/Flush/Unmap/FreeBuffer path, then the CE14 and outer PCI/IRQ/wake owners. Count every real success and retain uncertain or failed owners. Detach capture/pool references before wiping/freeing.

The persistent lifecycle's current10s quiescence budget can cover two3s ROM waits plus settle/configure/stop work; a new outer bound must remain below that budget or explicitly review a bounded adjustment. Clock rollback, ignored indicator clear, absent ROM transition, register/identity/IRQ/Flush error, active callback/reader or ambiguous reset must leave quarantine. No automatic reassert/replay or BME restart may mask the failure.

This adapter has not yet been implemented or tested in this scope. The current data path intentionally has no successful published-ring release API and keeps the actual47 owners. A future isolated adapter and producer composition with the new city parent must prove the complete path and negatives before physical admission.
