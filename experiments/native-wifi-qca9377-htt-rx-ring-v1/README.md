# HTT op3 default RX ring — pure resource/wire/ownership preparation

Read RESOURCE-CONTRACT.md before integration. This independent branch remains
outside the smaller native63 filter/ECHO/version/passive-scan experiment. No ring
configuration was sent, no DMA was allocated and no frozen component changed.

Primary references: exact Linux ath10k commit6b5a2b7d9bc156e505f09e698d85d6a1547c1206,
[RX_RING_CFG serializer](https://github.com/torvalds/linux/blob/6b5a2b7d9bc156e505f09e698d85d6a1547c1206/drivers/net/wireless/ath/ath10k/htt_tx.c),
[RX allocation/refill](https://github.com/torvalds/linux/blob/6b5a2b7d9bc156e505f09e698d85d6a1547c1206/drivers/net/wireless/ath/ath10k/htt_rx.c),
[QCA9377 hardware parameters](https://github.com/torvalds/linux/blob/6b5a2b7d9bc156e505f09e698d85d6a1547c1206/drivers/net/wireless/ath/ath10k/core.c).
All files are hash-pinned in references.json. fetch_references.py downloads only
those exact public sources; derive_layout.py extracts exact packed structs and
keeps the original ISC rx_desc.h/copyright in the oracle. No Linux runs on Dell:
these are wire/layout references for a new bare-metal component.

The independently compiled upstream oracle confirms descriptor-v1 size300,
RX_RING_CFG payload40/ring32 record36 and ten four-byte-unit offsets:
`[59,75,21,31,3,20,6,10,1,2]` for header/payload/PPDUstart/PPDUend/MPDUstart/
MPDUend/MSDUstart/MSDUend/attention/fragment respectively. The body is H2T type2,
num_rings1, reserved0, exact supplied32-bit ring/index DMA addresses,2048 entries,
2048-byte buffers, flags0xffff and actual current producer index. No WMI TLV
header is invented around it. Serializer bytes match exact packed upstream
layout, including canaries and deterministic reserved-zero policy.

`ring.c/h` is a pure structural state/action component, not a DMA allocator or
hardware authority. Caller supplies33 actual coherent mappings/identities/epoch,
32 slabs64KiB and one12KiB ring/index map, allocated while real BME was off, with
checked32-bit bounds/alignment/nonoverlap. All booleans require independent real
native proof; synthetic flags alone are not authority. Root still must validate
nonoverlap with existing CE/asset/runtime maps and complete47-owner lifetime.
State starts zero NEW or fully released CLOSED; rebinding an active ledger is
rejected. The8328-byte caller-owned state is not an embedded2MiB payload pool.

Each refill reservation owns a unique available buffer and ring slot before any
external publication. The returned action offsets require clearing attention at
byte4, preparing the whole mapped buffer, publishing the address entry, completing
a real device visibility barrier and publishing the producer shadow. Only then
publish-proof commits POSTED. Any ambiguity quarantines reservation/maps in FAULT;
there is no blind rollback/unmap/retry. Initial fill is1023, never half/full2048.
CFG serialization is followed by a fresh actual RX floor recorded immediately
before CE4 publication; older/duplicate/wrong-epoch indications cannot claim.
CE4 DMA completion advances CFG_TRANSFERRED only: it does not establish firmware
acceptance, RX readiness or a receive/data-plane milestone.

Claims are transactional, at most255 unique already-posted buffers, only after
an independent decoder validates the complete actual HTT indication and DMA
ownership/provenance. Copied completion requires actual DMA acquire and owned-copy
lifetime completion before reuse/refill. One coordinator owns the real ledger;
the decoder and this state machine cannot independently consume the same buffer.
A future adapter must map actual paddr/owner identity to those same entries.
Full reorder is a genuine SERVICE_READY capability, not inferred from HTT3.56;
normal RX_IND FIFO/MPDU/MSDU assembly remains outside this component.

Cleanup can record releases only after actual target halt, BME OFF, callbacks
stopped and device-write barrier for the current epoch. All33 extra maps release
exactly once; remaining14 CE resources belong to Root's separate existing ledger.
Software CLOSED is not an actual47-map cleanup proof. No descriptor/MSDU/EAPOL/
keys/IP parsing or authority is implemented here. Refill dispatch must remain
bounded by reference cap100 per pass; the API itself prepares one action per call.

`verify_remote.py` was run only on Yukabox in
/home/yuka/rabbit-world/parallel-htt-rx-ring-v1 with its own TMPDIR.27,764 synthetic
ASAN/UBSAN checks, independently extracted upstream oracle and a freestanding COFF
object passed. Tests cover bad/overlap/duplicate/unmapped/noncoherent/master-on/
wrong-epoch/high32-bit/range inputs; exact wire bytes; half-fill limits; transactional
claim negatives;4096 producer-wrap/refill cycles; stale RX floor; live-ledger
rebinding; ambiguous visibility quarantine; missing BME-off halt proof; duplicate
release and all33 cleanup bookkeeping. These are synthetic, not real DMA.

Final EFI/runtime allocation caps are unmeasured. Existing native62 channels
requires exactly14 and cannot accept these mappings unchanged. Root must create
a scoped external-map ownership adapter, real before-BME allocation, correct
cache synchronization and measured complete image/resource/lifetime proof before
any physical ring trial. No credential/key/BLE/state/sign/USB/HCI modification or
native deployment occurred in this scope. Missing scan61 WMI beacons remain an
unproved cause; this software work does not attribute them to HTT.
