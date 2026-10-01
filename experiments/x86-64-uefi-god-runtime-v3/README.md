# Detailed mouse / Graphics Runtime v3 candidate

Status: 10 host Python/C tests PASS, repeat UEFI builds match, Linux QEMU exact
missing-device gate observed. **Not physically installed.** Mac sender compilation,
physical BLE checkpoints and detailed Dell graphics remain untested. Working v2 stays
unchanged. The source PNG, exact imagegen prompt, source hash and importer recipe are
under `assets/`; art is data, never baked into EFI.

## Graphics boundary

256 RGBA palette entries (slot zero transparent), indexed8 RLE sprites up to 128x128,
up to 16 frames/sprite. Source geometry is separate from display geometry (1..64 logical
pixels/axis). The scene remains 160x90, displayed in a bounded 480x270 region. Alpha
blending, nearest sampling, a 262144 decoded-pixel ceiling, and a 65535-byte signed
package ceiling replace v2's 16 colors / 16x16 / 4096 bytes. The VM, Ed25519,
staging/active RAM, health-before-commit and retain-old-world boundaries are unchanged.
Exact legacy v2 packets are accepted by v3 without re-encoding.

The first detailed mouse has one 128x128 artwork frame, displayed at 96x96 physical
pixels. The existing VM moves it; a full anatomical walk cycle is not claimed.
The cat stays the old sprite. Native plugins, active scan, pairing, connections,
internal disk/firmware writes remain forbidden; worlds are volatile across reboot.

## Preview (commands in Mac terminal)

```sh
cd ~/rabbit-stack/experiments/x86-64-uefi-god-runtime-v3
python3 preview_world.py worlds/cat-chases-smooth-mouse.json --output runs/mouse-preview.html
open runs/mouse-preview.html
```

The HTML displays exact decoded package pixels in a static canvas, not physical
evidence or VM execution. Host tests separately run the actual freestanding C renderer
and VM for 240 ticks into a guarded framebuffer (`runs/mouse-c-frame.ppm`).

To preserve the currently pink cat, optionally import against your last world:

```sh
python3 import_mouse.py \
  --base ../x86-64-uefi-god-runtime-v2/runs/world-k0356k50/world.json \
  --output runs/my-smooth-mouse.json
python3 preview_world.py runs/my-smooth-mouse.json --output runs/my-preview.html
open runs/my-preview.html
```

Optional PNG import requires Pillow (install in a local venv); preview/compile/build
use the existing cryptography dependency without Pillow. The importer preserves cat
palette/pixels/programs, replaces mouse art with brown PNG colors rather than previous
flat green, increases its display size and relocates it inside the scene. Resource
license and Inventory v1 catalog registration are not inferred; owner review is needed
before publishing it as a licensed shared component.

## Transport limitations and retries

The reference is 8979 signed bytes / 1499 ordinary frames. Six payload bytes and 450ms
repeat time per advertisement make this about **13 minutes without losses**, including
checkpoints. This is a calculated duration, not measured real throughput. Each block
of 32 chunks has a prefix-hash receipt; lost blocks retry locally without resetting
staging. Lost final ACKs repeat without reapplying. Prefix receipts acknowledge staging
only, not signature verification or world activation. They are unauthenticated like
the old final ACK; they can be spoofed, but signature/bounds/health still reject an
incomplete/invalid world. Development-key and ACK authentication debts remain.

The sender reads a JSON frame bundle from a file to avoid macOS argument-length limits.
Do not use the block sender against an old v2 runtime, even for a legacy-format world:
the old receiver cannot produce checkpoint receipts. Faster transport is subsequent
work; no live reliability improvement is claimed by host tests.

## QEMU and physical gates

```sh
python3 verify.py
python3 run_qemu.py
```

Mac QEMU must visibly show `RABBIT GOD RUNTIME v3.0`, then
`TARGET NOT FOUND; NO DEVICE WRITE SENT` and no-reset/no-HCI/no-radio cleanup.
QEMU lacks the physical controller, so this cannot test real BLE/graphics. Linux
evidence binds source/runtime/target and exact EFI/image/screenshot; different Mac
toolchains may produce different deterministic EFI bytes. The exact Mac artifact
must be QEMU-observed before physical installation.

Then `python3 prepare_physical.py` builds a temporary image/report and only lists
external media; it never unmounts, erases or writes a device. Fresh USB identity and
owner approval are required before one runtime replacement. Keep v2 for rollback.
Moving/writing USB once is necessary for this graphics-format upgrade.

After approved v3 installation, test the small old world first:

```sh
python3 send_package.py ../x86-64-uefi-god-runtime-v2/worlds/cat-chases-mouse.json --counter 1
```

Then send the detailed world without moving USB again:

```sh
python3 send_package.py worlds/cat-chases-smooth-mouse.json --counter 2
```

Use a higher counter than the last accepted in this boot. Expected: `BLOCK RECEIVED`
progress, final correlated `ACK RECEIVED`, and visibly detailed mouse; the old world
continues during staging. The existing `ask_world.py` still emits v2 JSON. Codex edits
of v3 worlds via asset references, authored walk cycles and faster delivery remain next
work, not completed features.
