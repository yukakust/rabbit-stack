# Noise native port v2: retain borrowed RNG owners across rebind

2026-10-07, isolated offline correction. Frozen port-v1 is unchanged. The same
strict Noise/Monocypher backend, bounded allocator and simulated ABI remain;
see ../native-wifi-qca9377-noise-native-port-v1/README.md for the original scope and
limitations. No device, BLE, state, signatures, live private keys, credentials or
native candidate/provisioning action.

## Exact bug and minimal correction

Previously, with arena live count0, `qca_native_rng_bind` could overwrite
`owned->rng` while the previous borrowed RNG session still retained `pool` or
`pool_uncertain`. Reset checked only the newly recorded RNG, so replacing that
pointer hid the actual retained resource. No release had occurred.

V2 rejects rebind if the **previous** recorded RNG has either retained pool or
uncertainty, before examining candidate session/review pointers. Same/new/overlap/
invalid-pointer candidates cannot erase the old owner. A later genuine successful
cleanup permits normal use; uncertain allocation remains blocked and is not freed.
No invented release receipt, forced cleanup, pointer relocation or state overwrite.

`qca_native_reset` also rejects any different arena while an arena is bound, before
its field reads. This conservative fixed-arena policy blocks partial-overlap wipes
and unrelated-arena resets from hiding existing ownership. Reset is not a generic
multi-arena manager. Binding a genuinely separate preinitialized arena still needs
trusted ownership/lifetime proof and the existing prior-owner checks; complete
handle/coordinator integration is not supplied.

## Regression evidence

Yukabox ASAN/UBSAN **277113 checks**, plus five fresh-process cases including
`rng-uncertain`; actual19 COFF objects and matching host/COFF layout are preserved.

- A real injected `FreePool` failure leaves a retained known pool. Attempts to bind
  fresh session/review, same pair, misaligned/overlapping session/review aliases,
  arena aliases and unrepresentable pointers all fail. Previous arena/session bytes,
  recorded borrowed owner and firmware-call count remain unchanged.
- An allocation failure that returns a pointer produces a real `pool_uncertain` in
  reviewed RNG-v2. Cleanup, rebind and reset remain blocked. This case exits its own
  host process with an explicitly retained modeled owner; no released claim.
- Reset of a disjoint unbound arena or aligned partial-overlap arena is rejected
  before dereference; original arena/session bytes remain unchanged.
- Existing published NK vectors, tamper/replay, constructor NULL error/no doublefree,
 512-byte wiping/bounds,64-slot exhaustion and quarantine tests still pass.

`verify_port.py` binds all compiled sources, pinned references and logs. README is
bound separately after the run in evidence/bindings.json. Generated binaries stay
on Yukabox; no install or shared source mutation.

Reproduce:
`python3 /home/yuka/rabbit-world/parallel-noise-native-port-v2/experiments/native-wifi-qca9377-noise-native-port-v2/verify_port.py`

## Trusted pointer and admission obligations remain

Every arena/session/review is caller-owned valid mapped aligned disjoint storage;
arena initially zeroed. Borrowed RNG pointers must remain valid and immutable in
identity for their entire bound lifetime. Numeric range checks cannot prove mapping,
resource provenance or exclude trusted-caller field corruption. Unbound reset is
not permission to inspect arbitrary metadata/pointers. Caller must prove no old
raw handles survive reset; complete native owner inventory/coordinator remains
unimplemented.

`__chkstk` is still the unresolved runtime dependency; no fake probe is added here.
Full EFI budget/stack/runtime/actual TargetPack ABI, strong physical RNG approval,
owner AUTH/ACK/context, endpoint integrity and fresh physical fingerprint remain
required. This v2 prevents one demonstrated owner-loss path, not secure provisioning
admission or a complete coordinator.
