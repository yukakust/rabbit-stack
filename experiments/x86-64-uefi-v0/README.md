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

`run_qemu.py` locates the x86-64 UEFI firmware bundled with QEMU, builds the image in a
temporary directory, disables emulated networking, attaches the image read-only, and
opens a QEMU display. The expected screen is exactly `HI`; press one key to let the UEFI
application return, then close the QEMU window. This is still emulator evidence, not a
physical Dell result.

The builder may create `/tmp/rabbit-x86-64-uefi-v0.img`; it does **not** select or write
a physical device. Generated binaries are intentionally excluded from Git.

Current status is `BUILT-NOT-INSTALLED`. Before any USB write:

1. reproduce the image under x86-64 QEMU with UEFI firmware;
2. inspect the USB device read-only on the Mac and record its exact whole-disk identity;
3. review the fact that this v0 image is unsigned and the Dell currently has Secure Boot
   enabled;
4. request explicit authorization that names the removable target;
5. hash the artifact again immediately before and after the write.

Removing the USB and powering off is the recovery path. Nothing in this experiment
authorizes modifying an internal disk or firmware setting.
