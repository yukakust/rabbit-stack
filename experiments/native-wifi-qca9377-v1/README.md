# Native Wi-Fi QCA9377 v1 — physical diagnostics and initial driver port

Owner chose the internal Wi-Fi: there is no Ethernet cable. Dell in Georgia has
no installed OS/disk; Mac is command/control and Yukabox in Poland runs Unreal.
Latest recovery has exact native17/world13 receiver receipts; owner confirmed the
city visible. Historical native15/native16 packets are retired and preserved. A
new boot-IRQ/BMI profile retains native17 Bluetooth recovery, passes fresh source/
world gates and is delivered only through its newly saved native18 session. See
the latest handoff/evidence for its application result. Wi-Fi is not associated.
Wi-Fi authorization is explicit; the old handoff's "unrelated network runtime"
restriction concerned an earlier engine trial, not this requested transport work.

Current hardware evidence: chip003821ff/rev1 after cold reset, physical Dell
subsystem1028:1810 and D0 verified; ROM-ready still times out. No physical BMI
reply, firmware startup or Wi-Fi connection. Reversible boot-IRQ/post-reset ASPM
candidate is retested with preserved Bluetooth recovery; its physical result must
come from the latest exact receipt and QPD7 telemetry. Signed RAM chunk assembly,
isolated ATT channel and portable/Mac sender are separate tested components;
they are not integrated into the physical native driver. See the latest sections
of `docs/CONNECTED-NATIVE-MAC-HANDOFF.md` and `FIRMWARE-CHUNKS-CONTRACT.md`.

Historical physical discovery identified168C:0042 at02:00.0, without firmware
SNP/Wi-Fi services. The pinned iPXE source has ath5k/ath9k, but no ath10k/QCA9377
driver: Ethernet's ready-made `.efidrv` route cannot just be reused for this device.
Linux's existing ath10k code is the technical reference, not a kernel module that
can be loaded into UEFI. No Linux/OS installation or hardware purchase is planned.

## Concrete completed work

Pinned upstream ath10k PCI/BMI/CE/WMI/HTT sources and official linux-firmware were
downloaded on Yukabox with hashes in `evidence/2026-10-04/materials.json`.
`firmware_preflight.py` implements a bounded host-side TLV checker and exact board
selection.179 checks on malformed/truncated/duplicate/oversized data and real
firmware/board containers passed on Yukabox. It is not a native driver or QEMU
device emulation. `preflight.json` states upload/association=false.

`pci_identity.c` now decodes a pure PCI header snapshot: exact target/class,
subsystem IDs/revision and32/64bit BAR0, rejecting invalid/unassigned resources.
`pci_probe.c` uses typed UEFI PCI I/O Read/GetLocation, at most64handles, no PCI
write/MMIO/DMA/radio operation. Its positive fixtures pass ASan/UBSan on Yukabox.
Actual standalone EFI QEMU run enumerates6PCI handles and correctly finds no
QCA9377; evidence records this negative branch. It is NOT a successful physical
read and NOT a Wi-Fi connection. VM COM1/poweroff harness must be removed before
integrating the read-only routine into an active city native profile.

The real hw1.0 candidate has WMI-TLV op4, HTT-TLV op3, firmware image727125bytes,
OTP helper image24193bytes, no code-swap element. Board database contains multiple
different calibrations, including a Dell1028:1810 entry. **That is not evidence
that this Dell has that subsystem or hardware revision.** Selection without exact
physical identity fails. No firmware or helper image has been uploaded/executed.
No OTP, flash or persistent firmware operation exists in these scripts.

Raw blobs/sources/licenses remain ignored under `vendor`, on Yukabox; manifests
are inspectable. `fetch_materials.py` uses fixed upstream commits and HTTPS.
Its first acquisition records provenance; it is not an owner-signature gate.
Compatibility=false/true is not inferred from merely parsing a public blob.

## Next implementation boundaries

1. An owner-reviewed, read-only PCI probe integrated into the active native
   profile: fresh subsystem IDs/revision, BAR resources and DMA constraints,
   preserving world snapshot/animation and Bluetooth reader. Historical inventory
   does not supply these facts. Candidate init/health stays hardware-free.
2. Port ath10k's PCI/DMA Copy Engine and BMI transport behind a bounded Target Pack;
   obtain target revision and board identity. Mock protocol tests are not physical
   validation. There is no QEMU QCA9377 hardware model in this experiment.
3. Bind exact reviewed firmware/calibration hashes to that identity. Prove detach,
   stopped DMA, cancelled callbacks, hardware resource lifetime and rollback before
   native owner signing. The751436-byte firmware cannot simply be appended to the
   nearly-full4MiB native7 image; explicitly design delivery and memory budgets.
4. Firmware RAM startup → WMI-ready → bounded scan → association/key handshake →
   Ethernet-like packet interface → DHCP → existing authenticated frame receiver.
   Keep association and image transport errors out of the city's fatal path.
5. Verify exact normal+EMPTY native gates, current city preservation, dual radio
   lifetimes and failed-update rejection. Then locally sign the exact profile on
   Mac and transfer by the existing Bluetooth path; no owner key on Yukabox.
6. Physical observations: target identity, scan, connection, DHCP, packet transfer,
   image and continuing native city. Only these establish working Wi-Fi on Dell.

SSID/security mode question is pending; password must be entered locally when a
credential consumer exists, never in chat/evidence/Git/LLM input. No credentials
are accessed by the present scripts. WPA3 support is not assumed.

