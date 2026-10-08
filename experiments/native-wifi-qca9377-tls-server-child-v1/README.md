# Genuine Mbed TLS3.6.7 server child through private UEFI registration

New derivative; frozen tls13-ble-prototype-v1 unchanged. Unmodified upstream
vendor snapshot/license, engine, allocator and public fixture model copied with
exact source hashes. No user keys/credentials/RNG/BLE or native state operations.

`tls_child_entry` is a real boot-service-driver entry. It obtains LoadedImage via
HandleProtocol, validates new parent-private ModRegistration, copies epoch,
module counter/hash/parent hash, publishes one executable dispatch and unload
hook, and retains no LoadOptions pointer. No key/RNG/TLS work occurs at entry.

Typed dispatch:0 close,1 open server,2 feed,3 drain,4 poll,5 write,6 read,7 public
status. Child is single-owner, non-reentrant parent serialized-loop interface.
Input epoch must match registration. Request/output/pool/image/state overlaps
are rejected. Caller-owned aligned pool65536..131072 bytes; sole allocator is
held until all real Mbed TLS/PSA/heap owners free. Public status is available in
quarantine; unloading refuses open/live/quarantined state. Close revokes entropy
callback/context and wipes real protocol/key/heap storage, then actual parent
UnloadImage precedes wiping file bytes. Pool deallocation remains parent's duty.

Open requires certificate/key input, full32byte peer DER-SPKI fingerprint and
parent entropy callback. This narrow adapter does not generate/authorize device
identity or authenticate callback provenance. Parent must prove approved fresh
entropy, physical full-SPKI confirmation, ownership/lifetime of callback and key
material, owner AUTH signed payload and replay policy before real secrets.
No bool/test callback can satisfy those physical gates. Failed entropy callback
wipes partial output and returns actual PSA insufficient entropy, with no
RDRAND/timer/MAC/jitter fallback.

Actual cryptography/profile unchanged: TLS13 only P256/ECDSA/AES128GCM/SHA256,
mutual complete DER-SPKI pinning+CertificateVerify+Finished, no0RTT/PSK/resumption,
8KiB queues, <=240byte fragments, <=60s injected monotonic bound, <=1024 app bytes.
Serial transport ordering/checkpoints belong to future parent: drain transfers
ownership of returned ciphertext and is not an automatic retry/reconnect policy.

Yukabox proofs instrument every actual upstream unit ASAN/UBSAN. Seven genuine
child-entry interoperability/failure cases exercise public fixtures, fragment1,
pin error, entropy failure, epoch/sequence/time, corrupted encrypted application,
no pre-handshake plaintext, alias/admission failure and key/heap close. Original
nine TLS13 cases+260 actual SPKI bit/name/depth checks rerun unchanged. Native
113COFF+real import-free standalone PE server-Oz,117248file/159744mapped.
Conservative parent2224128+child159744=2383872mapped; perfile<=262144 andaggregate
<=4194304. Parent exact composition/source gate is not inferred from this sum.
Additional caller RAM pool<=131072 must have a distinct runtime arena budget.

Actual QEMU/OVMF parent fixture separately observes genuine signed child load,
options registration and unload. It deliberately does not open TLS or call RNG.
No physical Dell/RNG/QR/HTTPS success is claimed. This BLE pin profile does not
support the actual WAN SHA384/P384 issuer chain; HTTPS child remains separate.
