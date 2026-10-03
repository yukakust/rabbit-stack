# Rabbit Stack handoff

Updated: 2026-10-01

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
- U5 is complete: hosted Darwin ARM64, native QEMU RV32I, and a simulated framed bridge
  run the unchanged U4 world and patch through one Runner Contract on the learner's Mac.
- U6 is complete: simulated fixtures and a real read-only Dell OptiPlex 3060 firmware
  inventory pass validation. The real snapshot is honestly `UNSUPPORTED` by the v0
  target because Secure Boot is enabled and no removable device was present during
  discovery; no firmware setting or storage was changed.
- U7 began with a pre-physical artifact: the unchanged semantic `HI` world lowers
  deterministically to a reviewed x86-64 PE32+ UEFI application at
  `EFI/BOOT/BOOTX64.EFI` inside a 64 MiB MBR/FAT32 image. Structural, identity,
  tamper, policy, and repeat-build tests pass. QEMU 11.1.1 plus TianoCore EDK II on the
  Apple Silicon Mac manually displayed `HI` before the physical gate was opened.
- The owner authorized erasing a new external Kingston DataTraveler Duo. The 64 MiB
  image was written to the removable whole disk. macOS then auto-mounted FAT32 and added
  `.fseventsd`, so the whole-prefix hash changed; the actual `BOOTX64.EFI` hash remained
  exactly reviewed. That established the removable payload before physical execution.
- The exact USB then displayed `HI` on the physical Dell OptiPlex 3060 after the owner
  explicitly disabled only Secure Boot. No keys were deleted, Legacy mode remained off,
  no OS or internal storage participated, and the physical i5-8500T executed the UEFI
  application. The owner chose to keep Secure Boot off as a documented dedicated-home-
  lab policy. This completes the first physical U7 target slice, not the future two-device
  physical conformance goal.
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

## U5 verified result

`experiments/runner-contract-v1/` wraps the unchanged U4 world, patch, negotiation, and
backends in one strict contract for `native`, `hosted`, and `bridge`. Each target declares
transport, authority, remaining layers, temporary mutations, timeouts, recovery, whether
persistent writes occur, and whether execution is simulated.

The bridge is an explicitly labeled child-process simulator using canonical JSON frames
with a four-byte big-endian length prefix. Requests bind plan and artifact identities;
responses bind the request and observation. Request, response, and whole-transcript hashes
enter evidence. Native QEMU and bridge both observe exact `HI/HI!` with status `0`.

The verifier rejects mislabeled envelopes, unreviewed mutations, persistent writes,
missing recovery, protocol mismatch, replayed or tampered transcripts, timeouts, and
evidence bound to a stale runner revision.

The complete suite passed on the learner's Apple Silicon Mac. All three envelopes
observed exact `HI/HI!` with status `0`; the bridge remained explicitly labeled as a
simulation and produced independently hashed request, response, and transcript evidence.

## U6 real inventory result

The available target is a Dell OptiPlex 3060 with an Intel Core i5-8500T, 8192 MiB of
RAM, UEFI 1.2.22, working HDMI firmware display, working USB keyboard input, enabled USB
boot and front/rear USB ports, and no installed M.2 storage. The manually reviewed BIOS
screens performed no writes. Service Tag and Express Service Code are deliberately
excluded from the repository.

`inventories/dell-optiplex-3060-observed.json` validates as a real read-only inventory.
Against `x86-64-uefi-usb-v0` it deterministically returns `UNSUPPORTED` for exactly:

```text
secure-boot-state-unsupported
suitable-removable-media-missing
```

The second reason means only that the purchased USB device was not present in the
observed hardware snapshot; its identity and capacity must be collected on the Mac
before any write. The first is a separate human decision. U6 did not disable Secure
Boot or authorize installation.

## Immediate implementation sequence

1. Run the new read-only USB/Bluetooth probe under QEMU and record exact evidence.
2. After a fresh removable-device check and explicit authorization, run that exact image
   on the Dell. If standard Bluetooth class `E0/01/01` is present, stage a local BLE
   Rabbit bridge; otherwise return to native QCA9377 planning.
3. Implement receive-only framed `.rabbit` package transport over that selected path,
   then add authenticated transactional replacement and responses.
4. Put the package interpreter behind the UEFI framebuffer/input/network Target Pack so
   the Dell can change worlds without rebuilding or moving the boot USB.
5. Add microphone, speech recognition, and LLM proposal on the Mac above the deterministic
   validation boundary; move components onto the Dell only when useful.
6. Keep the persistent Secure Boot-off state explicit in every future physical evidence
   record; reconsider it if the Dell stops being a dedicated lab target.

The first part of the patch slice is implemented: `build_image.py --patch add-bang`
validates the existing immutable semantic patch, derives `HI!`, produces reviewed EFI
and image hashes, and proves that removing the patch restores the exact base `HI` image.
QEMU 11.1.1 and the physical Dell displayed exact `HI!`. The owner then rebuilt the
reviewed base, re-identified and rewrote the external Kingston device, verified the exact
base EFI payload hash, and observed exact `HI` again on the physical Dell.

The physical patched and rollback evidence bind the complete `HI -> HI! -> HI` lifecycle
to the base/effective worlds, patch, target, QEMU evidence, both EFI/image identities,
and both owner-reviewed physical observations. Secure Boot remained disabled under the
explicit dedicated-lab policy, and no internal storage participated.

The first direct-framebuffer graphics artifact exists in
`experiments/x86-64-uefi-framebuffer-v0/`. Its portable world requests one orange
`256 x 256` rectangle at `(100,100)`. The x86-64 UEFI Target Pack binds that request to
GOP's configured linear framebuffer. Reviewed machine bytes locate GOP, inspect
resolution/stride/pixel format, and directly write 65,536 pixels without calling Simple
Text Output or embedding `HI`. Deterministic and negative tests pass. QEMU 11.1.1 with
TianoCore EDK II displayed the expected square, and the owner-reviewed screenshot is
bound to the exact world, target, EFI, and image identities. After re-identifying the
external Kingston device and receiving explicit authorization, the owner wrote the exact
image, verified its EFI hash, and observed the orange square on the physical Dell with
no OS or internal storage involved.

`experiments/x86-64-uefi-interactive-v0/` is the first interactive artifact. It clears
the visible framebuffer, draws a `128 x 128` object, stores `(x,y)` in registers, reads
UEFI arrow scan codes, erases the old position, moves by 16 pixels, clamps every edge,
and redraws; Escape exits. The artifact comprises 542 reviewed x86-64 code/data bytes
inside the same deterministic PE32+/FAT32 envelope. Static instruction checks, an
independent movement model, boundary tests, policy rejection, and repeated builds pass.
QEMU 11.1.1 then demonstrated all four directions, clean old-frame erasure, boundary
clamping, and Escape; the owner-reviewed interaction is bound to exact identities. A
fresh device identification, explicit authorization, physical write, and exact EFI hash
check followed. The physical Dell then reproduced four-way movement, clean erasure,
boundary clamping, and Escape with no OS or internal storage involved.

The owner then described the first world in ordinary language: a yellow square jumps
and returns on Space; `Z` leaves a smaller yellow solid stone and moves the player away;
the player cannot cross the stone but can route around it. The reviewed v0 contract uses
one persistent stone, relocated by the next `Z`. The new experiment adds a semantic
`time.delay` capability bound to UEFI `Stall()`, 1,064 reviewed x86-64 code/data bytes,
and explicit AABB collision logic. Deterministic builds, an independent state model,
placement/blocking/route-around/replacement/boundary tests, and negative checks pass.
The owner manually reproduced the complete behavior in QEMU 11.1.1. That observation is
hash-bound; physical Dell execution was deliberately skipped and remains unclaimed.

`experiments/world-package-v0/` now separates that world from its first bespoke x86-64
program. The approved Russian intent and reviewed interpretation deterministically
produce a 1,060-byte `.rabbit` package with a canonical manifest and compact operations
for player setup, movement, timed jump, stone placement, clamping, collision, and exit.
The package identity is
`e7d642aef7810cb8edfeb51693b29c7909024ae5d3dc4fb9741e44e4b42b8d9b`.
An independent decoder recovers the exact operation stream; tampering, truncation, stale
interpretation, semantic drift, duplicate fields, and target-specific vocabulary are
rejected. It is `PACKAGE-BUILT-NOT-DEPLOYED`: no runtime consumes it yet and no physical
write is claimed.

The owner chose Wi-Fi rather than removable-media shuttling as the first live command
transport. `experiments/x86-64-uefi-network-probe-v0/` now builds a deterministic
read-only UEFI application that locates Simple Network, Wireless MAC v1, and Wireless
MAC v2 protocols and enumerates PCI base-class `02` devices. The original v0.1 used
direct CF8/CFC reads across every possible bus. It passed QEMU, but the physical Dell
remained dark for multiple minutes; power-off and USB removal recovered safely and no
inventory was claimed. That failed exact-bound attempt is retained as evidence.

V0.2 instead asks UEFI for handles of devices that actually exist, reads only those via
`EFI_PCI_IO_PROTOCOL`, and frees its temporary handle buffer. It sends and receives no
packets, writes no PCI configuration data, and changes no persistent state. The physical
chipset is still intentionally not guessed. Current v0.2 image identity is
`d9718a582019fc7d82cd3f87048471138d450d62422ccbbf526910372a60ce5e`.
The replacement is now QEMU-observed: it completed quickly and reproduced Simple
Network `YES`, Wi-Fi v1/v2 `NO`, and emulated `8086:10D3`. The evidence is bound to the
new v0.2 identities and does not reuse v0.1 approval. A fresh removable-device check and
explicit write authorization are the next gates.

The earlier v0.1 QEMU gate showed Simple Network, no Wireless MAC v1
or v2 protocol, and one emulated Intel `8086:10D3` Ethernet controller at `00:02.0`.
The owner-reviewed screen is bound to the exact probe, target, program, EFI, and image
identities. Those facts cannot approve v0.2 or predict the Dell.

V0.2 then passed QEMU quickly, but the physical Dell again remained dark for 30 seconds
after selecting the UEFI USB, before even the title could be confirmed. This falsifies
the claim that only brute-force PCI enumeration caused the visible failure. V0.3 removes
the early `ClearScreen()` call and prints `STAGE 1: TEXT OK`, `STAGE 2: PROTOCOL CHECKS`,
and `STAGE 3: PCI HANDLES` before the corresponding work. Its current image identity is
`afac5e6d866fcb6e0e7bd770d37bc77b755837dd0bdb2a8553aabd07ef502a61`.
Both failed physical attempts remain exact-bound. V0.3 passed QEMU 11.1.1 on the
Apple Silicon Mac: all three stage markers were visible, Simple Network was `YES`, both
Wi-Fi protocols were `NO`, and the emulated controller was `8086:10D3`. The exact
evidence makes no physical claim. V0.3 is now `QEMU-OBSERVED-NOT-PHYSICALLY-INSTALLED`;
a fresh device check and explicit authorization remain mandatory before another write.
The exact v0.3 image was subsequently written and verified, but the physical Dell again
remained dark before `STAGE 1`, disproving `ClearScreen()` as the complete explanation.
Code review then found a concrete ABI defect: the nested `print_ascii` helper called
firmware without its own 32-byte Microsoft x64 shadow space and correct pre-call stack
alignment. QEMU tolerated this undefined call frame. V0.4 repairs it with a reviewed
`0x28`-byte adjustment around the nested firmware call. The new image identity is
`cef4a46e3e3c73445f480cab1f19efc195163831f2423fb3aa7e63ed325614b4`.
V0.4 then passed QEMU 11.1.1 with its version marker, all three stages, and the same
emulated network inventory visible. This confirms that the correction preserves QEMU
behavior. The diagnosis remains a hypothesis until the separately authorized physical
Dell run.
The exact v0.4 image was then written and verified, and the physical Dell displayed all
three stages. It exposed no UEFI Simple Network or Wi-Fi protocol and reported Ethernet
`10EC:8168` at `01:00.0` plus wireless-class `168C:0042` at `02:00.0`. No packet or PCI
configuration write occurred. The physical A/B result supports the corrected nested
call frame as the earlier failure cause. Upstream ath10k maps device `0042` to QCA9377,
so the next experiment is read-only driver planning for that exact device, not a generic
or guessed Wi-Fi implementation.

Because the owner has no additional cable and both computers share one room, Bluetooth
is now tested as a potentially smaller first wireless bridge. The new
`experiments/x86-64-uefi-bluetooth-probe-v0/` artifact uses bounded UEFI USB I/O handle
enumeration and only the device/interface descriptor methods. It recognizes standard
Bluetooth class triple `E0/01/01` at either level, reports exact USB VID/PID and class
facts, and caps enumeration at 64 interfaces. Its reviewed program is 1,152 bytes; the
image identity is
`15bc2c6e19236bbb0a1f2823eda0ab89f55a93b51b682d81e53e85db8e5d69a2`.
Deterministic, PE/FAT, ABI, classifier, budget, policy, tamper, and duplicate-JSON tests
pass. QEMU 11.1.1 then displayed one emulated USB keyboard (`0627:0001`, interface
class `03/01/01`), correctly classified it as non-Bluetooth, and reported zero
Bluetooth candidates. Exact-bound evidence is committed and makes no physical Dell
claim. `prepare_physical.py` now combines verification, building, hashing, and read-only
external-media inspection into one command. It deliberately stops before unmounting or
writing: exact-device review and explicit authorization remain separate. The owner then
authorized the exact Kingston write and the physical Dell displayed five interfaces.
Two Bluetooth-class interfaces belong to one device, `0CF3:E009`, which upstream Linux
classifies as QCA Rome. No HCI command, pairing, radio packet, port reset, USB data
transfer, or persistent machine write occurred. The next boundary is a read-only HCI
controller-identity experiment, not connection or pairing.

