# Universal Rabbit roadmap — v3

## North star

Rabbit Stack explores a verifiable path from human intent to effects across different
computers and devices:

```text
human intent
    -> LLM-proposed universal world / patch
    -> deterministic validation and capability checks
    -> target selection and deterministic lowering
    -> hosted runtime, native boot, or device bridge
    -> measured result or rollback
```

The goal is **hardware-adaptive**, not hardware-blind. Hardware always matters: an
instruction set, memory budget, boot chain, display, sensor, actuator, and recovery path
are physical facts. Those facts belong in replaceable Target Packs rather than in the
portable world definition.

One world may therefore acquire different machine representations while preserving the
same observable contract:

```text
world: display.text("RABBIT")

Mac target       -> hosted window
phone target     -> sandboxed application view
old PC target    -> native framebuffer or serial console
board target     -> attached display driver
unsupported      -> explicit missing-capability rejection
```

Rabbit must never silently substitute a different physical effect. It may reject the
world or propose an explicit alternative for human approval.

## Architectural boundary

### Universal layer

The portable, target-independent layer contains:

- versioned world and patch schemas;
- module graph, typed ports, events, and dependencies;
- required capabilities and resource budgets;
- observable behavior contracts;
- canonical manifests, hashes, diffs, and rollback identity.

No ISA name, board name, boot protocol, driver register, MMIO address, or vendor SDK may
appear in this layer.

### Target Pack

A replaceable Target Pack contains:

- target identity and execution envelope;
- ISA, ABI, endianness, memory map, and resource limits;
- boot, loading, update, and recovery mechanisms;
- available device capabilities;
- instruction/image backend and device drivers;
- target-specific conformance tests.

The world hash is independent of the selected Target Pack. Build evidence identifies
and hashes both the world and target separately.

### Execution envelopes

Rabbit supports three honest ways to inhabit a device:

1. **Hosted** — inside an existing OS, application sandbox, or browser/runtime.
2. **Native** — Rabbit boots directly where the hardware and boot policy permit it.
3. **Bridge** — Rabbit controls another device through an explicit protocol such as
   USB, serial, network, Bluetooth, or a debug interface.

"Runs everywhere" means one portable world model with explicit target support and
capability negotiation. It does not mean bypassing locked boot chains, undocumented
hardware, physical limits, or owner policy.

## Product delivery track

### U0 — Verified vertical slice (complete)

The immutable `A` world and typed `A -> B` overlay lower to canonical 32-byte RV32I
images, run in QEMU, report exact hashes and byte diffs, reject malformed authority, and
roll back to the byte-identical base.

This proved the validation pattern, not portability: the original U0 world still
contained the target name `qemu-virt-rv32i`. U1 removed that coupling without changing
the resulting machine images.

### U1 — Separate world from target (complete)

Target identity is now outside the universal manifest:

```text
world.json
targets/qemu-rv32i.json
```

The Target Contract gives world, target, and built artifact separate canonical hashes.
The QEMU behavior, reviewed bytes, rollback, and negative validation tests are preserved.

### U2 — Two-backend portability proof (complete)

Run one unchanged world and patch through two substantially different backends:

- direct RV32I bytes in the QEMU bare-metal guest;
- an ARM64 hosted implementation on the Apple Silicon Mac.

Machine images differ while world identity and observable contract remain the same. The
combined verifier passes on the learner's Apple Silicon Mac and rejects cross-target and
stale-target evidence.

### U3 — Universal module graph (current: Mac confirmation pending)

Represent modules, typed ports, events, imports, dependencies, and resource budgets.
A patch must add and connect a supported module without editing the world runtime or
unrelated modules. The first demonstration extends `HI` to `HI!` on both backends.
Graph v1, its two revised Target Packs, deterministic lowerers, rollback, and negative
conformance suite are implemented. Completion awaits the combined verifier on the
learner's Apple Silicon Mac.

### U4 — Target Packs and capability negotiation

Define schemas and conformance suites for target resources and device capabilities.
Resolve portable capabilities such as `display.text`, `light.emit`, `storage.read`, or
`network.send` to explicit target drivers, or reject the deployment before building.

### U5 — Hosted, native, and bridge runners

Implement the three execution envelopes behind the same evidence contract. A runner
must expose its remaining software layers, authority, installation effects, and recovery
path rather than claiming universal bare metal.

### U6 — Hardware discovery and installation plan

Inspect a candidate device without mutating it. Select a compatible Target Pack and
produce a reviewable plan containing capabilities, missing support, writes, risks,
recovery steps, and expected observations. Installation remains a separate authorized
action.

