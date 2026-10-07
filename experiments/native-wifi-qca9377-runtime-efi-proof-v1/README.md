# Executed EFI runtime proof and rejected mapped-budget composition

2026-10-07. Isolated offline QEMU/Yukabox execution and composition assessment.
Frozen runtime-v1, port-v1/v2 and all controller/state/BLE scopes unchanged. No
hardware, actual RNG provider, credential, private owner key, signature or new
candidate counter/workflow. Published deterministic test inputs only.

## Actual EFI execution, not merely linking

Positive PE32+ EFI application **68096 bytes**, SHA256
`5f4942ff28ff5013d0b94217bf9a1a5fe685bfcad1871e61682586c76360d4c5`, executes
under QEMU q35/OVMF on Yukabox and exits **33** via explicit QEMU-only Target Pack.
Serial proof requires all real stages:

- Actual native memory shims execute their memcpy/memset/memcmp/memchr/strlen checks.
- A noinline volatile32768-byte frame executes its real compiler-generated
  `__chkstk` call; object disassembly requires the probe reference. Mature pinned
  LLVM probe/body/alias are unchanged. This exercises stack code under OVMF, not
  a physical stack reserve/guard approval.
- Two actual Noise NK handshake messages match published Cacophony ciphertexts;
  handshake hashes match. Valid owned objects are freed and all used512-byte arena
  slots are explicitly inspected for zero. Both old raw handles are discarded.
- Injected **explicit mock** RNG protocol/BootAPI performs successful and failed
  GetRNG paths through reviewed RNG-v2 and checked entropy callback. Fake provenance
  hash1 and constant public0x6b bytes are test fixtures, not provider approval or
  real entropy. No raw OVMF/Dell RNG or LocateProtocol is queried: callbacks are
  locally supplied. Failure causes SYSTEM/FAILED/zero output; scratch and owners
  are wiped/released and inspected. No sample/key data is logged.

Negative EFI SHA256
`245d0ac0f4d21d621367bbe1b09421cacf2e8816da75953468edf5e75239d7a5` executes and
exits **35**. It first generates the correct published message, then changes an
actual MAC-tag byte before the receiver. Receiver returns **MAC_FAILURE**, state
**FAILED**, payload length0. Actual objects are freed, every arena byte is wiped,
and a specific rejection/wipe marker is required; it cannot pass by simply exiting.

QEMU-only serial3f8 and debug-exitf4 are isolated Target-Pack facts, never physical
instructions. Fresh per-run OVMF variables and FAT directories live only in this
owned remote runs directory. No physical media or Mac/Dell controller is involved.
Positive/negative UART logs and firmware/image hashes are preserved in evidence.

Host regressions also re-pass233521 real memory-shim ASAN/UBSAN checks,65436 actual
LLVM guarded-stack/page-crossing checks, corrected port-v2 model277113 checks and
five ambiguity/uncertain-owner cases. Those remain separate from EFI execution.

## Whole Rabbit composition: file fits, mapped gate fails

The immutable native54 staged source baseline is copied into a new isolated build,
without calling candidate/counter/signature/key/state workflows. Native54 recompiles
**byte-for-byte**, SHA256
`3eefea77fbab35bca609216e4a418c2abad695f1a8a83da8aa2ee147bbfefca3`,187392 bytes.
No baseline source or counter is changed.

A fresh link retains the tested Noise/runtime as a callable TEST root beside the
actual Rabbit native54 driver, shares pinned Monocypher4.0.3 and namespaces new
memory calls. Compiler aggregate-zero lowering still requires global memset; a
small typed bridge delegates to the actual tested memory shim. No empty probe,
security-check removal or default runtime import. The root is retained by linker,
**not called by Rabbit**, not wired to provisioning and not composition-executed.
It contains public test vectors/QEMU helpers and is not a deployable candidate.

| Measured bound | Native54 baseline | Linked composition | Immutable cap |
|---|---:|---:|---:|
| EFI file bytes |187392|220160|262144|
| PE SizeOfImage bytes |4141056|4206592|4194304|

File increase32768 leaves41984 file bytes. **Mapped image exceeds cap by12288**:
composition budget is explicitly **REJECTED**, despite successful link and file fit.
No native admission follows. Global33392-byte TEST arena plus retained sections are
part of this measured image; a production caller-owned arena/reservation design,
actual owner inventory and linker layout need reviewed restructuring. No automatic
arena shrink, mapped-cap increase, bootstrap edit or pointer-lifetime shortcut was
made to hide the failure. RAM placement outside PE would itself need explicit owned
allocation/failure/uncertainty/lifetime proof; it is not free capacity.

Composition SHA256
`4d6ea82e9870b8757b699ff541251b5d263aa8c72fc998322ad596d9be255573`.
This is offline structural size/composition evidence, not behavioral integration of
Noise with Rabbit, physical scan evidence, owner authorization or real credentials.

## Reproduce and remaining gates

On Yukabox, no installs or shared-reference mutation:

`python3 /home/yuka/rabbit-world/parallel-runtime-efi-proof-v1/source/verify_runtime.py`

`python3 /home/yuka/rabbit-world/parallel-runtime-efi-proof-v1/source/assess_composition.py`

Shared /tmp tmpfs was full; compiler composition uses only its own run-directory
TMPDIR on the existing home filesystem. No shared cleanup/deletion was performed.
Generated binaries stay remote. Sources, inherited reference identities, original
staged baseline hashes, executed UART logs and both link reports are bound locally.

Required before admission: mapped-budget restructuring with complete owned memory/
RNG inventory; actual TargetPack stack reserve/guard/callback high-water/recovery and
whole integrated Rabbit execution; independently approved strong real RNG and fresh
recipient identity/fingerprint; canonical context/epoch/framing/replay/failed-state
coordinator; ordinary owner Ed25519 AUTH and recipient ACK before any real credential
read/send. Fixed ephemeral/mock paths are test-only and cannot become enrollment.
Upstream transient KDF mixing on DH error remains unedited and explicitly requires
its prior protocol/security review. QEMU receipts never substitute for physical ones.
