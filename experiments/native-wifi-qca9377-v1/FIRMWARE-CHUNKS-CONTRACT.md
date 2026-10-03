# Signed firmware assets in RAM

This component assembles opaque reviewed assets, not firmware compatibility or
radio operation. It is not integrated into native15, Bluetooth or BMI upload yet.
No production key is read by its verifier. Host tests use a public synthetic key.

Each packet is at most65760bytes: a160byte signed manifest,64byte Ed25519 signature,
then up to65536bytes of asset data. This fits the262144byte existing transfer budget
without altering the immutable bootstrap. Future native-owned Bluetooth service
must provide its own framing/receipts and call this receiver; the current world
and native update service must retain its handles and operation meanings.

## Packet layout

All integers are little endian. Signature covers exactly bytes0..159, beginning
with the unique `RABFW001` domain. SHA256 of the body is within that signature.

| Offset | Bytes | Meaning |
| --- | --- | --- |
| 0 | 8 | RABFW001 domain/version |
| 8 | 32 | Reviewed target identity |
| 40 | 32 | Whole asset SHA256 |
| 72 | 32 | Chunk SHA256 |
| 104 | 4 | Whole asset length |
| 108 | 4 | Chunk offset |
| 112 | 4 | Chunk length |
| 116 | 4 | Fixed chunk size65536 |
| 120 | 8 | Exact authorized transfer generation |
| 128 | 4 | Exact physical BMI target type |
| 132 | 4 | Exact physical BMI target version |
| 136 | 4 | Asset kind1=firmware container,2=board data |
| 140 | 20 | Reserved zero |
| 160 | 64 | Owner Ed25519 signature |
| 224 | variable | Chunk bytes |

The receiver policy is supplied by the reviewed native adapter: owner public key,
target identity, asset digest/length, generation, type/version and kind. None is
learned from an incoming packet. The future adapter must bind policy to a fresh
physical BMI reply, exact board selection and owner-checked asset provenance.
This implementation rejects empty/unknown BMI identity but cannot prove the
caller obtained it physically. Current host fixtures are explicitly synthetic.

## Lifetime and acceptance

Caller supplies a separately allocated RAM buffer, initially unpinned, of at
least the reviewed total length. Maximum asset length2MiB,32chunks; no allocation
or device register access is performed here. Buffer/state/policy/packet storage
must not alias. Callers serialize access; no interrupt or concurrent callback may
modify the state. Caller retains buffer ownership until cancel succeeds.

Validate all bounds, context, reserved fields, signature and body hash before
writing RAM. Offset must be chunk-aligned and every chunk must have its exact
expected length. Out-of-order arrival and exact duplicates work; duplicates whose
stored bytes differ fail. Chunks from another generation, target, type/version,
kind, whole digest or owner fail without changing the accepted bitmap.

Only after all chunks arrive and the whole SHA256 matches is the asset ready.
Rehash immediately before pinning for the eventual BMI consumer. Corruption
poisons the assembly until cancellation; no partial asset pointer is exposed.
Pinning prevents acceptance/cancellation/replacement; unpin only after the
consumer has stopped using the buffer, including any asynchronous/DMA lifetime.
Cancel zeroes the entire reviewed asset range and releases the assembly claim.
It does not free the caller's buffer or reset hardware. The adapter must stop
DMA before unpinning and freeing RAM. RAM state is lost on reboot; resume requires
matching live state/receipts, never an assumption from a saved Mac bitmap.

## Remaining integration

Add owner-bound target policy, separately framed Bluetooth RAM-asset service,
read-only progress/hash receipts, same-session recovery, bounded UEFI allocation
and native unload guards. Gate actual normal/EMPTY UEFI city/BT preservation and
current-world exact rebuild before any signed physical update. Firmware startup
still requires compatible physical BMI identity, container extraction/calibration,
BMI memory commands and firmware-ready handshake. Host RAM tests prove none of
those hardware outcomes and do not authorize executing the OTP helper.
