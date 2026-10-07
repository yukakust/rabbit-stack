# Provisional native54 passive scan profile

Offline actual-native integration of frozen52 READY, reviewed53 persistent RX,
serialized CE3 publisher, channel/regdomain codecs, station/scan dispatcher,
owned STOP and beacon parser. No keys, credentials, physical scan, signing or
RF admission are performed here. The parent reserved54 provisionally; physical
53 result and a separate deterministic RF gate remain admission prerequisites.

## Policy and ordering

`verify_policy_binding.py` independently verifies CMS using the Linux-pinned
public signer, checks the signed-regdb rebuild and tamper failures, reproduces
the exact GE×unchanged world108 proposal and verifies `scan_policy.h` byte-for-
byte. Source/trust/provenance hashes remain explicit. The original artifact
still says `OFFLINE-REVIEW-PROPOSAL-NOT-RF-ADMISSION` and `rf_admission_granted=false`.
No signature claim alone authorizes the hardware operation.

The fixed proposal has13 legacy20MHz passive rows2412..2472, NO_IR preserved on
last2, CTLs255/255 and no country/board override. Actual SERVICE_READY must match
regdomain108/capabilities2312..2732 and4920..6100. Actual PCI/board/owner/target
identity is established by the unchanged target/probe scope plus parent admission.
Code constants are not independent target attestation.

One publisher owns all credit reserve/commit/cancel actions; RX applies trailers
once. Order is SCAN_CHAN_LIST → PDEV_SET_REGDOMAIN → STA CREATE → passive scan.
Matching DMA completion permits ordering only. Real newer SCAN_STARTED and
terminal events establish acceptance/end. No CREATE/regulatory ACK is invented.
SSID detection additionally requires an owned management beacon during matching
FOREIGN_CHANNEL in the current epoch and selected frequency. AP authentication,
association, EAPOL/keys, HTT data, DHCP/IP and Yukabox exchange remain later.

## Bounds and retention

Command deadline2s, scan7s, credit2s, STOP3s and overall25s use cooperative polls.
Found SSID, archive saturation or RX backpressure requests owned STOP. End/fault/
overall expiry invokes checked `qca_stop` once; actual all-eight CE stop/BME-off,
flush/unmap/free and all14 owner release still govern unload. Expiry is not release.
An adapter fault can retain owners honestly instead of claiming a safe shutdown.

Unsupported/foreign/control events are explicitly transferred to a two-event
wrapper archive. Full archive never drops a packet to advance the queue. The
observation, coordinator orphan, dispatcher and RX FIFO retain remaining copies.
There is no raw RX clear after stop. Future native replacement must first save
the exact exports; status counts alone are not ownership-transfer proof.
Old53's two unknown packets lacked raw export and cannot be reconstructed here;
its archived limitation is distinct from the new54 export protocol.

## Read-only diagnostics and exports

`QSCN0001` is416 bytes, service UUID ending002a/characteristic002b, handles32..34.
Its64u32 fields come directly from `scan_build.py`, followed by proposal/ruleset/
location hashes at264/296/328, parsed SSID at364 and BSSID at396. It separates
submitted/DMA/STARTED/terminal/found/policy/credit/actual owners and logical state.
RF/association/IP proof fields remain zero until separately observed/admitted.

Export service UUID002c handles35..115 has40 read-only characteristics UUID0040
through0067, each value<=512 bytes and standard READ_BLOB offsets. Eight retained
slots, five pages per slot: archive0/1, observation, coordinator orphan, dispatcher
head/next, RX head/next. Slots are2084 bytes: magic8 +9u32 metadata +2040 payload.
Metadata records slot/presence/completion/epoch/endpoint/pipe/length/event. Empty
slots are explicit. `decode_exports.py` reconstructs exact bytes/hashes without
acknowledging or clearing anything. Freeze after real radio quiesce, save all40
pages, verify stable repeats/counts/current receipt/epoch, then admit later unload.
There is no write ACK or arbitrary-memory-read bypass and no device attestation.

## Evidence

Actual-entrypoint ASAN/UBSAN tests use the full native PCI/CE/DMA adapter with an
explicit simulated firmware. Physical-shaped HTC2credits/1792size and WMI1784
limit are used. Cases cover started/foreign-channel/beacon/owned STOP, unknown+
foreign archive, credit starvation, unsupported channel, malformed beacon,
publication stall/ambiguity and clock rollback. They prove all14 release and
stable export pages/READ_BLOB bounds/write rejection, not over-the-air behavior.

Whole EFI repeatedly rebuilds, checks source closure and runs real supervisor
QEMU normal+EMPTY with status/export absence behavior, city/restoration/rejection
and frozen world17 C ASAN120ticks/adversarial camera. Only generated module copies
receive whitespace-only statement separation for strict GCC; frozen code is intact
and those exact copies are also used in native model checks.

Candidate metadata remains `physical_verified=false`, `signing_admitted=false`
and `rf_admission_granted=false`. Do not treat a host fixture or a passive flag
as proof that no over-the-air probe occurred.
