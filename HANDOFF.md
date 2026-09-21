# Rabbit Stack handoff

Updated: 2026-09-21

## Mission

Build understanding from electrical state and machine instructions upward, while
testing whether a human can describe intent to an LLM and receive a portable world that
can be lowered into safer, explainable effects across different computers and devices.

This is simultaneously:

1. an interactive computer-science course;
2. a sequence of reproducible systems experiments;
3. early research toward a verified, hardware-adaptive LLM-to-world toolchain.

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
- Universal worlds must not contain an ISA, board, boot protocol, driver address, or
  vendor SDK. Those facts belong in separately validated Target Packs.
- Support three execution envelopes: hosted, native, and bridge.
- Select future physical targets from actual available inventory by documentation,
  observability, and recoverability; Raspberry Pi is optional, not foundational.
- The preferred first physical candidate is an available x86-64 UEFI computer booted
  from removable USB after the same target works in QEMU; never write its internal disk
  or firmware.
- FPGA comes only after a soft core or custom operation works in RTL simulation.
- LLVM MC, LLD, and mold are references and research subjects, not articles of faith.
- Every lowering step needs differential tests or another independent checker.
- The LLM may generate candidates, but it must not approve its own output.

## Current position

- E0 (native ARM64 baseline) is complete.
- E1 (direct RV32I bytes in QEMU) is complete.
- The learner manually changed `A` to `B`, predicted the exact byte change, and ran both
  the original verifier and the first deterministic `addi` encoder tests.
- U0 (the target-coupled patchable console world) is complete.
- U1 is complete: the portable world no longer contains a target field, while the QEMU
  RV32I Target Pack owns ISA, memory, device, image, and runner facts. The complete suite
  passes in both development environments.
- The architecture has changed from a Pico-oriented path to Universal Rabbit: portable
  worlds plus replaceable Target Packs.
- U2 is complete: one unchanged world and patch lower through QEMU RV32I and hosted
  Darwin ARM64 Target Packs, and the complete two-backend contract passes on the
  learner's Apple Silicon Mac.
- U3 is complete: graph v1 emits `HI`, and an immutable patch adds and connects
  punctuation to emit `HI!` through both QEMU RV32I and hosted Darwin ARM64.
- U4 is complete: semantic `display.text` resolves to QEMU UART or Darwin stdout through
  canonical deployment plans, and the combined capability contract passes on the
  learner's Apple Silicon Mac.
- U5 (hosted, native, and bridge runner contracts) is the next milestone.
- E2 now covers universal intent and the Target Contract boundary.

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

## U0 verified result

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

## U1 verified result

`world.json` and `targets/qemu-rv32i.json` now have independent canonical identities.
The builder derives UART address, exit-device address/value, byte order, image size, and
runner configuration from the Target Pack. Despite removing the target from the world,
the baseline and patched RV32I artifacts remain byte-identical to U0 and Day 01.

The verifier rejects target fields in portable worlds, malformed or incomplete Target
Packs, unsupported backends, stale target/artifact combinations, and evidence not bound
to the exact world and target revisions.

The full contract passed under QEMU 10.2.1 in the development environment and under
QEMU 11.1.1 on the learner's Apple Silicon Mac. Both reproduced the same world, target,
and machine-image identities.

## U2 verified result

The unchanged portable world and `say-b` patch now lower to two distinct artifacts:
the reviewed 32-byte RV32I image and deterministic Darwin ARM64 assembly. QEMU executes
the first as a bare-metal guest; Apple `clang` links the second into a temporary Mach-O
process that runs on the Mac's physical ARM64 processor. Both observe exactly `A` for
the base, `B` for the overlay, empty stderr, and status `0`.

World identity remains shared while Target Pack and artifact identities differ. Evidence
is bound to the exact Target Pack and artifact hashes, so QEMU evidence, stale target
evidence, and unsupported hosted bindings are rejected.

Two failed Mac runs became regression cases: a cold `clang` startup exposed the need for
separate compile and execution timeouts, and an infinite return loop exposed a missing
ARM64 `x30` save around `bl _write`. The backend now preserves `x29/x30`, compilation
gets a bounded 30 seconds, and the resulting program still must finish within 3 seconds.

## U3 verified result

