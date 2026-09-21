# Research roadmap

## North star — a patchable world machine

Rabbit Stack aims to let a person describe a world or a change in ordinary language
while retaining an inspectable path to physical effects:

```text
human intent
    -> LLM-proposed typed world / patch
    -> deterministic validation and capability checks
    -> canonical lowering and image construction
    -> emulator, then physical hardware
    -> measured result or rollback
```

The system is not a one-shot image generator. A world is a versioned graph of modules
and device capabilities. A patch is a typed, reviewable overlay that can add, replace,
connect, or reconfigure modules without silently gaining new authority. Every accepted
patch must identify the exact base revision by canonical hash, declare its expected
contract, produce a byte-level diff and canonical hash, and preserve a recovery path.

The long-term physical limit is the attached compute, memory, power, sensors,
actuators, displays, networks, and reconfigurable logic. A device without a programmable
interface requires a physical adapter and a driver module before it can participate in
the world.

## Product delivery track

### W0 — Patchable console world (complete)

Create an immutable `A` world and a typed `A -> B` overlay. Validate capabilities,
compile a canonical 32-byte RV32I image, execute it in QEMU, report the changed byte and
image hash, and demonstrate rollback by building the untouched base again. W0 uses a
cold patch: each variant is rebuilt and restarted.

### W1 — Module graph (next)

Represent modules, typed ports, events, dependencies, imports, and resource budgets.
Adding a module must not require editing the world runtime or unrelated modules.

### W2 — Transactional runtime patches

Apply hot and warm patches with quiescence, state migration, health checks, commit, and
automatic rollback. Classify changes that require reboot or reflashing explicitly.

### W3 — Device contracts

Define drivers as capability-bearing modules for UART, GPIO, timers, displays, phones,
appliances, and other attached devices. Test drivers against simulators or digital twins
before physical writes.

### W4 — Rabbit kernel

Add traps, interrupts, allocation, scheduling, isolation, and module lifecycle support.
The kernel becomes the minimal, owned substrate on which larger generated worlds run.

### W5 — Physical bridge

Run the same typed world and patch model on RP2350/Hazard3. Begin with reversible GPIO
or LED behavior, preserve debug access, and compare emulator and hardware observations.

### W6 — World builder

Connect the LLM interface to the typed module and patch language. Natural-language
requests may propose new worlds and devices, but only deterministic checks may authorize
builds and physical effects.

## E0 — ARM64 baseline (complete)

Handwritten ARM64 assembly, native Mach-O build, exhaustive one-byte behavior test.

## E1 — Direct RV32I bytes in QEMU (complete)

Run a 32-byte guest with no guest OS, firmware, assembler, or linker. Explain every
instruction and every external layer still involved.

## E2 — Intent and typed IR (current)

Represent a tiny behavior contract separately from its implementation. Reject invalid
states, widths, effects, and resources before encoding.

## E3 — Instruction encoder

Encode a small RV32I subset ourselves. Round-trip decode it and compare every result
against an independent reference such as LLVM MC.

## E4 — Labels and fixups

Resolve local control-flow targets. Make range and alignment failures explicit.

## E5 — Deterministic image builder

Combine two modules, lay out code/data, resolve typed imports, and emit a canonical
image plus a machine-readable memory map.

## E6 — Capability boundary

Demonstrate that a component permitted to write UART cannot silently gain access to a
different MMIO region.

## E7 — Linker laboratory

Dissect LLD and mold: parsing, symbol resolution, layout, relocations, compatibility
cost, parallelism, and reproducible benchmarks.

## E8 — Physical RP2350 target

Run the verified image on Pico 2 H in Hazard3 RISC-V mode. Inspect registers and memory
through the Debug Probe.

## E9 — RTL and FPGA

Simulate a RISC-V soft core and one candidate custom operation. Measure correctness,
cycles, area, and maximum frequency before selecting or buying an FPGA board.
