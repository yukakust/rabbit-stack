# Rabbit Stack handoff

Updated: 2026-09-21

## Mission

Build understanding from electrical state and machine instructions upward, while
testing whether a human can describe intent to an LLM and receive a machine image that
is safer and more explainable than ordinary vibe coding.

This is simultaneously:

1. an interactive computer-science course;
2. a sequence of reproducible systems experiments;
3. early research toward a verified LLM-to-hardware toolchain.

## Learner context

- Language: Russian.
- Host: Apple Silicon Mac (`arm64`) with zsh and Apple command-line tools.
- Preferred format: dialogue with a teacher, prediction questions, terminal work, and
  short explanations; no textbook prerequisite.
- The current fork is in builder mode: implement and verify the roadmap now; the
  step-by-step lesson continues separately later.
- Pace: roughly two hours per day when active.
- Prior work: basic C values, bytes, formatting, functions, conditions, branches,
  loops, exit statuses, compiler output, and introductory ARM64 assembly.

## Completed baseline

The ARM64 pill experiment implements this contract:

| Input | Output | Status |
|---|---|---:|
| `r` or `R` | `Wake up, Neo.` | 0 |
| `b` | `The story ends.` | 0 |
| any other byte or EOF | `Invalid choice.` | 2 |

It has been exhaustively checked for all 256 one-byte inputs plus EOF. Its source and
verifier are preserved in `experiments/arm64-pill/`.

What that experiment removed: C.

What it did not remove: assembler, linker, Mach-O, macOS, `getchar`, and `puts`.

## Decisions already made

- First clean target: **RV32I**, without optional `M` or compressed `C` instructions.
- First machine: QEMU `virt`, 32-bit RISC-V, with `-bios none`.
- First representation: explicit little-endian machine bytes, before introducing a
  reference assembler or linker.
- First physical target later: Raspberry Pi Pico 2 H / RP2350 Hazard3.
- FPGA comes only after a soft core or custom operation works in RTL simulation.
- LLVM MC, LLD, and mold are references and research subjects, not articles of faith.
- Every lowering step needs differential tests or another independent checker.
- The LLM may generate candidates, but it must not approve its own output.

## Current position

- E0 (native ARM64 baseline) is complete.
- E1 (direct RV32I bytes in QEMU) is complete.
- The learner manually changed `A` to `B`, predicted the exact byte change, and ran both
  the original verifier and the first deterministic `addi` encoder tests.
- W0 (patchable console world) is complete and starts E2 (intent and typed IR).
- W1 (a real typed module graph) is the next product milestone.

## Day 01 verified result

`hello.hex` contains eight 32-bit RV32I instruction words represented as 32 bytes in
little-endian order. When loaded at RAM address `0x80000000`, the program:

1. places the QEMU `virt` UART address `0x10000000` in register `t0`;
2. places ASCII `A` (`65`) in register `t1`;
3. stores that byte into the UART data register;
4. places the SiFive test-device address `0x00100000` in `t0`;
5. writes the success value `0x5555` there;
6. causes QEMU to exit successfully.

Expected observable contract:

```text
stdout: exactly A
exit status: 0
binary size: exactly 32 bytes
```

The experiment was independently reproduced with QEMU 10.2.1 before this handoff.

## W0 verified result

`experiments/rv32i-qemu/world-v0/` is the first complete vertical slice:

```text
typed world + typed patch
    -> strict validation and capability checks
    -> deterministic 32-byte RV32I image
    -> QEMU observation
    -> evidence report or rejection
```

The immutable base world declares `uart.write` and `machine.exit`, emits `A`, and exits
with status `0`. The `say-b` overlay changes only the UART module value to `66`. It does
not mutate the base and is bound to that exact base revision by its canonical manifest
hash. The resulting image differs only at offset `6`, `0x10 -> 0x20`. QEMU observes
exactly `A` for the base, exactly `B` for the overlay, empty stderr, and status `0` in
both cases. Removing the overlay rebuilds the byte-identical base image.

Run the complete positive and negative contract:

```sh
cd experiments/rv32i-qemu/world-v0
python3 verify.py
```

The verifier also rejects missing capabilities, unknown modules, out-of-range UART
values, dishonest output contracts, and undeclared patch fields.
It also rejects stale-base hashes, duplicate JSON fields, unsafe identifiers, and
evidence reports whose bytes were not built from the effective world.

This is a **cold patch** and a deliberately fixed lowering template. It is not yet a
general module system, a hot-patch runtime, an OS, physical RISC-V execution, or proof
that arbitrary generated code is safe.

## Immediate implementation sequence

1. Replace the fixed two-module arrangement with a typed module graph.
2. Give modules typed input/output ports, explicit dependencies, and resource budgets.
3. Let a patch add and connect one supported module without editing the runtime.
4. Add deterministic layout, symbols, labels, and fixups for the resulting graph.
5. Differentially check emitted instructions against LLVM MC or GNU `as`.
6. Enforce MMIO capabilities so a UART-only module cannot address another device.
7. Only then introduce transactional hot patches and state migration.

## Safety and honesty constraints

- Never call this literal bare metal on the physical Mac. It is bare-metal guest code
  inside an emulator hosted by macOS.
- Do not write OTP, enable irreversible secure boot, or disable debug on future RP2350
  hardware used for learning.
- Do not purchase new hardware merely to keep momentum; QEMU is the current target.
- Treat direct machine-code generation as unsafe until the verifier rejects malformed,
  out-of-policy, and non-terminating candidates.
- Record failures and counterexamples. They are evidence, not interruptions.

## Definition of the next milestone

W1 is complete only when:

- a world is a validated graph rather than a fixed list interpreted by special-case
  lowering code;
- ports and connections reject incompatible types;
- a patch can add and connect a supported module without modifying the runtime;
- resource and capability violations are rejected before image construction;
- the graph has a canonical representation, image, memory map, hash, and byte diff;
- baseline, patched result, invalid patches, and rollback all pass reproducibly.
