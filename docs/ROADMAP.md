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

### U3 — Universal module graph (complete)

Represent modules, typed ports, events, imports, dependencies, and resource budgets.
A patch must add and connect a supported module without editing the world runtime or
unrelated modules. The first demonstration extends `HI` to `HI!` on both backends.
The combined verifier passes on the learner's Apple Silicon Mac: both targets observe
`HI` and patched `HI!`, rollback is exact, and invalid graph changes are rejected.

### U4 — Target Packs and capability negotiation (complete)

Define schemas and conformance suites for target resources and device capabilities.
Resolve portable capabilities such as `display.text`, `light.emit`, `storage.read`, or
`network.send` to explicit target drivers, or reject the deployment before building.
The combined verifier passes on the learner's Apple Silicon Mac. QEMU UART and Darwin
stdout preserve one semantic contract; optional absence and required rejection are both
explicit, and plan-bound evidence prevents target or driver substitution.

### U5 — Hosted, native, and bridge runners (complete)

Implement the three execution envelopes behind the same evidence contract. A runner
must expose its remaining software layers, authority, installation effects, and recovery
path rather than claiming universal bare metal.
Runner Contract v1 passes on the learner's Apple Silicon Mac across hosted Darwin,
native QEMU, and an explicitly simulated framed bridge with transcript evidence.

### U6 — Hardware discovery and installation plan (complete)

Inspect a candidate device without mutating it. Select a compatible Target Pack and
produce a reviewable plan containing capabilities, missing support, writes, risks,
recovery steps, and expected observations. Installation remains a separate authorized
action.
The inventory schema, matcher, simulated supported/unsupported fixtures, and a strictly
non-executable removable-USB plan are implemented. A real Dell OptiPlex 3060 was
inspected through read-only firmware screens: x86-64, 8192 MiB RAM, UEFI, HDMI and USB
keyboard observation, USB boot enabled, no installed M.2 device, and Secure Boot
enabled. The exact snapshot is rejected for enabled Secure Boot and absent removable
media rather than silently changing either condition. No firmware or storage write was
performed.

### U7 — Physical conformance (current)

Choose targets from available hardware using documented and recoverable boot paths.
Prove the same small world on at least two dissimilar physical targets over time. A
Raspberry Pi Pico 2, old PC, phone, or another board may participate, but none is a core
architectural dependency.

The current preferred first physical candidate is an available x86-64 UEFI computer
booted from removable USB, first reproduced under x86-64 QEMU. The experiment must not
write its internal disk or firmware; removing the USB device is the recovery path.

The first pre-physical artifact now exists: the unchanged `HI` world lowers to a
deterministic x86-64 PE32+ UEFI application inside a 64 MiB MBR/FAT32 removable-media
image. The builder and structural verifier claim only `BUILT-NOT-INSTALLED`; they do not
convert an observation into physical evidence by themselves.

The exact image has now also been observed manually under QEMU 11.1.1 with TianoCore
EDK II on the Apple Silicon Mac: firmware started the removable-media application and
the display showed `HI`. That evidence is hash-bound and explicitly remains emulator
evidence. It completed the emulator gate before any removable-media write.

The owner subsequently authorized and completed a raw write to a newly identified
external removable Kingston USB device. macOS auto-mounted FAT32 and added `.fseventsd`,
so post-mount whole-image identity was correctly reported as changed; the boot payload
`EFI/BOOT/BOOTX64.EFI` still matched its reviewed SHA-256 exactly. That completed the
removable-media gate before physical boot.

The verified USB then displayed `HI` on the physical Dell OptiPlex 3060 after the owner
explicitly disabled Secure Boot without deleting keys, enabling Legacy mode, or updating
firmware. No OS or internal disk participated. The owner chose to retain Secure Boot-off
as a documented policy for this dedicated home lab machine. This completes U7's first
physical target slice; the two-dissimilar-device goal remains open. The next slice applies
the existing immutable `HI -> HI!` patch physically and proves rollback to `HI`.

