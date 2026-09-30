# Rabbit God Runtime v2 — one runtime, wireless worlds

This experiment moves the extensibility boundary from firmware code to a bounded,
signed data package. The removable USB contains one x86-64 UEFI Runtime. Ordinary
world changes then arrive over passive BLE and live in RAM; they do not replace the
UEFI image.

## What a package may contain

- up to 16 RGB palette entries;
- up to 16 indexed sprites, each up to 16x16 pixels and 16 animation frames;
- up to 16 live objects;
- up to 16 Rabbit VM programs with 32 bytes per program;
- movement, edge bounce, chase, flee, animation, and bounded collision impulse;
- initial positions, velocities, targets, and a 160x90 logical scene.

The complete signed package is limited to 4096 bytes. It contains data and reviewed VM
instructions, never native x86 code. The Dell stages the entire package in RAM, checks
frame order and checksums, verifies the trusted Creator's Ed25519 signature, validates
all references and budgets, performs one health step, and only then replaces the active
world. Rejection or failed health leaves the previous world active. A successful commit
produces the existing bounded BLE ACK.

Transport v2 uses a 16-bit chunk sequence and six payload bytes per BLE UUID frame. It
therefore supports 4096-byte packages and is no longer limited by the old 255-frame
ceiling. It is deliberately slow and correctness-first; a connected or Wi-Fi transport
can later carry the same package contract faster.

## Verify and emulate

```sh
cd ~/rabbit-stack/experiments/x86-64-uefi-god-runtime-v2
python3 verify.py
python3 run_qemu.py
```

QEMU must show `RABBIT GOD RUNTIME v2.0` and fail closed because it has no Dell
`0CF3:E009` controller.

The verifier accepts fail-closed evidence bound to the exact generated source,
Runtime core, and Target Pack. EFI and disk-image hashes may legitimately differ
between the Linux and macOS cross-toolchains; each host build must still be
deterministic, and its own hashes are printed for physical review.

## Prepare, but do not write, the physical candidate

```sh
python3 prepare_physical.py
```

The command validates everything, creates the image in the host temporary directory,
lists removable physical media, and stops before any device write.

## Send a complete new world after the Dell boots v2

```sh
python3 send_package.py worlds/cat-chases-mouse.json --counter 1
```

Edit or generate another strict world JSON, increase `--counter`, and run the same
command. No USB movement or Dell reboot is required. A power cycle clears received
worlds because this version intentionally performs no persistent write; resend the
desired world after boot.

## Honest boundary

“One final image” means no reflashing for new worlds expressible by this package ABI.
Adding a new hardware driver, cryptographic primitive, VM opcode, larger budget, or a
fix to the Runtime itself remains a Runtime upgrade. This is the same stable-kernel /
dynamic-program boundary used by mature systems, made explicit and testable here.