`experiments/x86-64-uefi-bluetooth-hci-identity-v0/` now implements that boundary. It
matches only `0CF3:E009` interface `00`, finds one bounded interrupt-IN endpoint, sends
only HCI opcode `0x1001` (Read Local Version Information), and accepts only a matching
Command Complete event within an eight-event/64-byte budget. The reviewed program is
1,952 bytes and the image identity is
`c5658d3edf41028089f72d2be324c12dddbaad1b3f0c037930a1d81bd91ec8de`.
Deterministic build, PE/FAT, exact-byte, HCI parser, budget, device-substitution,
authority-escalation, tamper, and ambiguous-JSON checks pass. `run_qemu.py` combines the
verifier with the fail-closed emulator gate; QEMU must show `TARGET NOT FOUND; NO HCI
COMMAND SENT`. Physical preparation remains programmatically closed until that evidence
is recorded. No scan, advertising, pairing, connection, firmware download, controller
reset, bulk/ACL data, or radio-data authority exists.

The owner then ran the combined QEMU gate. QEMU 11.1.1 reached Stage 1, did not find
`0CF3:E009`, displayed `TARGET NOT FOUND; NO HCI COMMAND SENT`, and therefore exercised
no HCI or radio authority. Exact evidence is now committed. This opens the combined
read-only preparation workflow, but not physical-media replacement: a fresh external
disk identity and explicit owner authorization are still required.

The owner subsequently authorized and ran that exact image on the physical Dell. The
program found `0CF3:E009` interface `00`, selected interrupt endpoint `81`, sent only
HCI Read Local Version Information (`0x1001`), and received Command Complete status
`00`. The controller reported HCI/LMP version `07`, manufacturer `001D`, and LMP
subversion `025A`, corresponding to Bluetooth Core 4.1 and Qualcomm in the Bluetooth
SIG Assigned Numbers. The observation is exact-hash-bound in
`evidence/dell-optiplex-3060-physical-observed.json`. No reset, firmware download,
scan, advertising, pairing, connection, ACL data, radio data, or persistent write ran.
The next boundary is one combined local-capability artifact, not yet a radio link.

`experiments/x86-64-uefi-bluetooth-local-capabilities-v0/` now implements that next
boundary in one boot. It permits exactly `0x1002`, `0x1003`, and `0x2003`, prints the
64-byte supported-command bitmap and both 8-byte feature bitmaps, and raises the event
buffer from 64 to a bounded 80 bytes because the first Command Complete packet is 70
bytes. Its reviewed program is 2,808 bytes; the image identity is
`006ed8b12843b7d91712764cc4b42462c1e192924d8a1ddb6ae05fa3232336ea`.
All deterministic and negative checks pass. The current status is PRE-QEMU and not
physically installed. QEMU must show the exact fail-closed result before evidence opens
physical preparation. Scan, advertising, pairing, connection, controller reset,
firmware download, ACL data, radio traffic, and persistent writes remain forbidden.

That QEMU gate now passes exactly. QEMU 11.1.1 on the Apple Silicon Mac displayed the
v0.1 title, reached the exact-device match stage, and reported `TARGET NOT FOUND; NO HCI
COMMAND SENT`. The owner-reviewed screen is bound to all five artifact identities in
`evidence/qemu-macos-arm64-observed.json`; it claims no physical execution. The combined
`prepare_physical.py` workflow is now open, while actual removable-media replacement
still requires a fresh device identity and explicit owner authorization.

The owner authorized the exact Kingston replacement and the physical Dell completed all
three local queries. It returned the 64-byte supported-command map
`FFFFFF03CEFFEFFFFFFFFF7FF20FE8FE3FF783FF1C00000061FFFFFF7F8620F5FFF0F90700000000000000000000000000000000000000000000000000000000`,
BR/EDR features `FFFE8FFED83F5B87`, and LE features `1F00000000000000`.
These bits confirm legacy LE advertising, scanning, and connection command support.
Exact evidence is committed; no scan, pairing, connection, or radio packet occurred.
The next boundary is one bounded receive-only scan for an exact Rabbit beacon from the
Mac, not yet a general Bluetooth connection.

`experiments/x86-64-uefi-bluetooth-beacon-rx-v0/` now implements that next candidate.
The reviewed Mac sender advertises one exact 128-bit service UUID through CoreBluetooth.
The Dell program issues only general/LE event masks, passive scan parameters, scan
enable, and mandatory scan disable. It listens for at most 100 events over 20 seconds,
accepts the Rabbit UUID in either on-air little-endian or canonical order, and never
authorizes active scan, radio transmit, pairing, connection, controller reset, firmware
download, or persistent writes. The program is 3,432 bytes; image identity is
`0fa4c4ce888d9a2ba916898f1ab43f579b92b52553d7f6a96b44fabddc2dd50c`.
All deterministic and negative checks pass. Status is PRE-QEMU and NOT-PHYSICALLY-
INSTALLED; the next action is the fail-closed QEMU gate on the owner's Mac.

The owner completed that QEMU gate. QEMU 11.1.1 on the Apple Silicon Mac displayed the
v0.1 receive-only title and mode, rejected the emulated USB keyboard at Stage 1, and
reported `TARGET NOT FOUND; NO HCI COMMAND SENT`. No passive scan or radio operation
started. Exact evidence is committed, so `prepare_physical.py` is now open; physical
media replacement still requires fresh device identity and explicit authorization.

The owner then wrote the exact receiver image to the reviewed Kingston device and
verified EFI identity
`8b9df03b61e21319c1d0329d185b080d17962a1b3763424ddb0d6ddc98c62840`.
The first Mac-sender launch failed before Bluetooth started because the installed Swift
compiler and Command Line Tools SDK were patch-level incompatible and exposed duplicate
`SwiftBridging` modules. This did not execute or alter the Dell receiver. The sender is
now the same exact CoreBluetooth advertisement implemented in reviewed Objective-C and
built temporarily with Apple `clang`, removing Swift toolchain compatibility from this
experiment while preserving the UUID, permission manifest, and Dell EFI/image hashes.
The repaired CoreBluetooth sender reported `RABBIT BEACON ADVERTISING`, and the physical
Dell accepted all four setup commands, listened passively for the bounded 20 seconds,
issued the mandatory scan-disable command, but displayed `RABBIT BEACON NOT RECEIVED
WITHIN BUDGET`. V0.1 did not count received events, so this result cannot yet distinguish
no visible advertisements from an advertisement/parser mismatch. Exact failure evidence
is preserved rather than presented as a successful wireless link.

V0.2 keeps the same five-command receive-only authority and adds hexadecimal counters
for successful scan-window USB events, LE Meta events, and LE Advertising Reports. Its
new EFI identity is `18a098c4168b1679c3d4d11a59d67c0d4ecb917a2f0720e21741bddbb62bc30d`
and image identity is `bd15cc66ee6340bd0225a4394bd6d754f0b31115b52b4ee6d98a513ac8e90df2`.
All deterministic and negative checks pass. Physical preparation was initially closed
pending a separate fail-closed QEMU observation. The owner then ran
that exact gate: QEMU displayed v0.2, the receive-only mode, Stage 1, and `TARGET NOT
FOUND; NO HCI COMMAND SENT`. No HCI command, scan, or radio operation occurred. Exact
v0.2 QEMU evidence is committed, so read-only physical preparation is now open.
The exact v0.2 image was then written and verified. With the reviewed Mac sender active,
the physical Dell again accepted the complete scan sequence and disabled scanning, while
the new line reported `RX/LE/ADV (HEX)=00/00/00`. No scan-window USB event arrived, so
UUID parsing was not the failure point. Linux identifies `0CF3:E009` as QCA Rome and
runs `btusb_setup_qca`, reading vendor target-version/status and conditionally loading
rampatch plus NVM before normal use. That makes a read-only QCA vendor-status probe the
next boundary; firmware download, reset, scanning, pairing, connection, and transmission
are not yet authorized.

`experiments/x86-64-uefi-qca-status-v0/` now implements that diagnostic. It binds to
the exact Dell USB ID and interface and permits only two device-to-host USB vendor
requests: `0x09` for the packed 20-byte ROM/patch/RAM identity and `0x05` for the
one-byte setup status. It displays `PATCH_UPDATED` (`0x80`) and `SYSCFG_UPDATED`
(`0x40`) independently. Vendor OUT, firmware download, controller reset, HCI, radio,
and persistent writes are absent and rejected by the verifier. The exact image identity
is `e7747dbd747ef9add8a5853d01f05e93ebaf20807399a0d697883b15fd235b1f`.
QEMU 11.1.1 on the Apple Silicon Mac showed the exact v0.1 title, read-only mode,
Stage 1, and `TARGET NOT FOUND; NO VENDOR REQUEST SENT`. No vendor request, reset,
download, HCI command, or radio operation occurred. Exact evidence is now committed,
so physical preparation is open; writing removable media remains a separate explicit
authorization boundary.

The physical Dell then returned ROM `00000302`, patch `00000111`, RAM `00000000`, and
status `20`; both `PATCH_UPDATED` and `SYSCFG_UPDATED` were `NO`. This explains why the
controller can answer local HCI queries while remaining a plausible source of the
zero-event radio scan. It is evidence for missing QCA setup, not yet proof that setup is
the only reception problem.

`experiments/x86-64-uefi-qca-ram-load-v0/` implements the next bounded experiment. It
fetches the exact unmodified Rome 3.2 rampatch and NVM from pinned linux-firmware commit
`797d34e622b2262ca0777e98fd40b1d29034169d`, rejects any size/hash mismatch, requires
exact USB `0CF3:E009` and ROM `0x00000302`, and permits only two vendor-OUT headers plus
18 bounded endpoint-02 bulk transfers. Payload writes are to volatile controller RAM;
full Dell power-off is rollback. No controller reset, HCI, scan, radio, controller
flash, internal-storage write, or firmware-setting write exists. The post-load status
read must show both setup bits. Status is PRE-QEMU; physical preparation remains closed
until the exact mismatch gate is observed and committed.

That QEMU gate passed exactly: the v0.1 title and transient-RAM/radio-off mode appeared,
Stage 1 rejected the emulated USB keyboard, and the program reported `TARGET NOT FOUND;
NO DEVICE WRITE SENT`. No controller RAM write, reset, HCI command, or radio operation
occurred. Exact evidence is committed, so physical preparation is open; removable-media
replacement remains a separate operation on the dedicated Rabbit test USB.

The exact physical Dell run then succeeded. It matched ROM `00000302`, reported both
`RAMPATCH TRANSFER: OK` and `NVM TRANSFER: OK`, and the post-load read returned
`PATCH_UPDATED=YES; SYSCFG_UPDATED=YES`. This proves the two hash-pinned upstream
payloads reached volatile QCA controller RAM and established the status expected by
Linux's setup path. No reset, HCI command, scan, or radio operation occurred. The next
artifact must initialize RAM and perform the bounded passive Rabbit-beacon receive in
the same boot, since full power-off is rollback and clears this state.

`experiments/x86-64-uefi-qca-beacon-rx-v0/` now implements that one-boot composition.
It chains into the already reviewed passive receiver only after exact ROM matching,
both pinned volatile payload transfers, and both ready bits. The exact five-command HCI
sequence ends with mandatory scan disable after at most 20 seconds. Active scan,
advertising, pairing, connection, Dell radio transmit, controller reset/flash, internal
storage, and firmware-setting writes remain forbidden and rejected. Deterministic
verification passes with image SHA-256
`50d5232d4914e33220d73bff53bd42f428244a96a96c9abbaa19b9766200ab7d`.
The exact QEMU gate passed on the owner's Apple Silicon Mac: the program displayed its
combined v0.1 identity, rejected the emulated USB keyboard, reported `TARGET NOT FOUND;
NO DEVICE WRITE SENT`, and did not reach the receiver chain. The evidence is bound to
the exact artifact. The physical v0.1 run then loaded both payloads, reached status
`E0`, and completed scan cleanup, but reported `RX/LE/ADV=00/00/00`. The controller
delivered no USB scan event at all.

V0.2 tests one narrow activation hypothesis: exactly one standard HCI Reset and a
100 ms wait after both ready bits, followed by the unchanged passive receiver. Linux's
QCA USB setup returns into generic HCI initialization, while its QCA core path explicitly
performs a post-download HCI Reset. The new deterministic image SHA-256 is
`7460a9fce26fc8aea329f0c169492e0c76b60d5df88cfdd0f9901eb9ac56ae5f`.
Its exact QEMU gate passed: v0.2 rejected the emulated USB keyboard before RAM writes,
reset, HCI, or radio. Physical preparation is open and installation is still pending.
Active scan, advertising, pairing, connection, Dell radio transmit, flash, internal
storage, and firmware-setting writes remain absent.

The physical v0.2 run succeeded. After transient setup status `E0` and exactly one
post-load HCI Reset, the passive receiver reported `RX/LE/ADV=0C/0C/0C` and
`RABBIT BEACON RECEIVED` for exact UUID
`52414242-4954-4C45-8000-000000000001`. The Dell transmitted nothing, paired with
nothing, connected to nothing, and performed no persistent machine write. This is the
first observed one-way wireless Rabbit identity from the Mac to the OS-less Dell. The
next boundary is a small exact-bound command vocabulary, not yet a general Bluetooth
connection or arbitrary code delivery.

`experiments/x86-64-uefi-ble-color-command-v0/` now implements that candidate. The
Dell starts with a centered yellow `128 x 128` GOP square and passively recognizes only
two exact Mac advertisements: `BLUE` (`...0002`) and `YELLOW` (`...0003`). A received
command repaints only that region; both commands close the receive window early, while
the hard ceiling is 120 seconds. Active scan, Dell transmit, pairing, connection,
arbitrary-code commands, disk writes, and firmware writes remain forbidden. The exact
pre-QEMU verifier passes with EFI SHA-256
`cfb0fc9dd6b6bc59514cf5181b09faa7c93022e62ba96b721d98ef054e78788e` and image
SHA-256 `bce85e8c67d71f45c0c118c3616e9a62c1d4ee6228d0b29a1bbe6b4ed52aa00d`.
The exact QEMU mismatch gate passed with the corrected visible artifact identity and
stopped before RAM, framebuffer, HCI, or radio. The next gate is one physical USB
installation and the live yellow → blue → yellow test without moving the USB.

