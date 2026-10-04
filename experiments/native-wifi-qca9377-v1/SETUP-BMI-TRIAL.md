# Finite initial configuration and BMI info trial

Physical baseline native32: full warm initialization and fixed CE7 configuration
reads pass; fourteen maps safely released. This candidate repeats the same fresh
reads and checks in the same live owner before any volatile target RAM write.
No old JSON values authorize writes. Native policy verifies completed HI and all
three read exchanges, matching bus/buffers, READY warm adapter and retained14 maps;
finite table windows/alignment/overlap/flags reject invalid destinations.

## Operations and evidence

Five pairs:168byte source-pinned pipe table write/readback;204byte service map
write/readback; config_flags bit0 clear write/readback; early_alloc OR6d8a0009
write/readback; option_flag2 OR10 write/readback LAST. Require every earlier
readback before submitting config-done. Full byte comparisons, fixed CE7 ring
cookies/lengths, ACTIVE PCI/MEM/BME/D0/wake/BAR/IRQ/ASPM guard on every poll.
Tables generated from init_tables.py and independently compared with pinned
upstream by verify_init_pack; no table/data bytes learned from incoming packets.
Count possible writes before posting, retaining uncertainty on failed submission.

Only after all five readbacks: core control OR2000 CPU interrupt. Read back
unchanged non-interrupt bits; CPU bit can self-clear. Borrow existing idle CE0 TX
and CE1 RX with their original mappings, post12byte RX before four-byte
BMI_GET_TARGET_INFO command8. No firmware write/execute/done command. Observe
completion before3second timeout, including delayed cooperative rendering calls.
Preserve raw info length/version/type; successful reply is not compatibility.

QPD18 remains924bytes, prefix716 plus SHA-bound extension244, serviceUUID0D.
Reuse280..355 for phase/error/op/write/readback masks, attempts, CPU and BMI
telemetry. Preserve config reads716..799 and full-channel HI888..923. Decoder
must reject out-of-order done/CPU wake and false setup/BMI success. Historical
CE snapshot fields at those offsets are not interpreted in QPD18. File service
UUID1 is unchanged. Manifest kind native-read-only-pci is historical route naming;
this exact profile explicitly declares target_ram_writes=true, firmware_upload=false.

## Loading, teardown and recovery

65 actual native-entrypoint ASan/UBSan scenarios: existing warm/cold/CE7/config
faults, ten operation timeouts, five readback mismatches, five invalid spans/flags,
ten operation cancellations, BMI timeout/bad length/zero version/BME loss, slow
BMI completion after timeout boundary. Repeated exact payload/source/current-world
checks, pinned tables, COFF ABI and normal/empty UEFI city/ATT/BLE/decoder gates
on Yukabox precede local owner signing. Send the SAME saved monotonic session;
exact APPLIED receipt is installation only, read physical telemetry separately.

Success/fault/cancel stops all eight CEs, BME off, then Flush/Unmap/Free14 maps,
IRQ/link/wake/PCI restore. Retain uncertain buffers/ownership; never force free or
unload. Target RAM contents are intentionally changed and are NOT claimed to be
restored by host-resource teardown. A next trial must repeat verified warm reset
and fresh reads; invalid remaining state rejects further writes. If ownership is
retained, separately gate recovery and ask owner for reboot, never reboot Dell
or change USB/bootstrap autonomously. Preserve world14/cat/history.

No flash/OTP programming, firmware RAM upload, board selection by guess, radio,
association/DHCP or video. Read fresh physical BMI/board-variant identity before
firmware policy or signed asset receiver integration. Owner screen/tail observation
is separate from machine receipts and diagnostics.
