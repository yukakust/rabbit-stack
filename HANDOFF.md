# Rabbit Stack handoff

Updated: 2026-09-15

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

The next learner action is environment discovery on the Mac:

```sh
uname -m
command -v brew
command -v qemu-system-riscv32
```

If QEMU is absent:

```sh
brew install qemu
qemu-system-riscv32 --version
```

Then perform Day 01 in `experiments/rv32i-qemu/day-01/README.md`.

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

## Immediate teaching sequence

1. Establish the difference between host (`arm64`) and emulated target (`riscv32`).
2. Build `hello.bin` from visible bytes and run it.
3. Inspect the 32 bytes with `xxd`.
4. Decode one instruction at a time, starting with `addi`.
5. Change `A` to `B` by editing only the immediate field and predict the changed byte.
6. Write a tiny deterministic encoder for one instruction family.
7. Compare our encoding against LLVM MC or GNU `as`.
8. Add labels/fixups, then the smallest possible image builder.

Do not jump directly to a large language, MLIR, FPGA, or a universal linker. The first
research milestone is a tiny end-to-end slice whose every byte can be explained.

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

Milestone E1 is complete only when:

- the learner can explain why the host and target architectures differ;
- the 32-byte image prints `A` and exits with status 0;
- the verifier passes;
- changing the intended character produces a predicted byte-level change;
- the result is reproducible from a fresh clone using documented commands.