The first physical v0.1 run loaded both QCA payloads and reached the receiver's
`TARGET FOUND; EVENT ENDPOINT=81`, but stopped before `DISPLAY READY`. Therefore no HCI
reset, scan, or color command ran. The failure exposed a nested-call ABI bug: GOP
`LocateProtocol` was called without a fresh Microsoft-x64 shadow-space/alignment frame.
V0.2 reserves `0x28` bytes around that call and rebases its persistent stack slots.
The corrected image SHA-256 is
`669b11d4313a1cb0c0d26404ffbbc0c56dd5321361e309beebe1ac2df69a8107`;
its fresh QEMU exact-device mismatch gate passed without RAM, framebuffer, HCI, or radio.
Physical candidate preparation is open for the second Dell attempt.

The v0.2 Dell attempt passed GOP lookup but lost HDMI during the first draw. The draw
helper had two stack additions (CALL return address and `PUSH RSI`) but compensated for
only one, so it read every persistent framebuffer field eight bytes early and used the
GOP interface pointer as the framebuffer base. No HCI reset or scan was observed. V0.3
uses `+0x10` for all five reads and brackets the draw with two visible stage messages.
Its image SHA-256 is
`63ea281431ca09cce91d7bedf0ca9684f17f2020422fee17bfe42021bac34f1f`;
its fresh QEMU mismatch gate passed without RAM, framebuffer, HCI, or radio effects.
Physical candidate preparation is open for the v0.3 Dell attempt.

The v0.3 physical attempt succeeded: one Dell boot drew yellow, accepted exact `BLUE`
from the Mac and drew blue, then accepted exact `YELLOW` and returned to yellow. No USB
movement or Dell reboot occurred between commands, and scan-disable cleanup completed.
No pairing, connection, Dell transmit, disk write, or firmware write occurred. This is
the first physical wireless command-to-state loop on the OS-less Dell. The next boundary
is a long-lived passive runtime with explicit local exit, replacing the 120-second proof
budget without expanding the two-command vocabulary.

V0.4 now implements that runtime. It has no automatic deadline or early exit after both
colors; each USB receive remains bounded to 200 ms so the local keyboard is polled.
`Esc` sends mandatory scan-disable cleanup and returns, while power-off remains the
fallback. Exact `BLUE`/`YELLOW`, the centered framebuffer region, passive-only Dell
radio, and all persistent-write prohibitions are unchanged. The deterministic image
SHA-256 is `1c42713850b25ede0f3064fdbfe2a6d09befd5e85f463a7eb25869bdb289b325`.
Its fresh exact QEMU mismatch gate passed without RAM, framebuffer, HCI, or radio.
Physical candidate preparation is open.

`experiments/x86-64-uefi-ble-program-loader-v0/` is now the active successor. It keeps
the proven volatile QCA initialization, GOP boundary, passive BLE receive path, local
`Esc` cleanup, and power-off recovery, but replaces the two fixed color UUIDs with a
transactional multi-frame transport. `BEGIN`, ordered `CHUNK`s, and `COMMIT` assemble a
program in RAM while the old scene keeps running. Only after frame checksums, complete
length, whole-program hash, and bytecode validation does Dell atomically activate it.
Rabbit VM v1 accepts `DEFINE_SHAPE`, `SET_POSITION`, and `END`: a program can select a
square or triangle, arbitrary RGB, position, size, movement step, and arrow controls.
FNV is explicitly corruption detection, not authentication. Native-code execution,
arbitrary memory access, pairing, connection, Dell transmission, disk writes, and
firmware writes remain forbidden. The exact v0.2 QEMU mismatch observation stopped
before RAM, VM, HCI, radio, or framebuffer effects. The physical v0.2 image then loaded
both pinned QCA payloads and reached `STAGE 5: BEGIN TRANSACTIONAL RABBIT VM RECEIVE`,
but the chained runtime title did not appear. Because `scan_entry` is reached by `JMP`,
expanding its frame from the proven `0x498` to `0x700` inverted Microsoft x64 call
alignment before its first `OutputString`. V0.3 keeps the expanded workspace but uses
`0x708`, restoring the 8-mod-16 frame relationship. Its deterministic pre-QEMU verifier
passes with EFI SHA-256
`7bb3b4875eb331213ae5bd4de8e58da35f634cb7960178d0862de4232ce95f54`
and image SHA-256
`3a40d06832762b6436e9410766bc3db781ae0e01020c0024c32a82367322b548`.
The fresh exact v0.3 QEMU mismatch observation passed: the corrected identity was
visible and the emulated-device mismatch stopped before RAM, VM, HCI, radio, or
framebuffer effects. The corrected image then passed physically: Dell initialized QCA,
bound the framebuffer, entered the long-lived runtime, received a complete six-frame
Rabbit VM program from the Mac, atomically applied it, and displayed the requested blue
triangle. No reboot, post-boot USB movement, or persistent write participated. Arrow
movement then worked in all four directions. In the same runtime, a second complete
six-frame program atomically removed the triangle and displayed an arrow-controlled
green square with different position, size, color, and movement step. Neither USB
movement nor Dell reboot occurred between programs. This completes the first physical
hot-program-replacement slice; transport authentication and Dell-to-Mac acknowledgement
were still absent in v0.3.

V0.4 is the pre-QEMU Dell-to-Mac acknowledgement candidate. After a valid `COMMIT`, Dell
temporarily disables passive scan, advertises one non-connectable receipt for exactly
1.5 seconds, disables advertising, and resumes passive scan. The 16-byte receipt binds
the transfer id, exact program FNV, and an in-RAM applied counter; Mac scans concurrently
and exits only after validating the matching receipt checksum and identity. Arbitrary
advertising, arbitrary Dell transmission, active scan, pairing, connection, native code,
and persistence remain forbidden. This acknowledgement gives the current sender a
correlated application receipt; it does not cryptographically prove who sent it. Keyed authentication,
anti-replay state, key lifecycle, and optional encryption are explicitly deferred in
`debts.md`. The deterministic pre-QEMU v0.4 image SHA-256 is
`a56c358736c4122d0f9aeb8b69d862d306bbcc370e5ad29681d9d0be2de05077`.
The exact v0.4 image was then observed in QEMU on macOS ARM64. It displayed the
v0.4 identity and stopped at `TARGET NOT FOUND; NO DEVICE WRITE SENT`; no controller
RAM, VM, HCI, radio, or framebuffer effect was crossed. The dedicated physical USB
may now be prepared for the acknowledgement test.
The first physical v0.4 run applied the exact blue-triangle program and displayed
`ACK ADVERTISED FOR 1500 MS; PASSIVE RECEIVE RESUMED`, but the original Mac sender
did not observe `ACK RECEIVED` and continued repeating its six frames. This is preserved
as partial negative evidence. The Mac-only follow-up adds an explicit 1.8-second quiet
receive window plus scanner-state and 128-bit UUID diagnostics; it does not require a
new Dell image or USB write.
That diagnostic sender then observed the exact UUID
`52411100-23B7-3DE7-0000-000147313E40`: its checksum, program hash, and applied counter
were valid, while its transfer id was `00` instead of expected `E7`. The cause was an
exact v0.4 instruction that zeroed the four-byte transfer state before copying byte 1
into the ACK. V0.5 moves that same clear until after the id is copied; no authority or
image size changes. Its pre-QEMU image SHA-256 is
`e3595bc3febf8d924cdb50f2685e41cc34b5f96016d7850596533ddc76d825e6`.
The exact v0.5 image then passed its macOS ARM64 QEMU mismatch gate: the v0.5 identity
was visible and execution stopped at `TARGET NOT FOUND; NO DEVICE WRITE SENT` before
RAM, VM, HCI, radio, or framebuffer effects. The physical v0.5 candidate may be prepared.
The exact v0.5 image was then written to the dedicated Kingston USB and booted on the
Dell. A six-frame cyan-triangle transfer produced ACK UUID
`52411138-BD38-F838-0000-00028BFDA39E`; CoreBluetooth observed it at RSSI -63, the Mac
validated transfer `38`, program hash `BD38F838`, and applied counter `2`, then exited
automatically. This completes the first physical Mac → Dell program → Mac receipt loop.
It is delivery evidence, not authentication; the first post-boot ACK was missed, so
idempotent retry also remains open.

## U7 pre-physical artifact result

`experiments/x86-64-uefi-v0/` builds, but does not install, a deterministic 64 MiB disk
image. Its FAT32 partition contains the standard removable-media path
`EFI/BOOT/BOOTX64.EFI`. The PE32+ application uses the x86-64 UEFI calling convention,
calls `EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL.OutputString()` with UTF-16 `HI`, waits for one
key through firmware input, and returns `EFI_SUCCESS`.

Current reviewed identities are:

```text
EFI SHA-256:   a82d77b43d636d63af9bfa76e0a998ed4b62746a0eab10ad0f6c1777dc8c6128
image SHA-256: 806d4fef5a33c1bc7d0451bd06d4c665ef21612acd32bddea93fd3f9ca56a594
status:        BUILT-NOT-INSTALLED
```

The binary image is generated into a disposable path and is not committed. The verifier
checks the MBR, FAT32 path, PE32+ machine/subsystem/entry point, exact reviewed machine
bytes and UTF-16 message, deterministic identities, no physical writes, and rejection
of altered worlds, policy escalation, signing claims, and code tampering.

On 2026-09-22 the owner ran QEMU 11.1.1 on the Apple Silicon Mac. TianoCore EDK II
reported starting `UEFI QEMU HARDDISK QM00001`, the exact application displayed `HI`,
and the runner returned to the shell. The owner-reviewed screenshot/transcript is bound
to the world, target, EFI, and image hashes in
`evidence/qemu-macos-arm64-observed.json`. This is manual emulator evidence, not an
automated display oracle and not physical Dell evidence.

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

U6 is complete only when:

- discovery is demonstrably read-only and yields a canonical hardware inventory;
- a real available x86-64 UEFI candidate is matched to a supported Target Pack or
  rejected with precise missing requirements;
- the installation plan targets removable media only and enumerates every intended write;
- internal disks, firmware, secure-boot changes, hidden effects, stale inventories, and
  missing recovery are rejected;
- planning and installation remain separate authorization boundaries;
- removing the USB device is the documented recovery path;
- inventory, match, plan, and negative conformance evidence pass reproducibly.

## Reusable Creation Inventory v1

`experiments/reusable-creation-inventory-v1/` is the first target-independent catalog
and Merge contract for reusable Rabbit parts. It defines versioned assets, capabilities,
Anima, policies, and Creations with typed ports, exact dependencies, authorities,
resource budgets, Creator identity, SPDX license, and content identity. The first
`Cat Plays With Ball` blueprint resolves thirteen components; a separate `Bouncing Ball`
blueprint reuses ten of their exact identities. A canonical provenance lock records the
resolved hashes and licenses.

Sharing uses a deterministic Ed25519-signed package and requires an externally trusted
Creator public key. Verification rejects tampering, unknown signers, stale locks, hidden
or unused authority, omitted dependencies, type mismatch, resource overflow, target
leakage, unreviewed native code, malformed sprites, dependency cycles, and duplicate
JSON fields. The catalog stays target-independent. Its exact `Cat Plays With Ball`
Creation is now executed by the hosted Scene/Anima v2 runner and lowered unchanged into
the separate Dell physical runtime described below.

## Scene/Anima v2 hosted execution

`experiments/scene-anima-v2-runner/` is the first executor for the exact Inventory v1
`Cat Plays With Ball` identity. It rejects a changed Merge, substituted sprite, altered
authority or runner budget before execution. The accepted scene uses only integer
state, a fixed 30-tick semantic clock, two bounded entities, the catalog's exact sprite
frames, and a 160-by-90 logical raster.

In the 240-tick reference execution the cat visits `look`, `chase`, `pounce`, `bat`, and
`wait`, bats the ball five times, animates both catalog frames, and observes twelve ball
edge contacts. A second execution yields the identical canonical trace and final RGB
raster. `run_hosted.py` writes `trace.json`, `report.json`, a final PPM, and an offline
HTML visualization to a disposable directory. No generated artifact is committed.

This is real hosted execution. The exact accepted identities are Creation
`c6e1def6497769bbaa3917a8dacba099b01676af459358d7e6551fb6fa82eab8`, runner contract
`7e6bc4af52f21da5001ed9be6068347799b312fe16021babab94b938530dd2cb`, and trace
`1cfa264a561935ffe591184400ddf66dc0482f94be16a5f188a8dd499b9d62ab`.

## Dell Scene/Anima v2 physical execution

`experiments/x86-64-uefi-scene-anima-v2/` preserves that exact Creation, the same
thirteen Inventory component identities, and the same trace semantics. Target-specific
x86-64, UEFI GOP, timing, removable-media, and recovery facts live only in its Dell
Target Pack. The first physical backend is a bounded AOT player for the canonical 241
frames: 160-by-90 logical pixels scaled to a top-left 480-by-270 framebuffer region,
30 ticks per second, two entities, and Escape-only exit.

The deterministic candidate identities are program
`1f33053936965726b66c92bf18fe929f6ea0244fbbf812faa6f51a3daecd40fe`, EFI
`afe6bb29cfdb5cdfdcf7acb375b3bbacdb344360365007a8f6aba4e1f3f5b834`, and disk image
`31d2dfb3cd8e8acdbf85893829022cf768f21c379b3bc4ea3409088cfa253480`.
Two headless QEMU screendumps show the orange cat and blue ball at distinct positions;
the first drawing bug that exposed only the cleared background was fixed by erasing
only prior sprite rectangles between frames.

