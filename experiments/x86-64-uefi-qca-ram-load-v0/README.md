# x86-64 UEFI QCA Rome transient RAM load v0

The physical status probe found exact USB `0CF3:E009`, ROM `0x00000302`, and
`PATCH_UPDATED=NO` plus `SYSCFG_UPDATED=NO`. This experiment implements the next
bounded boundary: load the exact upstream Rome 3.2 rampatch and NVM into volatile
controller RAM, then read the status bits again.

The payloads are fetched unmodified from a pinned official `linux-firmware` commit.
They are not committed to Rabbit Stack. Every fetch must match exact size and SHA-256:

```text
rampatch_usb_00000302.bin  68644 bytes  f0d15f6d7c4ce17270c951287222699c0909bea9028ecb84d2e8be6fa364691e
nvm_usb_00000302.bin        1998 bytes  9ee2cff5bd51523b65c941b72ecf05a8b5e7b9e280c79fa08c70ade7205088a5
linux-firmware commit: 797d34e622b2262ca0777e98fd40b1d29034169d
```

Their Qualcomm license permits unmodified binary redistribution for use with Qualcomm
Atheros chipsets and imposes notice and other conditions. Rabbit fetches them from the
upstream repository and records the upstream license/notice locations in
`firmware.json`; it does not claim ownership or reverse-engineer their contents.

## Exact authority

- only USB `0CF3:E009`, interface `00`, class `E0/01/01`;
- require ROM exactly `0x00000302` before any device write;
- two vendor-OUT headers: 28-byte rampatch header and 4-byte NVM header;
- at most 18 bulk-OUT transfers to endpoint `0x02`, each at most 4096 bytes;
- payload bytes must match the pinned hashes;
- writes affect controller RAM and disappear after full power-off.

There is no controller-reset, HCI, scan, advertising, pairing, connection, radio,
controller-flash, internal-storage, or firmware-setting path. This boot only asks:
did the exact RAM transfer change both setup flags to `YES`?

## QEMU fail-closed gate

```sh
cd ~/rabbit-stack/experiments/x86-64-uefi-qca-ram-load-v0
python3 run_qemu.py
```

QEMU lacks the exact controller, so the required result is:

```text
TARGET NOT FOUND; NO DEVICE WRITE SENT
```

On 2026-09-23 QEMU 11.1.1 on the Apple Silicon Mac displayed that exact result. The
observation is bound to the exact world inputs, payload manifest, program, EFI, and
image identities. `prepare_physical.py` is now open; it still stops before writing a
removable device.

Reviewed identities:

```text
loader template SHA-256: 7d5da33ee1fb62b6cd77495e0b886fc6620c43330d85d7e3d23bad3a3dfc1e59
loader + payload SHA-256: 6cada945ae22c1e1a7494ad437fb93dbd6c9fd552b816eb36105ce43569250f4
EFI SHA-256:              3fa8eacf475d4c711d365f1712e8494dd2c18666de2e2d124f42c20daa101bb5
image SHA-256:            2b4894f77181626cafd7369fd80f60ae3451e9d93ca8ee4ebf7f6cc696eccadd
```

## Physical Dell result

The exact image matched ROM `00000302`, transferred both pinned payloads, and displayed:

```text
RAMPATCH TRANSFER: OK
NVM TRANSFER: OK
PATCH_UPDATED=YES; SYSCFG_UPDATED=YES
```

No reset, HCI command, scan, or radio operation occurred. The controller RAM write is
explicitly recorded, while controller flash, internal storage, and firmware settings
remain untouched. Full power-off is the rollback.

Status: **PHYSICAL-DELL-OBSERVED-TRANSIENT-RAM-READY**. The next boundary combines this
initialization and the already reviewed bounded passive Rabbit-beacon receiver in one
boot, because a full power-off discards the controller RAM state.
