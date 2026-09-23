# x86-64 UEFI QCA initialization + Rabbit beacon receive v0

This is the first single-boot composition of two physically observed primitives:

1. load exact hash-pinned QCA Rome 3.2 rampatch and NVM into volatile controller RAM;
2. require `PATCH_UPDATED=YES` and `SYSCFG_UPDATED=YES`;
3. run the already reviewed 20-second passive scan for exactly
   `52414242-4954-4C45-8000-000000000001`;
4. always disable scanning before reporting the result.

The composition is necessary because a full Dell power-off clears the controller RAM.
The Dell only receives radio advertisements. It never performs active scan, advertises,
pairs, connects, sends ACL data, resets the controller, writes controller flash, or
writes the Dell's internal storage or firmware settings.

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

and must never reach `BEGIN BOUNDED PASSIVE RABBIT RECEIVE`. Physical installation is
closed until this exact result is observed and evidence-bound.

Reviewed pre-QEMU identities:

```text
template SHA-256: 5996cd6f6a1af50ca5a255769af0a39c2146f958f5147d7fd261e2ba9ea2a6d3
program SHA-256:  b5a672b9dad9624589f50f42f4ed55a44c29ba3b189e8f2e99e73275a329e236
EFI SHA-256:      4a25054ceb2acbb9806786028e1a601536531328a7396cecd7dc081d11f272df
image SHA-256:    50d5232d4914e33220d73bff53bd42f428244a96a96c9abbaa19b9766200ab7d
```

Full power-off is rollback for controller RAM. Removing the USB is recovery for the
boot application. Status: **PRE-QEMU; NOT INSTALLED**.
