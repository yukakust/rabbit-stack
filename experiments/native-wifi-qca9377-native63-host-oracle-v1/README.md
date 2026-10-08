Independent synthetic oracle for the frozen63 producer/host boundary.

`verify_oracle.py` copies byte-exact production/compiler inputs from the pinned
final native report and candidate closure. It adds output instrumentation only
to a new copy of the already verified fixture. Native C/ASAN/UBSAN/COFF runs only
in its isolated Yukabox tree with an isolated TMPDIR. Frozen63 files, signatures,
controllers and physical devices are untouched.

Captures contain three actual QF630001/QSCN reads and two actual110-page raw
export passes after checked release. Scenarios: positive passive target fixture,
READY-before-INIT-DMA with intervening credit frame, and missing-ECHO failure.
The exact producer returns filter.tx_count3 and filter.tx_completed1: the latter
is a current-command boolean, not an aggregate completed-command count.

Every capture is tagged `fixture_kind: synthetic-actual-C-producer` and
`physical: false`. These are not Bluetooth receipts and must never enter physical
admission. The pure host decoder can consume them as a compatibility oracle.
There is no physical discovery, association, key, DHCP or IP claim.

Reports/captures reside in runs/producer and public evidence/2026-10-08. The new
fixture compiles unchanged producer bytes; the production closure, original and
instrumented fixture hashes, actual commands, ASAN log, COFF object and capture
hashes are recorded. No new whole EFI build or signing is requested by this lane.