The exact image was written to the reviewed Kingston removable USB and booted on the
physical Dell. The owner confirmed the orange cat and blue ball were both visible and
moving. The new evidence binds this observation to the same Creation, trace, Target
Pack, program, EFI, and image identities. No guest OS or internal storage participated.
Status is `PHYSICAL-DELL-SCENE-ANIMA-V2-OBSERVED`.

## Rabbit God Runtime v1 contract

`experiments/rabbit-god-runtime-v1/` begins the stable runtime that will remove USB
shuttling for ordinary world changes. It treats the physically observed Cat Creation as
the fallback active slot. A new world must arrive through `BEGIN`, exact ordered chunks,
and `COMMIT`; the runtime verifies complete length and SHA-256, authenticates the trusted
Creator's Ed25519 signature, reruns Inventory graph validation, and enforces authority
and resource ceilings before provisional activation. Health success commits and allows
a receipt; health failure restores the exact prior world.

The universal contract contains no machine facts. Its separate Dell Target Pack binds
package receive to passive QCA Rome BLE advertisement bursts and receipts to bounded
non-connectable advertising. The current signed Cat Inventory package is 20,329 bytes
and fits 2,542 of the target's 4,096 eight-byte payload frames. This is deliberately a
correctness-first path; a faster transport can replace the Target Pack later.

Hosted verification rejects corrupted, missing and reordered data, an untrusted signer,
stale in-boot counters, oversized packages, authority escalation, native package code,
internal-disk writes, and ambiguous JSON. It also proves failed health restores the
previous active slot. Runtime contract identity is
`d59a36fd72c85732f1f5986ff61bd9b84a190ccaa5e3e9b1f83711b9ac617438` and Dell Target
Pack identity is `821fc353b0d2ab19a44a735360998fcb66869a0ead570a26010bb7e175628141`.

`experiments/x86-64-uefi-god-runtime-v1/` now implements the Dell lowering as one UEFI
image. The compiler validates the Inventory package and emits a fixed 192-byte capsule;
the resident image independently performs Ed25519 verification, Creation/component/
authority/budget checks, passive BLE staging, provisional activation, a health tick,
commit-or-rollback, and a bounded correlated receipt. The Scene/Anima core advances the
cat and ball from live integer state instead of replaying the old canonical trace.

`python3 verify.py` passes the 30-frame round trip, negative signature/reorder/signer/
replay cases, health rollback, the same freestanding C crypto verifier linked into EFI,
and deterministic repeated image builds. v1.0 Linux disk identity was
`5c7705c210b7cbf377061e31b25e7c20c2803e3159f7ee987e1fca7b5b985dd4`.

QEMU on Linux x86-64 and macOS ARM64 visibly reached `RABBIT GOD RUNTIME v1.0`, then
failed closed at `TARGET NOT FOUND; NO DEVICE WRITE SENT`. Each report under
`experiments/x86-64-uefi-god-runtime-v1/evidence/` binds the unchanged generated source,
Runtime Core and Target Pack to its exact toolchain-local disk image. Different MinGW
versions produced different PE/EFI bytes, so cross-toolchain byte identity is not
claimed; repeated builds under either individual toolchain are deterministic. Neither
report claims physical Dell execution.

Physical v1.0 subsequently booted the Cat fallback but stopped fail-closed at
`MATCHING HCI EVENT NOT RECEIVED WITHIN BUDGET` before passive receive. The Mac therefore
repeated all 30 capsule frames without an ACK. Revision v1.1 retains a finite bound but
raises both HCI Command Complete searches from 8 to 32 queued events; this accounts for
asynchronous QCA events accumulated while the Scene bootstrap draws. No authority was
added. Exact Linux v1.1 image identity is
`6e43b77fd8efe702a5f2672743233311440b31124f27d7beff7f044a2abf8fb9`; its mismatch
path is QEMU-observed. Status is `GOD-RUNTIME-V1.1-QEMU-OBSERVED-PHYSICAL-PENDING`.
The dedicated USB currently contains v1.0. Next: reproduce v1.1 on macOS QEMU, prepare
and inspect the toolchain-local image, then perform the owner-authorized replacement of
v1.0. Cross-reboot anti-replay and transport encryption remain debt.

macOS ARM64 QEMU has now reproduced the v1.1 gate. Exact Mac EFI identity is
`f355f4e3dd88a572fcd81db2c09d5452cc63c7b6f822cce04c7e593aa3d4e6be` and disk image
identity is `dce38fc1e478fa016d19964e07a070dc545a3cf751caea431eec67f6615220f9`.
The report is archived as `qemu-macos-arm64-v11-observed.json`. v1.1 is eligible for
the dedicated removable-media replacement after a fresh device-identity check.

v1.1 was then installed on the dedicated removable USB and booted on the physical Dell.
The first signed 192-byte capsule (`SHA-256 49b4d2a552f6080f5f8eafdf446db3f18be2700903414ef93f3930d332bf3198`)
arrived in 30 BLE frames. Dell reported `CAPSULE HEALTHY: PROVISIONAL WORLD COMMITTED`
and advertised its bounded receipt; Mac received the exact correlated result
`TRANSFER=14 HASH=5B5A6C14 APPLIED_COUNTER=1` and exited normally. Evidence is
`experiments/x86-64-uefi-god-runtime-v1/evidence/dell-optiplex-3060-v11-capsule-physical-observed.json`.
Status is `GOD-RUNTIME-V1.1-PHYSICAL-SIGNED-CAPSULE-COMMITTED-ACKNOWLEDGED`.

v1.2 is the next immutable candidate. Reusable Creation Inventory v1 now contains an
original blue-grey toon cat, brown toon mouse, scurrying-mouse behavior, cat-chases-mouse
behavior, dedicated scene graph, and renderer. Their exact Merge identity is
`52c76a8592f5929e31af97e020325afa53f93a63c94bce06a1ba6159b6875609`.
God Runtime v1.2 trusts both the already observed cat-and-ball world and this new world,
without changing the 192-byte/30-frame signed transaction. Linux QEMU observed the
exact v1.2 image fail closed before effects when the Dell controller is absent. Next:
reproduce the v1.2 gate on macOS, perform one removable-media Runtime upgrade, then send
cat-ball at counter 1 and toon-cat-mouse at counter 2 without rebooting Dell.

macOS ARM64 QEMU has now reproduced that v1.2 gate. Its exact disk image is
`1bafa657b929c4a59ba6bb8e9136d61fbf5959a4622f77ef0c59061196dbd8e7`; the visible
result was `TARGET NOT FOUND; NO DEVICE WRITE SENT` with the full zero-effect cleanup
line. The screenshot-bound report is `qemu-macos-arm64-v12-observed.json`. v1.2 is now
eligible for the dedicated removable-media replacement.

## Rabbit God Runtime v2 universal package candidate

The owner rejected another firmware-baked scene and approved the stable boundary:
one Runtime image on USB, then complete data-only worlds over Bluetooth. The new
`experiments/x86-64-uefi-god-runtime-v2/` implements that boundary rather than adding
another trusted scene id to v1.

Rabbit Universal Package v2 carries a palette, arbitrary indexed sprite frames within
budget, multiple objects, initial state, and bounded Rabbit VM behavior bytecode. The
first physical profile accepts up to 4096 signed bytes, 16 palette entries, 16 sprites,
16 objects, 16 programs, 16 animation frames per sprite, and 32 VM bytes per program.
It explicitly rejects native code, arbitrary memory access, unknown opcodes, invalid
references, stale in-boot counters, signature changes, chunk loss/reorder, and budget
overflow.

BLE framing v2 changes the chunk sequence from 8 to 16 bits and carries six package
bytes per UUID frame. The positive large-package regression uses 301 frames, proving
that the old 255-frame ceiling is gone. Dell assembly delegates accepted frames to a
static 4096-byte staging area in the freestanding C core. A complete package is checked,
health-stepped, copied into the active RAM slot, rendered from its own resources, and
acknowledged; failure leaves the prior active package untouched.

The included `worlds/cat-chases-mouse.json` lowers to a 310-byte signed package and 54
BLE frames. It contains two sprite assets, two objects, and two independent programs;
the firmware contains only the generic decoder, renderer, VM, transport, and hardware
bindings. The exact Linux artifact is EFI
`ae918f2e8641bc5a53ae0d3125b5bfa8f300df2b172a160118976da0ce4bc35d`, image
`d9798fcea80993cf056c3146c993f42458d6c6d4922615c9ac7df81614c76613`.
QEMU 10.2.1 visibly showed `RABBIT GOD RUNTIME v2.0` and failed closed at the missing
Dell controller with zero device, package, framebuffer, and radio effects.

Next: reproduce the v2 QEMU gate on the owner's Mac, run `prepare_physical.py`, perform
one reviewed replacement of the dedicated USB, then send counter 1 and counter 2 worlds
with `send_package.py` without moving USB or rebooting Dell. A power cycle intentionally
clears received worlds in v2 because persistent storage writes remain forbidden.

## God Runtime v2 physical receipt and text builder — 2026-10-01

The owner installed the Mac-built v2 image (EFI
`f0c9622195477487786e11ca1468236ddb21e36c69c1233341dfc621083b2d8e`, disk
`533883793a17d70b1d133f8fec2c03441c52ec8be3ba2880e3f18278242ed26c`) and booted
it on Dell. The first 310-byte world arrived in 54 frames without moving USB again.
Mac reported `ACK RECEIVED: TRANSFER=AB HASH=E1DEA1AB APPLIED_COUNTER=1`; the owner
then confirmed that the cat chases the mouse. The exact compiled package SHA-256 is
`ccd9a10ad43e96c2bddcc58a3b2c2ce1643e250d944df241ece3aefa9ec210bb`.
This is owner-observed physical behavior plus a correlated receipt, not authenticated
Dell attestation. The next package in that boot must have counter greater than 1.

The new text path is `experiments/x86-64-uefi-god-runtime-v2/ask_world.py`.
It calls OpenAI Responses with strict structured output, using `OPENAI_API_KEY` and
default `gpt-4.1-mini` (configurable). The key never enters model input or saved reports.
The proposal is locally schema-checked, compiled/signed, independently decoded, and
transport-roundtripped before optional `--send` invokes the proven sender. Saved
candidate mode allows any external LLM output to enter the same checks. Unsupported
requests fail explicitly. Runs are archived locally in ignored `runs/`; use explicit
`--base` for iterative edits, and explicit `--counter` for the current Dell boot.

`verify_llm_world.py` passes offline tests for API request shape, refusals/incomplete
outputs, invalid opcodes, references, geometry, booleans, budgets, unknown effects,
send gating, receipt status, and missing credentials. No live API call or new physical
LLM-generated world has been tested here because this environment has no API key.
Next: set the key locally on Mac and run a visible pink/faster-cat request at counter 2.
No Runtime upgrade or USB rewrite is needed for this text-builder step.

## Codex subscription text provider — 2026-10-01

The owner requested existing Codex subscription access instead of a separately billed
API. `ask_world.py` now defaults to `--provider codex`; the API remains explicit opt-in
with `--provider api`. `codex_world.py` calls local `codex exec` with ChatGPT-only auth,
ignored user config, read-only sandbox, disabled shell tool, ephemeral session, JSON
schema and final-output file in a disposable directory. No auth token is read/copied,
API key environment variables are removed, and there is no API fallback. Timeout,
CLI failure, missing/oversize/malformed output stop before signing/transmission.
The existing deterministic validation/signing/send/ACK path and Dell artifact are unchanged.

All 15 offline text-builder tests pass, including provider selection, CLI auth/command
boundaries, invalid output, no-fallback, and send gating. No live Codex request or new
physical world is claimed. Next on Mac: install/update CLI if needed, `codex login`
using the subscribed ChatGPT account, then ask for a pink/faster cat with a counter
greater than the last accepted one in this Dell boot. No USB move or rewrite is needed.

## Detailed mouse graphics v3 candidate — 2026-10-01

The owner approved a recognizable smooth mouse preview, then one graphics Runtime
upgrade. `experiments/x86-64-uefi-god-runtime-v3/` is separate from working v2.
Built-in imagegen produced a transparent original brown mouse; exact prompt/source
hash/import recipe are preserved. The reference carries a 128x128 frame, 256 RGBA
palette entries, bounded RLE, alpha blending and 32x32 logical display size. Existing
VM motion is preserved; a multi-pose walk cycle is not claimed. Optional PNG import
against the owner's latest v2 world preserves their pink cat. Art is reusable data,
not embedded in EFI; publishing license/Inventory v1 integration remain unclaimed.

v3 accepts unchanged v2 packages and signed RUP3 packages up to 65535 bytes, 262144
decoded pixels, 16 sprites/objects/programs, 128x128 source and 64x64 display geometry.
Thirty-two-chunk prefix receipts make retries local; exact repeated final COMMITs
re-advertise without applying twice. Prefix ACK means staging only, not authenticated
application. The 8979-byte reference takes about 13 minutes at the inherited six-byte/
450ms advertisement rate; this is a calculation, not a live performance observation.

Ten host tests cover exact Python/C acceptance, alpha and bounded 240-tick rendering,
legacy byte identity, signatures/replays, invalid RLE/decoded limits/JSON/VM, rollback,
and idempotent block/final-ACK retries. Repeat UEFI builds match. Linux QEMU visibly
reached v3.0 and failed closed at the missing device; screenshot/source/artifact bound
evidence is archived. Exact Linux EFI is
`b619505ae1f8e05815842217d8682aeef882f21e9bd2a658b39720fea56d14d6`, image
`2750397e9cfdb6efaa5b3e2f7a0d72c2be3d5be0632e183761059fe8a0db1618`.
No physical write occurred. Mac sender compilation, real checkpoint ACKs and physical
detailed mouse remain pending. Next: preview on Mac, exact local QEMU gate, read-only
preparation and fresh USB identity before one installation. Existing Codex builder
still targets v2; resource-reference editing and faster transport are future work.

## Wireless runtime updates prioritized — 2026-10-01

