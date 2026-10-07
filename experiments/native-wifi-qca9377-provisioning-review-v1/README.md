# Secure provisioning: mature AKE feasibility review

Host-only review, 2026-10-07. No device access, native candidate, RF transmission,
credential access, real private key/signature, or provisioning. All fixture keys are
public deterministic test bytes, including the published Cacophony vector. Earlier
experiments are unchanged. This is a protocol integration proposal, not security approval.

## Concrete verdict

Reuse a mature Noise handshake state machine rather than treating X25519/AEAD/HKDF
primitive tests as proof of the custom secure-provision-plan-v1 composition.
The narrow role fit is **Noise_NK_25519_ChaChaPoly_SHA256**, Mac initiator, Dell
responder. Dell's recipient static key lives in RAM for one enrollment/boot only;
Mac knows it through a physically verified fingerprint. It is static within Noise,
not a persistent device identity or remote attestation. Never negotiate a different
suite from peer input or fall back to plaintext/custom handshake.

NK authenticates the pinned recipient, **not the owner initiating from Mac**.
Anyone knowing the recipient public key can initiate. Noise also explicitly permits
zero DH outputs for some invalid public inputs; public keys are not secrets. Do not
claim a successful NK session proves owner possession, and do not redesign Noise
based on its permitted low-order behavior. Owner authorization remains mandatory.

The default Noise-C reference backend is not yet a defensible native budget choice:
optimized HOST library plus vector/dummy fixture is **116677 text + 2648 data bytes**.
The reference X25519 backend brings Donna general DH plus Ed25519 fast basepoint
code and a 24576-byte precomputed table. Native54 payload is 187392 bytes under
262144, leaving 74752 bytes. Host ELF figures are NOT a full EFI size prediction or
proof of overflow, but expose a material footprint risk. Existing owner crypto may
share code in a real link; future Wi-Fi supplicant/transport also needs headroom.
A reviewed small backend adapter to already used mature primitives is a possible
next isolated step; no such adapter, COFF build, allocator/RNG port or full EFI fit
has been proved here. Do not substitute a handwritten handshake to save bytes.

## Pinned primary implementation and APIs

