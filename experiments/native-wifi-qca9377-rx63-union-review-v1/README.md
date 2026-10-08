# Native63 RX byte-union proposal — conditional source review

The proposal is technically sound **for the currently admitted unbundled HTC profile**, pending corrected exports and full native production tests. The pinned decoder always places payload at raw+8 and removes trailer bytes from payload length. WMI and HTT inner dialects share this envelope. Bundles/unsupported HTC flags are rejected; this is not an all-dialect guarantee.

An embedded raw2048 / header8+payload2040 union owns bytes rather than pointers. Value copies stay independent of the DMA buffer and original queue object. Beacon/parser outputs also copy their fields and do not retain packet pointers. Raw bytes must be copied once from actual DMA; writing or zeroing a payload tail would destroy its overlapping actual HTC trailer.

Current source review found required integration changes:

- QEXP normalized export still reads all2040 payload-view bytes. It must virtual-zero serialized padding after event.bytes, preserving raw storage. A credit trailer otherwise appears as nonzero normalized padding.
- RX62 retains valid credit-only and HTT endpoint records. Old scan dispatch/coordinator rejects them. Explicitly archive valid unrelated records with ownership and strict scan-event checks intact.
- The old host QEXP decoder rejects populated zero-length credit-only records. Native63 needs a reviewed derivative; normalized payload-only records cannot prove their omitted raw trailers.

Actual native tests must assert raw/payload offsets and sizes, rebuild every consumer together, drive the genuine RX/CE producer with coherent HTC bytes, include credit-only/trailer/maximal-length/rejection/backpressure/copy/repost cases, and verify both normalized and full raw exports. Fabricated separate writes to raw and payload are no longer valid fixtures. No physical admission follows from this source review.

The pure Python byte model checked4081 length/trailer/copy/unsupported-flag cases. It is explicitly not a C ABI or actual-driver test. report.json records the inspected draft source hashes and pending conditions. No frozen61/62, native sources, hardware, keys or state are edited by this reviewer.
