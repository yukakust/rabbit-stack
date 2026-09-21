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
- Keep universal worlds independent of ISA, board, boot protocol, MMIO addresses, and
  vendor SDKs. Put those facts in separately validated Target Packs.
- Every hypothesis needs a baseline, a falsifiable claim, and a reproducible test.
- Be precise about layers still present. QEMU bare-metal experiments remove the guest
  OS and firmware, not macOS, QEMU, or the physical Mac.
- Keep `RV32I` as the first backend. Do not silently introduce `M`, `A`, `C`, floating
  point, an OS, or a runtime. Add another ISA only for a concrete portability test.
- Keep generated binaries out of Git. Store inspectable source bytes, manifests,
  contracts, and verifiers.
- Preserve learner-created work and unrelated changes.

## Hardware policy

No hardware purchase is required for the current phase. Select physical targets from
available inventory only after the portable World Contract and Target Pack boundary are
tested. A Raspberry Pi, old PC, phone, microcontroller, or appliance may become a target,
but none is an architectural dependency.

Require documented loading, observable behavior, and recovery before physical writes.
Do not write OTP, enable irreversible secure boot, disable debug, or make destructive
firmware changes during learning. Do not recommend an FPGA purchase until a concrete RTL
experiment works in simulation and has a measurable hypothesis.
