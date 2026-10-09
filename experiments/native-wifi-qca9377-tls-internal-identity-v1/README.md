# Dell-local TLS identity child — software only

NEW derivative of frozen tls-server-child-v1. No frozen files changed. Actual
Mbed TLS3.6.7 creates a P256 private key inside the child, writes a self-signed
SHA256 certificate, extracts complete DER SubjectPublicKeyInfo and computes its
full SHA256. The private key stays in owned Mbed TLS memory; there is no imported
Dell private-key field, private-key serialization/export or host-generated Dell
key fallback. Old OPEN1 is rejected. Only public certificate/SPKI/hash/QR leave.

Registration remains the112-byte parent-private ModRegistration/role1/ABI1;
exact child file hash pins these NEW application ops. Parents must not mistake
registration ABI compatibility for the old imported-key application interface.
Ops: GENERATE0x10, PUBLIC0x11, ACTIVATE0x12, RESET_SESSION0x13, PUBLIC_QR0x14;
old FEED2/DRAIN3/POLL4/WRITE5/READ6/STATUS7 and CLOSE0 remain typed. Generate208,
Public1272, Activate32 and PublicQr392 bytes are compile-time asserted.

Generate is a parent-private reviewed request: current epoch, owned aligned
64..128KiB pool, actual inventory/parent/code-set approval and an admitted leased
parent raw-source callback/context/full source hash. This is NOT a network
message or self-created physical authority. Parent must have installed all exact
reviewed executable modules, sealed their code set, validated actual65 inventory
and bound trusted-execution RDSEED-v2 before supplying ANY source. The child
cannot authenticate firmware/providers itself. Target/owner/parent/module
admission and physical full-SPKI confirmation remain parent/Root responsibilities.

Child performs mature AES256 CTR_DRBG seed/reseed with48 source bytes and
prediction resistance on every request. Parent source callback is explicitly
rounded to8-byte units <=64, output copied only on full success and all scratch
wiped. Scratch and code hash are in actual private child DATA for typed parent
span verification. Personalization includes domain, epoch, parent hash and code
set (never counted as entropy). Provider/heap/request/image/private-state aliases
are rejected. Busy/borrow guards reject recursive entropy, close and unload.
Source/DRBG failure is whole-identity fatal, blocks retry and publishes no key.

Identity lifetime600s uses parent-trusted monotonic time; transport handshake is
bounded<=60s. RESET_SESSION closes/frees/wipes only the TLS endpoint and requires
heap exactly back to its keystore baseline. It preserves the local key/source,
permits a NEW full TLS1.3 handshake with a fresh parent-authorized peer pin and
external owner nonce, at most64 sessions; no tickets/cache/resumption/0RTT.
Root must clear owner AUTH/cipher transport state on disconnect. Source/code-set
revocation still destroys identity/all clients; reset never clears fatal source
fault. POLL must run even without an active session to retire expired keys.

PUBLIC_QR uses copied source-pinned Nayuki + frozen pairing-qr-v1. It constructs
RABBIT1:<actual-child-epoch>:<FULL-UPPERCASE-SHA256> from the generated identity,
never host/GATT supplied pin. Version<=6, bounded212-byte packed symbol, complete
pin/text/expiry public panel. Repeated reads are nondestructive; QR expiry is
capped by the key deadline. Parent can paint exported public bits without the
encoder. Full publicDER/hash also remain separate for verification/display.

Host proof uses ONLY public upstream client certificate/key fixtures and
explicit synthetic parent entropy. Genuine P256/certificate/TLS13/full-pin/AEAD
and second full handshake, partial-source failure, aliases, reentry, expiry,
keystore reset and complete private heap wipe are checked. Host-only model borrow
helpers handle two endpoints sharing PSA globals; never compiled/exported in the
native child. All-library ASAN/COFF and actual driver11 PE link occur only Yukabox.
OVMF actually verifies public RFC8032 owner-fixture chunks, loads/starts the child,
generates a local key/cert with synthetic source, reads fullSPKI/QR, refuses live
unload and proves close→UnloadImage→private-pool/artifact wipe. It proves actual
code/lifetime, not physical Dell RNG, pairing, Wi-Fi/IP or credential admission.

BLE owner AUTH/ACK and actual physical QR confirmation are separate gates;
WRITE/READ are private trusted application methods, not credential admission.
No credentials/private owner keys/BLE/device/state/signing operations occur here.