Loading/recovery: the read-only diagnostic profile now uses the existing native
owner-signature/current-world gate and resumable Bluetooth transfer. Normal and
EMPTY UEFI trials verify exact loading, city4/5 snapshots, target-clock motion,
fullscreen/crop consistency, native rollback and bad update rejection. Both
native8 and native9 received exact correlated APPLIED receipts on physical Dell.
World12 package/counter remain unchanged. Normal native rollback remains available;
no immutable root, USB, disk, reboot or owner-key-copy change was performed.

```sh
python3 fetch_materials.py
python3 verify_preflight.py
python3 verify_pci.py
```

`verify_pci.py` requires the previous pinned iPXE header workspace at
`/home/yuka/rabbit-world/dell-network-viewer-v1` and the installed UE Linux Clang/LLD.
It uses `run_probe.py` only for an isolated virtual device. Its UART/poweroff
harness is never included in the active diagnostic profile.

## Read-only diagnostics deployed on Dell

`diagnostic_build.py` copies the reviewed actor profile and supplies bounded PCI
enumeration via `pci_collect.c`, with no PCI writes/MMIO/DMA/radio access. Physical
evidence is in `evidence/2026-10-04/diagnostic/`:16 PCI handles, one target,
`0000:02:00.0`, vendor/device168c:0042, subsystem1028:1810, PCI revision0x31,
BAR0=0xd1000000 (64-bit BAR, upper word0), command0x0100 (memory decode and
bus master disabled). PCI revision is NOT the SoC chip/BMI version.

Native8 added a fourth characteristic to the existing service. Mac continued
discovering only its old three characteristics; two read attempts failed. Native9
preserves the original file service range1..7 and adds a distinct primary service:
`52414242-4954-4649-8000-000000000005`, handles8..10; read-only characteristic UUID
ending0006 at handle10. `read_pci.m` then successfully read128 QPD1 bytes from the
same peripheral. This transport record is not device attestation. The snapshot
is taken at attach, not continuously on each read. No write API exists in reader.

The exact PCI catalog match is8124bytes, SHA256
`b2713b77c725b0ff81af75c85c3aeba97885d0f40174f715b1e39d5a9d50f4e7`.
This is a board candidate, not permission/proof to upload calibration before
fresh SoC/BMI/board-variant validation. Raw firmware751436bytes and even xz476792
exceed a single262144byte native transfer; firmware delivery needs a bounded,
owner-verified chunk/asset design, without enlarging immutable root limits.

Builds, host sanitizer checks and actual UEFI VM gates run on Yukabox under
`/home/yuka/rabbit-world/wifi-city-profile-v1` and `wifi-city-profile-v2`.
`remote_check.py` binds current source hashes, two identical rebuilds, pinned
crypto and actual C validation of the current world. `native_route.py` verifies
those records/current owner/current world and signs locally on Mac, then uses the
existing paced saved-session sender. Mac performs only control/signing/radio work.
EFI files, owner secret, downloaded Linux/firmware and credentials stay out of Git.

## Initial driver port: tested, not physically activated

`uefi_port.c` implements exclusive PCI IO claiming, fresh exact identity checks,
ACPI BAR extent validation, memory-only enable and allowlisted register IO. It
never enables bus master. `wake_core.c` implements cooperative wake, bounded
clock/timeout checks and supported chip revision filtering. Failed/ambiguous
writes keep ownership; shutdown must clear wake, restore original attributes and
close the protocol successfully before unload. `wake-target.json` separates the
QCA target facts from universal world data and records pinned ath10k provenance.

`verify_port.py` passed ASan/UBSan host hardware mocks and COFF compilation/ABI
offset checks against pinned UEFI headers on Yukabox. These components are NOT
linked into native9 and have NOT touched physical MMIO. DMA/Copy Engine/BMI,
firmware RAM startup, WMI/HTT, scan, WPA handshake, DHCP and packet transport
remain unimplemented. Owner observation of city/animated cat after diagnostics
is pending before physical bring-up. SSID/security mode is pending; password must
use a future local-only credential consumer, never chat/LLM/logs/Git.

