# Compact Monocypher backend for the pinned Noise-C state machine

2026-10-07, isolated host-only adapter. No device/RF/native profile/candidate,
credentials, live private keys, owner signatures, provisioning or existing-scope
changes. Published deterministic fixtures only; never a production RNG substitute.

## Implementation

The Noise-C protocol, handshake, HKDF, pattern, hash and nonce state machines are
**unmodified** at commit `cfe25410979a87391bb9ac8d4d4bef64e9f268c6`.
New provider factories implement its documented internal backend interfaces:

- `noise_curve25519_new`: Monocypher4.0.3 `crypto_x25519_public_key` /
  `crypto_x25519`, preserving Noise's permitted zero-DH/low-order semantics.
  It uses a mandatory externally supplied **checked** `qca_noise_entropy` callback,
  returning `NOISE_ERROR_SYSTEM` and wiping public/private buffers on failure.
  No native entropy implementation exists here. Noise-C's ordinary void random
  callback is not used by this provider. DH keypair-validation temporary is wiped.
- `noise_chachapoly_new`: `crypto_aead_init_ietf`, then one `crypto_aead_write/read`
  with **nonce = four zero bytes || LE64(Noise-owned counter)**. Context is created
  afresh from the Noise key for every message. Monocypher's streaming rekey is
  discarded, never substituted for Noise key progression. Context and nonce are
  wiped. Authentication failure maps to `NOISE_ERROR_MAC_FAILURE`; no decrypt,
  payload modification or counter advance before authentication.
- SHA256 is the existing pinned Noise-C SHA256 provider/core, not BLAKE2 or
  Monocypher's optional SHA512. XChaCha is never called. Owner ordinary Ed25519 AUTH
  remains a separate application layer, not implemented or authenticated by NK.

Monocypher commit `ab2b16dd619ad5f6979a4fbe69cfa324a6fcc35f`; source SHA256
`f1f838cdd483bdebe0df0ff5c5ed60535e496f769c6a2f933ac4c0b114207123`, header
`fcaf6ed771358bb4f40fba016f6518ae86ec02b1b877d2cc35ad92d3a26fd7b3`.
The SHA256/Noise source and transitively included headers/C files are hash-bound in
report.json. All references were read-only. `dh_monocypher.c` adapts the MIT
reference provider and retains its copyright/license. Other unused factory symbols
in the HOST fixture return unavailable, never substitute insecure algorithms.

Fixed suite for the reviewed application is **Noise_NK_25519_ChaChaPoly_SHA256**,
Mac initiator, physically pinned fresh RAM Dell responder. Factory interfaces are
cryptographic mechanisms, not a suite/purpose/admission gate. Native caller must
hardcode this suite and reject negotiation/fallback; it must also implement the
provisioning-review-v1 owner AUTH/ACK/context/physical fingerprint requirements.
No claim that NK authenticates the Mac owner or permits credential transmission.

## Meaningful independent checks

Yukabox bundled clang20, ASAN/UBSAN, **3672371 checks**. The mature reference
providers are separately compiled with factory-symbol renames only; their upstream
bodies remain unchanged. Tests compare actual ciphertext/plaintext and X25519
outputs against those providers, not just round-trip our adapter:

- Six exact published Cacophony NK handshake/transport ciphertexts, header checked
  byte-for-byte against the pinned upstream JSON, plus the original10743 fixture
  checks: action order, handshake hash, peer/prologue mismatch, every first-message
  byte tamper and truncation0..47, both transport directions and replay.
- 13068 independent cipher combinations: six nonces0,1,2^32-1,2^32,
  0x0102030405060708,2^64-2; AD lengths0..65; payload lengths0..512 step16.
  Ciphertext including tag equals actual reference; corrupted tag rejects without
  advancing nonce; valid decryption matches reference. Library forbids backwards
  nonce assignment and encrypting at exhausted nonce2^64-1.
- 256 public-key/shared-DH comparisons and low-order encodings0,1,p-1,p,p+1:
  adapter/reference agree on zero DH. Zero output is permitted by Noise and grants
  no owner authorization. This is not exhaustive X25519 conformance testing.
- Invalid DH keypair/length, checked entropy failure, and **actual handshake write**
  propagation of entropy failure: system error, FAILED action, zero output length.
  Private/public provider buffers cleared. No handshake edit was needed.
- Failure injection at20 constructor allocation positions, no live owner leak;
  calloc/malloc/free wrappers verify every freed library/prologue byte is wiped.
  Important pinned-library API nuance: failed constructor may leave a non-NULL
  output pointing to an already freed intermediate object (3 observed injected positions). Caller must set output
  to NULL on any error, never dereference/free it, and never treat it as owned.
  No upstream patch or bypass is made; this boundary needs a tiny reviewed wrapper
  in native integration. Tests exercise the return-code/ownership contract.

The compact-only fixture separately passes10743 checks. Tracked two-party fixture
heap peak3008 bytes is not a native memory or stack cap. Context wiping invokes
mature Monocypher wiping; tests observe heap wiping, not arbitrary native stack.

## Footprint observations and exact limitation

| Host observation at -Os | Bytes |
|---|---:|
| DH adapter object text, strict -Wall/-Wextra/-Werror |729|
| Cipher adapter object text, strict -Wall/-Wextra/-Werror |724|
| Compact library plus identical vector/dummy fixture text |45575|
| Compact linked data |2640|
| Compact linked BSS including fixture tracking |1072|
| Previous default reference library plus fixture text |116677|
| Text reduction in these HOST builds |71102|

The two adapter objects add1453 host text bytes atop reused primitive/protocol code.
This is **not** the total Noise overhead: protocol core, SHA256, enabled mature
primitive routines and their constants also need linking. Conversely Monocypher
already used in a real candidate may share routines; object sums cannot establish
incremental native bytes. The compact host build removes the previous reference
Donna/Ed25519 fast-basepoint table cost and now looks feasible to investigate.

Native54 measured payload187392 bytes; max262144; headroom74752. These are existing
candidate facts, not an updated native image. Host ELF text/data are not EFI file
layout; no candidate was rebuilt, no COFF/full EFI fit or future supplicant budget
was proved. Do not publish/sign/admit solely from these host size observations.

Reproduce on Yukabox without install or modifying reference trees:
`python3 /home/yuka/rabbit-world/parallel-noise-monocypher-backend-v1/experiments/native-wifi-qca9377-noise-monocypher-backend-v1/verify_backend.py`

## Remaining integration gates

Independent cryptographic/application review; authoritative native checked entropy
and bounded allocation/stack/lifetime port; fixed suite and return-code/ownership
wrapper; full COFF + EFI link/incremental budget verification; canonical native
boot/epoch/image/role/owner context; real owner Ed25519 AUTH and recipient ACK inside
confirmed transport; transport framing/deadlines/replay/duplicate handling; then
physical fingerprint verification of the fresh Dell key/context before any real
credential is read or sent. No cryptographic primitive tests replace those gates.
