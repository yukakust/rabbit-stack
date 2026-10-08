# Independently signed RAM module artifact + private UEFI loader

New software-only scope. No immutable bootstrap or frozen native sources changed.
Root owns any future signatures/actual credentials/Bluetooth/state operations.
This native child is privileged owner-authorized code, not a memory sandbox.

## Distinct authenticated framing

`RABMOD01`, header288 (224 signed ordinary Ed25519 bytes +64 signature),
up to4×65536 payload chunks, exact final short chunk, max262144 file bytes.
Header offsets: owner8, target40, parent-code hash72, full-artifact hash104,
chunk hash136, parent epoch168 (u64), module counter176 (u64), total184,
offset188, length192, role196, ABI200, mapped size204, chunk size208,
zero reserved212..223, signature224. All integers little endian.

This is not `RABFW001`, RRT1, an existing firmware policy, or an engine counter.
Only role1/TLS-server ABI1 is admitted by this version. Trusted parent supplies
exact authorized owner/target/parent hash/epoch/counter/size/hash policy;
self-asserted file metadata cannot establish that policy. Module counter must
exceed last consumed counter and is consumed before LoadImage. Counter persistence
and authenticated current-parent binding belong to the future parent operation.

Every accepted chunk verifies real copied Monocypher Ed25519 and SHA256;
complete manifest digest is checked again at pin. Exact duplicates are idempotent,
contradictory signed duplicates poison, incomplete/tampered/wrong-policy/overlap
frames cannot acquire ready. No public model key is allowed by a physical gate.

## Loader lifetime and bounds

`ModEfi` binds genuine existing UEFI BootServices LoadImage(200), StartImage(208),
UnloadImage(224), HandleProtocol(152), FreePool(72), using the actual parent
handle and LoadedImage.options layout. Injected firmware is test-only. Function
availability/layout is not firmware/RNG attestation. Valid firmware object
pointers are an explicit caller trust boundary; arbitrary pointers are not probed.

Signed bytes pass restrictive PE32+ AMD64 boot-service-driver validation before
LoadImage. No nonempty imports/TLS/CLR/delay imports/writable-executable sections;
section bounds/entry executable/image size checked. Mapped bytes are reserved in
parent's exclusive aggregate<=4194304 budget before entry and compared with real
LoadedImage size. New ModRegistration ABI is parent-private, exact112bytes;
epoch/counter/digest/parent hash and role must survive entry unchanged. Dispatch
(and optional unload callback) must lie in validated executable sections. Options
are borrowed only across StartImage and cleared immediately afterward.

Close(op0) must succeed before UnloadImage. Dispatch is revoked before unloading;
only successful unload releases mapped reservation and unpins/wipes artifact RAM.
Unknown nonnull/error outputs, invalid firmware mappings, exit-data cleanup errors,
failed close/unload preserve pointers/reservations/pinned bytes in quarantine.
No retry API pretends those owners released; no blind LoadImage/re-sign replay.
Caller still owns artifact pool allocation/free and exclusive operation lock.
The loader does not implement BLE, a signer, DRBG, or credential admission.

## Proofs

Yukabox-only `verify.py`: real Monocypher/SHA signed public RFC8032 fixtures,
4 full chunks/short-final sizes/header-byte mutations/body/hash/conflicting
signed duplicate/alias/replay/cap cases, 18 explicit injected-UEFI modes, ASAN+
UBSAN,5COFF. Count includes262144 bytewise wipe assertions; it is not263k distinct
security scenarios. No private user key or hardware calls.

`qemu_probe.py`: dedicated QEMU-only bootstrap fixture embeds this genuine TLS
child with public RFC8032 signatures. Actual OVMF LoadImage→StartImage→private
options registration→uninitialized public status→close→UnloadImage→artifact wipe
observed. No TLS/entropy/credential/radio calls occur in QEMU; full TLS is tested
in the child host proof. Existing Dell USB bootstrap is never touched.

Copied dependencies retain licensing and source pins (Monocypher dual licensing
in file headers). Source patterns: frozen firmware_chunks, actual supervisor
UEFI ABI; parent-private module loader is newly implemented and not yet admitted
on physical Dell. Root must compose exact parent+child hashes and budgets,
trusted owner/target/current epoch and pool ownership before any future use.
