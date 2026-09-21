# Rabbit World v0 — patchable console

World v0 is the first vertical slice from a typed world and patch to measured machine
behavior. It deliberately supports only two module types:

- `uart-byte`, requiring the `uart.write` capability;
- `successful-exit`, requiring the `machine.exit` capability.

The immutable base world emits `A`. `patches/say-b.json` is an overlay that changes the
UART module value to ASCII `B` and replaces the expected contract. Its `base_hash`
binds it to the exact canonical base manifest, not merely a world with the same name.
The tool validates the world and patch, builds a canonical 32-byte RV32I image, runs it
in QEMU, and reports the world hashes, image hash, and exact byte diff.

Run from this directory:

```sh
python3 rabbit_world.py world.json
python3 rabbit_world.py world.json --patch patches/say-b.json
python3 verify.py
```

Optional inspectable outputs must be written outside the repository or kept untracked:

```sh
python3 rabbit_world.py world.json \
  --patch patches/say-b.json \
  --output /tmp/rabbit-world-b.bin \
  --report /tmp/rabbit-world-b-report.json
```

This first patch is **cold**: the image is rebuilt and QEMU is restarted. The base JSON
is never mutated, so removing the overlay is the v0 rollback mechanism. Hot patching,
module state migration, and runtime module loading belong to later milestones.

## What this establishes

- Intent (`world.json`) and change (`patches/say-b.json`) are data, not hidden inside
  the instruction bytes.
- A patch cannot name an unknown module, add an unreviewed field, or use authority the
  base world did not declare.
- A patch for an older or otherwise different base revision is rejected even when the
  `world_id` is unchanged.
- The same valid input always produces the same image and SHA-256 hash.
- `A -> B` changes exactly image offset `6` from `0x10` to `0x20`.
- QEMU observes the declared output and exit status; rebuilding without the overlay
  returns to the byte-identical `A` image.

World v0 is not yet a general compiler, operating system, hot-patch runtime, or physical
hardware result. Its two module types lower through a deliberately fixed, reviewed
32-byte template. The next milestone replaces that fixed arrangement with a typed module
graph while preserving the same validation, evidence, and rollback rules.
