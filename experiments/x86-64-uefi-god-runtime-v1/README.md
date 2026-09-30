# Dell UEFI Rabbit God Runtime v1

This experiment is the first single physical image containing all of these boundaries:

```text
reviewed Inventory package
  -> deterministic 192-byte signed capsule
  -> 30 passive BLE frames
  -> isolated staging RAM
  -> Ed25519 + identity + authority + bounds checks inside UEFI
  -> provisional Scene/Anima activation
  -> one health tick
       healthy -> commit + correlated receipt
       failure -> restore the exact prior active world
```

The resident Scene/Anima core is no longer the old fixed trace player. It advances the
cat and ball with bounded integer state, collision behavior and two sprite frames. The
physically observed Cat Creation remains the embedded fallback and starts immediately.
Ordinary accepted world changes use Bluetooth and RAM; they do not write the USB,
internal disk, controller flash, or firmware settings.

The full Inventory JSON is still validated on the creator machine. Its deterministic
lowering is signed again as `rabbit-god-capsule-v1`; the UEFI image independently checks
that Ed25519 signature and accepts only the reviewed Creation, component-set identity,
authorities, budgets and a newer in-boot counter. This is not “trust the Mac”: a changed
capsule or a different signing key is rejected on Dell.

## Verify and run the mismatch gate

```sh
cd ~/rabbit-stack/experiments/x86-64-uefi-god-runtime-v1
python3 verify.py
python3 run_qemu.py
```

QEMU must show the Runtime identity and fail closed at `TARGET NOT FOUND`, because it
does not emulate the exact Dell Bluetooth controller. No controller RAM, radio,
framebuffer or capsule effect is allowed on that mismatch path.

The headless QEMU run was observed on 2026-09-30 and is bound to the exact EFI and disk
identities in `evidence/qemu-linux-x86-64-observed.json`.

## Prepare, but do not install

```sh
python3 prepare_physical.py
```

This writes only `/tmp/rabbit-god-runtime-v1.img` and lists removable media read-only.
It does not alter the current Cat USB. Physical status remains
`BUILT-NOT-INSTALLED` until the owner explicitly performs the one final Runtime upgrade
and reports the screen.

The current capsule accepts the exact Cat Scene/Anima component set. Adding new trusted
component implementations expands this inventory without changing the transport or
transaction protocol. Cross-reboot replay protection and encrypted transport remain
recorded debt; the current monotonic counter lasts for one boot.