The owner paused graphics v3 installation and requested runtime updates over Bluetooth
first. Installed Dell remains v2. Do not call another candidate the final flash image;
current v2 cannot acquire an updater through its bounded data-only VM.

`experiments/runtime-update-contract-v1/` implements a NON-EXECUTING host reference:
domain-separated RRT1 Ed25519 envelopes, target/base/state/ABI bindings, separate owner
authority rejecting the known world development key, ordered 256KiB RP v3 transport,
and trial/commit/retain-old/duplicate-receipt/reboot model. Ten tests use non-executable
opaque fixtures. No native code, Bluetooth, UEFI loader, real health observation or
automatic watchdog runs. No completed wireless runtime updater is claimed.

Next decision is privileged owner-reviewed native modules versus isolated portable
modules. A signature and saved RAM copy do not sandbox native code or recover a hang.
Remaining gates: key lifecycle, real supervisor ABI, QCA ownership, quiescent state,
stream/checkpoint I/O and throughput, execution/isolation, observed fault recovery,
then exact bootstrap/QEMU/physical tests. No USB write occurred. Persistence remains
forbidden; future RAM updates revert to bootstrap on power-off.

## Owner-approved native supervisor execution — 2026-10-01

The owner selected separately reviewed privileged machine-code updates, rather than
isolated VM modules. This expands runtime-release authority only; ordinary data worlds
remain under their prior no-native-code boundary. No production private key or physical
installation was requested/performed. Do not treat signatures as native-code isolation.

`experiments/x86-64-uefi-runtime-supervisor-v1/` now executes actual signed PE32+ UEFI
boot-services drivers loaded from bounded assembled RP v3 RAM frames. The resident
supervisor verifies domain-separated Ed25519, SHA-256, target/base/state/ABI and in-boot
counter, validates PE and callback addresses, runs init/one tick on copied state and
commits or retains the exact old driver/state. Successful swap unloads the prior driver;
exact latest completed retries return a cached result without re-execution. No payload
allowlist is baked into the loader: the separately trusted owner's signed envelope
authorizes the exact release. `owner_key.py` supports random owner-local 0600 raw keys,
no-overwrite and explicit reviewed-hash signing; keys are unencrypted, never sent, and
rotation/authenticated receipts remain pending.

Ten previous model tests and nine native host tests pass (C/Python signatures, SHA
differential boundaries, PE rejection, key/signing safeguards, streamed lost/reordered/
corrupt chunks, checkpoint retries and >65535-byte assembly). Automated QEMU repeats
identical builds and observes two native replacements in one boot, receipt-only retry,
failed init retaining B's exact state/identity/handle, signature/counter/ABI rejection,
then a marked infinite native init loop triggering the firmware watchdog. QEMU reboots
into the unchanged bootstrap without relaunching volatile candidates. Exact report/log
are under the probe's `evidence/`; this is emulator-only evidence. Recovery covers the
reviewed interrupts-enabled loop, NOT memory corruption or disabled interrupts/watchdog.

The probe forbids physical installation and uses public test fixtures. It has no live
Bluetooth adapter, no full Scene/Anima module ABI and no Dell watchdog observation.
The working physical Dell remains God Runtime v2. Next: resident Scene/Anima ABI and
actual Mac/QCA streaming/result adapter with explicit quiesce/state export, then owner
key provisioning and separately gated bootstrap/physical tests. The six-byte/450ms
transport remains slow (~128 minutes per 100KiB); RAM updates vanish at power-off.

## Resident Scene and wireless native dispatcher — 2026-10-01

The owner requested connecting Bluetooth and Scene/Anima to the native loader.
`experiments/x86-64-uefi-wireless-supervisor-v1/` implements the real QCA assembly
adapter for world RPv2 / native RPv3, separate staged/applied/rejected native ACK
families, Mac checkpoint sender and explicitly reviewed owner-local signing.
The hardware controller, physical GOP and Esc/radio cleanup remain in an immutable
supervisor. A real resident UEFI boot-services Scene driver reuses unchanged v3
world validation, RGBA/RLE graphics and VM. Its reviewed ABI renders offscreen.

RRT2 is a distinct signature domain/profile, not a silent weakening of RRT1. It
signs the immutable active world revision while the world continues moving during
assembly; the cooperative swap locally exports/imports exact canonical RSS2 state
(package, positions/velocities/frames, tick and world counter) before one health
tick and driver swap. A changed world rejects the release. Failed authorized trials
consume their native counter, retain the old scene/pixels and cache their status.
Exact latest final retries advertise status without re-execution. Candidate native
code is privileged, not isolated; callback/unload watchdogs cannot guarantee recovery
from memory corruption or disabled interrupts/watchdog. Dell recovery is unobserved.

Host checks cover signature/profile/key/counter/PE gates, canonical live snapshots,
unchanged RUP2 and full RUP3 graphics with framebuffer canaries, failed trial, chunk
checkpoint retries, sender family separation and explicit create-only signing/dry-run.
Ten legacy model and nine prior native tests remain passing. QEMU integration loads
two replacement Scene drivers in one boot, observes moving state during staging,
exact retry idempotence, failed health retaining the old live world, and tamper
rejection. That harness uses embedded canonical frames instead of physical radio;
it is NOT linked into the real receiver. Repeat image/module builds match. Exact
test artifacts and source/firmware bindings/logs are archived in the new evidence.
The actual QCA receiver separately fails closed in QEMU before device effects.

Early real-bootstrap captures showed only firmware text while an instrumented image
displayed the expected stop. Timing alone was not a sufficient explanation. Legacy
caller-frame string conversion was replaced with bounded supervisor-owned ConOut
for initialization (the prior receiver helper is retained); the unmodified selected receiver visibly reaches the
expected title and no-device/no-reset/no-HCI/no-scan/no-radio stop. Capture remains
manual visual confirmation, not automatic OCR. Native modules use a smaller stripped
driver-only linker profile; mixed assembly bootstrap retains the prior normal profile.

No owner production key was generated and no physical medium was changed. Public
fixture keys cannot build a production candidate or be sent to physical devices.
Installed Dell remains v2. Next: owner-local key generation/provisioning, exact Mac
bootstrap gate, separately approved bootstrap installation, real Mac compilation,
live staged/applied/rejected ACKs, two native engine swaps and Esc/watchdog Dell
checks. The immutable supervisor/QCA bootstrap/root key remain non-updatable via
this Scene ABI; changing them still needs a bootstrap release. No last-ever USB
promise. RAM updates/worlds disappear at power-off; authenticated ACKs and cross-boot
freshness remain debts. The reviewed Linux module is ~25KiB and takes ~35 minutes
minimum through the inherited six-byte/450ms advertising transport.

## Physical wireless supervisor and interrupted native transfer — 2026-10-01

The owner generated a local key (public SHA256
`58744820acd038de35d01eaf6afbad2aa4bb4e4022c8078d4e665270d41f36b4`), observed the
owner-provisioned Mac bootstrap fail closed in QEMU, and explicitly approved fresh
external DataTraveler Duo `/dev/disk4` replacement. Mac image SHA256 was
`996e4414e1a3fd2f752a8fdf1bea1f39f52ebc03e07ec6b7b5aef5d9446f1ba0`, EFI
`7c89a1f32d40f9322e784d0eb8fdce8af6bce42b5635d01a0a843661dbef2746`. Dell photo
shows supervisor/QCA/passive receive ready. Unchanged cat/mouse world counter 1 gave
`TRANSFER=AB HASH=E1DEA1AB APPLIED_COUNTER=1`; the owner confirmed moving objects.
This is owner-observed behavior/correlated receipt, not attestation.

Mac Scene revision 2 SHA256 is
`e1faf6f5de1d2eb18305bf4a1e66b300e9005e69fb72ac89be1c7e2d330f72eb`, baseline
`04a43128cf923697e495e213205f03259b1e01ea5ecda00b4437c64f19e644e0`, target
`254bd9b5e7b127651217e1206ac992b49326fb89b6627fa1062ea4373429609b`. Native
transfer repeated chunks 0x0720..0x073f/checkpoint 0x0740 (block 58), transfer 93,
without a matching ACK in the supplied tail. Owner stopped it; the world kept moving.
No native application is claimed. Later world replay gave the exact counter-1 ACK
again. Reboot completion was not independently observed. Missing payload versus
missed ACK remain hypotheses, not a diagnosed physical cause.

Mac sender now journals exact confirmed progress/full logs, limits per-block attempts,
and implements explicit same-boot `--resume` / confirmed-reboot
`--restart-after-reboot`. Resume probes the NEXT unconfirmed checkpoint then replays
that block; unchanged receiver C rejects a previous checkpoint after partial later
assembly. Ctrl-C/timeout stops child advertising, retaining progress. Atomic journals
bind release/world/owner/target/base/counter/transport and refuse mismatches or silent
restart. ACKs are unauthenticated. Only Mac adapter/helpers/tests/docs changed;
installed supervisor and Scene PE remain unchanged. Old non-journaled sessions cannot
be resumed by this mechanism. Default dwell remains 450ms, with explicit 450..2000ms
tuning (not a proven physical fix). Next: compile on Mac, fresh native transfer with
confirmed clean receiver state, Ctrl-C/same-boot resume, final receipt and two live
replacements. No USB rewrite is required. Dell watchdog recovery remains unobserved.

## Block 58 parser diagnosis and Mac-only workaround — 2026-10-02

The owner supplied the exact signed RRT2 release SHA256
`d16b740da692ab45e680cb0a91304ffd9559e129026865889a0c76b6c33b01db` (25,344 bytes).
Owner public fingerprint, signature, payload/world/target/base/counter verified.
The unchanged C assembler accepts all 132 blocks, but the extracted installed assembly
UUID scanner rejects block 58/frame 32
`52503293-3F07-488D-5250-4881F9520AE8` in a synthetic legacy HCI report. Payload RP
bytes create an earlier false reversed-window match; failed validation exits the event
instead of searching onward. This reproduces the exact observed stopping point. Radio
capture is absent, so live explanation confirmation remains the resumed physical test.

Sender `--uuid-order reversed` reverses only advertised CBUUID octets, not signed native
bytes or transport hashes. Resume keeps the existing 57-block journal, probes/replays
block 58 and uses the already supported alternate UUID order. The exact release's
4,357 synthetic HCI frames all pass the extracted x86 assembly in this mode; standard
order rejects just that blocker. The partially staged receiver resumes past it without
reset/BEGIN and reconstructs exact bytes. No native payload execution occurs in these
diagnostics. `verify_uuid_order.py` preserves this boundary regression; non-x86 hosts
use an independent scanner model. This is an exact-package/layout workaround, NOT a
general repair of the blind HCI window search. Robust AD parsing remains future
supervisor work. Live workaround success/final native application remain unobserved.
No supervisor/module source, firmware image, key or signature changes; no USB rewrite.

## Owner-confirmed native swap and walking-cat art — 2026-10-02

The supplied Mac log reached native checkpoint 132/132 and final applied receipt
`TRANSFER=93 HASH=70E75893 APPLIED_COUNTER=1`. The owner confirms the preserved
cat/mouse world moves. This supersedes the preceding pending native-application
status, but is an owner-observed correlated receipt, not attestation or a watchdog
recovery test. No Dell reboot since that successful swap is reported.

Requested one higher-quality cat, not a mouse. Built-in imagegen generated a
four-pose ginger-tabby sheet with actual RGBA alpha. V3 `import_cat.py` performs
only cell extraction/resizing/shared-palette export, not hand-painted substitute
art. Source PNG, both exact prompts, provenance, exact-pixel local GIF and portable
world are under `experiments/x86-64-uefi-god-runtime-v3/`. Four source poses are
128x85, displayed at 64x43 logical / 192x129 surface pixels, using the existing
MOVE/BOUNCE/ANIMATE program. No native/supervisor image change is required.

Twelve graphics/import Python/C tests pass, including exact re-import, actual C VM
240 ticks/framebuffer guards/replay rejection. All segmented frames pass extracted
installed assembly in synthetic legacy HCI reports in standard UUID order. No
radio capture is claimed. Counter-2 package: 33,349 bytes, 5,561 ordinary frames,
174 checkpoint blocks, minimum 48.2 minutes at 450ms dwell, before losses.

**Art is NOT SENT / physical appearance pending.** Show the preview and obtain
owner approval before the long live send. Same-boot world counter 2 assumes the
current world counter remains 1. No reboot or flash movement is needed.
Current VM lacks velocity-dependent sprite facing: right-facing cat walks backward
on the return leg. Preview/docs explicitly disclose this; natural turns need an
additional engine capability, which can now be delivered through the native channel.

## Connected file channel — host core, integration BLOCKED — 2026-10-02

Owner requested a real Bluetooth file connection instead of 48-minute advertising
transfer. `experiments/ble-connected-file-transfer-v1/` adds a bounded C file receiver
and ATT/GATT subset plus Mac central source and a preparation-only adapter. Twelve
host tests exercise the ACTUAL existing C Ed25519/world bounds/health/renderer,
including detailed cat, corruption/reorder, reconnect offsets, duplicate writes,
lost final reply, rollback-by-retaining-old-world, replay and malformed PDUs.
Signature/health commit is separate from ATT acknowledged writes. Connected worlds
only; no native execution authority inferred from the world development key.

Status is NOT INSTALLED / NO PHYSICAL FAST LINK / MAC COMPILE UNVERIFIED. Neither
ACL/L2CAP nor a live USB adapter is implemented here. No throughput result claimed.
No bootstrap/native image or owner key changed, no packet transmitted.

Important correction to the prior proposed wireless rollout: the installed Scene
ABI supplies no exclusive HCI event ownership. Immutable legacy assembly still
reads the USB interrupt endpoint and ignores connection/disconnection/credit events.
Two independent readers are unsafe; a privileged Scene module's UEFI access does
not itself provide a checked handoff/rollback/callback-cleanup mechanism. The native
updater swaps Scene drivers, NOT this supervisor/radio loop. Do not promise that a
connected receiver can be safely deployed by merely swapping a Scene module.

