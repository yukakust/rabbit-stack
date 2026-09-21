# Rabbit World v0 — portable console plus Target Pack

World v0 is the first vertical slice from a portable typed world and patch, through a
separately validated Target Pack, to measured machine behavior. It deliberately supports
only two module types:

- `uart-byte`, requiring the `uart.write` capability;
- `successful-exit`, requiring the `machine.exit` capability.

`world.json` contains no ISA, machine, address, byte order, boot, or runner field. The
Target Packs supply those facts separately:

- `targets/qemu-rv32i.json` builds the reviewed 32-byte bare-metal guest image and
  runs it in QEMU;
- `targets/hosted-arm64.json` builds deterministic Darwin ARM64 assembly, compiles a
  temporary Mach-O with Apple `clang`, and runs it as a macOS process.

The immutable base world emits `A`. `patches/say-b.json` is an overlay that changes the
UART module value to ASCII `B` and replaces the expected contract. Its `base_hash` binds
it to the exact canonical world revision. The tool validates and hashes the world and
Target Pack independently, builds the canonical 32-byte image, runs it in QEMU, and
reports exact evidence and byte diff.

Both targets consume the exact same `world.json` and `patches/say-b.json`. The hosted
target maps the v0 `uart.write` intent to POSIX standard output; the capability keeps
its historical name until the universal module graph generalizes it in U3.
Compilation and execution have separate limits: a cold Apple toolchain gets up to 30
seconds, while the resulting one-byte program must still finish within 3 seconds.

Run from this directory:

```sh
python3 rabbit_world.py world.json --target targets/qemu-rv32i.json
python3 rabbit_world.py world.json \
  --target targets/qemu-rv32i.json \
  --patch patches/say-b.json
python3 rabbit_world.py world.json \
  --target targets/hosted-arm64.json \
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
- Target facts live only in `targets/*.json`; changing or replacing a Target Pack does
  not change portable world identity.
- World, Target Pack, and machine image have independent SHA-256 identities.
- A patch cannot name an unknown module, add an unreviewed field, or use authority the
  base world did not declare.
- A patch for an older or otherwise different base revision is rejected even when the
  `world_id` is unchanged.
- The same valid input always produces the same image and SHA-256 hash.
- `A -> B` changes exactly image offset `6` from `0x10` to `0x20`.
- QEMU observes the declared output and exit status; rebuilding without the overlay
  returns to the byte-identical `A` image.

World v0 is not yet a general compiler, operating system, hot-patch runtime, or direct
physical-hardware result. Its two module types lower through deliberately fixed RV32I
and Darwin ARM64 templates. The ARM64 path still includes Python, Apple `clang`, the
Mach-O linker, macOS, libc, and the physical Apple Silicon processor.

On an Apple Silicon Mac, `python3 verify.py` runs the complete two-backend conformance
suite. On another development host it verifies both deterministic artifacts and all
RV32I behavior, but prints `SKIP` for the ARM64 execution that host cannot perform.

## Verified environments

- QEMU 10.2.1 in the development environment;
- QEMU 11.1.1 on the learner's Apple Silicon Mac.

Both environments reproduced the same portable world hash, Target Pack hash, baseline
and patched image hashes, observed output, rejection cases, and rollback result.
