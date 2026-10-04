# Native26 warm/full-channel trial — 2026-10-04

Purpose: test the pinned QCA9377 warm sequence and full owned host channels on
physical Dell without target RAM writes, firmware upload, BME enable or reboot.
Preserve world13 and the roof cat. No USB/bootstrap change or owner key export.

Build host: Yukabox. Mac: read-only BLE, owner signing and saved-session sender.
Source reference: pinned Linux6b5a2b7d9bc156e505f09e698d85d6a1547c1206.

## Exact prerequisite evidence

- report.json: QCA-WARM-FULL-CHANNEL-CITY-PROFILE-GATES-PASS.
- Payload SHA256: d8a6dd6805c3862e201b43a05cdf860e71895227b6c94f471af391c33f4cd583.
- reproduction.json:273 current source files, two identical rebuilds and actual
  C/sanitizer checks of unchanged world package.
- init-report/init-host: pinned pack, warm each-I/O/every-phase fault injection,
  channels27/mapped IRQ36/native adapter13, ASan/UBSan and freestanding COFF.
- probe-report/probe-host:17 scenarios of the actual generated native entrypoints,
  successful cleanup, warm faults/verified cold recovery, retained timeout/flush
  failures and outer port/reset failures. MOCK hardware, not physical evidence.
- host.log: actual QPD14 fixture snapshots, malformed envelope/hash/active probe,
  bounds/false success rejection and preserved BLE loss baseline/regression.
- actors-qemu and actors-empty-boot-qemu: actual UEFI load, absent-QCA diagnostic
  ATT reads, fullscreen city restore/motion-clock/rejection checks. QEMU cannot
  prove the QCA reset or physical tail animation.
- route-negatives.json:11 bad prerequisite/modified payload/world/component
  cases rejected by the signing gate. No owner key touched by these negatives.
- physical-before26.json: fresh known Dell UUID QPD13, native25 terminal cleanup,
  no outstanding DMA/BME/reset ownership, before sending26.

## Physical result

Exact APPLIED receipt: counter26, session pci-native-wg2f6n8n,
packet SHA2563b0748f9cdec1a0b369e1d631bfe20bae6fa59657cd0a3d8e41aa3dab8de3d18,
76064bytes transferred in one staged connection, followed by COMMIT/reconnect.
World13/package SHA unchanged, journal/pending slots idle. Do NOT replay26.

Fresh known Dell F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF returned hash-bound QPD14.
Stage20/adapter13 RETAINED: warm error2 timeout, CPU resets2/pipe inits2,
fourteen mapped pages held, no BME enable. Counts place timeout in second ROM
wait; both configurations completed before it. Cold recovery phase3/unowned,
ROM indicator2, mapped guard error0 and IRQ quiesced. Recovery not certified:
the all-eight-stop proof failed after cold reset, so buffers/PCI/IRQ/link remain
owned. This is NOT a warm-reset success or cleanup completion.

The code stops engines before cold reset and checks their stopped state after
cold reset without stopping them again. Cold reset may reset halt bits/registers;
this is the next recovery hypothesis to reproduce explicitly in fixtures and
instrument. Actual physical post-reset CE register values were not captured.
No unsafe flag-clearing or unmap/free is allowed to work around retention.

City/tail observation after26 has been requested and is pending. Existing last
owner observation applies only to native25 (city visible). Firmware, association,
DHCP and streaming remain unperformed. No autonomous Dell reboot.