[Noise-C](https://github.com/rweather/noise-c/tree/cfe25410979a87391bb9ac8d4d4bef64e9f268c6)
commit `cfe25410979a87391bb9ac8d4d4bef64e9f268c6`, MIT, calls itself a reference
implementation. Its docs target Noise specification revision30; the current
[revision34 specification](https://noiseprotocol.org/noise_rev34.html) is a separate
compatibility/security review input. Pinning and vectors establish reproducibility,
not an audit or assurance all current fixes are present.

Use `noise_handshakestate_new_by_name`, recipient
`noise_handshakestate_get_local_keypair_dh` / initiator
`noise_handshakestate_get_remote_public_key_dh`, `noise_dhstate_set_keypair_private`
/ `noise_dhstate_set_public_key`, `noise_handshakestate_set_prologue`, `start`,
`get_action`, `write_message`, `read_message`, `get_handshake_hash`, `split`.
After Split, directional `noise_cipherstate_encrypt_with_ad` /
`noise_cipherstate_decrypt_with_ad` own nonce counters; caller does not invent KDF,
handshake nonce, key schedule, or encrypt/decrypt directions. Free every handshake
and cipher through library APIs; no alias or copied state owns the same key.

Ref backend `noise_rand_bytes` is void and cannot report entropy failure to the
caller. A native RNG design must obtain unpredictable boot/static/ephemeral material
through checked platform entropy and fail closed; review the integration path that
propagates failure before admitting a session. Default OS random backend is not EFI.
`get_fixed_ephemeral_dh` is explicitly testing-only and never an application RNG
solution. It is used here solely to replay published vectors and public fixtures.
Library objects use calloc, prologue uses malloc, and `noise_free` cleans then frees;
a bounded EFI allocation/stack/lifetime port and allocation-failure behavior remain.

## Minimal application protocol and trust boundaries (proposal, not implementation)

1. Dell creates fresh RAM recipient key and unpredictable boot/enrollment nonce only
   after checked entropy. Display a full fingerprint or QR over canonical domain,
   protocol revision/suite, recipient public key, signed native image hash/target,
   runtime boot/enrollment generation and nonce. Mac compares the physical display
   to the connected recipient/context. A BLE name/address alone is insufficient.
2. Encode fixed canonical prologue over that same context, owner public-key identity,
   roles and purpose. Runtime target/native/boot fields must come from trusted local
   state, not be accepted merely because a peer supplies equal bytes. Both sides
   reject wrong suite, native hash, target, owner identity, expired enrollment and
   any reboot/update/runtime epoch change. Context hash must be covered by the
   physical fingerprint, not just an unauthenticated announcement.
3. Perform two NK messages with **empty application payloads** (48 bytes each for
   this suite). No Wi-Fi credential or owner signing material in first/0-RTT message.
   Any bad length, library error, unexpected action, timeout, cancellation or context
   change destroys session and cached packets. Split is transport establishment,
   not application authorization or proof of an active native WLAN connection.
4. First encrypted Mac record is canonical owner AUTH, ordinary SHA512-Ed25519
   authorization using the already pinned owner public key. Its signed bytes bind
   domain/roles/purpose, final Noise handshake hash, prologue/context digest,
   recipient identity and current enrollment/epoch plus a bounded request ID.
   Dell verifies signature and all runtime fields before authorizing any credential
   operation. BLAKE2b EdDSA is not interchangeable with existing ordinary Ed25519.
5. Dell sends encrypted AUTH_ACK bound to that authorization/request/context.
   Mac verifies it before loading a credential from its protected local store.
   The exact AUTH and ACK encodings/state transitions and negative signature tests
   are still unimplemented and require independent review.
6. Only authorized transport may carry bounded credential records (existing plan
   ceiling: plaintext credential128, encrypted framed record512). Direction/type/
   context/request/sequence metadata is authenticated as associated data. Receiver
   admits ordered fresh records once, rejects replay/cross-direction/cross-epoch,
   and never applies before complete authenticated decoding. Retransmission uses
   exact cached ciphertext at the transport boundary, not new encryption with a
   reused nonce or a second application. If sender/receiver counters diverge, abort
   and re-enroll; no guessed counter reset. Credential acceptance and WLAN join/IP
   are different receipts, with no password echo or persisted secret log.
7. One enrollment owner at a time, bounded fragments/records/timers/memory. MAC
   failures, unrelated sessions and foreign identities do not renew deadlines or
   change authorization. Clear secrets, cached ciphertext and allocation owners on
   every success/failure/reboot/native update. MAC, host app and physical display
   are trust boundaries; cryptography does not remedy compromised endpoints.

First host NK message already has a responder-static-dependent tag, but that is not
owner authorization. Mac's verified response plus encrypted AUTH_ACK supplies the
explicit application confirmation needed before sending credentials. A malicious
or untrusted remote initiator never gets a credential privilege from NK alone.

## Reproducible, deliberately limited evidence

`verify_noise.py` builds the unmodified pinned protocol/reference backend directly
with Yukabox bundled clang20, no installation/configure/autoconf. Unavailable suite
factories return unavailable; selected suite uses actual library primitives.
`noise_vector.h` is checked byte-for-byte against the pinned upstream Cacophony NK
vector, all six handshake/transport ciphertexts are independently expected bytes.
Additional empty-message fixtures verify action ordering, equal handshake hash,
prologue/recipient mismatch, each first-message byte tamper, every truncation0..47,
129 payload sizes0..128, directional backchannel and ciphertext replay rejection.
Allocation wrappers verify every freed library/prologue byte is wiped and live heap
returns to zero. Deterministic fixtures abort if library RNG is invoked. **10743
checks**, ASAN/UBSAN pass; two-party peak tracked heap **3968 bytes**, not a native
stack/memory cap. Six upstream Poly1305 macro warnings are retained build context.

Run only on Yukabox:
`python3 /home/yuka/rabbit-world/parallel-provisioning-review-v1/experiments/native-wifi-qca9377-provisioning-review-v1/verify_noise.py`

Evidence binds all selected and transitively included source/headers, upstream
vector, local fixture/header/verifier and output logs. It proves the above host
behavior/size observation. It does not prove AUTH/ACK/signatures, production RNG,
full Noise spec conformance, 0-RTT safety policy enforcement in native code, physical
identity, native integration or Wi-Fi credentials securely provisioned.

Remaining blockers: independent protocol/application security review; actual
failure-aware native entropy and memory port; reviewed smaller mature backend and
full EFI budget/COFF proof; exact owner AUTH/ACK/context/replay implementation; then
physical fingerprint verification for the fresh live Dell recipient. No new user
approval/provisioning request is made by this offline review.