The UEFI builder now accepts that exact hash-bound `add-bang` patch and deterministically
produces a distinct `HI!` PE32+/FAT32 artifact. Structural verification passes and patch
removal restores the exact original `HI` image. QEMU 11.1.1 has manually displayed exact
`HI!`; the patched payload was then hash-checked and the physical Dell also displayed
exact `HI!`. The owner subsequently removed the patch, rewrote the exact reviewed base
payload, verified its EFI hash, and observed exact `HI` again on the same Dell. This
closes the physical cold-patch cycle `HI -> HI! -> HI`.

The next U7 graphics slice is now built but not yet observed. A new portable world asks
for one orange rectangle rather than text. Its Target Pack binds `display.region` to the
UEFI GOP linear framebuffer. Reviewed x86-64 bytes locate GOP, read the framebuffer base,
resolution, stride, and packed RGB/BGR format, then directly store 65,536 pixels. The
artifact contains no `HI` string and never calls Simple Text Output. QEMU 11.1.1 has now
displayed the exact orange square; the owner-reviewed screenshot is hash-bound to the
world, target, EFI, and image. No physical-media write is authorized by that emulator
observation alone. After a separate device check and explicit authorization, the exact
payload was written to the removable Kingston device, hash-verified, and observed on the
physical Dell: the i5-8500T directly stored 65,536 orange pixels with no OS present.

The next artifact is now built but not yet observed: a keyboard-controlled `128 x 128`
orange object. Reviewed x86-64 bytes clear the screen, retain coordinates, read standard
UEFI arrow scan codes, erase the old object, clamp the next position, and redraw. Escape
returns success. Its deterministic build, instruction checks, movement model, boundary
tests, and negative policy tests pass. QEMU 11.1.1 has now manually demonstrated all
four directions, clean old-frame erasure, boundary clamping, and Escape; the observation
is bound to exact world, target, EFI, and image identities. Physical Dell interaction is
the next gate. After a fresh removable-device check, explicit authorization, write, and
EFI hash verification, the physical Dell reproduced that complete interaction with no OS
or internal storage. The next qualitative capability is time: autonomous frame updates,
velocity, and collision rules rather than movement only in direct response to a key.

The owner then supplied the first ordinary-language world request. Its reviewed v0
contract makes a yellow player jump and return on Space, leave one small persistent
yellow stone and step away on `Z`, reject movement through that stone, and permit routing
around it. The implementation adds a UEFI `Stall()` time binding and explicit AABB
collision logic to the existing framebuffer/input substrate. Deterministic construction,
exact instruction identity, semantic simulation, collision/route-around tests, and
negative policy tests pass. QEMU 11.1.1 has now manually reproduced the complete world;
that evidence is exact-bound and explicitly does not claim physical Dell execution.

The next boundary is also implemented in `world-package-v0`: the approved Russian
intent, reviewed interpretation, and portable semantic world compile deterministically
to one 1,060-byte `.rabbit` package. An independent decoder recovers the complete
operation sequence. The package contains no x86, UEFI, QEMU, framebuffer, firmware,
USB, or Dell binding and has performed no deployment. This is the first reusable input
contract for the Rabbit Runtime rather than another bespoke boot image.

### U8 — Transactional patches

Apply cold, warm, and hot patches through prepare, validation, staging, health checks,
commit, and automatic rollback. State migration and unsupported transitions must be
explicit.

### U9 — Rabbit runtime and kernel (current prototype boundary)

Add only the substrate required by native targets: traps, interrupts, memory,
scheduling, isolation, drivers, and module lifecycle. Hosted and bridge targets may use
their existing environments while preserving the same world contract.

