# Bounded Noise native-port preparation (HOST model and actual COFF objects)

2026-10-07. Necessary portability preparation, **not native-ready or provisioning
admission**. No full EFI candidate, physical/device call, live key, credential,
owner signature/AUTH, radio, counter/state change or existing-source edit.

## Fixed-suite construction and owned memory

Actual pinned Noise-C `cfe25410979a87391bb9ac8d4d4bef64e9f268c6` handshake/state
machine and SHA256 are unchanged. The strict compact Monocypher-v2 providers are
copied unchanged, including zero-DH rejection and checked entropy error propagation.
Noise-C still transiently mixes a wiped shared-zero on provider error before FAILED;
this prior reviewed limitation is not bypassed or portrayed as resolved.

Compile-time symbol redirects route allocation calls into explicit port providers:
`noise_new_object` -> `qca_noise_new_object`; **noise_free itself** ->
`qca_noise_free`; malloc/calloc/free -> bounded port functions. Hooking free alone
would be insufficient because upstream noise_free cleans an arbitrary pointer
before calling free. The new free validates exact owned slot and recorded size
before dereferencing or wiping. The unused utility allocation/free definitions are
separately renamed, their allocator references bounded; no OS allocator is admitted.
No upstream handshake function body is changed.

Caller supplies zero-initialized, aligned16, mapped, disjoint `QcaNoisePort` storage.
It owns64 slots of512 bytes, total payload32768; full metadata/storage structure is
**33392 bytes**. Each allocation is at most512, zero-filled, multiplication checked;
zero/oversize/exhaustion fails. Slots are **never reused within one admitted port
lifetime**. Valid release wipes the entire512-byte slot, changes owned state exactly
once and decreases actual live count. Wrong-size/interior/foreign/double-free does
not dereference or free the ambiguous pointer: it permanently quarantines allocation
admission and retains the actual still-live owners. Known owners may then be wiped
by explicit trusted teardown; quarantined state cannot reset or switch arenas.

Reset is permitted only with no live arena owners, no quarantine and no retained/
uncertain RNG pool. Caller must prove all borrowed raw handles were discarded and
control runtime generation; numerical epoch does not grant that proof. The model
uses epoch19, not an observed Dell epoch. Resetting a RAM arena is not reboot/native
identity attestation. No stale-pointer safety after a caller illegally reuses old
handles across reset is claimed. One active binding/single-thread admission only.

`qca_nk_new` admits exactly `Noise_NK_25519_ChaChaPoly_SHA256` and known initiator/
responder roles. On any construction error its valid/disjoint output is NULL; an
upstream dangling temporary is never freed or dereferenced a second time. Range,
alignment and port/RNG/review overlap checks happen before output writes. Invalid
unmapped/overlapping output must simply be rejected without writing it. Constructor
output slots must not hold a live older handle. Library raw operations/destructors
still require trusted valid owned objects and error checks; this is not a complete
opaque-handle protocol/admission wrapper. A future coordinator must gate every call,
teardown failed sessions and integrate exact arena/RNG owners with the native owner
inventory. Public factory mechanisms alone do not authorize Mac or credentials.

## Reviewed RNG adapter integration, no provider approval

The exact reviewed `efi-rng-port-v2` C/header are copied into dependencies/rng and
verified against frozen hashes:
C `5ac751cc0d2e0feed19e7ed1e8bc4f2a92e9aaec729bbacc1b8c3368885f6752`,
header `c68480b6b5677d907d6b535fe1ead1d03ef4d27096cb5b56417415305bb9fd31`.
The trusted caller lends a valid discovered `RngSession` and independent `RngReview`
of the same current port epoch; session/review/arena must be disjoint and aligned.
A nonzero provenance hash remains structural policy input, not authentication or
proof of entropy. No physical provider has been approved.

