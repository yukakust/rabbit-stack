# Rabbit Stack handoff

Updated: 2026-09-23

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
the exact artifact. Physical candidate preparation is open; the dedicated USB has not
yet been replaced with this image.

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
