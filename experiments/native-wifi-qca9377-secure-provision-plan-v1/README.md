# Confidential Wi-Fi provisioning: concrete boundary, not an enabled channel

This continues security-plan-v1 and supplicant-port-v1 rather than replacing their
WPA/HTT/key-install work. No real credential file/private key was read, no signing,
radio operation, native profile/state edit or provisioning was performed.

## What actually exists

The checked native project has an installed **owner public** Ed25519 identity and
public target hashes; it already pins Monocypher4.0.3, commit
`ab2b16dd619ad5f6979a4fbe69cfa324a6fcc35f`. Its core provides X25519 and XChaCha20-
Poly1305 AEAD; the optional SHA512/Ed25519 module also provides mature HKDF-SHA512.
The optional `crypto_ed25519_check` matches the existing owner's ordinary
SHA512-Ed25519 signature scheme. Core `crypto_eddsa_*` uses BLAKE2b and must not be
silently substituted for that owner signature scheme.

No project-integrated Dell private device identity, device attestation chain or
EFI_RNG_PROTOCOL/GetRNG invocation was found in the reviewed native Wi-Fi/runtime
source. This is a source-integration finding, **not** proof that Dell firmware lacks
RNG or TPM hardware. BLE UUID/receipts, PCI IDs, MAC addresses and target hashes
are public identifiers. Owner signatures authenticate Mac authorization; they
neither encrypt a credential nor authenticate a substituted Dell ephemeral key.

Do not derive a device secret from those public identifiers or reuse the owner
private signing key as an ECDH key. No Dell NVRAM/TPM/disk provisioning is proposed.
This first approach uses fresh RAM-only recipient identity per boot/session.

## First gate: strong native randomness

Before any real handshake, add a separate bounded read-only discovery/test of
UEFI RNG through a reviewed Target Pack: LocateProtocol, GetInfo and exact-size
GetRNG requests from a documented strong provider/approved algorithm. Protocol
availability, EFI_SUCCESS and a nonzero sample alone are not an entropy-quality
proof. Record provider/algorithm provenance and failure behavior; validate lengths
and every returned status. Unsupported, absent, failed or unreviewed providers
abort and erase temporary buffers. No timer/TSC/MAC/PCI identifier, deterministic
test seed or opportunistic unreviewed RDRAND fallback may become entropy.
Mac uses its established OS CSPRNG. No physical RNG request was made here.

## Proposed minimal enrollment profile

This is an implementable **draft requiring protocol/state review and end-to-end
negative tests**, not a production-authorized custom handshake. Prefer a mature
authenticated-key-exchange implementation if one fits the measured native budget;
primitive tests below do not independently prove this composition secure.

1. Dell creates ephemeral X25519 private/public key D, a fresh boot nonce and
   session identifier from approved secure RNG. Its private key never leaves RAM.
   It displays a QR/full256-bit fingerprint committing to D-public, boot nonce,
   session ID, target/native identity and epoch, algorithm/version and role.
   The Mac obtains that value from the **physical Dell screen**, not a BLE field
   or pasted network-generated claim. No session is physically confirmed by an
   agent inventing an observation or by elapsed time/silence.
2. Mac creates a fresh ephemeral X25519 key M and fresh nonce. Both endpoints
   build one canonical bounded transcript containing the exact role-tagged
   public keys/nonces, target ID, current native payload digest/generation,
   positive acquisition epoch, session ID, owner public identity, suite/version,
   selected security profile and lifetime/message budget. Reject missing fields,
   duplicates, unknown suite, noncanonical encodings or another session/context.
   Owner signs this **complete transcript** locally; Dell verifies against its
   already pinned owner public key. No real signing occurs in this branch.
3. Both compute X25519. Reject an all-zero shared result/invalid peer; wipe on
   failure. Raw X25519 output is never an AEAD key directly. Use mature
   `crypto_sha512_hkdf`, transcript-bound salt/info and explicit domain/direction/
   message-class labels to derive separate32-byte keys for Dell confirmation,
   Mac confirmation, Mac→Dell credentials and Dell→Mac acknowledgment. Freeze
   exact transcript/KDF encodings and publish interoperability vectors before
   integration. This avoids reflection, role/algorithm/context confusion and
   cross-direction nonce reuse; a shared secret alone is not peer authentication.
4. Dell sends an authenticated **empty key-confirmation** record bound to the
   complete transcript. Mac verifies it only after the physical recipient
   fingerprint comparison. Mac returns its separate empty confirmation; Dell
   validates it and owner authorization. These checks establish possession of
   the selected ECDH keys and explicit transcript agreement, not hardware/TEE
   attestation. No credential is opened/read/encrypted before this state.
