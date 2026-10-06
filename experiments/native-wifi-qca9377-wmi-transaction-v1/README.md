# Pure WMI INIT transaction coordinator

Reuses the existing checked INIT serializer, credit ledger, HTC frame codec and
WMI READY parser. Not included in frozen native45. No actual DMA allocation,
station resource policy approval, descriptor publication, WMI transmission,
credentials, scan, association or IP. The opaque resource vector in fixtures
is a test input, not an approved radio configuration.

Exclusive borrowed ledger reserves at construction, commits BEFORE descriptor
publication, refunds only unposted cancellation or valid firmware credit reports.
DMA completion never refunds credit. A READY received before TX completion is
retained but does not mark startup complete. Both TX completion and valid READY
(major and namespaces checked; minor preserved as firmware metadata) are required. Firmware error,
malformed/foreign frames, duplicates or out-of-order consumed completion IDs
preserve state. Completion IDs are caller-provided actual hardware-consumption
sequence, not cryptographic replay detection. Ambiguous publication calls fault
and retains committed credit; actual all-owner stop/flush/unmap/free is external.
After RUNNING, ordinary WMI dispatcher takes over the exclusive ledger.

Before native integration: actual SERVICE_READY memory requests, independently
reviewed station vector, retained live32-bit DMA owner scope with non-overlap
against control buffers, bounded deadline/cancellation/cleanup and reproduction.
Legacy boot DMA allocator requires bus mastering off; it cannot simply be called
while the current CE adapter runs. That lifetime change still requires its own
checked implementation. This coordinator does not solve or bypass that guard.

The 2026-10-06 revision removes a redundant READY minor==53 restriction.
The pinned Linux ath10k READY parser reports abi_ver1; it does not compare it
with the INIT minor. Our existing strict major/namespace, status, frame, MAC,
credit and ordering checks remain. Physical native46 SERVICE_READY reported
minor574, but no physical WMI READY has yet been observed. Tests use synthetic
READY minors 0, 53, 54, 574, 65535 and UINT32_MAX with both DMA/READY orders,
and independently corrupt every major/namespace word before acceptance.
This host-only module is not part of the frozen native47 input manifest.