The first step is intentionally smaller than a kernel: implement the reviewed package
decoder and opcode interpreter in a hosted reference runner, then place the same runtime
inside the recoverable x86-64 UEFI image. Once both consume the identical `.rabbit`
package, add an explicit transport for replacing a package without recompiling or
rewriting the runtime. Microphone and LLM input sit above this deterministic boundary.

The owner selected Wi-Fi as the first live transport. `x86-64-uefi-network-probe-v0`
is the read-only discovery gate: it checks UEFI Simple Network and both standardized
UEFI Wireless MAC protocols, then enumerates PCI network controllers by exact
bus/device/function, vendor, device, and subclass. It sends no packets and writes no PCI
configuration data. QEMU observation comes before a separately authorized physical
probe. The observed Dell result will choose between firmware-provided Wi-Fi and a
driver for the actual controller; no chipset is assumed in advance.

QEMU 11.1.1 validated v0.1: TianoCore exposed Simple Network but not
either standardized Wi-Fi protocol, and PCI enumeration reported the configured Intel
`e1000e` identity `8086:10D3`. On the physical Dell, however, brute-force reads across
all possible PCI buses remained on a dark screen for multiple minutes. Recovery by
power-off and USB removal succeeded; the run is preserved as failed evidence rather
than inventory. V0.2 now uses bounded UEFI PCI I/O handle enumeration and must pass a
fresh QEMU gate before another authorized physical write. That v0.2 QEMU gate now
passes quickly with the same expected emulated result and distinct exact identities;
physical USB replacement remained separately gated. The exact v0.2 image was then
written and verified, but the physical Dell again remained dark before its first title.
V0.3 therefore removes the early console clear and adds three visible stage markers,
turning the next run into a precise localization test. It repeated the QEMU gate:
all stages appeared and the same emulated network result was observed. A fresh removable
device check and explicit authorization are still required before the physical v0.3 run.
That authorized run remained dark before `STAGE 1`, so removing the console clear was
not sufficient. V0.4 fixes a subsequently discovered x86-64 UEFI ABI violation in the
nested text-output helper: it now supplies the firmware call's mandatory shadow space
and stack alignment. The corrected v0.4 passed a fresh QEMU gate with every stage and
the same emulated inventory visible. It now awaits a fresh device check and separately
authorized physical run.
That run succeeded: the Dell displayed every stage and reported no firmware network
protocols, Ethernet `10EC:8168`, and wireless-class controller `168C:0042`. The next
transport must be wireless because no additional cable is available. Before committing
to the substantially larger QCA9377 path, `x86-64-uefi-bluetooth-probe-v0` performs a
bounded read-only UEFI USB inventory and identifies standard Bluetooth class
`E0/01/01`. QEMU displayed its emulated USB keyboard and the probe correctly rejected
that device as Bluetooth; the exact evidence is bound to the artifact without claiming
physical execution. The safe preparation steps are now collapsed into one command that
verifies, builds, hashes, and inspects external media read-only. Device writing and the
first activation of a new hardware authority remain explicit separate boundaries. A
positive physical result selects a staged BLE Rabbit bridge; no candidate selects the
read-only QCA9377 planning path. HCI commands, pairing, firmware loading, association,
credentials, receive, and transmit all remain outside this discovery step.

The authorized physical Dell run was positive: five interfaces were described, and
interfaces `00` and `01` of one USB device `0CF3:E009` carried Bluetooth class
`E0/01/01`. Upstream Linux independently classifies this exact ID as QCA Rome. The BLE
route is therefore selected. The next slice may issue only bounded controller-identity
HCI commands and must keep pairing, advertising, scanning, connection, user data, and
radio transmission outside its authority.

That bounded slice now exists as `x86-64-uefi-bluetooth-hci-identity-v0`. It is bound to
the exact physical USB ID, permits only Read Local Version Information (`0x1001`), and
waits for at most eight small interrupt events. Its QEMU gate is deliberately negative:
without the exact controller it must issue no HCI command. Only after this fail-closed
result is evidence-bound may the separately authorized physical local-controller query
occur. A successful identity response still does not authorize discovery or connection.

