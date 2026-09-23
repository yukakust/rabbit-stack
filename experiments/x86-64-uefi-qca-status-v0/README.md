# x86-64 UEFI QCA Rome status v0

This experiment diagnoses why the physical Dell controller accepted passive-scan
commands but delivered zero USB events. It targets only USB `0CF3:E009`, interface
`00`, class `E0/01/01`, and performs exactly two device-to-host vendor reads used by
Linux's reviewed QCA Rome setup path:

1. request `0x09`, 20 bytes: ROM, patch, RAM, chip, platform, and flag values;
2. request `0x05`, 1 byte: setup status, including `PATCH_UPDATED` (`0x80`) and
   `SYSCFG_UPDATED` (`0x40`).

The artifact cannot send a vendor-OUT request, HCI command, controller reset,
firmware payload, scan/advertising command, or radio traffic. It writes neither the
internal disk nor firmware. If the target is absent, no vendor request is sent.

## QEMU gate

On the Mac:

```sh
cd ~/rabbit-stack/experiments/x86-64-uefi-qca-status-v0
python3 run_qemu.py
```

QEMU does not contain the exact Qualcomm controller. The required result is:

```text
TARGET NOT FOUND; NO VENDOR REQUEST SENT
```

Photograph the result and close QEMU. Physical preparation stays closed until that
observation is recorded and bound to the exact hashes.

Reviewed identities:

```text
program SHA-256: 7746e8954e4a14daec9a494c730fcee7b6fe56c1e72ad02db5f1109cb16efcc0
EFI SHA-256:     aa1f1f9dbbd4ae92749ea6c7154066746c16bef2c3b56b4dc2ab69bad31b148d
image SHA-256:   e7747dbd747ef9add8a5853d01f05e93ebaf20807399a0d697883b15fd235b1f
```

Status: **PRE-QEMU**. No physical-device write has been authorized or performed.
