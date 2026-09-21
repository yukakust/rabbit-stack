# Rabbit Stack

Rabbit Stack is a learning and research project about a verifiable path from human
intent to hardware:

```text
human intent
    -> LLM candidate
    -> typed intent IR
    -> deterministic verifier
    -> instruction encoder
    -> image builder
    -> emulator / hardware
```

The central hypothesis is that probabilistic interpretation can stop at a strict,
testable boundary. Below that boundary, every transformation should be deterministic,
inspectable, and independently checked.

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

The working architecture and experiment map lives on the private Miro board:
[Rabbit Stack board](https://miro.com/app/board/uXjVHnNnOoY=/).

## Project rule

```text
LLM proposes. Deterministic machinery decides. Evidence updates the plan.
```
