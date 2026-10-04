# QCA9377 initial configuration boundary

This is preparation for the next native trial, not a Wi-Fi connection or a
physical initialization write. Dell remains on applied native25/world13.

## Checked data

`init_tables.py` encodes seven little-endian target pipe records (168 bytes)
and seventeen service records including the terminator (204 bytes). An
independent parser in `verify_init_pack.py` reconstructs both blobs from the
pinned Linux sources and checks every byte. The QCA6174/QCA9377 override changes
target CE5 to OUT/2048 and redirects HTT downlink to CE1. Host CE5 is disabled
by that same upstream override; CE6 is target-autonomous. Neither gets an
invented host queue. CE7 is the host diagnostic channel and is absent from the
seven target pipe records.

Before writes, active host channels must be CE0 TX, CE1 RX, CE2 RX, CE3 TX,
CE4 TX, and CE7 TX/RX. Rabbit's host ring limit remains32: target-side entry
counts are different allocations, not a reason to enlarge host rings. Every
active direction needs mapped, owned descriptors and a transfer buffer. RX
channels need bounded posted receive capacity. This inventory checker currently
accepts only synthetic host fixtures; it has **no native write authorization
path**. The live adapter must derive its inventory from actual owned rings and
mapped buffers, not accept user JSON as DMA proof. Current native25 owns only
CE0/CE1/CE7 and cannot pass the full channel boundary.

`init_preflight.py` separately revalidates exact current applied receipt,
physical QPD13, cleanup, bounded/aligned/nonoverlapping destinations and flags.
Its saved span result alone does not authorize table writes. Destinations must
be read and checked again within the same new probe after reset, never reused
from a previous device state without validation.

## Required reset order

The verifier also checks pinned source call order for QCA6174/QCA9377:

1. Cold reset, then wait for ROM initialization.
2. Isolate IRQs. SI0 set/read,10ms,clear/read,10ms (chip SI0 mask0).
3. Clear FW indicator3a028; assert CPU warm-reset mask40 at RTC reset800.
   Initialize pipes, wait for target initialization.
4. Clear LF timer enable mask4 at850. Assert CE reset mask1 at800, wait10ms,
   deassert; reset CPU again, initialize pipes, wait for target initialization.

Addresses here are BAR offsets;800 is not the cold-reset offset80008.
Never reset CE while the target CPU is still operating on it. The future native
state machine must make delays cooperative, fail closed on failed waits/reads,
revalidate PCI identity and ownership, retain ambiguous reset/DMA ownership on
errors and provide observable bounded cleanup. Checking upstream order does not
prove that our native implementation executes it; that implementation is pending.

Only after correct reset and live host-resource checks: finite CE7 writes and
readback of the two tables; clear PCIe L1 config bit1; set early allocation
magic6d8a/banks9. Read back all data before setting EARLY_CFG_DONE10 as the last
marker, then wake target CPU with CORE_CTRL mask2000 and query BMI version.
No firmware upload is authorized by a successful memory transfer or table check.

## Reproduction and evidence

Run on Yukabox with pinned vendor sources:

```sh
python3 verify_init_pack.py --pack init-target.json --vendor /path/to/pinned/ath10k --output report.json
```

The source verifier rejects optimized Python so assertions cannot be disabled.
Evidence `evidence/2026-10-04/init-tables-host` contains byte identities, source
hashes,42 negative resource cases, upstream reset order and a fresh host span
check against physical25 data. These are host checks, not QEMU or new physical
execution. No payload was signed or transmitted in this stage. Next candidate
must include these new files in its reproducible source snapshot and native
gates before signing; old native25 gates do not cover them.

## Cooperative components implemented and checked on Yukabox

`warm_core.c/h` implements the pinned two-CPU-reset sequence as bounded polling
steps. The pipe callback is cooperative (-1 fault,0 waiting,1 complete), allowing
the adapter to halt and configure all engines without a blocking loop. Each ROM
wait is bounded3s; the whole sequence is bounded7s. Every normal poll rechecks
the adapter guard. A failed read/write, invalid clock, failed guard or cancelled
operation keeps exclusive ownership. CE reset ownership is marked before its
possibly ambiguous assertion and is removed only after10ms and verified clear.
`qca_warm_recover_ce` only deasserts an already owned CE reset; it never reasserts,
continues initialization or releases the device. Caller must bound those retries.

`channels_core.c/h` prepares14 mapped pages (57344bytes): descriptors and data
for seven directions across six active host channels. Allocation is one page per
poll. Every mapping is checked and registered; duplicate DMA pages are rejected,
and aliased host allocations retain uncertain ownership to avoid double free.
The live preparedness check validates actual owned buffer/ring objects, page
bounds, registration, current PCI command, hardware CE bases/sizes and disabled
host CE5/6. It is not a standalone target-write authorization API. CE1/CE2 get
one bounded2048byte receive buffer after explicit bus start. CE7 RX belongs to
each diagnostic exchange and is not pre-posted. Reconfiguration reuses retained
mappings only after all-eight halt/zero/BM-off; cleanup closes at most one buffer
per poll using existing Flush/Unmap/Free guards. Faults retain the cleanup cursor.

`verify_init_core.py` passes ASan/UBSan plus freestanding x86-64 COFF compilation
on Yukabox. Warm tests inject failure at every read/write, cancel and fail guards
at every phase, cover both ROM/pipe failures, clock reversal, overflow, delayed
pipe initialization and CE-deassert recovery.27 channel scenarios cover partial
map failures, ambiguous bus enable, stuck CE7, flush/unmap/free failures,
publication failure, duplicate mappings, malformed live resources and a joint
warm/full-channel fixture. That joint fixture proves two pipe initializations
reuse the same14 pages with no bus-master enable, unmap or free during warm reset.
Source and transitive ABI hashes are checked before/after compilation and tests.
Evidence is `evidence/2026-10-04/init-core-host`; no physical hardware was exercised.

```sh
python3 verify_init_core.py
```

These components are **not linked into bmi_probe.c/bmi_build.py yet**. A new
physical packet is not ready. Required integration work:

1. Add a native adapter that proves fresh PCI/D0/wake and IRQ isolation on each
   warm step and connects cooperative pipe configuration to retained mappings.
   Current boot_irq.c deliberately rejects polls while dma_users is nonzero.
   Do not remove that guard: add a separately verified scoped boot-IRQ path for
   retained mapped channels with bus-master off and actual ownership checks.
2. Integrate cancellation and bounded verified cold recovery. After a warm fault,
   exclusive ownership remains held even if CE deassert succeeds; it must not be
   cleared by assigning a flag. Stop all engines and prove safe reset/ROM state
   before releasing mappings/PCI or allowing module unload. Irreducible allocation
   ambiguity still requires retaining ownership, as in the existing DMA contract.
3. Add latched physical telemetry, decoder and hash-bound split transport for
   warm/resource/recovery results. Run integrated fault scenarios and actual
   normal/EMPTY UEFI city/ATT gates plus exact two builds/current-world checks.
4. Only then sign a fresh candidate>=26 and deliver its saved session, obtain
   exact APPLIED receipt and physical diagnostics, and ask for scene observation.

Finite target RAM writes/readback, EARLY_CFG_DONE/CPUwake and firmware gates are
still later boundaries. No native packet, USB/bootstrap change or reboot was
performed during these component checks.
