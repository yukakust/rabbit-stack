# Proposed HTT op3 RX address-ring resource contract — no deployment

Exact upstream ath10k commit6b5a2b7d9bc156e505f09e698d85d6a1547c1206 is the
reference used by `htt-version-v1`. Existing six reference hashes are retained;
additional exact core.c/rx_desc.h/hw.c files are separately pinned. QCA9377 PCI
hw1.0/hw1.1 tables select qca988x descriptor-v1 ops, target64bit=false. Descriptor
offsets must be mechanically derived from those exact packed structs on Yukabox,
not substituted from another chip or inferred from version3.56.

RX_RING_CFG is H2T type2, one-byte command header plus three-byte setup header and
one36-byte ring32 record:40-byte payload. It carries coherent address-ring and
producer-shadow DMA physical addresses, ring entry count,2048-byte RX buffer
size, all16 reference RX flags and ten descriptor offsets in four-byte units.
This is the op3/TLV HTT dialect's native command encoding, not a WMI TLV wrapper.
The producer shadow is host-published after buffer/map/ring preparation and a
real device visibility barrier. Its actual current value initializes firmware's
index; firmware notification/completion is not inferred from writing it.

Prefer the actual upstream default:2048 ring entries, fill1023 (<half ring),
2048-byte buffers,8-byte descriptor alignment and conservative128-byte DMA/cache
alignment. The full-reorder path has no implicit acknowledgment of consumption;
post at most half-minus-one outstanding, and claim/release only from a validated
indication owner. Default is a source proposal, not physical firmware proof.

Proposed bounded runtime ownership:32 caller-owned DMA slabs of16pages/65536
bytes (1024 RX buffers,1023 posted maximum); one3page/12288-byte common mapping
for8192-byte address ring plus separate128-byte-aligned4-byte producer shadow and
padding.33 extra real DMA maps, CE14 unchanged,47 total maps (<portlimit64).
A33-entry HTT map ledger is separate from existing14-entry CEaccess inventory.
Approximate additional mapped allocation is2,109,440 bytes; exact firmware/runtime
memory policy and future EFI bookkeeping size still require measured admission.
No cap is enlarged by this proposal. The unused spare buffer is not silently
posted to firmware. Any reduced ring/fill variant is unapproved for hardware.

All allocations require actual PCI bus mastering OFF before setup/bootstrap,
real mapping return values,32-bit physical DMA range and exact byte spans,
identity/lifetime/epoch, nonoverlap with every CE/asset/runtime/shared map,
and coherent common-buffer/device visibility contract. Frozen channels currently
requires dma_users14: Root must implement separately reviewed external HTT owner
accounting and cleanup; neither accepting an unexplained47 nor pretending14 is
permitted. No allocation/map/register/reset/BME operation exists in this scope.

The component can only produce bounded deterministic bytes/action state after
caller supplied verified mappings and visibility operations. Publishing an address
requires cleared RX attention word, full mapped buffer visibility, visible address
entry, barrier and producer shadow publication in that order. On any ambiguous
failure retain ownership/quarantine, never unmap while firmware may DMA. Refill is
bounded (reference cap100 per pass), after transactional owned indication claim,
DMA acquire/sync and copied frame/descriptor lifetime completion. Duplicate/stale/
wrong-epoch/unposted physical address cannot release or republish a buffer.

Cleanup requires explicit quiesce, actual target/CE halt and confirmed BME OFF,
IRQ/RX/TX callbacks stopped, device-write barrier completion, then33 HTT maps
released exactly once plus existing14 CE resources. Root's future adapter must
prove actual47-owner cleanup; a software ledger zero is not a hardware proof.
No RX/data-plane-ready/SSID/association/IP authority follows from CFG TX completion.

Pending joins: actual authenticated firmware op3 and local VERSION_CONF metadata,
actual SERVICE_READY full-reorder service interpretation, hardware_filter_reset
CREATE/DELETE/ECHO barrier, HTT aggregation setup, CE4 single publisher/CE1 single
consumer, descriptor/MSDU decoder and public raw evidence. These are independent
of assuming that missing WMI beacons were caused by an unconfigured RX ring.
