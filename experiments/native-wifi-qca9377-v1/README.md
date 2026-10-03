# Native Wi-Fi QCA9377 v1 — preparation, not a working driver

Owner chose the internal Wi-Fi: there is no Ethernet cable. Dell in Georgia has
no installed OS/disk; Mac is command/control and Yukabox in Poland runs Unreal.
Preserve native7/world12 and its city; no replacing bootstrap/USB or reboot implied.
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

Loading/recovery **today**: run host scripts on Yukabox; they touch only their
workspace files. Delete that workspace to remove them. There is no hardware
loading path yet, and no claim that the Dell Wi-Fi currently works. Future native
RAM profile must use the existing signature/current-identity/QEMU gates, with
documented close/rollback and preserved city before hardware activation.

```sh
python3 fetch_materials.py
python3 verify_preflight.py
python3 verify_pci.py
```

`verify_pci.py` requires the previous pinned iPXE header workspace at
`/home/yuka/rabbit-world/dell-network-viewer-v1` and the installed UE Linux Clang/LLD.
It uses `run_probe.py` only for an isolated virtual device; no driver is loaded on
physical Dell. Read-only helper integration and exact native gates remain to do.

References: [ath10k architecture](https://wireless.docs.kernel.org/en/latest/en/users/drivers/ath10k/architecture.html)
and [calibration/board data](https://wireless.docs.kernel.org/en/latest/en/users/drivers/ath10k/calibration.html).
Driver source is GPL2; firmware distribution terms/notices are fetched alongside
the blobs and remain applicable. This repository includes only our preparation
tools and hashes, not Linux or proprietary firmware binaries.
