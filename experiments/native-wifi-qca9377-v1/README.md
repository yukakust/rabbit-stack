# Native Wi-Fi QCA9377 v1 — physical diagnostics and initial driver port

Owner chose the internal Wi-Fi: there is no Ethernet cable. Dell in Georgia has
no installed OS/disk; Mac is command/control and Yukabox in Poland runs Unreal.
Current physical profile is native9/world12. Preserve its city; no replacing
bootstrap/USB or reboot implied. Wi-Fi is still not associated.
Wi-Fi authorization is explicit; the old handoff's "unrelated network runtime"
restriction concerned an earlier engine trial, not this requested transport work.

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
