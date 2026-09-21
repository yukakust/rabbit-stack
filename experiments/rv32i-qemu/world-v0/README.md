# Rabbit World v0 — portable console plus Target Pack

World v0 is the first vertical slice from a portable typed world and patch, through a
separately validated Target Pack, to measured machine behavior. It deliberately supports
only two module types:

- `uart-byte`, requiring the `uart.write` capability;
- `successful-exit`, requiring the `machine.exit` capability.

`world.json` contains no ISA, machine, address, byte order, boot, or runner field. The
separate `targets/qemu-rv32i.json` Target Pack supplies RV32I, little-endian memory,
image loading, UART and exit-device bindings, and QEMU execution facts.

The immutable base world emits `A`. `patches/say-b.json` is an overlay that changes the
UART module value to ASCII `B` and replaces the expected contract. Its `base_hash` binds
it to the exact canonical world revision. The tool validates and hashes the world and
Target Pack independently, builds the canonical 32-byte image, runs it in QEMU, and
reports exact evidence and byte diff.

Run from this directory:

```sh
python3 rabbit_world.py world.json --target targets/qemu-rv32i.json
python3 rabbit_world.py world.json \
  --target targets/qemu-rv32i.json \
  --patch patches/say-b.json
python3 verify.py
```

Optional inspectable outputs must be written outside the repository or kept untracked:

```sh
python3 rabbit_world.py world.json \
  --target targets/qemu-rv32i.json \
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
- Target facts live only in `targets/qemu-rv32i.json`; changing a Target Pack does not
  change portable world identity.
- World, Target Pack, and machine image have independent SHA-256 identities.
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
32-byte RV32I backend. The next milestone adds an ARM64 hosted Target Pack and backend
for the first one-world/two-backend portability proof.
