# x86-64 UEFI v0 — first physical target

This experiment began U7 by lowering the unchanged semantic `HI` world from
`capability-negotiation-v1` into a deterministic x86-64 UEFI application at the standard
removable-media path. That artifact has now been observed in QEMU and on the physical
Dell; the later sections preserve the complete evidence sequence.

```text
64 MiB MBR disk image
└── FAT32 partition
    └── EFI/BOOT/BOOTX64.EFI
```

`BOOTX64.EFI` is a tiny PE32+ application made from reviewed machine bytes. It receives
the UEFI System Table, calls the standard Simple Text Output `OutputString` function with
the UTF-16 string `HI`, waits for one key through Simple Text Input, and returns
`EFI_SUCCESS`. It contains no OS, filesystem driver, network stack, internal-disk code,
or firmware-writing code. UEFI remains an explicit layer.

Build into a disposable path on the Mac:

```sh
cd ~/rabbit-stack/experiments/x86-64-uefi-v0
python3 build_image.py --output /tmp/rabbit-x86-64-uefi-v0.img --report /tmp/rabbit-x86-64-uefi-v0.json
python3 verify.py
python3 run_qemu.py
```

The existing immutable semantic patch can be built and exercised separately:

```sh
python3 build_image.py --patch add-bang --output /tmp/rabbit-x86-64-uefi-hi-bang.img --report /tmp/rabbit-x86-64-uefi-hi-bang.json
python3 run_qemu.py --patch add-bang
```

Reviewed patched identities:

```text
effective world SHA-256: 3bdda867e932c39e1ed68079609463c53627914b7eca886a41f2b4bf68109586
patch SHA-256:           43a0914a14d78dace32013ece24c45c92d66a52414c3aa7ff285a87d5d923868
EFI SHA-256:             b20888a358ddd69c42d249a76f128f4684dc460098db6863614d51b0d322c796
image SHA-256:           2099b5e4cd07551ecabda7262a6ae2b882bfe495dd32d45070e3d35d10fd26b5
expected display:        HI!
```

The verifier also proves that removing `add-bang` rebuilds the exact original `HI`
world, EFI application, and disk image. Neither variant is permitted to edit the base
world in place.

On 2026-09-22 the owner ran `python3 run_qemu.py --patch add-bang` with QEMU 11.1.1
and observed exactly `HI!`. The manual emulator observation is bound to the base world,
effective world, patch, target, EFI, and image identities in
`evidence/qemu-macos-arm64-add-bang-observed.json`. No physical media was written by that
run.

`run_qemu.py` locates the x86-64 EDK2 code and variable-store template bundled with
QEMU. It attaches the code as read-only pflash, copies the mutable variable store into a
temporary directory, builds the disk image there, disables emulated networking, and
gives only that disk a temporary snapshot overlay. The expected screen is exactly `HI`;
press one key to let the UEFI application return, then close the QEMU window. This is
still emulator evidence, not a physical Dell result.

The runner deliberately does not use QEMU's global `-snapshot` flag: that flag also
makes the pflash variable store read-only. Persistence is still impossible because the
only writable pflash file is the disposable copy inside the temporary directory.
The emulated SATA controller receives a writable snapshot overlay rather than direct
write access to the generated base image; the overlay is deleted with the same temporary
directory.

On 2026-09-22, QEMU 11.1.1 on the Apple Silicon Mac loaded the exact reviewed image
through TianoCore EDK II. The firmware screen showed that `UEFI QEMU HARDDISK QM00001`
started and the application displayed `HI`. The owner supplied a screenshot and terminal
transcript; `evidence/qemu-macos-arm64-observed.json` binds that manual observation to
the exact world, Target Pack, EFI, and image hashes. This is deliberately labeled manual
QEMU evidence, not an automated oracle or a physical-hardware result.

The builder may create `/tmp/rabbit-x86-64-uefi-v0.img`; it does **not** select or write
a physical device. Generated binaries are intentionally excluded from Git.

Current status is `OBSERVED-MANUAL-QEMU; NOT-INSTALLED`. Before any USB write:

1. inspect the USB device read-only on the Mac and record its exact whole-disk identity;
2. review the fact that this v0 image is unsigned and the Dell currently has Secure Boot
   enabled;
3. request explicit authorization that names the removable target;
4. hash the artifact again immediately before and after the write.

Removing the USB and powering off is the recovery path. Nothing in this experiment
authorizes modifying an internal disk or firmware setting.

## Physical removable-media write

On 2026-09-22 the owner explicitly authorized erasing a new external removable Kingston
DataTraveler Duo. macOS identified the whole physical USB device as `/dev/disk4` at the
time of the write, with size 123,983,626,240 bytes. Exactly 67,108,864 source bytes were
written through `/dev/rdisk4`; no internal disk or firmware write was reported.

The first post-write 64 MiB hash did not equal the source image. Investigation showed
that macOS had automatically mounted `RABBITBOOT` and added
`.fseventsd/fseventsd-uuid`. The exact boot payload remained byte-identical:

```text
EFI/BOOT/BOOTX64.EFI
SHA-256: a82d77b43d636d63af9bfa76e0a998ed4b62746a0eab10ad0f6c1777dc8c6128
```

`evidence/kingston-usb-write-observed.json` records both the successful payload check
and the whole-image mismatch instead of hiding the host mutation. At that checkpoint the
USB was prepared while physical execution and the Secure Boot decision still remained
open; the following section records how those gates were resolved.

## First physical execution

On 2026-09-22 the owner selected `UEFI: KingstonDataTraveler Duo0000` on the physical
Dell OptiPlex 3060. With Secure Boot enabled, the unsigned image did not reach `HI` and
firmware fell through to the no-internal-drive path; the transient rejection text was
not captured, so that result is recorded as inferred rather than direct display evidence.

The owner then explicitly authorized disabling only `Secure Boot Enable`. No keys were
deleted or replaced, Legacy mode was not enabled, and no BIOS update occurred. The same
verified USB subsequently displayed `HI` on the physical monitor and waited for a key.
There was no guest or host operating system and no internal storage; the physical
i5-8500T executed the PE32+ application while Dell UEFI remained responsible for loading
and text output.

The owner chose to keep Secure Boot disabled because this is a dedicated home lab
machine. That is an explicit policy decision, not a restoration claim. It remains
reversible and should be reconsidered if the machine gains an everyday OS, untrusted
users, untrusted boot media, or another role. Exact evidence is recorded in
`evidence/dell-optiplex-3060-physical-observed.json`.

This completes the first physical target slice of U7. Overall U7 remains open until the
same meaning is shown on another dissimilar physical target. The immediate next slice is
an immutable physical cold patch `HI -> HI!` followed by exact rollback to `HI`.

On 2026-09-22 the patched payload was independently hash-checked on the removable media
and selected through the same Dell UEFI boot entry. The physical display showed exactly
`HI!`. `evidence/dell-optiplex-3060-add-bang-physical-observed.json` binds that result to
the base world, immutable patch, effective world, target, QEMU evidence, EFI, image, and
the earlier physical base observation.

The owner then rebuilt the exact base image without `add-bang`, re-identified the
external removable Kingston device, wrote exactly 67,108,864 bytes, and verified the
restored `BOOTX64.EFI` hash before ejecting it. The same Dell booted that payload with
the documented Secure Boot-off lab policy and displayed exactly `HI`. Evidence in
`evidence/dell-optiplex-3060-rollback-physical-observed.json` therefore closes the
physical cold-patch lifecycle `HI -> HI! -> HI`; it does not infer physical rollback
from the deterministic builder alone.
