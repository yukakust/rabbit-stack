# Research roadmap

## E0 — ARM64 baseline (complete)

Handwritten ARM64 assembly, native Mach-O build, exhaustive one-byte behavior test.

## E1 — Direct RV32I bytes in QEMU (current)

Run a 32-byte guest with no guest OS, firmware, assembler, or linker. Explain every
instruction and every external layer still involved.

## E2 — Intent and typed IR

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
