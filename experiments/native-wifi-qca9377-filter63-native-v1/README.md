NEW unsigned generation63 partial startup experiment. No device operation,
owner key, BLE session, credential provisioning, association or IP claim.

Actual production path: full authenticated firmware bootstrap and WMI READY;
CREATE0 STA using READY MAC, DELETE0, exact new ECHO processing barrier;
authenticated HTT VERSION_CONF3.56; same owned TX adopted without serial reset;
13 reviewed passive channels (0x21), target ASCII `iPhone (9)`; finite scan stop
and exact fourteen-owner release. TLV baseMAC operation is unsupported and is
not invented. RX_RING_CFG and aggregation remain absent: this is a partial
startup diagnostic experiment, not an HTT data plane.

`filter63_build.py` derives new bytes from frozen60/61/62 components and the
frozen filter-barrier-v1 component. `component-inputs.json` binds every copied
component. `filter_fixture.py` drives actual production driver polling and DMA
fixtures, not manually synthesized QcaRxEvent payload/raw pairs.
`verify_native.py` runs ASAN/UBSAN and COFF only on Yukabox. Sixteen model
scenarios include ordering, missing/wrong Echo, unsupported VERSION, retained
unknown HTT and bounded archive overflow. `handover_test.c` compiles the actual
production query transfer and tests84 alias combinations and8 failed inputs.
None of these fixtures is physical evidence.

`prove_filter.py` requires an exact native report, three identical whole EFI
builds within262144 file/4194304 mapped caps, source/compiler closure, distinct
normal and EMPTY QEMU, and exact world19 host/tail timing/semantic proof. Fixed
public test keys are synthetic fixtures only. Local owner material is never read.
Final reports live in `runs/native-host/report.json` and
`runs/checked-candidate/report.json`; public copies may be archived in evidence
by Root after review. No report or generator grants hardware admission.

The raw schema, storage/lifetime tradeoffs and first-READY prefix semantics are
specified in SOURCE-CONTRACT.md and native-abi.json. The status requested-SSID
annotation is a local plan, not discovery evidence. Actual discovery requires
a retained owned WMI beacon at the current scan epoch and live-frequency stage.
Historical exported frames never grant association or controlled-port authority.