That QEMU gate passed exactly: Stage 1 rejected the emulated hardware and explicitly
reported that no HCI command was sent. Physical preparation may now proceed, while the
removable-media write and first real controller command remain separate owner-authorized
boundaries.

The authorized physical run then completed on the Dell. The exact `0CF3:E009` interface
accepted HCI Read Local Version Information and returned Command Complete status `00`
on interrupt endpoint `81`: HCI/LMP version `07`, manufacturer `001D`, and LMP
subversion `025A`. Assigned Numbers map these values to Bluetooth Core 4.1 and Qualcomm.
No radio operation or persistent write occurred. The next artifact will combine the
remaining bounded local capability queries in one boot before any separately authorized
scan, advertising, pairing, or connection experiment.

That combined artifact now exists as
`x86-64-uefi-bluetooth-local-capabilities-v0`. A single boot permits exactly three
local informational opcodes: Read Local Supported Commands (`0x1002`), Read Local
Supported Features (`0x1003`), and LE Read Local Supported Features (`0x2003`). Its
80-byte event budget accommodates the 64-byte supported-command map while remaining
bounded. Deterministic build, byte identity, parser, PE/FAT, target-binding, budget,
tamper, and authority-escalation checks pass. QEMU must next demonstrate the unchanged
fail-closed path before physical replacement is opened; no radio authority exists.

The QEMU gate passed exactly on the Apple Silicon Mac: v0.1 reached Stage 1, rejected
the emulated USB hardware, and reported that no HCI command was sent. Exact-bound
evidence now opens the combined read-only physical-preparation command. Removable-media
replacement remains a separate explicit authorization boundary.

The authorized Dell run then completed all three local queries. Its 64-byte map confirms
support for legacy LE advertising, scanning, and connection commands; its LE feature map
is `1F00000000000000`. The controller therefore has the primitives for a small BLE
bridge. No radio operation occurred. The next boundary is deliberately narrower than a
full connection: a bounded, receive-only scan for one exact Rabbit beacon from the Mac,
with no pairing or persistent state.

That first-radio candidate now exists as `x86-64-uefi-bluetooth-beacon-rx-v0`. The Mac
advertises only UUID `52414242-4954-4C45-8000-000000000001` through CoreBluetooth. The
Dell Target Pack permits a fixed five-command sequence that exposes advertising reports,
configures passive scan, enables it for at most 20 seconds, and disables it before the
result. Bluetooth passive scan receives but does not transmit scan requests. Exact
machine bytes, UUID agreement, event parsing, timeout, cleanup, and rejection of active
scan, transmit, pairing, connection, reset, firmware, persistence, tamper, and ambiguity
pass. QEMU fail-closed observation remains the next gate before physical replacement.

That QEMU gate passed exactly: the emulated machine reached exact-device matching,
rejected its USB keyboard, sent no HCI command, and never started passive scan. The
screen observation is bound to the five exact artifact identities. Read-only physical
preparation is now open; removable-media replacement remains separately authorized.

The physical v0.2 scan then completed its exact setup/cleanup sequence but reported
`RX/LE/ADV=00/00/00`: the controller delivered no USB event during the scan window.
Linux's QCA Rome setup path reads target version and setup status before normal use and
conditionally installs rampatch and NVM. The next diagnostic is therefore
`x86-64-uefi-qca-status-v0`: exactly two device-to-host vendor reads (`0x09` and `0x05`)
for ROM/patch/RAM identity and `PATCH_UPDATED`/`SYSCFG_UPDATED`. It cannot download
firmware, reset the controller, issue HCI commands, or operate the radio. Its QEMU
fail-closed gate comes before any separately authorized physical run.