The backend checked callback permits only32-byte DH generation destinations wholly
inside an active owned slot, and invokes `rng_fill` without timer, seed, Unix, RAW
algorithm or default-algorithm fallback. Missing/stale review, epoch change, changed
method, provider failure or ambiguous scratch release fails; actual DH write fails
SYSTEM/FAILED/zero output. A failed RNG FreePool remains an owned resource of the
borrowed RNG session, blocks arena reset/switch, and is not magically released by
arena wiping. Borrowed RNG/session/review lifetime and full owner inventory remain
trusted caller obligations. This model invokes only fake MS-ABI provider methods
with public deterministic dummy bytes; they provide no real entropy assurance.

## Actual portability evidence and remaining runtime dependency

**277103 checks** under Yukabox clang20 ASAN/UBSAN; four additional fresh-process
quarantine scenarios. Actual library/provider sources compile into **19 x86-64 COFF
objects**, including checked RNG port, bounded allocator, factory availability,
minimal memory functions and a layout probe. No rand_os/randstate/random fallback
source is compiled. The explicit simulated target settings are x86_64-pc-win32-coff,
WIN32=1, freestanding, no red zone, no builtin libc or stack protector. WIN32 bridges
upstream's include conditional to an explicit minimal alloca/stdlib/string port.
Internal alloca remains compiler-provided and requires stack/runtime review.

A COFF read-only layout array was decoded and matched to executed host compiler
layout: port33392/align16, size_t8, pointer8, lengths offset32768, states33280,
epoch33344, RNG pointer33376; RNG protocol16/get_rng offset8. Mock callbacks execute
with `ms_abi`, exercising actual cross-ABI calls. These are simulated ABI facts,
not validation of the physical Dell BootServices/protocol pointer mapping.

After matching definitions across the object set, **__chkstk remains unresolved**.
No fake implementation, empty probe or stack-check bypass is supplied. A reviewed
native stack-probe/runtime integration is required before a full EFI link. Memory
shim bodies compile for COFF; host protocol tests use trusted host libc, so native
memory-shim runtime/stack behavior still needs independent verification.

Unlinked COFF sums: **62553 text,0 data,8 BSS bytes**; include all compiled provider/
Monocypher/core code and constants, not a garbage-collected full executable. The
caller-owned33392-byte arena is a separate RAM reservation, not hidden in this object
BSS sum. Existing native54 payload187392 / max262144 leaves74752 file bytes. Object
sums are neither actual incremental EFI bytes nor proof of fit; reused primitives,
linker sections, relocations, stack support and future supplicant change the result.
No native image was linked or signed, and no whole EFI budget approval is implied.

## Checks and reproducibility

- Exact six published upstream Cacophony NK ciphertexts, empty-message handshake
  action/hash checks, peer/prologue mismatch, all first-message byte tamper and
  truncation0..47, transport payload sizes0..128, both directions and replay.
- Allocations0..513, overflow rejection, every released512-byte slot wiped;64-slot
  exhaustion and no same-lifetime reuse;20 failure-injected real constructors,
  NULL error outputs, no double-free/quarantine or actual live-owner leak.
- Rejected output/arena aliases, range overflow and misaligned port; missing/stale
  review, changed callbacks, actual GetRNG failure and retained failed scratch-free.
  Model successful RNG path is deterministic dummy data only, never quality proof.
- Fresh-process foreign/interior/wrong-size/double frees retain untouched unrelated
  owners, quarantine admission/reset, and allow only exact known-owner teardown.

Run on Yukabox, no install or shared-reference writes:
`python3 /home/yuka/rabbit-world/parallel-noise-native-port-v1/experiments/native-wifi-qca9377-noise-native-port-v1/verify_port.py`

Source and transitive reference hashes, actual object hashes, model logs, layout and
unresolved symbols are recorded in evidence. Generated binaries remain remote.

Before any native/provisioning admission: actual TargetPack ABI/mapping review,
full EFI link and stack/allocator lifetime proof; exact complete owner inventory
including RNG pool; strong approved provider/fresh identity; fixed context/epoch/
framing/replay/error coordinator; real ordinary owner Ed25519 AUTH+recipient ACK;
physical fingerprint/context verification. None is replaced by these model tests.
