# Provisional native63 partial startup experiment — not signed or deployed

Exact frozen60 boot, frozen62 HTT-aware single CE1/2 receive owner and real version
query, frozen61 reviewed13-channel passive scan logic, frozen filter-barrier-v1
body-only coordinator. Target local matcher is exactly b'iPhone (9)' length10;
START_SCAN remains passive0x21 with empty SSID/BSSID/probe-IE lists. No radio-policy,
active-probe, USB/HCI/resident, bootstrap/OTP/flash or hardware change is authorized
by this source construction. Generation63 is provisional; no counter reserved.

Sequence: actual INIT/READY owner adoption; actualREADY-MAC dummy STA VDEV0 CREATE
then DELETE then exact newly owned ECHO reply as the WMI processing barrier;
actual owned HTT VERSION_CONF without quiescing successful query; same actual
retired CE3 TX owner into real STA VDEV0/scan. Unsupported TLV baseMAC command is
explicitly omitted. No RX_RING_CFG or aggregation: this is a partial source-
backed startup experiment and does not claim complete ath10k startup/data plane.

New derived RX event representation keeps one2048-byte actual HTC raw frame,
with payload byte view at raw+8. Metadata bytes bounds remain authoritative;
HTC trailer is never zeroed by normalized padding. QEXP exports pad virtually
beyond normalized bytes. No pointers to DMA or borrowed buffers are retained.
Every valid htc_decode branch must prove payload==raw+8. This new ABI needs full
actual-producer ASAN/COFF models and independent review, not fixture-created raw.
Frozen prior structs/sources are not edited. All14 actual DMA maps remain unchanged.

One persistent CE3 transmitter is begun for filter and reused only after actual
request DMA completion+retirement with IDLE phase, same radio/life/credit/epoch,
zero reservation/inflight and exact serial/request lineage. No memset/reset of
that TX owner or cookie serial at scan handover. Filter APIs never alter credits;
qca_tx_submit/poll is the sole framing/credit/CE3 publisher. POSTED observation
occurs immediately after publish poll and before another RX pump.

All raw pre-scan events, ECHO and VERSION remain owned/captured in existing16
archive slots; accepted target observation uses the existing slot16. Same22
slots/110 pages/ATT255 bound. Successful HTT query has a distinct READY phase,
not RELEASED while radio is ACTIVE; only eventual checked stop releases14 owners.
Source/debug schemas are provisional until native models and whole EFI caps pass.

The status will preserve actual SERVICE_READY base bitmap/count for later service65
(full reorder) interpretation using four low bits per word. Neither HTT3.56 nor
synthetic bitmap establishes that hardware capability. No credential read,
association/key installation/IP or physical success is claimed by this scope.
All C/ASAN/COFF/QEMU execution is restricted to isolated Yukabox paths/TMPDIR.

The NEW63 startup prefix is explicitly the first validated READY frame once
READY is seen, rather than the last credit-only frame. `ready_frame_bytes`
records that accepted raw length. Latest input diagnostic fields remain latest;
the filter decodes the retained first frame, never reserializes parsed READY.
The model drives READY first, subsequent real CE1 credit-only completion, then
INIT DMA completion and checks retained READY versus latest input length.

The query uses caller-owned static archive slots13/14/15 for response/archives.
At most13 common records may exist at begin. `query_handover.c` transactionally
validates epoch, bounds and distinct completion IDs before copying response13
first then archive14/15 toward lower/equal destinations. Both pointers are
revoked afterward. The actual response completion scalar is retained for status;
scan reuse of these slots cannot authorize any further query packet access.
The independent ASAN model covers all84 count/response/archive combinations
plus8 immutable-failure controls. This structural model is not DMA evidence.

Generated `filter_barrier.c` embeds exact frozen bytes inside a GCC diagnostic
push/ignored-misleading-indentation/pop wrapper only. Other warning classes stay
errors. The component source, wire bodies, runtime logic and frozen hashes are
unchanged; this wrapper changes compiler diagnostics, not production tokens.

QFEX0001 is2104 bytes: magic8,12 little-endian32-bit values (slot,present,
validated,completion,epoch_lo,epoch_hi,endpoint,pipe,payload_bytes,raw_bytes,event,
error), followed by actual retained raw HTC bytes padded virtually to2048.
22 slots ×5 pages, page512 except final56; ATT raw values37+2*page to255.
No normalized-byte padding is emitted over actual HTC trailers. Rejected slot17
is diagnostic only, validated0; QSCN.has_orphan reflects populated rejection.

QF630001 is448 bytes: magic8,64 scalar fields from pipeline_status.inc, then
up to32 actual SERVICE_READY words at264, actual READY MAC at392, requested
SSID length10 at398 and bytes400..409, raw Echo/VERSION slot indices432/436
(or UINT32_MAX), and partial-startup marker1 at440. Requested SSID annotation
is not a discovered SSID. SERVICE_READY word grammar is TLV four bits perword,
not32; service65 cannot be inferred from HTT3.56. No RX_RING_CFG or aggregation
is enabled in this partial diagnostic trial. QSCN is416 bytes, generation63,
13 reviewed passive channels, flags0x21. No association, keys or IP authority.