That QEMU gate passed exactly on the Apple Silicon Mac: the artifact reached Stage 1,
did not find `0CF3:E009`, and sent no vendor request. The observation is exact-bound and
opens read-only physical preparation. Removable-media replacement remains a separate
owner-authorized boundary.

The physical status read found ROM `0x00000302`, patch `0x00000111`, RAM `0`, and
status `0x20`; neither `PATCH_UPDATED` nor `SYSCFG_UPDATED` was set. The next artifact,
`x86-64-uefi-qca-ram-load-v0`, pins the exact upstream Rome 3.2 rampatch/NVM by an
immutable linux-firmware commit, size, and SHA-256. It permits only their documented
headers plus bounded endpoint-02 bulk transfers into volatile controller RAM and then
re-reads setup status. Reset, HCI, scanning, radio, controller flash, and persistent
writes remain forbidden. A fresh QEMU mismatch gate precedes any physical run.

The QEMU mismatch gate passed exactly and stopped before the first device write. Its
evidence is bound to the payload manifest and final embedded-program identity. Physical
candidate preparation is now open while the actual Dell controller has not yet been
modified by this experiment.

The authorized physical Dell run then transferred both pinned payloads successfully and
the controller reported both setup bits as ready. This establishes a verified transient
initialization primitive without reset or radio. The next boundary composes that
primitive with the already reviewed 20-second passive exact-UUID receiver in one boot;
it still forbids active scanning, pairing, connection, and Dell radio transmission.

That composition now exists as `x86-64-uefi-qca-beacon-rx-v0`. Its exact program first
requires ROM `0x00000302`, installs only the two pinned upstream payloads into volatile
controller RAM, requires both setup bits, and only then chains into the fixed five-HCI-
command passive receiver. Mandatory scan-disable cleanup remains last. Deterministic
build, payload, machine-byte, PE/FAT, command-sequence, budget, UUID, and authority-
escalation tests pass. Its QEMU exact-device mismatch gate passed without RAM writes,
HCI, or radio and is exact-bound. Physical candidate preparation is now open; physical
media has not yet been replaced with this image.

The physical v0.1 composition reached post-load status `E0` and completed scan cleanup,
but its counters remained `RX/LE/ADV=00/00/00`. V0.2 therefore tests one narrow
activation hypothesis: exactly one standard HCI Reset plus a 100 ms wait after the
ready flags, followed by the unchanged passive receiver. A fresh mismatch gate is
required because reset authority is new; that v0.2 QEMU gate passed and the reset stayed
unreachable on the emulated-device mismatch. Physical preparation is open. Transmit,
pairing, connection, flash, storage, and firmware-setting prohibitions remain unchanged.

That physical v0.2 hypothesis succeeded: after status `E0` and one HCI Reset, the Dell
received twelve LE advertising reports and matched the exact Rabbit UUID sent by the
Mac. This establishes a one-way wireless identity primitive on the OS-less target. The
next slice encodes one bounded command vocabulary into reviewed advertisements and
binds each command to an allowed physical effect; it does not accept arbitrary code.

That candidate now exists as `x86-64-uefi-ble-color-command-v0`. One boot loads the
same pinned volatile QCA inputs, performs the one required reset, binds a bounded GOP
region, draws an initial yellow square, and listens passively for at most 120 seconds.
Only exact `BLUE` and `YELLOW` service UUIDs can repaint that centered `128 x 128`
region. Both commands end the window early and mandatory scan disable remains last.
Deterministic verification passes. The exact QEMU mismatch gate also passed: the visible
artifact identity was correct and execution stopped before RAM, framebuffer, HCI, or
radio authority. Physical Dell evidence is the next gate. This is a live command
vocabulary, not arbitrary wireless code.

