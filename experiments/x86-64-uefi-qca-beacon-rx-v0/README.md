# x86-64 UEFI QCA initialization + Rabbit beacon receive v0

This is the first single-boot composition of two physically observed primitives:

1. load exact hash-pinned QCA Rome 3.2 rampatch and NVM into volatile controller RAM;
2. require `PATCH_UPDATED=YES` and `SYSCFG_UPDATED=YES`;
3. issue exactly one standard HCI Reset and wait 100 ms;
4. run the already reviewed 20-second passive scan for exactly
   `52414242-4954-4C45-8000-000000000001`;
5. always disable scanning before reporting the result.

The composition is necessary because a full Dell power-off clears the controller RAM.
The Dell only receives radio advertisements. It never performs active scan, advertises,
pairs, connects, sends ACL data, writes controller flash, or writes the Dell's internal
storage or firmware settings. V0.2 permits exactly one post-load HCI Reset and rejects
zero or multiple resets. This is not a USB-port reset or persistent firmware write.

Pinned firmware inputs remain the unmodified files from linux-firmware commit
`797d34e622b2262ca0777e98fd40b1d29034169d`:

```text
rampatch_usb_00000302.bin  68644 bytes  f0d15f6d7c4ce17270c951287222699c0909bea9028ecb84d2e8be6fa364691e
nvm_usb_00000302.bin        1998 bytes  9ee2cff5bd51523b65c941b72ecf05a8b5e7b9e280c79fa08c70ade7205088a5
```

## Current gate

Verify and start the fail-closed QEMU run:

```sh
cd ~/rabbit-stack/experiments/x86-64-uefi-qca-beacon-rx-v0
python3 verify.py
python3 run_qemu.py
```

QEMU has no exact `0CF3:E009` device. It must display:

```text
TARGET NOT FOUND; NO DEVICE WRITE SENT
```

and must never reach `BEGIN BOUNDED PASSIVE RABBIT RECEIVE`. V0.1 passed this gate and
then ran physically: RAM setup reached status `E0`, but its scan reported
`RX/LE/ADV=00/00/00`. V0.2 adds only the bounded post-load reset hypothesis and requires
a fresh QEMU observation before physical preparation reopens.

Reviewed pre-QEMU identities:

```text
template SHA-256: 384631ecf1d1011532aec4f700d1eb36639383ba740c3c4b6f49b6193db7d66d
program SHA-256:  44702cdc7e96a8ba80ab8bfd92378b98a4d1f0169a0277fab4c07ccae194b3a9
EFI SHA-256:      b5572f8e6f23daea9568d2e07ffc684bbbe4b25e591e3ac61bc8c42354c862ba
image SHA-256:    7460a9fce26fc8aea329f0c169492e0c76b60d5df88cfdd0f9901eb9ac56ae5f
```

After the fresh v0.2 QEMU result is evidence-bound, prepare the candidate with:

```sh
python3 prepare_physical.py
```

Full power-off is rollback for controller RAM. Removing the USB is recovery for the
boot application. Status: **V0.2 PRE-QEMU; NOT INSTALLED**.

Primary references: Linux's
[`btusb_setup_qca`](https://code.googlesource.com/linux/torvalds/linux/+/21e4675d9305f6ccd20b95d943882d607c8ae288/drivers/bluetooth/btusb.c)
downloads the USB payloads and returns to generic HCI initialization; QCA's core setup
also documents a post-download HCI Reset in
[`btqca.c`](https://github.com/torvalds/linux/blob/master/drivers/bluetooth/btqca.c).
