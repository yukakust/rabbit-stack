# Native64 bounded filter timing correction

New isolated unsigned producer derived from frozen63; frozen63 and its physical
completed firmware session remain untouched. No BLE, controller state, signing,
USB/HCI, reboot, credential, flash or physical device operation occurs here.

Each filter command has a3s stage budget; a new stage starts only after actual
prior-command DMA completion. Exact ECHO's3s reply budget starts at the observed
actual POSTED publication, rather than before CREATE. An independent12s overall
cap bounds the operation. The existing sole TX owner's2s request timeout, credit
ledger, epoch, request/byte counts, immediate POSTED/refund order, raw reply/floor,
and fourteen-map release guards are unchanged. At/beyond a deadline cannot pass.
Firmware ECHO alone does not prove DMA completion.

QF640001544 bytes preserves the old first448 field layout with generation64 and
adds twelve LEu64 observational times described in native-abi.json. These are
host observation times, not RF/USB arrival timestamps. Last-command DMA remains
a boolean; cumulative persistent TX completions are separate. The terminal
filter's poll-gap ledger stops moving, permitting stable read-only snapshots.
QSCN416/gen64 and rawQFEX0001/22slots/110pages/last56 remain unchanged in layout.

The exact actual C producer models passed18 scenarios, including500ms slow polls
whose CREATE/DELETE/ECHO total exceeds3s while each command remains valid, and
an ECHO-present/missing-third-DMA case that still faults at the unchanged TX2s
limit. Actual query transfer has92 ASAN checks. The independent derived filter
component passed140125 existing regression checks and11 timing/order/boundary
checks, with5 COFF objects. Producer15 COFF objects also passed.

Three whole EFI builds match: payload202752 bytes, mapped4194304 bytes under the
unchanged262144/4194304 limits. Normal/EMPTY QEMU and exact world19/tail timing
checks passed. All outcomes are synthetic/software proof; no physical64 result,
RX_RING_CFG, aggregation, association, keys or IP is claimed.

Evidence/2026-10-09 contains exact native/candidate/reproduction reports and
`timing-production-join.json` binding the component proof, ABI, actual scenarios,
source closure and protected driver/USB/BT/PCI/TX byte equality to frozen63.
The candidate report has470 source inputs and207 generated compiler sources.
Public artifacts are under runs; Root performs independent admission separately.