`experiments/universal-graph-v1/` introduces explicit versioned imports and dependencies,
capabilities, resource budgets, modules, typed port endpoints, event connections, and an
observable contract. The deliberately linear base graph derives `HI` by traversing
`start -> letter-h -> letter-i -> exit`.

`patches/add-bang.json` is bound to the exact base graph hash. It adds only a punctuation
module, removes the final `letter-i -> exit` edge, and inserts punctuation between them.
It cannot request a backend edit or change resource authority. The same lowerers build a
40-byte RV32I base artifact, a 48-byte patched artifact, and distinct Darwin ARM64 source
artifacts. QEMU has observed exactly `HI` and `HI!` with status `0`.

The verifier rejects dangling and unknown ports, byte-to-event type mismatches, cycles,
missing authority, module/output budget overflow, stale patches and targets, backend-edit
fields, ambiguous JSON, and cross-target evidence. Removing the patch restores the exact
base graph, artifact, and output.

The complete suite passed on the learner's Apple Silicon Mac. QEMU RV32I and hosted
ARM64 both observed exactly `HI` and patched `HI!` with empty stderr and status `0`,
while sharing graph identity and retaining separate target and artifact identities.

## U4 verified result

`experiments/capability-negotiation-v1/` removes target-shaped `console.write` from the
portable world. It requests versioned `display.text` and `machine.exit` semantics with
constraints and also requests optional `light.emit`. Target Packs separately advertise
reviewed offers, limits, concrete bindings, authority effects, and remaining layers.

The deterministic resolver binds `display.text` to `qemu-virt-uart` on RV32I and to
`darwin-posix-write` on hosted ARM64. Because neither target offers a light, both plans
record optional `light.emit` as `not-offered`; making it required rejects deployment
before artifact construction. A reviewed adapter feeds the plan into the unchanged U3
backends. QEMU observes the original `HI` and patched `HI!` contracts.

World, target, plan, and artifact identities are independently bound into evidence. The
verifier rejects incompatible capability versions, target-limit violations, hidden
drivers, undeclared authority effects, stale and cross-target plans, substituted drivers,
stale Target Packs, and evidence from another plan.

The complete suite passed on the learner's Apple Silicon Mac. QEMU UART and Darwin POSIX
stdout both observed the unchanged semantic contracts `HI` and patched `HI!`; optional
`light.emit` was explicitly omitted, while required `light.emit` rejected deployment
before artifact construction.

## Immediate implementation sequence

1. Define one Runner Contract that explicitly labels the execution envelope, command or
   protocol, authority, remaining layers, mutations, timeouts, and recovery path.
2. Migrate the proven hosted Darwin and native QEMU execution behind that contract
   without changing semantic worlds or deployment plans.
3. Add a deterministic simulated bridge target using an explicit framed protocol to a
   separate child process; label it simulation, not physical hardware.
4. Observe `HI/HI!` through all three envelopes and bind runner identity and protocol
   transcript into evidence.
5. Reject mislabeled envelopes, undocumented effects or writes, protocol mismatch,
   stale/replayed transcripts, timeout, and missing recovery information.

## Safety and honesty constraints

- Never call this literal bare metal on the physical Mac. It is bare-metal guest code
  inside an emulator hosted by macOS.
- Do not write OTP, enable irreversible secure boot, or disable debug on hardware used
  for learning.
- Do not purchase new hardware merely to keep momentum. Prefer available inventory and
  require a reviewed Target Pack and recovery path before physical writes.
- Treat direct machine-code generation as unsafe until the verifier rejects malformed,
  out-of-policy, and non-terminating candidates.
- Record failures and counterexamples. They are evidence, not interruptions.

## Definition of the next milestone

U5 is complete only when:

- hosted, native, and simulated bridge execution implement one explicit Runner Contract;
- each runner declares remaining layers, authority, mutations, timeouts, and recovery;
- one unchanged semantic world and patch observe `HI/HI!` through all three envelopes;
- bridge communication uses a deterministic framed protocol with transcript evidence;
- runner, plan, artifact, and transcript identities are bound into the final report;
- mislabeled envelopes, hidden writes/effects, protocol violations, replay, timeout, and
  missing recovery information are rejected;
- the combined three-envelope conformance suite passes reproducibly.