### U7 — Physical conformance

Choose targets from available hardware using documented and recoverable boot paths.
Prove the same small world on at least two dissimilar physical targets over time. A
Raspberry Pi Pico 2, old PC, phone, or another board may participate, but none is a core
architectural dependency.

The current preferred first physical candidate is an available x86-64 UEFI computer
booted from removable USB, first reproduced under x86-64 QEMU. The experiment must not
write its internal disk or firmware; removing the USB device is the recovery path.

### U8 — Transactional patches

Apply cold, warm, and hot patches through prepare, validation, staging, health checks,
commit, and automatic rollback. State migration and unsupported transitions must be
explicit.

### U9 — Rabbit runtime and kernel

Add only the substrate required by native targets: traps, interrupts, memory,
scheduling, isolation, drivers, and module lifecycle. Hosted and bridge targets may use
their existing environments while preserving the same world contract.

### U10 — Universal installer

Given a world and a device, select among hosted, native, and bridge deployment; resolve
compatible Target Packs; refuse unsafe or unsupported operations; and preserve a tested
recovery route.

### U11 — LLM World Builder

Translate natural-language intent into candidate worlds and patches. The model may
propose new target support, but only deterministic validators and authorized installers
may approve builds or physical effects.

## Research track

### E0 — ARM64 baseline (complete)

Handwritten ARM64 assembly, native Mach-O build, exhaustive one-byte behavior test.

### E1 — Direct RV32I bytes in QEMU (complete)

Run a 32-byte guest with no guest OS, firmware, assembler, or linker. Explain every
instruction and every external layer still involved.

### E2 — Universal intent and Target Contract (current)

Separate portable behavior from target facts. Reject invalid capabilities, resources,
effects, target bindings, and stale revisions before encoding.

### E3 — Instruction encoders

Encode a small RV32I subset ourselves, round-trip decode it, and compare against an
independent reference. Add other ISAs only when demanded by a concrete second backend.

### E4 — Labels, symbols, and fixups

Resolve local control flow and imports. Make range, alignment, width, and relocation
failures explicit.

### E5 — Deterministic multi-backend builder

Lay out code and data, resolve typed imports, and emit a canonical artifact plus a
machine-readable memory/resource map for each Target Pack.

### E6 — Capability boundary

Demonstrate that a component permitted one effect cannot silently address another
device or request new host authority.

### E7 — Boot and deployment laboratory

Study hosted process loading, QEMU direct loading, PC boot protocols, mobile sandboxes,
microcontroller flash paths, and bridge protocols as separate adapters.

### E8 — Physical target comparison

Compare emulator and hardware observations on recoverable targets selected from actual
available inventory. Record every host tool, boot ROM, firmware, and physical adapter
still present.

### E9 — Toolchain and linker laboratory

Use LLVM MC, LLD, GNU tools, and mold as independent references and research subjects.
Measure compatibility, determinism, performance, and complexity rather than treating
any tool as an article of faith.

### E10 — RTL and FPGA

Simulate a RISC-V soft core and candidate custom operations before selecting or buying
an FPGA board. Keep this optional and evidence-driven.

## Hardware selection policy

- Prefer hardware already available to the project before buying anything.
- Never name one board or vendor in the universal schema.
- Require a documented loading path, an observable effect, and a tested recovery path.
- Do not write OTP, enable irreversible secure boot, disable debug, or make destructive
  firmware changes during research experiments.
- Test Target Packs against emulators, fixtures, or digital twins before physical writes.
- Treat phones and locked appliances as hosted or bridge targets unless their owner and
  boot policy explicitly allow native execution.

## Evidence and communication

Every result should preserve:

- the human intent, world, patch, and exact base revision;
- world, Target Pack, and artifact hashes;
- capability and resource decisions;
- deterministic build and byte-level evidence;
- expected and observed behavior;
- recovery or rollback evidence;
- a clear label: `PROVEN`, `PROPOSED`, or `UNSUPPORTED`.

The public story is: **one intent, many bodies, one verifiable meaning**.

## Definition of U3 completion

U3 is complete only when:

- a portable graph explicitly represents modules, typed ports, connections, events,
  imports or dependencies, and resource budgets;
- one base graph produces `HI` through both existing Target Packs;
- one patch adds and connects a punctuation module to produce `HI!` without changing
  either backend or unrelated modules;
- dangling connections, incompatible types, undeclared authority, stale revisions, and
  resource-budget overflow are rejected;
- removing the patch restores the exact base graph and observed behavior;
- both documented CLIs and the combined two-target conformance suite pass reproducibly.
