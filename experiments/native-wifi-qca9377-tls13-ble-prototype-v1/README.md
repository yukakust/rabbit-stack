# Mbed TLS 3.6.7 bounded BLE prototype — software evidence only

Official release archive SHA256:
`a7e8bcbec0e6f761b4af24f25677626b35f762f68eef79c08677a363212d11f6`.
This matches the [official release](https://github.com/Mbed-TLS/mbedtls/releases/tag/mbedtls-3.6.7).
`vendor/` retains unmodified inspectable library/headers and LICENSE. Public
upstream test certificates/private test keys are fixtures, never physical keys.
Apache-2.0 is selected from the upstream dual license.

All C, ASAN/UBSAN, COFF and EFI links ran exclusively on Yukabox. Every upstream
library C unit is instrumented in the final host proof. Nine actual both-endpoint
TLS1.3 cases pass: mutual pin authentication, wrong pin, entropy failure, deadline,
wrong sequence/epoch,1/17/240-byte fragmentation and corrupted encrypted record.
Additional260 checks call the actual installed certificate verifier: every one of
256 fingerprint bit mutations rejects, name/expiry errors reject, wrong depth
rejects and the correct complete pin accepts. Output never contains key/seed bytes.

The controlled BLE profile is P256/ECDSA/SHA256/AES128-GCM, TLS1.3 only. NoTLS1.2,
PSK,0-RTT, resumption/tickets, sockets, filesystem, OS entropy, threads or clock/date
fallback is configured. External PSA entropy is mandatory. Only host fixtures
provide explicitly synthetic deterministic entropy. The standalone link probe
returns EFI_UNSUPPORTED and its unbound entropy adapter returns
PSA_ERROR_INSUFFICIENT_ENTROPY; neither is an operational native TLS endpoint.

`VERIFY_REQUIRED` stays enabled. A mature trusted-certificate callback explicitly
finds no issuer candidates; the leaf verifier grants trust only to the exact
SHA256 of canonical complete DER SubjectPublicKeyInfo. It clears only the
NOT_TRUSTED flag and retains hostname/key-usage/other certificate errors. TLS
CertificateVerify and Finished remain actual upstream cryptography. Client
hostname is explicit and bounded. This physical-pin policy has no trusted UTC or
CA-chain approval and must not silently become an Internet HTTPS profile.

BIO owns two8192-byte queues per endpoint, max240 bytes per fragment, monotonic
feed sequence and caller epoch. Reordering/overflow/fatal TLS errors stop; no
reconnect/replay is implemented. Application bytes remain inaccessible until
handshake, peer pin and mature verify result pass. Failed reads keep caller output
unchanged; scratch is wiped. Owner Ed25519 AUTH/provisioning is a separate protocol
layer and remains unimplemented here; TLS-ready does not admit credentials.

The caller-owned allocator has512 bounded records, max2MiB data arena, overflow
checks, zero/wipe and quarantine on invalid free. It forbids rebinding while any
owner exists. The two-endpoint test high-water is20096 bytes; each endpoint is17880
bytes and heap metadata12328 bytes. These are fixture peaks, not a complete native
stack high-water or all-owner inventory. Native real entropy and physical full256bit
SPKI QR confirmation remain prerequisites before keys/credentials.

## Measured code limits

| Profile | Standalone file/mapped | Combined original native64 file/mapped |
|---|---:|---:|
| Both roles, `-Os` |130048 /143360|330240 /4325376|
| Both roles, `-Oz` |120320 /135168|321024 /4313088|
| Server, `-Oz` |114688 /131072|315392 /4308992|
| Client, `-Oz` |114688 /131072|315904 /4308992|

Every ordinary combined build exceeds immutable file262144/mapped4194304. These
are real links using byte-verified frozen64 compiler sources and original GCC
driver profile, with unused TLS API roots forced reachable. TLS is not attached or
executed by these size images. Source, compiler/profile and all-owner/full-QEMU
admission still need review for any actual new image.

An existing-GCC `-flto/-Oz` benchmark is preserved as a failed experiment: frozen
overlay declares `qca_diagnostic[888]`, producer defines the larger actual buffer,
and strict LTO type matching rejects it. Frozen64 was not patched and that error
was not suppressed. It is not evidence of an observed physical overwrite.

## Concrete split feasibility

Root's separately measured city-arena parent is212480 file/2195456 mapped. A
114688-file/131072-mapped TLS server child yields aggregate mapped2326528 below4MiB
and each file below262144. This establishes size feasibility, not loader readiness.
Data pools (including city's1958415-byte allocation) still count as actual RAM
owners and must not be hidden in the mapped-code limit.

Existing code already uses genuine UEFI RAM LoadImage200/StartImage208/UnloadImage224,
HandleProtocol152, LoadedImage.options56 and unload refusal. `uefi_abi_test.c`
checks9 actual pinned EDK2/current ABI offsets; no firmware method is invoked.
References are `x86-64-uefi-runtime-supervisor-v1/supervisor.c`, its `abi.h`, and the
frozen64 `driver.c:141` registration entry. The existing immutable bootstrap ABI
remains unchanged. A NEW parent-private child registration, new signed artifact
magic/policy, epoch/counter/hash/target bounds and ownership accounting must be
implemented/admitted before using those standard services for TLS.

Required split guards: authenticate complete bounded source before LoadImage;
account parent+children mapped/code and every data pool; reject OS imports and
out-of-code callbacks; validate loaded parent/system/image ranges; retain ambiguous
LoadImage/StartImage/FreePool/Unload failures; clear callback registrations before
unload; reject unload with live/quarantined TLS/PSA/allocator/RNG/transport owners.
StartImage options are transient and must not become a dangling retained pointer.
Firmware security-policy rejection fails closed. No unsigned execution or new
bootstrap protocol is granted by this evidence.

Future WAN needs a distinct SHA384/P384 issuer-chain/name/trusted-time/record-size
profile. The current actual Tailnet chain cannot be validated by this narrow BLE
profile. No physical BLE, private owner key, credential, actual RNG, native state,
signature, hardware write or Funnel operation occurred.