5. Only then Mac reads its existing owner-local credential store through the
   dedicated secret path. For the supported WPA2-PSK/CCMP profile it may derive
   PMK using mature PBKDF2 with exact SSID bytes and send PMK rather than raw
   passphrase. PMK still grants network access and requires the same protection.
   WPA3/enterprise/unknown RSN profiles must not be downgraded into this format.
   No real credential store was opened for this plan.
6. Dell validates the complete encrypted credential record and bounded schema
   before publishing any plaintext to the supplicant. Apply once in this exact
   boot/session/profile and acknowledge with a separate authenticated record,
   never the secret or its fingerprint. Association/HTT/key confirmation/port
   authorization still follow the mature supplicant path; provisioning alone
   is not Wi-Fi connection or IP evidence.

Full fingerprint/QR is the first profile. A short six-digit SAS without a reviewed
commitment protocol and attempt limits permits adaptive guessing; it is not an
acceptable shortcut. A later mature SAS scheme needs separate review. A photo/
trusted physical QR capture can minimize typing, but must truly show Dell.

## Record and lifecycle contract to freeze before implementation

Use XChaCha20-Poly1305 from the pinned library, bounded records (credential body
≤128 bytes, full serialized record≤512), exact lengths, no compression. Clear
associated data commits to version/suite, direction/type, target/native identity,
transcript hash, boot/session/epoch, sequence and ciphertext length. Session keys
are never serialized. Derive per-direction nonce prefixes; append a monotonically
checked64-bit sequence. Key-confirmation, credentials and acknowledgment use
distinct derived keys/domains. Never encrypt different messages with the same
key/nonce. Retransmission may repeat only the exact cached ciphertext; reception
must not reinstall/apply credentials twice. Old/out-of-order sequence, wrap,
context mismatch, unknown record type, unauthenticated/truncated ciphertext or
wrong length fails without plaintext publication. MAC failure must not modify
caller plaintext; primitive negative tests exercise this library property.

One serialized native owner controls handshake state and secret buffers. BLE
connection receipt is not the session identity. Disconnect, reboot, native/epoch
change, timeout, bad transcript, failed signature/confirmation, attempted replay
or native replacement invalidate the session; erase private key, ECDH/KDF outputs,
plaintext and AEAD contexts with mature nonoptimizable wipe. Secrets stay outside
worlds/assets/diagnostic export/DMA/public logs. Erase before native replacement.
Retained ciphertext may be logged only with bounded nonsecret context; no key,
plaintext credential or PMK enters Git, Yukabox, agent chat or screen diagnostics.
Wall-clock claims from an untrusted peer are not a deadline: use monotonic local
timeouts, detect rollback and bound attempts/session resources. Fresh boot nonce
and ephemeral private key are required because RAM-only replay state vanishes.

## Unique physical blocker and next actual actions

First prove approved native secure RNG and finish deterministic protocol/codec/
KDF/confirmation/nonce/replay/wipe tests with dummy values. Then deploy reviewed
enrollment UI alongside the city and request **one concrete physical observation**:
the user verifies/imports the current fingerprint/QR displayed on Dell against
the Mac session. Existing public identity cannot substitute for it. Without a
previously established persistent device identity, each fresh boot/session needs
that binding. It cannot be bypassed while the user sleeps. No approval/question
is being issued now: there is no concrete physical enrollment screen yet.

## Completed host evidence

38476 checks ran **only on Yukabox**, with hash-pinned existing Monocypher4.0.3:
AEAD roundtrips for dummy lengths0..128, every AD/key/nonce/tag/cipher byte
mutation with unchanged output on failure; X25519 two-party agreement and the
all-zero low-order result which a real caller must reject; HKDF-SHA512 comparison
with an independent Python stdlib HMAC/SHA512 oracle and info-byte tampering.
Core and optional module compile freestanding x86-64 COFF. No primitive was
modified; no owner/device key, real credential, signing or hardware was used.
Dummy deterministic arrays are public fixtures, not an entropy source or live
key/nonce reuse example. These tests prove primitive behavior/build feasibility,
**not** RNG quality, endpoint identity, physical comparison, a reviewed handshake,
credential delivery or protection of an actual network password.

Source inventory/proof is scoped to reviewed native project integration; future
hardware/provider discovery remains separate. Before deployment review current
upstream security fixes and final image/RAM budget; a pinned historical version
and passing fixture suite are not blanket security approval.

References: [Monocypher AEAD](https://monocypher.org/manual/aead),
[pinned Monocypher source](https://github.com/LoupVaillant/Monocypher/tree/ab2b16dd619ad5f6979a4fbe69cfa324a6fcc35f),
[UEFI secure technologies/RNG](https://uefi.org/specs/UEFI/2.10/37_Secure_Technologies.html).
Reproduce with `verify_primitives.py --reference <pinned-library> --clang
<reviewed-clang> --output <ignored-runs>` in the isolated remote directory
`/home/yuka/rabbit-world/parallel-secure-provision-v1`.