Next owner decision: approve a reviewed supervisor/radio-handoff design, with a
possible separate bootstrap installation, or restrict progress to proving a
no-bootstrap-rewrite takeover mechanism. No physical rewrite is authorized by this
request; do not instruct another flash replacement silently. Old Dell/world/slow
channel remain unchanged and working. Cat art has not been sent this turn.

## Cat owner observation and connected lower layers — 2026-10-02

Owner reports "котик уже ходит по экрану:)" and asks to record success without a
photo. V3 `evidence/dell-cat-walk-owner-observed.json` records appearance and motion
only. No exact ACK, packet identity, independently verified counter, photo or
measured time was supplied. Candidate world/hash/counter bindings are contextual,
not observed/attested. Pending-appearance status is superseded; facing limitation
remains. Owner permits one future bootstrap installation, with the intent of
updating both engine AND Bluetooth driver wirelessly thereafter. This is NOT
approval to write an unidentified current disk.

Connected experiment now has a C HCI/ACL/L2CAP layer: sequential command-complete
setup; controller/shared buffer queries; connectable advertising; exact connection
handle; credits; bounded fragmentation/reassembly; arbitrary USB bulk stream
splits/coalescing; reconnection retaining RAM staging; pairing rejection. Twenty-one
link/file/GATT tests pass, including exact signed cat data carried through simulated
connected ACL into existing C Ed25519/health/renderer.

Candidate UEFI `usb_port.c` binds read-only exact VID/PID/interface/endpoints,
releases handle lists, polls as sole reader, submits bounded control/bulk output,
and confirms advertising-off/disconnection before declaring shutdown. Four mock
UEFI tests pass. MinGW object compilation passes. No real USB, BLE connection,
asynchronous callbacks or throughput result. No bootstrap image/native release
has been built or sent in this increment; installed Dell and keys are untouched.

Still NOT INSTALLABLE: exclusive supervisor dispatcher, owner-authenticated
combined radio/Scene driver updates and unload/rollback/watchdog/Esc gates must be
completed together. Do not ship a fast but fixed radio bootstrap recreating the
current trap. Mac compilation and physical interop remain pending. See connected
README migration gates. No Mac action or flash movement required yet.

## Connected supervisor pre-installation review — 2026-10-02

Owner requested checking the new supervisor and permits one bootstrap rewrite.
Review result is NOT READY FOR INSTALLATION: there is no integrated new supervisor
EFI/image yet. Do not imply the existing component tests constitute that artifact.
Sole-reader dispatcher plus owner-authenticated combined radio/Scene driver
updates, unload/rollback/watchdog/Esc and two driver swaps/recovery QEMU gates
remain outstanding. No fresh Mac disk identity was supplied this turn.

Fixed USB shutdown false-positive: Command Status acceptance does not prove
advertising-off; neither Status nor unexpected Command Complete for Disconnect
proves Disconnection Complete for the exact handle. Hardware Error fails closed.
Four regression cases added; eight mock-UEFI tests plus 21 link/file/GATT tests pass.
MinGW freestanding USB object compiles with -Wall -Wextra -Werror. No real USB/radio,
owner keys, image installation or current Dell world touched. Do not give a dd
command using historical disk4/disk10 or install an old fixed-radio image instead.

## Connected combined-driver supervisor candidate — 2026-10-02

Owner requested finishing the unified image before the approved one bootstrap
migration. `experiments/x86-64-uefi-connected-supervisor-v1/` now builds an actual
deterministic EFI/FAT candidate, not merely USB object files. The QCA RAM prefix
chains directly to a new C root loop, NOT the old assembly interrupt reader.
ABI3 owner-updateable driver includes Scene/VM AND HCI/ACL/ATT/USB code. The root
owns file staging/final receipt, dispatch, watchdog/timers, signature/loader and
framebuffer. Baseline world is EMPTY; old/new downloaded worlds/drivers remain
RAM-only. No last-ever-USB promise for immutable root/ABI/hardware changes.

RRT3 is a distinct ABI3/state2/domain-separated owner envelope bound to target,
base, payload and active signed world. Public world Creator cannot authorize
native modules. Trial imports/exports exact RSS2 state on copied pixels, health
ticks without radio attach, retains old driver on failure. Native commit is
deferred until the ATT/poll callback returns, so the old module is not unloaded
with code on its stack. Old radio close must be confirmed before unload; candidate
attach failure reattaches old. Unknown cleanup/unload fails under watchdog.

Root-owned file kind1 world (65,535), kind2 native (262,144), state4 pending.
Pending forbids abort/substitution/data and repeats no apply; explicit root finish
produces final receipt. Native/world counters remain separate, uint32-receipt
bound, in-boot only. Authorized failed trials consume native counter. Mac source
adds bounded reconnect/query of the SAME session after deliberate swap disconnect;
no actual Mac SDK compilation yet. `send_file.py` compiles only by default, explicit
--send needed to start Bluetooth; private signing remains owner-local/create-only.

Nine owner/deferred/bundle host tests, 23 actual C world/GATT/HCI tests and ten mock
UEFI USB tests pass. Connection-before-enable-complete is preserved. Shutdown
tracks connection-during-close, requires actual disconnection and a final confirmed
HCI Reset barrier. New repeated Reset/reattach behavior still requires Dell testing.

QEMU with actual compiled resident UEFI drivers and MOCK USB carried signed world
and owner files through ACL/L2CAP/ATT into root staging, performed TWO combined
driver swaps in one boot, receipt-only retry, exact failed-health/tamper state
retention, then firmware watchdog recovery from reviewed interrupts-enabled hung
init to baseline. Separate actual root loop test exercised timers and Esc with
confirmed close/unload. These are emulator/mock-USB tests, not physical Bluetooth,
speed, arbitrary-native isolation or Dell watchdog proof. Linux exact no-QCA
bootstrap screenshot was visually inspected with title and all fail-closed lines.

Next on Mac: git pull; run `python3 preflight.py --owner-public
"$HOME/.rabbit-owner/runtime.pub"` in the new experiment. It runs host/QEMU gates,
compile-only Mac sender, repeated owner-public build, exact interactive Mac QEMU
observation, and read-only external disk listing. No private key read, radio send,
unmount, erase or device write. After checking expected missing-device lines, close
QEMU and answer YES. Then inspect its image/report plus FRESH external-medium info
before the separately approved write. Installed Dell/walking cat are untouched;
do not reboot it or move USB during the Mac-only preflight.

## Mac preflight interrupted and sender property repair — 2026-10-02

Owner Mac passed 42 host checks, mock-USB native swaps/watchdog and actual root
loop Esc QEMU checks. Compile-only sender exposed an Objective-C `hash` property
conflict with NSObject: NSData storage/setter synthesis was not reliable. Renamed
it `expectedDigest` at declaration, initialization and exact final receipt check;
the two related compiler warning classes now fail compilation. A source regression
checks this fix, but Apple SDK recompilation remains owner-side pending.

Owner screenshot shows connected v1.0 fail-closed no-device gate for Mac candidate
image `1627487b491dd1c4b496a936075c9dc6b0bfab6f0a5405b2ba485b699f9cc855`.
Ctrl-C interrupted the Python parent before YES/report save. This is not an
observed physical Bluetooth failure and does not open installation. Rerun updated
preflight, close QEMU using its window close control (not terminal Ctrl-C), answer
YES and supply report plus fresh device identity. Sender-only change does not
change runtime C, but source bindings change, so obtain a fresh complete report.
No media or physical radio was changed.

## First physical connected attempt — 2026-10-02

Owner verified fresh external DataTraveler Duo disk4 and owner Mac candidate image
1627487b491dd1c4b496a936075c9dc6b0bfab6f0a5405b2ba485b699f9cc855, then
reported exact installed EFI e9ce08113bdd3a2824ecd59203994e7a2c2932b0e58a8a9e5978ee408ceb1da1.
Dell displayed CONNECTED FILE SERVICE STARTING; ESC TO STOP. New sender compiled
without property warnings. Cat world counter1 package SHA256
f2dedcd16ad2987aa5740748af88873fc048f23b761aa01f995c159cb7651113 was prepared
in /tmp/connected-cat-world-1.rup with saved /tmp/connected-cat-session-1.json.
Mac logged reconnect then 300-second timeout; owner says Dell screen unchanged.
No cat application, live throughput or cause of disconnect established. Unchanged
screen alone does not prove receiver is alive or frozen. Correction: the original
root fatal path already printed a generic watchdog warning; it did not identify
the failed stage, and driver poll did not print state/error diagnostics.

Mac-only diagnostics now log discovered peripheral/RSSI, successful connection,
service/characteristic discovery, BEGIN/write limit/control ACK and disconnect
phase/offset/NSError domain/code/reason. stdout unbuffered. This changes neither
installed EFI nor protocol or saved session. Next rerun SAME bundle once to locate
failure; no bootstrap rewrite, owner key change or new radio action performed here.

## LE outgoing flag repair and Dell-visible diagnostics — 2026-10-02

Fresh owner attempt after reboot discovered Dell RSSI -63, connected, then
disconnected during service discovery with phase0/offset0, NSError absent. No
successful world application or physical cause is established. Review reproduced
an actual C reply header 40 20 with PB=10, forbidden for LE Host -> Controller
by Bluetooth HCI section 5.4.2. PB=00 first/PB=01 continuation now replaces it;
incoming Controller -> Host PB=10 remains supported. Prior tests reconstructed
payloads while missing the direction-specific header violation: admitted test gap.

Owner explicitly requested fix, regression, visible Dell diagnostics and QEMU
verification, NOT another physical write. All outgoing headers are asserted in
host request helper; explicit small-controller fragmentation test added. QEMU
mock bulk-OUT rejects wrong first PB/BC/handle. 24 actual C link/world tests,
11 mock-UEFI USB tests and 10 owner/deferred checks pass. Poll error categories
preserve bound/unknown-outcome state. Driver logs advertising/connection changes,
error code/state/HCI opcode; root logs fatal stage before existing watchdog.
No second endpoint reader or module-owned async callback was introduced.

Actual UEFI QEMU strict-header integration again observed two driver swaps,
receipt-only retries, failed health/signature retention and hung-init watchdog
return; actual root loop Esc cleanup passed. New fault fixture injects bulk-IN
EFI_DEVICE_ERROR, captures/forwards real ConOut messages: error5/linkstate2,
RADIO POLL fatal stage and watchdog recovery, then reboot. Screenshot visually
checked with readable exact messages. Fixture fault/proxy absent from real image.
Reports/logs under connected evidence bind corrected sources and exact test
artifacts; these remain mock-USB/emulator observations, not a physical fix proof.

New Mac preflight includes the fault test. Corrected owner-key image must be
built/observed on Mac again, and corrective USB installation requires new explicit
owner approval plus fresh device identity. Installed old connected candidate,
owner key and physical medium untouched by this repair turn. Do not reuse old
Mac image/report approval or imply a working wireless delivery of this repair.

## PB-fixed physical retry and raw-event diagnostic candidate — 2026-10-02

Owner Mac preflight passed 45 host checks, all QEMU gates and exact no-device
screen; corrected owner image SHA256
62922e4c5dfec4df9c7f9661c8691159fe44761b9075dee46cbc404f83ecfb2e.
Owner separately authorized corrective USB replacement, fresh disk4 DataTraveler
Duo identity matched, 64MiB dd succeeded, installed EFI verification returned
359fa04010a510a558890f6a92c0f58e7bc777127b9cbe3b5ac8ce41abd77a9a.
Dell showed BLE FILE SERVICE ADVERTISING; READY TO CONNECT. Same saved cat session
still connected then disconnected at phase0/offset0 with no NSError. Photo shows
no BLE CONNECTED or error line. PB defect correction did NOT establish interop or
the actual physical cause. Esc produced an unread line then UEFI no-disk alert;
owner confirms manually powering off afterward. This proves key response, NOT
confirmed radio cleanup. Dell has RAM but no internal storage; do not confuse them.

Owner requested raw Bluetooth event diagnosis. Candidate RlUsb observes the
existing sole interrupt read BEFORE parser validation: status/result/reported
length, successful-byte prefix24, saturating read/timeout/poll counters. Driver
prints max48 observations per attach, actual bytes only after successful bounded
reads, and four bounded poll-count heartbeat samples. Unchanged-length timeout
is NOT data; failed/oversized reads never expose uninitialized bytes. Malformed
length/unhandled LE subevent labels are diagnostic, NOT parser fixes. No event
acceptance, extra reader, command, async callback or radio authority change.
Console output may perturb timing; no throughput claim.

Three new actual mock-USB tests cover parser-ignored raw bytes, timeout versus
partial read metadata, prefix bounds and oversized lengths. New QEMU fixture
injects malformed length and unknown LE subevent, then valid connection and
USB bulk-IN failure. Observer checks actual ConOut raw bytes/classifications;
visible screenshot inspected. Existing driver-swap/idempotence/rollback/hung-init
and root-loop Esc QEMU gates pass with this diagnostic driver too. No owner key,
physical packet capture, radio operation or medium write performed here. Next:
fresh Mac preflight; diagnostic installation is a new physical write and still
requires separate explicit owner approval and fresh identity/hash checks.

## Physical missing-connection event investigation — 2026-10-03

Owner installed the separately approved raw diagnostic image from Mac
owner-gate-jf9qj9iy: image b9a041cf2d019c6ed14f03fde4f818bd3d5e6b8d96894336a431d1776297622d,
verified EFI 124574956747813909cc35d5c8a541b427559961e2a4229fe56327588fde9149.
Baseline photo shows seven successful command completions and advertising ready;
LE buffer query reports 123 bytes/16 buffers. SAME saved cat session then logs
Mac connected/disconnected at phase0 offset0/33381. Follow-up Dell photo shows
exact successful input 05 04 00 01 00 13, reads8 and timeouts0000FFF8, but no
connection event, no parser warning, and no application. Reason13 indicates remote
termination, not its underlying cause. Likely peer Mac is contextual, not identity
authentication. The interrupted read/firmware behavior remains unobserved.

