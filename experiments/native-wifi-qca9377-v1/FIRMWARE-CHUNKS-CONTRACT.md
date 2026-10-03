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

`firmware_port.c` owns UEFI BootServicesData allocations for the reviewed asset
and65760byte packet workspace, with at most one allocation/free per step. It
checks System/Boot table headers and exact AllocatePool/FreePool pointers before
calls. Before allocating, it requires a native-owned QPD7 successful BMI/clean
shutdown snapshot with exact Dell identity and manifest type/version match.
It does not accept client-supplied diagnostic bytes or infer compatibility from
the match. The owner/target adapter still must authorize the exact firmware/board
policy. Allocation failures with NULL output can unwind; non-NULL failure output,
pointer overflow or overlapping buffers retain uncertain ownership without any
dereference/free. FreePool error retains the corresponding allocation for retry
under the trusted UEFI API contract. Pin blocks cleanup; cancel zeroes accepted
asset RAM before free. Opaque/uncertain ownership blocks native unload.

`asset_build.py` wires this adapter/ATT service into the existing city+BMI driver,
including stop/close/unload guards. Its compiled policy is deliberately disabled:
there is no physical BMI reply or compatibility evidence yet. The signed native15
candidate and all its sources remain unchanged. The separate unsigned asset
candidate has actual normal/EMPTY UEFI city/ATT discovery/read/blob/denied-write
gates, with QCA absent and no asset allocation. This proves service integration
and rejection, not firmware reception or positive UEFI allocation. RAM allocations
and BMI snapshots in the11 host adapter scenarios are mock fixtures. No owner
signing, physical update, firmware execution or Wi-Fi connection in these gates.

`mac_firmware_sender.m` sends one previously signed chunk. The portable
firmware_sender_core parses exact64byte receipts and decides BEGIN/DATA/COMMIT
or finish/reject/loss/busy. It detects confirmed-prefix regression and refuses
foreign staging/aborted sessions without ABORT or a new session identity. Only
matching accepted receipt with correct asset bitmap/ready flag finishes. Even
an ACK does not advance progress; read the server status after every write.

Checkpoint binds the whole packet SHA256, confirmed floor and attempted flag.
Write it atomically and fsync file/directory before any radio write and after
receiver status. A lost connection/timeout keeps the same signed packet and
checkpoint. Current-world controller lock serializes this with native/world
delivery; pending operations block firmware send. Wrapper verifies the current
installed owner gate/public identity and Ed25519/body hash before radio, then
gives the helper a private immutable copy of the verified packet bytes. It
never accesses a private signing key. Complete asset/compatibility authorization
remains with the future owner/target policy and native receiver.

`send_firmware_chunk.py` compiles only by default. `--preflight` checks a signed
packet/checkpoint offline without a Bluetooth manager. `--query-only` performs
characteristic reads; `--send` uses ACKed writes with100byte bodies and50ms delay,
one packet per invocation. Receiver acceptance means RAM only, never firmware
startup. Mac compile/offline tests do not prove CoreBluetooth radio callbacks.
Actual send is bounded240seconds, read-only query60seconds; reconnect by querying
the same session before retry. New receiver service must be installed/gated first.

The standalone `firmware_channel.c` and `firmware_gatt.c` implement the secondary
ATT channel. They are not wired into the current native driver. Service UUID is
52414242-4954-4649-8000-000000000007, handles11..17. Control13, data15 and status17
have UUID suffixes8,9,10. Existing file handles1..7 and diagnostics8..10 delegate
unchanged; legacy server owns MTU negotiation and reconnect resets only its MTU.
An adapter calls `qca_fc_att` before the legacy handler and delegates SIZE_MAX.
Do not initialize or replace asset/channel policy from an incoming BEGIN packet.

Control messages are44bytes: RFC1 magic, operation byte1=BEGIN/2=COMMIT/3=ABORT,
three zero bytes, LE32 packet length, SHA256 of the entire signed chunk packet.
DATA is LE32 packet offset followed by1..240bytes. Exact duplicate DATA is allowed
only inside the confirmed prefix; gaps, partial overlaps, changed retries and
out-of-bounds offsets fail without advancing it. Foreign BEGIN cannot replace
active staging. COMMIT requires complete bytes and matching transport hash, then
invokes the signed RAM core. Repeated matching final BEGIN/COMMIT returns the same
terminal receipt. ABORT clears staging without altering accepted asset chunks;
an explicit subsequent BEGIN can restart an aborted packet. Disconnect alone
must not reinitialize either channel or asset. Module replacement/reboot can
lose RAM state; the Mac must query, compare hashes and detect prefix regression.

Status is64bytes, readable with ATT Read/ReadBlob even at MTU23:
RFCS0001[8], state/error/length/received[4bytes each], packet SHA256[32], accepted
asset bitmap[4], ready/pinned/poisoned/reserved[1byte each]. States0=idle,1=staging,
2=accepted into RAM,3=rejected,4=aborted. Error20=transport hash failure; errors1..7
come from the signed RAM core. Status is an observable receipt, not attestation
or firmware startup proof. No World/native counter is advanced by this channel.
Only write requests with ACK are supported; write commands do not modify state.
Channel close clears workspace state, but does not release the asset buffer;
adapter closes the channel before cancelling/freeing the asset, after stopping
its consumer/DMA. Pin blocks control/DATA/close until the consumer unpins.

Add owner-bound target policy, separately framed Bluetooth RAM-asset service,
read-only progress/hash receipts, same-session recovery, bounded UEFI allocation
and native unload guards. Gate actual normal/EMPTY UEFI city/BT preservation and
current-world exact rebuild before any signed physical update. Firmware startup
still requires compatible physical BMI identity, container extraction/calibration,
BMI memory commands and firmware-ready handshake. Host RAM tests prove none of
those hardware outcomes and do not authorize executing the OTP helper.
