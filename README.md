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
  patchable, target-independent world. A separate QEMU RV32I Target Pack lowers the
  immutable `A` world and `A -> B` overlay to canonical images, reports their exact
  identities and byte diff, and supports rollback.
- [`experiments/universal-graph-v1`](experiments/universal-graph-v1): the first portable
  typed module graph. One immutable patch adds and connects a punctuation module,
  changing `HI` to `HI!` through the RV32I and hosted ARM64 targets without backend edits.
- [`experiments/capability-negotiation-v1`](experiments/capability-negotiation-v1): a
  deterministic resolver that turns semantic requests such as `display.text` into
  reviewed, plan-bound QEMU UART or Darwin stdout drivers—or rejects deployment.
- [`experiments/runner-contract-v1`](experiments/runner-contract-v1): one explicit
  execution contract for native QEMU, hosted Darwin, and a framed simulated bridge with
  transcript-bound evidence and recovery declarations.
- [`experiments/hardware-discovery-v1`](experiments/hardware-discovery-v1): strict
  read-only inventory matching and a non-executable, removable-USB-only installation
  proposal, including the real read-only Dell OptiPlex 3060 firmware inventory.
- [`experiments/x86-64-uefi-v0`](experiments/x86-64-uefi-v0): the unchanged semantic
  `HI` world lowered into deterministic PE32+/FAT32 UEFI images, physically patched to
  `HI!`, and rolled back to exact `HI` on the Dell.
- [`experiments/x86-64-uefi-framebuffer-v0`](experiments/x86-64-uefi-framebuffer-v0):
  the first semantic color object lowered to reviewed x86-64 instructions that obtain
  the UEFI GOP framebuffer and write pixels directly, observed in QEMU and on the Dell.
- [`experiments/x86-64-uefi-interactive-v0`](experiments/x86-64-uefi-interactive-v0):
  the first keyboard-controlled world candidate: arrow keys update persistent position,
  erase the old rectangle, clamp it to the screen, and draw the next framebuffer frame.
- [`experiments/x86-64-uefi-jump-stone-v0`](experiments/x86-64-uefi-jump-stone-v0):
  the first natural-language-requested world: a yellow player jumps on Space, leaves a
  solid stone on `Z`, moves away, collides with it, and can route around it.
- [`experiments/world-package-v0`](experiments/world-package-v0): the same owner-approved
  world compiled into a 1,060-byte target-independent `.rabbit` package. It binds the
  Russian intent interpretation and semantic world without embedding x86, UEFI, QEMU,
  framebuffer, firmware, USB, or Dell facts.
- [`experiments/x86-64-uefi-network-probe-v0`](experiments/x86-64-uefi-network-probe-v0):
  a read-only boot probe for selecting the Dell's real Wi-Fi path. It reports standardized
  UEFI network/Wi-Fi protocol availability and exact PCI network-controller identities
  without transmitting packets or changing device configuration.
- [`experiments/x86-64-uefi-bluetooth-probe-v0`](experiments/x86-64-uefi-bluetooth-probe-v0):
  a bounded read-only UEFI USB descriptor inventory that identifies standard Bluetooth
  class candidates without HCI commands, pairing, radio traffic, reset, or configuration.
- [`experiments/x86-64-uefi-bluetooth-hci-identity-v0`](experiments/x86-64-uefi-bluetooth-hci-identity-v0):
  the next bounded boundary: one local informational HCI command to exact USB
  `0CF3:E009`, with no scan, advertising, pairing, connection, firmware download, or
  radio-data authority.
- [`experiments/x86-64-uefi-bluetooth-local-capabilities-v0`](experiments/x86-64-uefi-bluetooth-local-capabilities-v0):
  one bounded boot queries the controller's supported-command, BR/EDR-feature, and
  BLE-feature maps without reset, discovery, connection, or radio traffic.
- [`experiments/x86-64-uefi-bluetooth-beacon-rx-v0`](experiments/x86-64-uefi-bluetooth-beacon-rx-v0):
  the first intentional radio boundary: a reviewed Mac CoreBluetooth beacon and a
  20-second receive-only Dell passive scan match one exact Rabbit service UUID without
  active scanning, pairing, connection, or radio transmission from the Dell.
- [`experiments/x86-64-uefi-qca-status-v0`](experiments/x86-64-uefi-qca-status-v0):
  two read-only Qualcomm vendor-IN queries expose ROM/patch/RAM identity and the
  `PATCH_UPDATED`/`SYSCFG_UPDATED` setup bits without firmware download, reset, HCI,
  or radio authority.
- [`experiments/x86-64-uefi-qca-ram-load-v0`](experiments/x86-64-uefi-qca-ram-load-v0):
  exact hash-pinned Rome 3.2 rampatch and NVM payloads are bounded to volatile
  controller RAM; post-load status is observed without reset, HCI, or radio activity.

## Start here

Read [`HANDOFF.md`](HANDOFF.md), then continue with
[`experiments/x86-64-uefi-bluetooth-probe-v0/README.md`](experiments/x86-64-uefi-bluetooth-probe-v0/README.md).
The active next gate is
[`experiments/x86-64-uefi-qca-ram-load-v0/README.md`](experiments/x86-64-uefi-qca-ram-load-v0/README.md).

The hardware-adaptive architecture and delivery sequence are in
[`docs/ROADMAP.md`](docs/ROADMAP.md). A short invitation for researchers and builders is
in [`docs/INVITATION.md`](docs/INVITATION.md).

## Project rule

```text
LLM proposes. Deterministic machinery decides. Evidence updates the plan.
```

One intent. Many bodies. One verifiable meaning.
