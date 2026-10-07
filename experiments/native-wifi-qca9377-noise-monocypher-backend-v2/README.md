# Strict NK provisioning backend v2: reject zero DH

2026-10-07. New isolated HOST-only policy profile; v1 source/evidence unchanged.
No device, RF, live private key, credential, signature, native candidate/profile,
state or provisioning action. Mature Noise-C handshake/SHA256 are unedited.

## Exact source finding, not inferred from passing vectors

Pinned Noise-C `cfe25410979a87391bb9ac8d4d4bef64e9f268c6`:

- `src/protocol/dhstate.c`, `noise_dhstate_calculate`: provider calculation is called,
  then if the remote state's `nulls_allowed` is1 and its public key is all-zero,
  output is zeroed **and provider error is masked to NONE**. Thus returning an
  error from a stricter provider alone is insufficient while that bit remains1.
- `noise_dhstate_set_public_key` similarly masks validation errors for allowed-null
  public keys. v2 uses `nulls_allowed=0`, preventing either special override.
- `src/protocol/handshakestate.c`, `noise_handshake_mix_dh`: calculate, then
  **unconditionally** `noise_symmetricstate_mix_key(shared)`, then clean shared and
  return the DH error. There is no generic shared-zero rejection.
- Write/read token processing returns DH error. Public `write_message` sets FAILED
  and output size0; `read_message` sets FAILED and payload size0. Split rejects
  FAILED state. Native/application caller must destroy the whole session on error.

Consequently the strongest claim available with unchanged upstream core is:
**reject invalid DH before any handshake payload output, successful Split/transport,
owner AUTH or credential admission**. The core still mixes the wiped zero bytes
transiently into a doomed symmetric state before failure. We explicitly do NOT
claim no internal KDF mixing on a rejected DH. If that stricter invariant is
required, the exact blocking location is `noise_handshake_mix_dh`; it needs a
separately reviewed upstream-core correction, not a provider bypass. No core edit
is made in this experiment.

## Deliberate provisioning-policy change

`dh_monocypher.c` now uses:

1. `parent.nulls_allowed=0` for every created DH state.
2. Public-key validation rejects the exact all-zero32-byte encoding with
   `NOISE_ERROR_INVALID_PUBLIC_KEY`.
3. Actual Monocypher `crypto_x25519` result is tested using Noise's constant-time
   `noise_is_zero`. On any zero shared result, wipe all32 output bytes and return
   `NOISE_ERROR_INVALID_PUBLIC_KEY`. This also rejects nonzero low-order encodings
   and their top-bit aliases rather than guessing curve membership from a list.

All valid published NK ciphertexts remain identical. Rejection of zero-DH invalid
inputs intentionally differs from the legacy reference and its permissive Noise
invalid-input behavior; v1 differential equality on those inputs was compatibility
evidence, not proof the prior provisioning draft's stricter policy was met.

A configured all-zero static-key setter fails before a handshake starts; the caller
must abort/destroy configuration. It must not ignore the error and reuse a previous
valid key retained in the state. Nonzero low-order static inputs fail actual first
write. Both incoming ephemeral roles fail actual read. None yields Split. A provider
factory is not a complete secure application admission/ownership wrapper.

## Unchanged mechanisms and pins

Fixed proposed suite: `Noise_NK_25519_ChaChaPoly_SHA256`. Mac initiator; Dell
responder with a fresh per-boot RAM key physically pinned by fingerprint/context.
NK does not authorize Mac owner. Owner ordinary Ed25519 AUTH and recipient ACK must
still be implemented inside confirmed transport and bound to final handshake hash,
target/native image/boot/epoch/context. No AUTH or signatures are implemented here.

Monocypher4.0.3 commit `ab2b16dd619ad5f6979a4fbe69cfa324a6fcc35f`, source/header
hashes from v1 are verified unchanged. X25519 is used; ChaChaPoly is exact IETF
nonce `0^32 || LE64(Noise counter)` with fresh context per message, no retained
Monocypher streaming rekey, no XChaCha. SHA256 uses unchanged Noise-C mature provider.
No BLAKE2-signature substitution or custom handshake/KDF. DH source retains the
upstream MIT license; all referenced library bytes and local sources are hash-bound.

Checked entropy callback failure still wipes provider public/private buffers and
propagates SYSTEM to an actual handshake write: FAILED and output0. HOST callback
always fails after filling public dummy bytes; fixed ephemeral API only serves
published/test vectors. Native checked RNG and native allocation port do not exist.

## Independent evidence

**3672981 ASAN/UBSAN checks**, plus compact-only10743 checks, Yukabox clang20:

- Exact six published Cacophony NK ciphertexts from pinned upstream JSON, including
  valid handshake and both transport directions. Derived vector header checked
  byte-for-byte. All previous mismatch, tamper, truncation0..47 and replay tests.
- Cipher differential against separately compiled actual unedited reference bodies:
  six nonce boundaries, AD0..65, payload0..512 step16 (13068 combinations), tag
  failure/no counter advance, valid plaintext, exhausted/backwards nonce errors.
- 256 valid DH public/shared-output comparisons retain exact reference equality.
- Independent reference computes shared-zero for encodings0,1,p-1,p,p+1; v2
  returns INVALID_PUBLIC_KEY and wipes output. Null-state override cannot hide error.
- 30 adversarial handshake configurations: five low-order encodings times canonical/
  top-bit alias in three roles (configured responder static, received initiator
  ephemeral, received responder ephemeral). Static setter or actual write/read
  fails closed; read/write error produces FAILED/zero output and cannot Split.
  Tags from a genuine baseline are retained while replacing only the32-byte input,
  so rejection is from actual key policy rather than fabricated tag acceptance.
- Entropy failure, invalid keypair/length,20 allocator-failure positions, every
  freed object/prologue byte wiped, no tracked live-owner leak. Pinned constructor
  returns error with nonnull already-freed output at3 injected positions: native
  wrapper must null error output and never dereference/free it.

Tracked two-party peak heap3008 bytes is a fixture observation, not native memory/
stack cap. The tests prove rejection/compatibility behavior, not complete AKE safety,
endpoint integrity, production entropy, owner authorization or credential admission.

Optimized compact HOST text **45643**, data2640, BSS1072 including fixture. Native54
payload187392/max262144 leaves74752 bytes, but HOST ELF figures do not establish full
EFI fit or actual incremental native cost. Strict adapter objects compile with
-Wall/-Wextra/-Werror; object sizes are in report. No COFF/native full link performed.

Reproduce without installs or reference edits:
`python3 /home/yuka/rabbit-world/parallel-noise-monocypher-backend-v2/experiments/native-wifi-qca9377-noise-monocypher-backend-v2/verify_backend.py`

## Admission remains blocked

Independent protocol/application review; explicit decision on upstream internal
mix-on-error invariant; native checked entropy/allocator/stack and ownership wrapper;
fixed suite/context/epoch/framing/deadlines/replay policy; COFF/full EFI budget proof;
real owner Ed25519 AUTH/ACK; and physical fingerprint verification of the fresh live
recipient/context. No native/provisioning approval follows from this host proof.
