# Rabbit Stack agent instructions

Read `HANDOFF.md` before changing the project or continuing a lesson.

## Working principles

- The learner is Russian-speaking. Explain in Russian and introduce English terms
  alongside their meaning.
- Teach interactively: one small experiment at a time, ask for a prediction before
  execution, and explain the observed result afterward.
- Do not assume that pasted source code belongs in the shell. State explicitly when
  text must be entered in an editor and when a command must be run in the terminal.
- Keep the LLM outside the trusted computing base. Generated candidates must be
  accepted or rejected by deterministic checks.
- Every hypothesis needs a baseline, a falsifiable claim, and a reproducible test.
- Be precise about layers still present. QEMU bare-metal experiments remove the guest
  OS and firmware, not macOS, QEMU, or the physical Mac.
- Target `RV32I` first. Do not silently introduce `M`, `A`, `C`, floating point, an OS,
  or a runtime.
- Keep generated binaries out of Git. Store inspectable source bytes, manifests,
  contracts, and verifiers.
- Preserve learner-created work and unrelated changes.

## Hardware policy

No hardware is required for the current QEMU phase. The planned first physical target
is Raspberry Pi Pico 2 H (`SC1632`) in RISC-V mode with a Raspberry Pi Debug Probe
(`SC0889`). Do not recommend an FPGA purchase until a concrete RTL experiment works in
simulation and has a measurable hypothesis.