The first physical v0.1 color candidate reached exact QCA readiness and selected the
interrupt endpoint, then stopped before `DISPLAY READY`. No HCI reset, scan, command,
or framebuffer result was observed. The failure localized a Microsoft-x64 ABI error in
the nested GOP `LocateProtocol` call: it lacked its own shadow-space/alignment frame.
V0.2 adds that exact `0x28`-byte frame and changes no command or radio authority. Its
new deterministic identities pass. Its fresh exact QEMU mismatch gate also passed
without RAM, framebuffer, HCI, or radio effects. The dedicated USB may now be replaced
for the second physical attempt.

The v0.2 physical attempt passed the nested GOP call but lost HDMI at the first draw.
Review found that the draw helper accounted for CALL's 8-byte return address but not
its own additional `PUSH RSI`; all persistent framebuffer fields were therefore read
eight bytes early. In particular, the GOP interface pointer was treated as
`FrameBufferBase`. No HCI reset or scan was observed. V0.3 changes those five offsets
from `+0x08` to `+0x10` and prints separate `FRAMEBUFFER BOUND` and `INITIAL SQUARE
DRAWN` stages around the first write. Its deterministic build passes; a fresh QEMU
mismatch gate passed without RAM, framebuffer, HCI, or radio effects. Physical
candidate preparation is open for the v0.3 Dell attempt.

The v0.3 physical attempt succeeded. In one Dell boot the runtime bound the framebuffer,
drew yellow, received exact `BLUE` from the Mac and drew blue, then received exact
`YELLOW` and returned to yellow. The USB was not moved and the Dell was not rebooted
between commands. It then disabled passive scanning as designed. This is the first
physical Rabbit state changed repeatedly over a wireless channel while the target ran
without an operating system. The next revision replaces the 120-second proof window
with a long-lived receive loop and an explicit local exit/cleanup action.

That long-lived candidate now exists as v0.4. It removes the automatic deadline and
early completion, polls the Dell keyboard between individually bounded 200 ms receive
operations, and accepts unlimited alternation of the same exact `BLUE`/`YELLOW`
vocabulary. Local `Esc` sends the reviewed scan-disable command before returning;
power-off remains rollback. The command set, framebuffer region, receiver-only radio
authority, and persistent-write prohibitions are unchanged. Deterministic pre-QEMU
verification passes. The fresh v0.4 QEMU mismatch gate also passed without RAM,
framebuffer, HCI, or radio effects. Physical candidate preparation is open.

The next candidate is `x86-64-uefi-ble-program-loader-v0`. It crosses the boundary from
two compiled-in command UUIDs to a tiny versioned program format. BLE UUID frames carry
`BEGIN`, sequenced seven-byte `CHUNK`s, and `COMMIT`, each with an FNV-1a corruption
checksum. Dell stages the bytes in RAM and preserves the old scene until length, order,
transfer identity, whole-program hash, and bytecode all validate. Rabbit VM v1 programs
use fixed-width `DEFINE_SHAPE`, `SET_POSITION`, and `END` instructions to choose square
or triangle, arbitrary RGB, position, size, and arrow movement. The interpreter cannot
jump to received native code or address arbitrary memory. Authentication remains a
later gate. Deterministic verification passes with image SHA-256
`0d0b53b980bd4645b624aeb7489aa0d36fb93e302bd0edfa77e869e6cb161c9f`.
The next gate is its exact QEMU fail-closed observation, followed by one final physical
USB installation and multiple complete interactive scene programs without moving USB.

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

## Definition of U6 completion

U6 is complete only when:

- read-only discovery produces a canonical inventory of architecture, firmware/boot,
  removable-media support, memory, observable I/O, devices, and security state;
- an available x86-64 UEFI computer is matched to a supported Target Pack or rejected
  with precise missing requirements;
- a separate installation plan names every removable-media write, expected observation,
  verification step, risk, and recovery action;
- internal disks, firmware changes, hidden effects, stale inventories, and missing
  recovery are rejected;
- discovery, planning, and installation remain separate authorization boundaries;
- inventory, target matching, plan, and negative conformance checks pass reproducibly.