Added tests only; production C, masks, timeouts, sender and installed image are
UNCHANGED. Actual C-generated general mask 10 E0 04 00 00 00 00 20 independently
matches spec bits4/13/14/15/18/61; LE mask1F enables legacy connection complete.
Actual adapter accepts a synthetic full21-byte connection with handle1, and link
accepts the observed controller buffer sizes. 26 link/world/GATT plus16 mockUSB
checks pass. A deliberately synthetic timeout with unchanged requested length
shows the diagnostic ambiguity: no valid-byte observation, then only disconnect.
That fixture does NOT establish Dell losing bytes or validate a timeout repair.

Current interrupt timeout is1ms with a260-byte requested buffer. Bluetooth USB
permits an HCI event to span multiple USB transactions; actual Dell interrupt max
packet/interval have not been recorded here. EDK2 Xhci.c XhcTransfer cancels timed
out requests; this is reference implementation behavior, NOT proof of Dell firmware
implementation. Suspected timing/USB loss versus controller event suppression
cannot be distinguished from the current photos. Do not blame GATT or report a fix.

Proposed next controlled diagnostic candidate: record actual interrupt descriptor
packet/interval and submitted masks; compare bounded20ms read timeout to baseline1ms
while retaining sole-reader ownership and cleanup gates. No such candidate or
physical installation is authorized/performed by this diagnosis turn. Stop Mac
sender; retain powered Dell/session. New installation requires separate approval.
Primary references: Bluetooth Core HCI Set Event Mask / LE Set Event Mask,
USB Transport Layer, UEFI USB synchronous interrupt transfer, and upstream
https://github.com/tianocore/edk2/blob/master/MdeModulePkg/Bus/Pci/XhciDxe/Xhci.c.

## Bounded20ms connected candidate — 2026-10-03

Owner requested implementing progress toward the fast channel. Candidate changes
interrupt-IN timeout1->20ms in polling and confirmed-close searches; bulk waiting,
event masks, GATT/file/signature/world semantics are unchanged. RlUsb retains actual
interrupt descriptor max-packet/raw bInterval and exact mask bytes after successful
control submission. Driver prints these once per attach/submission, with20ms shown
as hex00000014. No second reader or asynchronous callback; same unknown-cleanup
and watchdog gates. Console traces may affect timing; no throughput claim.

55 host checks pass (11 owner/deferred/observer,26 actual link/world/GATT,18 mockUSB).
Independent mask bits, observed123-byte/16-buffer profile, synthetic full21-byte
handle1 connection, timeout ambiguity, descriptor provenance and actual submitted
mask observations are covered. Mock timing threshold2ms is deliberately synthetic,
NOT a Dell measurement; it rejects the old1ms policy in the fixture.

All three QEMU gates pass with actual compiled UEFI drivers and MOCK USB: two
combined swaps/receipt-only retries/state retention/hung-init watchdog, actual
root-loop Esc close, and real-ConOut raw/mask/endpoint diagnostics followed by
deliberate bulk failure/watchdog. Diagnostic screenshot visually inspected;
current public-fixture candidate image40780501139236284fe30725d27e1d10404e1f02f0b2111378658733d4f63abe.
These are emulator checks, not QCA interop or a proven physical timeout repair.

Next owner step: pull and run fresh Mac preflight with owner PUBLIC key; close
QEMU after checking exact fail-closed lines and answerYES. No private key, packet
or medium write required. Then separately review new report/fresh USB identity and
authorize installation. Keep current Dell/session powered while preparing; never
reuse owner-gate-jf9qj9iy or an old disk id for this new candidate. After installation,
run SAME saved cat session once, record raw events, exact final receipt/appearance
and time. If only disconnect remains,20ms is not a sufficient fix; do not repeat
blind sends or report completion. Current physical fast-channel outcome is PENDING.

Evidence cross-check exposed a QEMU observer archive race: fault-loop log continues
growing after watchdog reboot, so separate reads for hashing and copying could
disagree. All three observers now hash/archive one immutable byte snapshot; source
regression added and QEMU gates rerun. This fixes evidence recording, not Bluetooth.
The captured no-device artifact is unchanged by observer/test-only edits; its source
bindings are updated only after confirming byte-identical candidate hashes.

## Connected delivery observed; Mac-only controlled resume follow-up

Owner confirmed exact connected receipt and walking ginger cat. Evidence:
`experiments/x86-64-uefi-connected-supervisor-v1/evidence/dell-connected-cat-owner-observed.json`.
Owner image d9561b29..., installed EFI17368188..., package f2dedcd1..., counter1.
First connection timed out at sender17040; second receiver offset0 completed.
Reset cause UNKNOWN; no elapsed measurement or authenticated attestation.

Mac sender adds receiver-authoritative checkpoints, regression warning, strict
shared C status validation, elapsed measurement, stale timer guard, and explicit
`--stage-only-bytes` stop WITHOUT COMMIT. No receiver/EFI change or flash required.
Host test reproduces actual C/GATT17040-byte retained prefix, resumes and applies
once; reset fixture returns zero. Owner must compile on Mac and run controlled
counter2 staging-stop/same-session-resume experiment in README before claiming
physical nonzero resume. Keep Dell powered; never regenerate the saved session
after an interruption. Existing unrelated network-runtime work is not in scope.

## Connected resume observed; first native connected trial prepared

Owner Mac compiled sender d2a89f16.../status validator9bf98c86..., deliberately
stopped world counter2 at receiver8400, then resumed SAME saved session at8400.
Exact receipt matched cc545d03b210bd3ebdef2141368bd6daa90cc3ec966b7cfb357afc53d30d7645.
Remaining transfer15.525s, NOT full-file speed. Evidence records controlled
same-boot resume only, not unexpected fault/power-loss retention or attestation.

Owner requests native engine update over fast channel. New prepare_native_trial.py
uses EXISTING owner-gate-s0bxi9d8 driver-revision-2, verifies installed report/image,
unchanged production source hashes, public key and exact active counter2 world.
No new receiver C, driver, root, key or flash change. Default prepares a create-only
review plan without private access/sign/send; explicit reviewed-plan-hash sign mode
rechecks inputs, requires owner private/public match, signs/verifies RRT3 and saves
one kind2/nativecounter1 session. First visible effect: blue bottom line with same
cat world/live state. Native/world counters independent; assume same powered boot,
baseline driver1 and no prior connected native trial. Owner review/sign/send and
physical commit/state preservation remain PENDING. Failed-health rollback and
watchdog are emulator tests, not guarantees for arbitrary privileged native code.

## Owner Mac exact native plan and agent takeover

Owner pulled1cd1752, passed full-ginger Mac QEMU (`runs/q-aqcn0ciu/report.json`),
and prepared `/tmp/connected-native-trial-1.json`, SHA256
2b483eb704db585f5d3e841d4fcc787826b78465e8c4c3609c075abd43290835.
Plan binds owner public fingerprint58744820..., installed EFI17368188...,
baseline02e3a839..., payload0954cba9..., active counter2 worldcc545d03...;
nativecounter1. NOT SIGNED OR SENT, no native commit claimed.

Owner now requests commit/push and full agent handoff because they do not want
to paste terminal commands. Complete takeover instructions, exact full hashes,
Mac paths, pending operations, evidence/recovery limits and scope live in
`docs/CONNECTED-NATIVE-MAC-HANDOFF.md`. Next agent must execute on the ACTUAL Mac;
Linux agents do not inherit Mac/private-key/radio access. No SSH or remote access
has been provided. Private bytes must never enter conversation/Git/Linux.
No further flash rewrite/reboot/world change. Preserve same current boot and plan.


## Mac-operated first connected native receipt — 2026-10-03

Actual owner Mac agent verified and signed the exact reviewed trial, delivered
native counter1 over Bluetooth, reconnected after COMMIT and received exact
SHA256/session/counter application receipt (exit0, 27.261s including reconnect).
Release SHA256 d7f19e81d91c27f1a35f7f53aaf7e6dfcc1a70280e1a559cb2de00fa497a1def.
Owner confirmed pre-send same powered boot, walking cat and no intervening update.
Post-send physical screen observation is PENDING; no QEMU/attestation claim.
See connected evidence/dell-connected-native-trial-1.json and sender log, and
updated docs/CONNECTED-NATIVE-MAC-HANDOFF.md. Native counter1 has an applied receipt;
do not assume driver1 remains active or repeat the initial plan as a new trial.
Second transition/failed-health physical tests remain pending. No flash/reboot or
private-key output; owner-local saved session preserved.

Owner confirmed the engine2 blue bottom line appeared. Explicit post-update
cat-motion confirmation remains pending. First native exact receipt and visible
revision effect are observed; second physical transition is not yet performed.


## First walking-cat confirmation and second native receipt — 2026-10-03

Owner confirmed cat motion after engine2 update. Agent returned exact installed
driver1 over Bluetooth with nativecounter2: exact applied receipt,69.404s including
reconnects; SAME-session partial resumes10800/14400 observed on timeout. World
counter2 unchanged. Post-return screen confirmation remains pending. See connected
evidence/dell-connected-native-trial-2.json and sender log, plus takeover doc.
Separate deterministic failed-init counter3 trial prepared only, not signed/sent;
no hung module. Mac sender recognizes exact consumed-counter error2 rejection
separately from application;14 connected+14 world/GATT checks and Apple compile pass.
No receiver/module/media change, no private-key output, no Dell reboot.


## Physical unhealthy trial NOT committed; staging regression — 2026-10-03

Owner confirmed blue line disappearance on return and authorized continuation.
Counter3 signed deterministic init-error test began transfer, but after timeout
receiver SAME session offset regressed12960->0. Agent stopped exact sender; no
COMMIT or final receipt, so unhealthy code was not executed and rejection is NOT
physically verified. Cause and current Dell base/world/counter unknown; screen
observation requested. Preserve power/session; no blind retry or world restoration.
See connected trial3 evidence/log and updated takeover. Mac sender now stops
immediately on regression; Apple compile-only passed. No receiver/media change.

Owner now reports scene disappeared after trial3 staging loss. Reboot/root
failure cause remains unknown; current display diagnostics requested before
further radio action. No COMMIT was sent; unhealthy candidate was not executed.


## Post-loss read-only diagnosis and interrupted restoration — 2026-10-03

Owner photo shows live Rabbit advertising diagnostics, no visible fatal/watchdog
line. Mac read-only RFS query: exact trial3 STAGING13440/36640, receiptcounter0,
indicating prior file counter2 lost; root reset plausible, cause/boot not proven.
Exact-session ABORT confirmed IDLE. Announced prior-world2 restoration attempt
using preserved signed package/session (no new key/sign/counter) stopped after
1920-byte timeout and phase0 disconnect without reconnect/COMMIT/receipt.
Cat restoration is NOT complete. All senders stopped; owner asked to place Mac
within0.5–1m of Dell for next read-only diagnosis. No native trial retry now.
Photo/query/abort/recovery logs archived; see takeover and connected trial3 evidence.
Mac-only query and exact-staging abort modes compiled, focused3 checks pass;
receiver/bootstrap/module/media unchanged. No unhealthy module executed.


## Near-Mac read-only recovery queries fail — 2026-10-03

Owner placed Mac nearby. Rabbit service scan found no device; cached UUID direct
read-only connection expired60s without connecting/status. No writes, all sender
processes stopped. Cat not restored; cause not established. One restart from
unchanged USB followed by same signed world2 restoration is prepared as recovery,
but owner decision is required to override original no-reboot constraint.
See connected takeover/evidence. Query-only cached option Apple-compiles and2
focused checks pass; no receiver/media/key change or native resend.


## Exact world recovery after owner reboot — 2026-10-03

Owner reboot confirmed. Default240-byte same-world2 transfer regressed21600->0
before COMMIT on fresh boot with no native update in that boot. Read-only query
then controlled100-byte writes of SAME signed world2/session obtained exact applied
receipt in58.173s without disconnect; owner screen observation pending. Restores
world package, not prior live positions/tick. Cause and general reliability unproven.
Sender-only chunk override bounds checked,14 world/GATT checks and Apple compile
pass; root/receiver/module/media/key unchanged. See connected recovery evidence.
Same signed deterministic init-error nativecounter3 release revalidated against
baseline1/world2 and chronologically assumed nativecounter0; no re-sign/new nonce/
counter, no retry yet. Wait for walking-cat confirmation before next failed-init
trial. Existing RRT3 accepts counter gap0->3. No hung fixture or further reboot.


## Native3 smaller-write attempt stops before COMMIT — 2026-10-03

Owner reported «Код есть, синей линии нет.» after exact world2 receipt. Context
suggests cat present/no blue line; movement not explicitly reconfirmed. SAME
signed native3/session was checked against post-reboot review34bb8be3..., then
sent with100-byte DATA payloads. Four timeouts; retained resumes300/700/1400.
Sender stopped at bounded reconnect limit, exit1. Read-only query confirmed
STAGING1500/36640/error0/last file receipt counter2. No COMMIT, module did not
execute, failed-init rejection still NOT physically verified. Exact session ABORT
confirmed IDLE/received0/length0/counter2. All radio processes stopped.

Query-only now also reads connected RSSI before file status. Apple compile and
actual read-only query succeeded: connectedRSSI -84dBm, discovery -93dBm; IDLE
and retained filecounter2. Mac WiFi channel8/2.4GHz/20MHz, no network modification.
Shared-band interference is a hypothesis, not an established cause. Asked owner
whether5GHz or wired internet is available for a controlled comparison; answer
pending. Do not blindly resend or reboot. Logs/hashes and limits preserved in
connected evidence/dell-connected-native-trial-3-small.json and four archived logs.
No new signature/counter/nonce, receiver/module/bootstrap/media change.


## Controlled Mac pacing comparison and world recovery — 2026-10-03

