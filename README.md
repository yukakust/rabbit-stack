# Rabbit Stack

Rabbit Stack is a public learning and research project about a verifiable,
hardware-adaptive path from human intent to effects across computers and devices:

```text
human intent
    -> LLM candidate
    -> universal world / patch
    -> deterministic verifier and capability gate
    -> separately validated Target Pack
    -> target-specific artifact
    -> hosted runtime / native boot / device bridge
    -> observed result or rollback
```

The central hypothesis is that probabilistic interpretation can stop at a strict,
testable boundary. Below that boundary, every transformation should be deterministic,
inspectable, and independently checked. Worlds describe portable effects; replaceable
Target Packs contain ISA, boot, memory, driver, deployment, and recovery facts.

This repository starts much smaller than that final system. Its first job is to expose
every layer we would otherwise be tempted to hide.

## Current experiments

- [`experiments/arm64-pill`](experiments/arm64-pill): the working Apple Silicon ARM64
  baseline. It removes C but still uses the assembler, linker, macOS, and `libSystem`.
- [`experiments/rv32i-qemu/day-01`](experiments/rv32i-qemu/day-01): eight RV32I
  instruction words supplied directly as 32 machine-code bytes. There is no guest OS,
  firmware, compiler, assembler, or linker.
- [`experiments/rv32i-qemu/world-v0`](experiments/rv32i-qemu/world-v0): the first typed,
  patchable world. An immutable `A` world and an `A -> B` overlay lower to canonical
  RV32I images, run in QEMU, report their exact byte diff, and support rollback.

## Start here

Read [`HANDOFF.md`](HANDOFF.md), then run
[`experiments/rv32i-qemu/world-v0/README.md`](experiments/rv32i-qemu/world-v0/README.md).

The hardware-adaptive architecture and delivery sequence are in
[`docs/ROADMAP.md`](docs/ROADMAP.md). A short invitation for researchers and builders is
in [`docs/INVITATION.md`](docs/INVITATION.md).

## Project rule

```text
LLM proposes. Deterministic machinery decides. Evidence updates the plan.
```

One intent. Many bodies. One verifiable meaning.
