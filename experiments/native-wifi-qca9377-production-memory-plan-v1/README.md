# Caller-owned EFI pool placement: preparation, not native readiness

2026-10-07. Only a new derivative changes the previous TEST root's static arena to
caller-owned BootServices memory. Frozen proofs/sources, immutable file262144 and
mapped4194304 caps, controller/state/BLE/counters/signatures remain unchanged.
All builds/models/QEMU execute exclusively on Yukabox with owned TMPDIR. No device,
actual strong RNG, private owner key or real credential operation.

## Concrete ownership and lifecycle

`pool_target.c` extracts genuine EFI AllocatePool/FreePool callbacks from platform
SystemTable/BootServices. Independent pinned EDK2 `fbe0805b2091393406952e84724188f8c1941837`
UefiSpec.h SHA411733fc1da5e084971f6a70c59b3699adee73a060fc5e7067eee3d2fb850db9
confirms SystemTable size120/BootServices offset96 and AllocatePool64/FreePool72.
HOST/MS-x64 COFF methods use exact uint32 memory-type, size_t64, status64 and ms_abi.
Signatures/header sizes, arithmetic ranges/alignment and output aliases are checked;
they establish consistency, **not authenticity or mapping**. Trusted caller still
proves platform-provided valid tables/code/lifetimes. Allocator trust is not RNG trust.

`pool_owner.c` retains a separate caller-owned owner record plus a single active
holder. AllocatePool(EfiLoaderData2) reserves **33407 bytes**: QcaNoisePort33392 plus
alignment slack15. Raw pointer/size are recorded separately; internal port is aligned16
without assuming firmware supplies16-byte alignment. Full raw allocation is zeroed
before initializing/binding the port. Arena remains64 slots512 bytes; no shrink.

- Failure with NULL output records no allocation. Success/NULL is rejected.
- Failure with nonNULL pointer, impossible range or returned owner/API alias records
  **uncertain owner**, never dereferences/wipes/frees that pointer. Admission is blocked.
- A second owner cannot replace any active/uncertain/retained holder.
- Cleanup refuses live/quarantined arena or retained/uncertain borrowed RNG pool.
  It does not erase ownership to make progress.
- New derivative-only `qca_native_detach` validates exact current arena, no live/
  quarantine/borrowed RNG owners, then clears library's global bound pointer **before**
  wiping/freeing storage. Merely freeing a static-port replacement would otherwise
  leave the old `owned` pointer and create UAF on subsequent queries/bind/reset.
- Cleanup wipes **every raw allocation byte**, including alignment padding/metadata,
  then calls the recorded FreePool once. Success clears raw/port owner and holder.
  Nonzero/warning status retains pointer/owner with uncertainty and forbids automatic
  retry/re-wipe/free: it cannot assume memory still mapped or invent release. Detached
  library returns no bound owner without dereferencing the old pool.

Owner records/API and borrowed objects must remain valid mapped, aligned, disjoint,
caller-owned and protected for their lifetime. No malicious trusted-caller field
corruption, leaked raw handles or complete application coordinator safety is claimed.
Pool cannot outlive BootServices; real target lifecycle is a remaining obligation.

## Actual tests and genuine QEMU pool

**534736 ASAN/UBSAN model checks** plus eight fresh failure processes. All16 raw
alignment offsets acquire/use/detach/release with full33407-byte zero check. Real
constructors and live-owner cleanup blocking, alias/overflow/header checks, wrong
arena detach, allocation NULL/error/impossible/alias/uncertain cases and FreePool
failure are checked. Borrowed known/uncertain RNG owner cases explicitly block detach,
whole wipe and free. Failure processes preserve their modeled owner, not a fake
released receipt. EDK2 layout oracle is checked in the actual executable.

Three actual QEMU q35/OVMF EFI images execute:

1. Success exit33: genuine firmware pool allocated; published NK messages/hash match;
   arena wiped; actual memory shims and real32768-byte probed frame execute; only RNG
   is explicitly mocked. A typed observer scans every raw pool byte zero and forwards
   **genuine FreePool**, then owner/binding become empty.
2. Tampered-MAC exit35: receiver MAC_FAILURE/FAILED/zero payload; every slot and raw
   pool wiped; actual detach/FreePool completes. Specific serial receipts required.
3. Injected FreePool-failure exit35: genuine allocation made; full raw wipe observed;
   test observer explicitly returns a failure instead of forwarding release. Helper
   retains the allocation, blocks retry and leaves no library dangling binding.
   This is an injected status, not a claim real OVMF/Dell FreePool malfunctioned.

No raw actual RNG/LocateProtocol is queried. Constant public test RNG bytes/provenance
hash1 are not entropy approval. Fixed-ephemeral API is public-vector-only, not an
actual enrollment path. QEMU-only UART/debug-exit ports never reach physical media.
Inherited233521 memory oracle/65436 genuine LLVM guard and corrected port-model
checks also rerun separately from EFI receipts.

## Actual composition now fits both immutable bounds

The native54 baseline is reproduced byte-for-byte,187392 bytes,
SHA3eefea77fbab35bca609216e4a418c2abad695f1a8a83da8aa2ee147bbfefca3.
Staged source/counter are unchanged. The new callable TEST root is retained beside
Rabbit, shares pinned Monocypher, keeps namespaced actual memory and real probe.
It is **not wired/called by Rabbit or composition-executed**, nor a deployable profile.

| Bound | Baseline | Pool-placement composition | Immutable cap |
|---|---:|---:|---:|
| File bytes |187392|222208|262144|
| PE SizeOfImage |4141056|4177920|4194304|

File headroom39936, mapped headroom16384. Previous mapped4206592 rejection is preserved
in its frozen proof; this derivative removes only the TEST arena's image BSS and adds
explicit pool ownership. The **separate33407-byte pool remains real RAM consumption
and an additional owner**, not free/unaccounted capacity. Actual native allocator/
whole-owner budgets, failure/uncertainty/lifetime and future supplicant growth still
need integration review. No cap increase/bootstrap bypass/signing admission.

Composition SHA05aa313a2741283629b10360390014022a53d229d5ea5934ee265a083a01718e.
Budget admission means only these measured offline size gates passed, not native or
security readiness. Binaries remain remote; source/log/UART/reference hashes local.

Reproduce:
`python3 /home/yuka/rabbit-world/parallel-production-memory-plan-v1/source/verify_runtime.py`
`python3 /home/yuka/rabbit-world/parallel-production-memory-plan-v1/source/assess_composition.py`

Required next: root review owner/detach/API/placement; full trusted native owner and
coordinator inventory including this pool and RNG scratch; actual TargetPack stack/
guards/callback high-water/recovery/BootServices lifecycle and combined execution;
independent strong RNG/fresh recipient identity/physical fingerprint; canonical
context/replay/framing/failed-state teardown and ordinary owner Ed25519 AUTH plus
recipient ACK before credentials. Upstream transient mix-on-DH-error remains unedited
and its explicit protocol-review gate remains. No physical receipt is inferred.