References: [ath10k architecture](https://wireless.docs.kernel.org/en/latest/en/users/drivers/ath10k/architecture.html)
and [calibration/board data](https://wireless.docs.kernel.org/en/latest/en/users/drivers/ath10k/calibration.html).
Driver source is GPL2; firmware distribution terms/notices are fetched alongside
the blobs and remain applicable. This repository includes only our preparation
tools and hashes, not Linux or proprietary firmware binaries.


## 2026-10-04 — native10 physical wake probe, identity still unresolved

Owner confirmed native9 city visible and roof-cat tail moving: «виден и двигается».
`bringup_build.py` integrates the port into a separately reviewed city profile.
One-shot attach claims exact1028:1810/PCI31, validates BAR, enables memory only,
requests wake, cooperatively polls for at most1second, reads chip-ID and clears
wake/restores attributes/closes PCI IO. Reattach cannot repeat hardware writes.
Candidate init/health stays hardware-free. Failed cleanup retains ownership and
blocks unload; it must not silently release a live device. No bus master, DMA,
chip reset, firmware/OTP, root/USB/disk changes or Dell reboot.

Yukabox passed15 ASan/UBSan production-code lifecycle scenarios, port ABI gates,
normal+EMPTY actual EFI city/snapshot/clock/restore/bad-update gates, two identical
rebuilds bound to current world12 and pinned crypto. OVMF QCA-absent coverage is
separate from physical evidence. BAR validation corrected before signing:
EDK2 GetBarAttributes AddrRangeMax can encode alignment; checked extent uses
base+AddrLen, with translation rejected. No physical operation used the old check.

Exact payload `a721f3fcab4749f4fda5ad98018cdf0fc2d2d6396a68991f07e372a1caabfe60`
was locally signed on Mac and delivered as native10, saved session
`pci-native-uis35sur`. Transfer staged53024bytes; COMMIT disconnected, then the
sender reconnected to the SAME session and obtained exact SHA/session/counter
APPLIED. State native_pending=null, world12 package unchanged. Secret stayed Mac.

Fresh physical QPD2/160-byte read from the same peripheral reports BAR extent
2097152, original PCI attributes0, stage3/error3 (chip-ID rejected), raw chip-ID0,
cleanup complete. The code reaches CHIP validation only after RTC state ON;
PCI open/BAR/memory-enable/wake therefore advanced to that point. Do NOT claim
supported chip revision, BMI version, firmware compatibility or association.
PCI config bytes were captured BEFORE the wake operation; cleanup status, not
those earlier bytes, reports restoration/close. This is Bluetooth telemetry,
not device attestation. Native10 city/tail visual observation is pending.

Pinned Linux uses qca6174_regs for QCA9377, RTC_SOC0x800 + CHIP_ID0xf0 =0x8f0.
Its normal probe reads identity AFTER chip reset, while ours deliberately does
not reset. Linux's supported-revision table permits revision0, but a zero raw
read here is kept inconclusive rather than treated as proof. Next: establish
PCI power/read/reset ordering and a bounded chip-only reset/recovery policy,
then CE/DMA/BMI get-target-info; do not blindly reclassify zero as verified or
upload guessed firmware. Preserve city/Bluetooth and exact loading/rejection
checks for every subsequent physical native candidate. Full Wi-Fi still needs
firmware RAM startup, WMI/HTT, scan/security and DHCP. Firmware asset chunk
transport is also required within unchanged native/bootstrap bounds.

Evidence: `experiments/native-wifi-qca9377-v1/evidence/2026-10-04/bringup`
contains gate/reproduction hashes, pre-update receipt/owner observation, full
saved-session delivery records, raw/decoded physical telemetry and a manifest.
Remote workspace: `/home/yuka/rabbit-world/wifi-bringup-v1/source`.


## 2026-10-04 — native11 power diagnostics, D0 confirmed; cleanup audit corrected

Full goal remains working Wi-Fi: verified chip/CE/BMI, exact firmware RAM loading,
radio scan/security, DHCP/two-way traffic and reconnect without city/BT failure.
Owner explicitly authorized continuing all these stages. Association remains false.

Read-only `power_build.py` profile reads conventional PCI config256 at attach;
`power_core.c` bounds capability traversal (48 aligned entries, loop/duplicate/
truncation rejection). QPD3/144 preserves file handles1..7 and diagnostic service.
Host sanitizer gates cover all255 capability pointers, D3, malformed/missing
chains and actual collector+ATT. Normal+EMPTY real UEFI city/snapshot/clock/
restore/rejection and current-world two-rebuild checks passed on Yukabox.
Locally signed and delivered native11 (`pci-native-y8kegeov`), exact correlated
APPLIED, world12 unchanged. No PCI/MMIO writes, power transition, reset or DMA
in this profile. Evidence under `evidence/2026-10-04/power`.

Physical: PM capability0x40, PMCSR0x0000 => D0; PCIe capability0x70,
LinkControl0x0143 => ASPM enabled. D3-to-D0 transition is NOT the next justified
step. Device/subsystem/BAR unchanged. PCI command now0x0102, bus master disabled.
This contradicts a stronger interpretation of native10 cleanup telemetry:
Attributes(Set0)/CloseProtocol returned success, but MEM command bit stayed on.
Do not describe API-success telemetry as proof that actual PCI settings restored.
The native10 log is retained as observed; this new finding supersedes its earlier
restoration conclusion. Before reset/CE add actual command capture/readback and
bounded16-bit fallback restoration (never32-bit write into W1C PCI status).
Failed readback must retain ownership and prevent unload. Preserve real initial
command rather than blindly trusting cached UEFI attribute flags.

NEXT: command lifecycle repair and adversarial API-success/stale-command tests;
then separately gated cooperative QCA-only cold/warm reset/readiness/SoC-ID using
pinned ath10k ordering. No PCIe accesses during reset settling intervals; recovery
must deassert/reset-settle before releasing ownership. Native11 city/tail visual
observation remains pending, distinct from exact Bluetooth receipt and telemetry.
SSID/security mode still needed before association; no password in chat/LLM/logs.
All native compilation/rendering/tests remain Yukabox; Mac control/signing/radio.


## 2026-10-04 — command lifecycle correction, host/ABI verified only

`uefi_port` now captures real original16-bit PCI Command, verifies actual
memory-only enable and real command restoration. Attributes(Set) success alone
is insufficient. On mismatch, Write16 restores exactly the captured command
without writing PCI Status W1C; a subsequent read must match. Failure/ineffective
write keeps claim and memory_attempted until successful retry; unload remains
blocked. Tests simulate stale-success attributes, config read/write errors,
successful-but-dropped config writes and an initially enabled MEM bit with cached
attributes0. Unrelated command bits/status remain preserved. ASan/UBSan and COFF
PCI Write ABI checks passed on Yukabox; evidence/2026-10-04/command-lifecycle.

This correction is NOT loaded on physical Dell yet. Current native11/world12
is the read-only power profile. Next separately gated native reset profile must
include this correction and fresh D0/resource/identity checks; no extra native
probe sent merely to repeat the same zero chip-ID. Native11 confirmed MEM0102,
so preserve the actual starting command rather than claim historic0100 restored.
Full Wi-Fi goal remains active and incomplete. SSID/security and post-update
city/tail observation questions are pending; password stays out of chat.


## 2026-10-04 — cooperative cold-reset core host gates passed

Previous goal turn was concrete progress: physical native11 D0/ASPM evidence
changed the next action and actual PCI command cleanup was corrected/tested.
Current continuation revalidated native11/evidence/current sources. Added
`reset_core.c/h`, `reset-target.json`, adversarial `reset_test.c` and
`verify_reset.py`. Based on pinned ath10k PCIe-local GLOBAL_RESET0x80008,
assert and deassert each require20ms without accesses to the claimed Wi-Fi
PCI device. Target minimum extent is0x8000c, not wake-only0x80008.

Errors on reset writes are ambiguous: ownership starts before assertion and is
not released until deassert readback confirms clear after settling. Poll has
bounded3-attempt recovery; a stuck asserted bit, error/all-ones readback, or
ineffective clear retains ownership. Explicit recovery retries deassert/verify,
never another assertion. Reverse-clock and expired-deadline cases still require
safe cleanup. Host mocks test no early access, ambiguous assert/clear, stuck bit,
read failure/all-ones, retries, repeated poll and invalid inputs. ASan/UBSan and
freestanding x86 COFF passed on Yukabox with source-bound evidence/reset-core.
A successful write is NOT proof that reset asserted; current component proves
ordering/recovery in mocks, not physical reset or useful post-reset identity.

NEXT concrete implementation: native reset adapter/profile. Fresh exclusive
PCI/D0/BAR identity and actual Command checks first; safely wake without treating
zero chip-ID as already verified. Gate allowlisted GLOBAL_RESET RMW, retain the
PCI claim through reset settling and recovery. After reset revalidate actual
PCI configuration/resources/memory-only state before further MMIO; do not trust
pre-reset cached flags. Observe FW indicator and repeated chip-ID. Integrate
reset lifetime into close/unload and candidate rollback, preserve city/BT, run
normal+EMPTY/current-world/source/native size gates before signing. Include the
command lifecycle correction; hardware-free candidate health/init stays so.
Native11/world12 remains physically installed; NO reset profile has been signed,
sent or executed yet. No DMA, firmware RAM upload, scan/association/DHCP yet.
Full original Wi-Fi/reconnect goal stays active. SSID/security-mode and post-
update city/tail observation pending; they do not block independent port work.


## 2026-10-04 — native12 physical reset/identity verified, chip revision1

Previous goal continuation was progress (reset component code/host+COFF gates).
This turn integrated that component and actual Command lifecycle correction into
`reset_probe.c`/`reset_build.py`, preserving city and existing file service.
Fresh exclusive PCI/identity/BAR/D0 checks precede wake/reset; post-deassert20ms
checks revalidate PCI identity/BAR/no bus master and memory decode. If reset
clears MEM, memory-only enable is repaired and read back before further MMIO.
Close during either reset settling window cancels forward work, retains claim,
finishes deassert/settle and then verifies Command restoration. Failed clear
or readback retains ownership. Explicit close can request bounded cleanup retry
without another assertion. Reattach never repeats one-shot hardware work.

Eleven actual generated-production host scenarios passed ASan/UBSan (UBSan halt):
normal/zero-before-reset/unsupported chip/D3/no target, stuck clear/ambiguous reset
write, post-reset memory loss, zero-after-reset, and cancellation during either
settling window. Port/component gates and normal+EMPTY real UEFI city/fullscreen/
clock/snapshot/rollback/rejection gates passed on Yukabox; current-world/pinned-
crypto two rebuilds matched. Earlier host test fixture failures were corrected
before this exact profile was signed; no failed fixture profile was sent.

Exact payload99463fa0068204926a2d4988e2d5dfe62c5f2ed2f22ed96a3f36dfc50ea8c67e
signed locally Mac, delivered saved session `pci-native-23kicu1u` (56096bytes).
COMMIT disconnected/reconnected to SAME saved session and exact APPLIED. Fresh
query confirms native counter12/session matches. World counter12/package remain
unchanged; native_pending=null. No root/USB/disk/OTP/Dell reboot or key copy.

Physical QPD4/196 read: stage5/error0, chip-ID003821ff, supported SoC revision1,
reset DONE/error0/owned=false, original/readback GLOBAL_RESET0, D0/PMCSR0,
BAR extent2097152, original/active Command0102, original attrs0200, no revalidation
error, cleanup complete. Actual Command restoration is verified by corrected
port before CloseProtocol; this preserves the real initial0102, not historical
0100. Bluetooth remains responding. Physical city/tail observation after native12
is pending; previous owner observation was native9, do not silently extend it.

Immediate FW indicator read was0. This is NOT a timed readiness failure and NOT
firmware-ready proof. No firmware, CE/DMA, BMI target version, scan, association,
DHCP or reconnect implementation verified yet. NEXT: bounded ROM-ready wait and
CE/DMA/BMI get-target-info; bind actual target type/version before selecting/
uploading exact firmware/board chunks in RAM. Known revision1 is a completed
physical identity substep, not completion of the original Wi-Fi goal. Keep full
original goal active. SSID/security mode question pending; password never chat.

Remote exact workspace `/home/yuka/rabbit-world/wifi-reset-v1/source`.
Evidence/2026-10-04/reset-profile contains source-bound gates/reproduction,
full saved-session logs/raw+decoded telemetry/current receipt and manifest.


## 2026-10-04 — CE ring core implemented, host/COFF gates only

Previous goal turn was physical progress: native12 cold reset yielded supported
chip revision1, with command/cleanup and saved-session receipt evidence. This
continuation revalidated current sources/physical handoff; native12/world12
remains installed. Implemented `ce_ring.c/h`, `ce_ring_test.c`, `verify_ce_ring.py`
and separate `ce-target.json`. Pinned ath10k32-bit descriptor8bytes (address32,
length16, flags16), qca6174 metadata0xfffc/shift2, gather/byte-swap flags. Native
world data does not contain these target facts.

Core implements bounded power-of-two rings2..32, one reserved entry, explicit
little-endian descriptor bytes, descriptor/buffer32bit address/end bounds, cookies,
TX gather publication and queued-versus-published completion invariants. Ownership
/bookkeeping is recorded before an ambiguous doorbell. Invalid hardware indices,
changed descriptor address/oversized length or doorbell errors fault the ring but
retain its mapping. Zero RX length is a valid transient after DRRI advances:
return WAIT, preserving ownership, until descriptor update (as pinned ce.c).
Close calls adapter stop before clearing any descriptors; failed stop retains
ownership and blocks free/unmap. Hardware stop callback must actually verify CE
quiescence, bus-master-off and DMA flush: mock success is NOT hardware proof.

5000 fill/wrap cycles across sizes, gather publication, RX update race, hostile
length/address/index, 32bit overflow, invalid sizing/metadata and failed publish/
stop retry passed ASan/UBSan (halt_on_error) on Yukabox. Freestanding x86 COFF
compiled. An initial host UB in descriptor zero-fill shifting a32-bit zero beyond
31bits was caught and fixed before successful gates; no physical code was sent.
Evidence/2026-10-04/ce-ring hashes bind exact tested source/log. No Mac native
build, no owner signing or physical transfer this continuation.

NEXT: UEFI coherent DMA allocation/Map/Unmap/Free adapter and exact CE MMIO setup/
stop with actual-command verification and flush. Enforce32bit device addresses,
retained resources on ambiguous enable/stop/unmap and no callback after release.
Then bounded ROM-ready wait and BMI get-target-info on physical Dell. Current
ring core alone does NOT implement DMA mapping, CE MMIO, BMI, firmware loading,
scan/association, DHCP or reconnect. Full original goal remains active/incomplete.
SSID/security and city/tail observation pending; no password in chat/LLM/evidence.


## 2026-10-04 — UEFI DMA lifetime adapter implemented, host/ABI gates only

Previous goal turn was progress (CE ring code and tested bounds/lifetimes).
Current native12/world12 evidence and current sources revalidated before work.
Added `dma_buffer.c/h`, adversarial tests and `verify_dma.py`. PCI IO
AllocateBuffer(any pages/BootServicesData/attributes0), Map(CommonBuffer2), Unmap,
FreeBuffer and Flush typed method offsets verified against pinned UEFI headers.
Full mapped length, page alignment and32bit device-address/end bounds required;
no physical address truncation. Successful Map with NULL token still records a
mapping and passes the returned token to Unmap. EDK2 Map can fail after returning
a token (IOMMU SetAttribute failure); retain/unmap that token before free.
No bus-master enable or CE MMIO is implemented by this adapter.

`dma_users` now guards PCI close/reopen until buffers are released. Exposure is
marked before any future CE/doorbell/BM write. Close starts irreversible-to-reuse
closing state: no new exposure after a failed close. For exposed buffers, adapter
stop callback must verify CE engines stopped; then actual PCI Command must show
bus master off, Flush succeeds, Unmap succeeds, then FreeBuffer. Errors retain
remaining resources/claim; no free-after-failed-Unmap or early protocol close.
Ambiguous allocation error with nonnull output is quarantined, never guessed
safe to free. Limits16pages/buffer and64buffers are explicit Rabbit policy.

18 ASan/UBSan scenarios passed: full success/order, allocation failure/ambiguous
allocation, failed Map with/without token, short/above32bit/misaligned/overflow
mapping, successful NULL-token mapping, failed stop/still-enabled BM/Flush/
Unmap/Free/config read, invalid host alignment and multiple-buffer ownership.
Freestanding x86 COFF and ABI Map72/Unmap80/Allocate88/Free96/Flush104 checks pass.
Existing port tests reran after dma_users guard changes. Source-bound evidence
under evidence/2026-10-04/dma. All builds/tests Yukabox; no physical DMA activation,
owner signing or new Bluetooth native transfer this continuation.

NEXT: actual CE MMIO setup/stop adapter (halt verification, interrupt masking,
ring base/size/indices, doorbell ordering) and real bus-master lifecycle. Bind
CE ring+DMA lifetime to that adapter, then ROM-ready wait and BMI get-target-info.
Stop callback is MOCK ONLY at this stage; it does not prove physical CE quiescence.
Do not physically enable bus master until the complete stop/recovery/native gate
exists. Native12 remains physically installed; firmware upload/WMI/HTT/scan/WPA/
DHCP/reconnect remain incomplete. Full original Wi-Fi goal stays active. Pending
SSID/security mode and city/tail observation do not block independent port work;
no password in chat/LLM/logs. EDK2 references are technical implementation context,
not evidence of this Dell's actual Map behavior.

Reference: https://raw.githubusercontent.com/tianocore/edk2/master/MdeModulePkg/Bus/Pci/PciBusDxe/PciIo.c
(PciIoMap/Unmap/AllocateBuffer/FreeBuffer/Flush); pinned iPXE headers remain the ABI
reference, and actual physical mapping still needs separate evidence.


## 2026-10-04 — CE MMIO and PCI bus-master lifetime, host/COFF gates

Added ce_hw.c/h, ce_uefi.c/h and ce_bus.c/h. Fixed QCA6174-family CE bases
and register masks are recorded in ce-target.json and checked against pinned
Linux hw.c SHA256. Halt requests are owned before ambiguous writes; bounded
cooperative polling requires HALT request + ACK. After halt, mask interrupts,
clear ring addresses/sizes and read them back. Configure only while halted,
verify configuration readback, preserve supported control bits, clear W1C status
without treating readback as a value register, seed software ring indices from
hardware and publish with release ordering. Primary-source review caught swapped
watermark halves before physical deployment: high threshold occupies bits15:0,
low threshold bits31:16. Exact watermark assertions now cover this.

PCI IO adapter restricts engine/register access, requires retained exclusive PCI
claim/MEM/awake/BAR lifetime, and validates descriptor windows against registered
mapped32bit DMA buffers. Exposure is recorded before writes, including ambiguous
failures. Resume/doorbells reject closing or unmapped regions. Zero-size disabled
queues accept only zero indices while halted. Halting/zeroing still works after
DMA close has set closing, so failure recovery remains possible.

Bus lifecycle controls ALL8 engines, including inactive pipes. Before bus-master
activation mark every registered descriptor/data buffer exposed, resume configured
engines and write only16bit PCI Command, then require exact readback. Failed enable
retains ownership; an ambiguous error cannot authorize free. Stop requests every
engine, cooperatively verifies halt and zero addresses/sizes, disables bus master
with actual16bit readback. On failed halt, attempt disabling DMA capability but
retain ownership. DMA close callback requires completed stop plus FRESH all-eight
halt/zero-ring and bus-master-off reads, then existing adapter Flush/Unmap/Free.
No callback dereferences a released PCI protocol. All caller operations must be
serialized with native unload, and all DMA buffers must be registered.

Evidence: experiments/native-wifi-qca9377-v1/evidence/2026-10-04/ce-hw.
21 actual core/UEFI/bus scenarios pass ASan/UBSan on Yukabox: ambiguous enable,
dropped enable/readback, failed disable, missing halt ACK, corrupt stop readback,
failed config reads, closing buffers, failed Flush/Unmap and safe retained-resource
recovery. All3 production components compile freestanding x86 COFF. Updated ring
core passes5000 wrap cycles and seed-at-nonzero tests; updated source-bound report
and log are included alongside CE gate evidence. Mock completion is NOT physical
CE/DMA/BMI success. No owner key, signing, radio send or native update in this turn.
Saved state still identifies native12 payload99463fa0... and no pending operation;
this is saved receipt state, not a fresh physical observation.

NEXT: integrate cooperative ROM readiness and CE0/CE1 BMI get-target-info into a
native profile, bind DMA/ring/bus lifetimes to its stop/unload gate, pass exact
normal+EMPTY city/BT and rebuild gates, then owner-sign/send and obtain physical
telemetry. Firmware chunk upload, radio/WMI/HTT, scan/WPA, DHCP/two-way traffic and
reconnect remain incomplete. Original full Wi-Fi goal remains active.


## 2026-10-04 — cooperative ROM readiness and first BMI exchange

Added rom_ready.c/h and bmi_transport.c/h, BMI target facts, integration tests
and verify_bmi.py. ROM wait reads only validated PCI IO firmware indicator at
0x3a028, at10ms intervals with3s deadline; all-ones is never interpreted as ready,
crash bit takes priority over initialized bit. Handle clock reversal, near-UINT64
clock overflow, protocol release and PCI IO errors without blocking a city tick.
Caller must first complete reset and fresh PCI/D0/wake validation.

First transport query is ONLY BMI_GET_TARGET_INFO (LE32 command8), with12byte
reply length/version/type retained. CE0 source and CE1 destination use actual
ring/CE/bus/PCI IO production components. Verify empty seeded rings match live
hardware base/size and registered descriptor memory; refuse unmapped/closing
buffers, descriptor/data aliasing, parallel exchanges and clock overflow. Post
response before request, use BMI transfer metadata0x3fff, and require both TX
and RX completion. RX hardware-index-before-length race remains WAIT. Bad length,
address, cookie/index or zero/all-ones identity faults retain rings/mappings for
explicit bus stop. Ring close callback requires fresh all-engine halt/zero rings,
bus-master-off AND successful PCI IO Flush before zeroing descriptors. Actual
DMA close still owns Unmap/Free ordering. No firmware-write/execute/done command.

11 integration scenarios pass ASan/UBSan on Yukabox, each also exercising ROM
ready/all-ones/crash/timeout/clock/IO/lifetime gates. Includes nonzero seeded
indices, RX-before-TX publication order, delayed descriptor update, invalid reply
length/oversize/address/index/version, failed RX doorbell, close only after stop,
rejected descriptor aliases and unmapped input. Freestanding x86 COFF for both
new production components passes. Exact source/log and pinned reference hashes
in evidence/2026-10-04/bmi; tests use synthetic target version/type, NOT Dell data
or firmware-compatibility proof. Native profile integration/physical ROM ready/
physical BMI response are explicitly false in report. Saved native12 unchanged,
no Bluetooth send/signing/new physical observation in this turn.

NEXT: integrate this first query into reset profile with4 coherent DMA pages
(TX descriptors, RX descriptors, request, response), fresh PCI/D0/reset/ROM gates,
all-eight bus stop/start and unload retention. Allocate1page at a time, register
all4 buffers, initialize8entry rings before configure, seed from hardware, then
start bus and query. On success/error/cancel cooperatively stop all engines,
close both rings, close all buffers, then port/wake; any uncertain allocation or
failed stop/unmap retains native ownership and blocks unload. Include telemetry
for ROM/BMI raw reply/error and resource cleanup, preserve city/BT normal+EMPTY
QEMU gates and exact reproducible owner-bound package before physical delivery.
Full firmware RAM chunks/radio/scan/WPA/DHCP/reconnect goal remains incomplete.


## 2026-10-04 — native13 applied physically; ROM-ready timeout before DMA

Added bmi_probe.c/bmi_build.py/verify_bmi_profile.py and delivery/reproduction/QPD5
support. Full profile links production reset, ROM,4coherent DMA buffers,8CE bus
lifetime, seeded CE0/1 rings and BMI transport; one allocation/cleanup per poll.
Stop/cancel retains reset/CE/DMA ownership until cooperative cleanup completes,
blocks unload on failed halt/Flush/Unmap/Free, supports cleanup retry after errors.
17 integrated hardware-mock scenarios including D3/unsupported/absent, reset
ambiguity/cancel, ROM timeout, above32bit mapping, malformed reply, BMI timeout,
ambiguous bus-master enable and Flush failure pass ASan/UBSan on Yukabox. Exact
normal+EMPTY UEFI QEMU city/BT/rejection/recovery gates pass; QCA absent in VM.
Same native bytes rebuilt twice against current actual saved city package with
sanitizer world checks. QPD5 is240bytes, fits247byte ATT MTU; decoder distinguishes
raw BMI reply from firmware compatibility, and rejects invalid DMA hold masks.
All native compilation on Yukabox; Mac only control/Bluetooth/reader/signature.

Owner-authorized exact native13 payload SHA256:
ec846096da49cc5eea9b118405e9024cfcbe6ee0be190df60564d072a1abb362.
Signed locally (key never printed/copied) and66848byte session sent over Bluetooth.
Staging timed out at29000bytes; same nonce/session resumed from receiver-confirmed
29100. COMMIT disconnected as expected on module replacement; same session then
received exact SHA/session/counter APPLIED. Saved engine native13, city world12,
no pending operation. Fresh pre-native13 QPD4 proves previous cleanup/chip identity;
post-native13 actual QPD5 obtained after applied receipt and Bluetooth recovery.
Session: runs/text-world/pci-native-7e7wgk_a under connected supervisor experiment.

PHYSICAL RESULT: chip003821ff/SoCrev1, D0, verified cold reset clear and PCI original
Command0102 restoration. ROM indicator remained0 for bounded3second wait;
stage6/error0x504 (ROM error4 timeout). BMI was NOT sent; DMA was NOT activated or
allocated. Bus phaseIDLE/ownedfalse, buffer count/held-mask0, port cleanup complete.
No firmware/radio/WPA/DHCP success. Exact evidence under
experiments/native-wifi-qca9377-v1/evidence/2026-10-04/bmi-profile, including gate
reports, source-bound reproduction, physical receipt, raw/decoded diagnostic and
physical-summary.json. QEMU PASS must not substitute for this physical timeout.
Async owner observation city/tail after native13 remains pending; no visual claim.

NEXT: account for native PCIe bringup differences. Pinned ath10k hif_power_up
saves and disables LinkControl ASPM BEFORE reset; our fresh prior physical power
probe found LinkControl0143 (both ASPM bits enabled) and current profile does not
change those bits. Implement bounded reversible16bit LinkControl save/disable/
readback/restore under exclusive PCI claim (never32bit write touching LinkStatus),
with retained ownership on ambiguous failure and cleanup before port release.
Then repeat ROM wait physically in next owner-checked profile. Also inspect
ath10k wait_for_target_init's legacy-INTx workaround (repeated interrupt-enable
writes with readback) and QCA6174 cold+warm reset ordering. Do not blindly enable
host interrupts or claim either hypothesis as established; no further physical
writes until matching deterministic gates. Full original Wi-Fi goal remains active;
firmware RAM chunks/radio/WPA/DHCP/two-way traffic/reconnect remain incomplete.


## 2026-10-04 — native14: reversible ASPM tested physically; ROM still times out

Added pcie_link.c/h. Under exclusive validated PCI claim, decode fresh256byte
capability list and require D0 + matching Dell QCA identity + PCIe endpoint cap.
Save LinkControl; clear only ASPM bits0:1 using PCI IO Write16 and exact readback.
Own before ambiguous write. Restore exact saved word with fresh cap/identity/D0
check, no DMA users/BM; adjacent LinkStatus is never written. New port link_owned
blocks close/reopen until verified restore. Cleanup failure retains native/PCI
ownership and supports explicit retry. Full integrated gate extends to21host
scenarios: rejected capability, ambiguous/drop disable, failed/drop restore and
retry, with original reset/DMA/BMI failures. DMA gate rerun for new port guard.
QPD6 is246bytes (full Read response247 fits ATT MTU); adds saved/last LinkControl
and ownership/error, preserves pre-reset active snapshot at182. Decoder gates
ownership/size and distinguishes restoration from firmware readiness.

Exact21host sanitizer + component host/COFF/ABI gates, normal+EMPTY real UEFI QEMU
city/BT/rejection/recovery gates and two fresh native/current-world rebuilds pass
on Yukabox. Candidate payload SHA256:
50e1d3d34a76d6adbfa930474b6bedd7ebdf93ff4daa0f278963bb8dd6ecb54a.
Locally signed exact native14,67872byte Bluetooth session staged fully; same session
COMMIT/reconnect got exact SHA/session/counter APPLIED. Saved native14/world12,
no pending operation. Receipt session runs/text-world/pci-native-_pexlbhw.
No owner key output/copy, Mac native build, USB/bootstrap change or Dell reboot.

PHYSICAL QPD6: LinkControl0143 -> verified0140 BEFORE reset -> restored0143,
ownedfalse/error0. Chip003821ff/rev1 and D0/cold-reset checks remain good. ROM
indicator0 after3s, stage6/error0x504; no BMI response, no DMA allocation/activation,
held resources0 and cleanupcomplete. Evidence under native-wifi experiment
/evidence/2026-10-04/pcie-rom-profile includes all source-bound reports and raw
physical receipt/diagnostic. Active link snapshot is BEFORE reset, not a separate
measurement during ROM wait: this experiment does not prove ASPM stayed disabled
through cold reset. Do not overstate a ruled-out hypothesis. Owner visual
city/tail observation remains pending; Bluetooth restoration is observed.

NEXT: augment fresh post-reset PCI snapshot with LinkControl and ensure/reapply
ASPM-off before ROM polling if reset changed it. Pinned ath10k
wait_for_target_init repeats PCIE_INTR_ENABLE at SOC_CORE_BASE+offset with
firmware|CE masks for legacy INTx boot race and flushes posted write via readback;
current profile does not perform that step. Add a reversible boot-IRQ adapter,
with host INTx disabled and MSI/MSI-X state validated before device IRQ enable,
actual-command/target-register readback and cleanup/port-close ownership guard.
Never blindly enable an unhandled host interrupt. All writes need matched mock,
COFF, exact normal/EMPTY city/BT, reproduction and owner gates before next send.
Another source difference is Linux pci_claim enables bus mastering BEFORE reset/
ROM wait, while ours leaves it off until ROM-ready. If IRQ ordering is insufficient,
plan a DMA-lifetime-aware earlier master enable only after all8CE quiescence and
reviewed mapped empty rings, retaining mappings across reset and revalidation.
No DMA activation, firmware compatibility/upload, scan/WPA, DHCP/two-way traffic
or reconnect success yet. Full original Wi-Fi goal remains active/incomplete.

## Native18 physical result, after city recovery

Native18 preserves separately tested Bluetooth disconnect recovery. Updated normal/
EMPTY UEFI gates reproduce lost-event recovery;34 integrated Wi-Fi plus sanitized
baseline/fixed link tests pass;248 sources/two native rebuilds/current-world checks
are bound before local owner signing. Exact70432byte session received APPLIED18.
City world13/content and12-version history retained; owner visual city/tail check
following18 pending. Payload00324a1214b556ef23e406993a905700e9beba3b7152b041e557f475346aea51.
Physical QPD7 NOW sees ROM indicator2/ready. BMI target-info still times out3seconds
(error5/overall0x805). PCI/ASPM/IRQ resources restored, DMA held0 and bus_ownedfalse;
no firmware/association success. This narrows the next work to CE0/CE1 transport
telemetry before cleanup, not ROM readiness. Evidence and exact next constraints
are in the latest connected-native handoff and evidence/2026-10-04/
bootirq-ble-profile-native18/physical. Never deliver retired15/16 packets.

## Latest19/20 continuation

Native19 QPD8 snapshot profile applied exactly, but physical diagnostic stopped
before chip reset at actual MemoryEnable Command readback(error0x10b00): cached
attributes200, actual Command0100. No exchange snapshot, no BMI result. Original
port sources/physical receipts kept in ce-snapshot-native19/physical. Added bounded
Write16 MEM-only repair for exactly unchanged Command, exact readback, ambiguous/
dropped/foreign-command retention tests. Fresh Yukabox gates/rebuild/current-world
checks pass; locally signed20. Bluetooth stopped at1400/71456 without COMMIT or
APPLIED. Current engine19/world13; native_pending is pci-native-_g6coe4s. Same
session/resume required, no reboot/new packet. See latest connected-native handoff
and evidence cached-memory-native20. Physical repair/CE/BMI/Wi-Fi remain unproven.

## Native20 physically applied: exact next boundary

Owner brought Mac nearby. SAME20 packet resumed to full71456bytes, exact APPLIED20
receipt. Current native20/world13/no pending. Physical QPD8 crosses cached-memory
failure: activePCI0102, chip003821ff, ROMready2; BMI still times out. Immutable
snapshot confirms posted08000000 request, softwareTX/RXwrite1/read0, last observed
hardware0/0, neither completion, responsezero. Cleanupcomplete, mappingsreleased,
PCI/ASPM/IRQ restored. Evidence physical summary updated; initial failed-transfer
summary retained. Physical scene/motion question pending. Next bounded diagnostic
must inspect CE queue configuration BEFORE all-engine halt/zero, then compare with
pinned ath10k host-side initialization. No cause/firmware/Wi-Fi success inferred.
New profile must preserve20 memory repair and BLE recovery; do not resend20.