Owner asked agent to investigate Bluetooth without waiting for alternate WiFi.
Read-only baseline now connectedRSSI -67 rather than prior -84dBm, without network
change. Both unpaced and50ms-paced same-native3 3000-byte prefixes succeeded.
Exact abort between short trials reset staging only and preserved worldreceipt2.
Long unpaced same-native3 transfer resumed3000, confirmed15300, disconnected at
sender17300, reconnected with receiver0. Read-only query showed filecounter0 and
connectedRSSI -61. Stronger signal alone did NOT prevent root-state loss. BEGIN
and disconnect do not reset filecounter in reviewed C; root reset/reinitialization
or corruption suspected, exact failure/watchdog stage still unproven. No COMMIT
or bad-init module execution. Exact partial-session abort confirmed IDLE/counter0.

SAME original signed world2/session with100-byte payloads and50ms delay staged
33000/33381 without disconnect; normal immediate sender resumed33000, sent381
remaining bytes and got exact applied SHA/session/counter2 receipt (finish1.282s).
World restored by receipt; owner walking-cat screen confirmation pending.
Then SAME signed native3/session from0 with100-byte payloads/50ms delay staged
35000/36640 without disconnect. Subsequent read-only query confirms retained35000
and previous world filecounter2, connectedRSSI -66. Still STAGING, NOT APPLIED.
All sender processes stopped; keep Dell powered. Do NOT re-sign/change nonce or
counter. Native rejected receipt remains pending; screen-motion confirmation
requested before continuing remaining1640 bytes and deterministic failed-init test.
No requested/manual reboot, network modification, USB/media writes or native COMMIT
in this comparison. Earlier root-state loss was observed, cause unproven.

Sender-only --data-delay-ms1..100 is restricted to explicit --send plus staging
limit; default sends remain unchanged. Delay timers guarded by connection
generation/peer/characteristic/offset, so stale callbacks cannot resume a new
connection. Apple compilation and actual short/long pacing tests pass;2 focused
helper checks pass (existing staging-stop source assertion updated for scheduler
call);4 invalid diagnostic modes rejected before SDK/radio.18 mock USB checks
pass, NOT a physical USB fix. No receiver/root/native code change.
Evidence/log hashes: connected evidence/dell-radio-pacing-comparison.json and11
associated logs. Two long successes support a candidate mitigation, not proven
causation or general reliability. Precise reset cause needs physical diagnostics.


## Exact native3 rejection receipt retained — 2026-10-03

Owner confirmed walking cat («кот ходит») before final native3 COMMIT. SAME signed
release606594a7.../saved sessionfbf8c737... reverified against unchanged installed
gate, owner PUBLIC key and exact restored world2. No private-key access/signing.
Read-only query confirmed retained35000/36640/counter2; same-session normal100-byte
sender resumed35000, sent remaining1640, COMMIT, and exact REJECTED receipt
SHA/session/counter3/error2 (exit2, expected rejection,2.254s, no disconnect).
New connection read-only query independently reverified exact60-byte REJECTED
status: received=length36640, counter3, releaseSHA606594a7..., exact nonce.
Thus authenticated native trial was consumed and rejected; this is a physical
Dell result. Generic error2 does not attest which load/health callback failed.
Expected known fixture returns1 from scene_init; no hung fixture used.

Native counter3 is NOW consumed. Next fresh native release must use at least4
and current retained driver1/world2 basis, with refreshed review. Reusing the
same rejected receipt/session is idempotent; do not re-sign/relabel counter3.
Owner post-trial walking-cat/no-blue-line confirmation requested, PENDING.
All radio processes stopped; no USB/media/network change or manual reboot.
Evidence: connected evidence/dell-connected-native-trial-3-rejected.json plus
three archived final query/finish/requery logs; earlier failed attempts preserved.
Paced staging followed by small unpaced tail succeeded, but radio reset cause
and general reliability remain unproven. Sender source unchanged this turn.


## Owner confirms post-rejection scene — 2026-10-03

Owner: «ходит и линии нет». After exact native3 rejection and retained receipt,
cat continues walking and blue line absent. Physical rejection/scene preservation
trial complete; exact live frame/tick continuity unmeasured. Nativecounter3 consumed,
worldcounter2/current driver1 retained; next fresh native>=4. Evidence updated.
Next work: data-only text intent -> checked V3 candidate -> existing world authority
-> saved connected session -> paced staging/tail -> exact receipt -> current world.
World development authority remains distinct from owner-native key; do not silently
claim worlds are owner-authorized or change installed bootstrap.


## V3 text-world path ready for first physical intent — 2026-10-03

Added ask_connected_world.py: reuse existing subscription-only Codex runner through
generic propose_json; strict small objects/programs schema, unchanged V3 sprites/
palette/identity, exact current-world hash, deterministic Python bounds/signatures
and actual installed runtime C activation/240 ticks/render sentinels before radio.
world_check.py pins/rechecks crypto and gate runtime source; no owner-private key
access. Installed world authority remains PUBLIC development Creator, distinct from
owner-native. Do not silently claim owner-authenticated data worlds.

Persistent state initialized against exact current ginger-cat JSON/packagecounter2
and installed gate in ignored runs/text-world/state.json (pending=null). Saved
worldcounter and nativecounter are separate; nativecounter3 consumed, next fresh
native>=4. Proposal/delivery run saves exact package/session;100-byte/50ms-paced
whole-stream staging stops before COMMIT, next SAME-session call commits. Current
state advances only on exact applied receipt. Unknown delivery retains same pending
nonce/counter/bytes and blocks fresh intent; --resume --send. Never-sent drafts may
be explicitly discarded; ambiguous delivery cannot. Atomic save/single state lock.

6 new host flow checks pass, including actual C healthy speed edit and invalid MOVE
without boundary handling rejection, stale/extra/boolean proposal rejection,
unknown delivery/counter preservation, exact receipt gating and packet/session
substitution rejected before radio; only never-sent draft discard permitted.15 existing LLM tests pass after generic runner
refactor. Whole-stream STAGING/zero callbacks until explicit COMMIT tested in actual
C core/validator. No runtime/bootstrap/native source change.

Real local Codex smoke proposal: vx1->2 only; exact cat art/palette/program retained,
worldcounter3 candidate package d47182e6..., C240ticks checked. No radio; smoke
draft explicitly discarded with archive preserved in runs/text-world-smoke. Actual
Dell/current managed state staysworld2. Host evidence and saved proposal in connected
evidence/connected-text-world-host-ready.json and speed-proposal.json. Asked owner
which first text change to send (double speed, second same cat, or keep scene);
response pending. No physical text-intent orchestration claim yet. Missing mouse
art/background changes are currently unsupported, not fabricated. Voice and
Creation Inventory extension remain subsequent work.


## First text-to-art connected world receipt: cat wears red hat — 2026-10-03

Owner intent «давай коту наденем шапку» authorized graphic change/delivery. Used
imagegen skill/built-in tool: transparent red knitted beanie reference, then edit
original 2x2 cat walk source to wear same hat in4 poses. Copied both generated
source images into V3 assets; prompt/provenance saved. Existing import_cat.py does
RGBA format conversion only, no painted/keyed alpha; source1536x1024 RGBA, alpha0..254.
Imported4 distinct128x85 poses/shared256 palette/logical64x43, unchanged original
objects/programs/vx1. AI edit is visual preservation, not identical outside-hat
pixels. Local indexed PNG/GIF previews and user output copies saved.

Extended ask_connected_world.py with explicit --world-candidate for generated V3
art worlds; shared prepare_world uses same strict compiler/Python signature/pinned
C240ticks/render guards/session/counter/receipt gate. Small LLM patch schema remains
unchanged; no native fields accepted.6 existing flow checks pass after refactor,
plus added asset native-field/legacy-world rejection test passes (7 total).

Actual currentworld2 package binding checked; pre-send read-only status retained
old rejected native3 receipt, no active foreign staging. Hat worldcounter3 package
35017 bytes SHA8761fa34ce8af4365864f7b668cd66e5a3ecede02ac81a5a0edabbcbf37b71c3.
Saved session in runs/text-world/edit-0866els1. Entire35049-byte stream staged with
100-byte payloads/50ms delay, stopped before COMMIT. SAME session next connection
resumed35049 and got exact applied SHA/session/worldcounter3 receipt; commit
connection1.694s, no disconnects. Managed current state atomically advanced to
world3/current hat world, pending=null, only after exact receipt. Nativecounter3
remains consumed; next native>=4 must bind NEW active hat signed world.

Owner screen hat/walking-cat confirmation requested, PENDING. Evidence/log hashes
in connected evidence/dell-connected-cat-red-hat.json; generation provenance V3
assets/cat-red-hat-walk-v1.provenance.json. No USB/media/firmware/network changes,
manual reboot, owner-private key access or native update. Current world authority
remains public development Creator. Do not claim authenticated device attestation
or physical screen from preview. First text/art managed delivery receipt physically
observed; exact screen outcome still pending.


## Owner confirms red hat on physical Dell — 2026-10-03

Owner: «супер, кот в шапке...что дальше делаем?». This supersedes the
previous pending hat appearance observation: physical cat wearing hat confirmed.
Movement after the hat update was not explicitly reconfirmed. Exact applied
receipt and worldcounter3 unchanged; no new radio or hardware action. Evidence
and generation provenance updated with verbatim observation. Next roadmap work:
consolidate convenient text edits/current world assets, then voice through the
same checked delivery path and reusable Creation Inventory components.


## Connected controller recovery and global roadmap — 2026-10-03

Owner authorized global reliability/common execution work («делай»), not another
scene modification. Added read-only preflight and exact receipt reconciliation to
ask_connected_world.py. Local lost COMMIT response can finish from exact saved
session/hash/counter/full-length applied receipt without replay. Saved confirmed
prefix survives across process invocations/partial logs; Mac sender receives a
minimum prefix before DATA/COMMIT to catch reset between query and BEGIN. Prefix
loss, foreign active session, exact rejection, application pending and unreachable
receiver remain explicit distinct statuses. At most two resumable attempts per
call; no new nonce/counter or reboot used to hide uncertainty. Locks inherited
through Python/native senders retain custody if a parent exits; competitor fails
busy. --status emits common local JSON; --status --query adds read-only receiver
state without promoting current state. Partial logs are archived even on timeout.

16 orchestration checks and16 C/native/transport host checks pass. Changed sender
compiled on actual Mac; real Dell returned retained exact applied hatworld3 receipt.
Separate local simulated lost-response fixture (current2/pending3) reconciled via
ONE real read-only Dell query to isolated current3/pending=null. No new world/native,
BEGIN/DATA/COMMIT/ABORT, media write, reboot, network change or owner-key access.
Managed runs/text-world/state.json remains byte-identical, actual hatworld3.
Do not call this an induced physical radio failure: local uncertainty was simulated.
Source hashes/logs/results: connected evidence/connected-world-control-recovery.json.
Radio reset cause and sustained reliability are still unproven. Common controller
supports bounded text data edits and supplied generated V3 asset worlds; automatic
artwork planning/native upgrades, voice and inventory integration remain unfinished.
Next global milestones and acceptance criteria: docs/CONNECTED-WORLD-CONTROL-PLAN.md.
Nativecounter3 separate/consumed; next new native>=4 bound to active hat signedworld.
Owner hat appearance confirmation supersedes older pending observation; movement
after hat update was not explicitly reconfirmed.


## Unified controller, Mac app and new physical trials — 2026-10-03

Owner expanded authorization to finish all five global steps, collecting required
human actions into one batch; USB rewrites authorized but no media write or Dell
reboot performed. New world_control.py/world_planner.py/engine_route.py combine
structured LLM plans, bounded original sprites, checked existing inventory/assets,
persistent journal/history, reviewed native background family and shared receipt
transport. Entire world candidate C gate precedes native private signing. Engine
source binds installed gate; exact payload deterministic PE/QEMU gate precedes
owner-key match/signing. Arbitrary generated native code remains unsupported.

Actual physical exact APPLIED: native4 background203050 payloadb5ece667..., native5
restored driver1 background121826 payload02e3a839..., world4 cat+mouse intentionally
stopped staging3000/35202 and resumed SAMEsession to application, world5 restored
initial hat. This is controlled physical staging stop, not unexpected RF failure.
Owner screen observation after these new trials pending. Current confirmed state
world5/native5. QEMU uses mock USB and is recorded separately from physical logs.

RabbitWorld.swift/build_control_app.py produce ignored local Rabbit World.app:
text, voice, resume, version restore and separate OS permission setup. Loopback
server requires ephemeral Bearer token0600; text/voice share same checked path.
12 new controller tests and16 transport checks pass, including actual C asset
checks, invalid-world-before-native, no-op, crash-after-receipt history recovery,
idempotency/pending session and authenticated loopback source routing. GUI built
and codesign verified. No tests masquerade as live microphone verification.

GUI text speed request saved checked world6; exact APPLIED still pending. Initial
child sender TCC abort due missing Bluetooth purpose fixed in Info.plist. Later
tccd AUTHREQ_PROMPTING for org.rabbit.world-control BluetoothAlways; read-only
queries time out before DATA. Pending exact sessiona817c934... retained; no new
nonce/counter/reboot used. Voice implemented but OS speech/mic permissions and
live utterance-to-receipt require owner. Russian recognizer on-device unavailable
in CLI diagnostic, falls back to Apple Speech service after permission.

One owner batch: allow app Bluetooth/speech/mic; resume saved text operation;
then speak a mouse request and observe physical scene. Do not mark full goal
complete before actual voice delivery and owner observation. Full hashes/reports/
logs/plans: connected evidence/world-control-2026-10-03/summary.json. Current world
authority still public development Creator; native uses owner key never logged.
Historical radio reset root cause and sustained reliability unproven. V1 inventory
exists; local V3 highres assets LicenseRef-Not-Assigned not shareable V1 cards.
Updated roadmap: docs/CONNECTED-WORLD-CONTROL-PLAN.md.
