# Native64 producer/host oracle

This new isolated oracle copies exact final64 production/compiler inputs and
instruments only a new copy of its verified synthetic fixture. Frozen64 files
are not edited. All native C, ASAN/UBSAN and COFF runs occur only on Yukabox in an
isolated directory/TMPDIR. No BLE, signature, controller, credential or hardware
operation occurs.

Five actual C scenarios export three544-byte QF640001 and416-byte QSCN reads plus
two110-page QFEX passes after checked release: positive, early READY/credit,
500ms slow polls, missing final DMA and missing ECHO. Every capture is tagged
`synthetic-actual-C-producer`, `physical:false`, formatQF641-QSCN1-QFEX1. These
are API snapshots from the model, not actual Bluetooth callback receipts.

The slow-poll capture's observed final-DMA time minus start is3,501,000us with
maximum poll gap500,000us, and it passes. Missing DMA has exact ECHO observed but
last-command DMA false and the unchanged TX2s timeout faults. Missing ECHO has
observed timeout at its posted-ECHO deadline. These facts test source semantics;
they do not measure Dell latency or establish physical Wi-Fi readiness.

Evidence/2026-10-09/report.json binds original native report, unchanged producer
bytes, supplemental compiler inputs, instrumented fixture, actual compiler/test
commands, ASAN log, COFF object and all five capture hashes. Host decoder bindings
can use these fixtures only for semantic compatibility, never physical admission.
