# Dell x86-64 UEFI Scene/Anima v2

This experiment lowers the exact target-independent `Cat Plays With Ball` Creation
from `reusable-creation-inventory-v1` to a bounded Dell-compatible UEFI application.
The Creation identity, its thirteen reusable component identities, and the hosted
Scene/Anima runner contract are unchanged. Machine facts live only in `target.json`.

The first physical backend is deliberately small: it embeds the exact canonical
241-frame semantic trace already produced by the hosted runner and plays it at 30
ticks per second. It draws the catalog's exact cat and ball sprites into only the
top-left 480-by-270 GOP region, uses UEFI `Stall` for timing, and accepts only Escape
to exit. It has no network, radio, internal-storage, firmware-write, or extension
authority.

This is an AOT trace player, not yet a general Scene/Anima interpreter. That boundary
lets us establish that one portable Creation has the same identity and visible story
on the hosted runner and the physical target before expanding the physical runtime.

## Verify and preview

```sh
cd ~/rabbit-stack/experiments/x86-64-uefi-scene-anima-v2
python3 verify.py
python3 run_qemu.py
```

QEMU must show the orange pixel cat chasing and batting the moving blue ball. Press
Escape to exit. The checked evidence records two distinct QEMU frames, but makes no
claim about physical Dell execution.

## Prepare the physical candidate

```sh
python3 prepare_physical.py
```

This builds `/tmp/rabbit-scene-anima-v2-dell.img`, verifies it, and lists external
physical media read-only on macOS. It does not unmount or write a device. A fresh
exact-device review is still required before replacing the dedicated Rabbit USB image.

The exact image was subsequently written to the dedicated Rabbit USB. The owner booted
it on the Dell OptiPlex 3060 and confirmed that the orange cat and blue ball were both
visible and moving as in QEMU. The exact physical evidence is bound to all Creation,
trace, target, program, EFI, and image identities.

Current status:

```text
PHYSICAL-DELL-SCENE-ANIMA-V2-OBSERVED
```

Power-off or Escape is recovery. The next boundary is Rabbit God Runtime v1: preserve
this scene while accepting validated reusable Creation packages over a transactional
wireless transport.
