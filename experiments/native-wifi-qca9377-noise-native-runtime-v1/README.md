# Real stack-probe/runtime integration: offline preparation

2026-10-07. Frozen port-v1/v2 and earlier scopes unchanged. No real device/BLE/RF,
state/counter, private key, credential, signature or physical native candidate.
All compilation/execution occurred on Yukabox, using public deterministic vectors.
This resolves an isolated runtime link dependency; it is not provisioning admission.

## Mature runtime, no empty probe or bypass

No existing Rabbit `__chkstk` implementation was found. Reuse official LLVM
compiler-rt20.1.8, commit `87f0227cb60147a26a1eeb4fb06e3b505e9c7261`:
https://github.com/llvm/llvm-project/blob/87f0227cb60147a26a1eeb4fb06e3b505e9c7261/compiler-rt/lib/builtins/x86_64/chkstk.S

Original source SHA256
`eadb9b028c8fc2ea1c685c61f61a84bd3defe82f8441a6845b14123de3b478c5`;
Apache2 with LLVM exceptions, retained license/source. Instruction body is unchanged.
A minimal platform-only assembly.h supplies symbol directives; `chkstk_bridge.S`
aliases MS-x64 `__chkstk` to original `___chkstk_ms`. COFF symbol addresses must be
identical. No stack-probe-disable compiler flag, fake successful return, substitute
instruction body, Unix random or allocator fallback is introduced.

The mature routine preserves RAX/RCX, leaves RSP unchanged, touches every4096 bytes
and the final requested address. Caller performs its own stack adjustment afterward.
It is a compiler-internal RAX-size ABI, not an ordinary C argument convention.
It does **not** impose a semantic maximum or provide recoverable error status:
insufficient protected stack faults. Actual target stack mapping, reserve, guard
and recovery remain separate obligations; touching unguarded RAM is not a bound check.

## Actual bounded model and memory checks

- **65436** real-probe checks on an explicitly mapped65536-byte usable Linux stack
  between guard pages. Sizes0,1,4095,4096,4097,8192,16384,32768,65500 preserve RAX,
  sentinel RCX and RSP. Deep canary bytes remain unchanged. Fresh child processes
  actually fault SIGSEGV on bottom guard and a middle-page guard even when final
  requested address lies in valid memory. Thus an empty probe or endpoint-only
  probe cannot satisfy the test. Probe/guard test is unsanitized to preserve native
  signal behavior; it is not a physical UEFI-stack observation.
- **233521 ASAN/UBSAN** checks run actual native_memory.c bodies (renamed only for
  host oracle coexistence): memcpy/memset/memcmp/memchr/strlen against host libc,
  lengths0..4096 and misalignment offsets0..7, return semantics, boundary canaries
  and comparison sign. Overlapping memcpy and invalid unterminated/unmapped inputs
  remain forbidden caller conditions, not invented behavior.
- Corrected owned port-v2 derivative re-runs **277113 checks** and five ambiguity/
  uncertain-RNG process cases. Prior borrowed RNG pool cannot be hidden by rebind;
  old-pointer lifetime/mapping and complete coordinator review remain obligations.
  All referenced/copy bytes are independently hash-bound; no parent approval inferred
  from the model passing.

## A complete isolated EFI application links, not the Rabbit engine

All actual port/library/provider COFF objects plus mature probe, real memory shims
and `efi_smoke.c` link via bundled LLVM lld into **public-vector-runtime.efi**.
It is an entire PE32+ x86-64 EFI application with relocations and no default libraries,
not just a set of objects. Existing `__chkstk` reference now resolves to real code.

The entry uses only published Cacophony private/static/ephemeral test bytes, performs
both valid NK handshake messages and expected ciphertext/hash checks, frees owned
objects and returns EFI status. Fixed-ephemeral test API exists solely for this
OFFLINE test image, never actual enrollment RNG. The image is **linked but not
executed in EFI/QEMU or deployed**; host tests establish mechanisms and linker
checks establish format/dependencies, not a native execution receipt.

Image file **66048 bytes**, SHA256
`d1c977f238caea438b687009bf9ddd6c5d73dfd00ed0e374e6a574cdcf6bc938`.
Generated objects/executables/EFI remain only in the unique remote runs directory.
No signed package, native profile/counter or physical controller session was created.

Existing native54 payload187392/max262144/headroom74752 are comparison facts only.
A standalone66048-byte EFI does not establish incremental engine cost or actual
Rabbit whole-image fit; headers, shared primitives, dead sections, relocations,
world/driver and additional runtime interact in a combined link. Caller arena33392
bytes is RAM, separately reserved/owned, not a claim of free file-budget capacity.

Compiler `-fstack-usage` observations for actual MS-x64 Noise objects identify dynamic
frames: mix_dh40, HMAC72 and HKDF88 bytes of reported fixed component, plus dynamic
alloca. Fixed suite limits DH/hash lengths32 and SHA256 block64, but those facts do
not alone prove a whole call-chain high-water mark. EFI RNG/BootServices callbacks
and entry stack provenance remain unbounded by this test. No64KiB physical stack
approval or eliminated upstream mix-on-DH-error limitation is claimed.

Reproduce on Yukabox without install/reference mutations:
`python3 /home/yuka/rabbit-world/parallel-noise-native-runtime-v1/source/verify_runtime.py`

## Exact remaining admission obligations

1. Root review corrected port-v2 and runtime bridge/ABI; trusted pointer, lifetime,
   raw-handle and complete owner coordinator, including retained/uncertain RNG pool.
2. Actual TargetPack owned stack reserve/guard/probe/callback high-water/recovery;
   complete Rabbit EFI combined link/budget and actual native memory/ABI execution.
3. Physical strongly reviewed RNG provider, fresh RAM recipient identity/context,
   no test fixed-ephemeral path in actual enrollment; physical fingerprint binding.
4. Canonical target/native-image/boot/epoch/role/prologue, timeout/framing/replay and
   failed-state teardown; separately reviewed handling of upstream transient KDF
   mixing on DH error, which remains unchanged.
5. Ordinary owner Ed25519 AUTH and recipient ACK inside confirmed transport before
   any real credential read/send, then explicit physical application receipts.

No cryptographic/guard/link tests replace these gates. This artifact provides real
runtime code, reproducible failures and a concrete offline link for their review.
