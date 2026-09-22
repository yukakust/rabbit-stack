# x86-64 UEFI v0 — first pre-physical artifact

This experiment begins U7 without touching the purchased USB device. It lowers the
unchanged semantic `HI` world from `capability-negotiation-v1` into a deterministic
x86-64 UEFI application and places it at the standard removable-media path:

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
and the whole-image mismatch instead of hiding the host mutation. The USB is prepared,
but physical execution is still unverified and the Dell's enabled Secure Boot remains a
separate blocker.
