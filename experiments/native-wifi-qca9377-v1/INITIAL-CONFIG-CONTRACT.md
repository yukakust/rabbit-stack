# QCA9377 initial configuration boundary

Physical native30/world14 passed the warm/reset/full-channel one-shot trial.
Target configuration writes, firmware loading and Wi-Fi connection remain pending.
See the final evidence sections for current status; early sections record the
initial native25 preparation boundary.

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
wait is bounded3s; the whole sequence is bounded20s (originally7s). Every normal poll rechecks
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

## Integrated warm/channel trial (QPD14)

A separate `init_build.py` profile links `init_probe.c` and `init_adapter.c`.
The native25 BMI profile stays intact as an earlier experiment. The new profile
performs outer PCI/wake/cold-reset/ROM checks, allocates fourteen coherent pages,
executes the pinned warm sequence and both full-channel configurations with bus
mastering off, then stops all eight engines and releases resources. It does not
upload firmware, query BMI, write target RAM tables, set EARLY_CFG_DONE or request
CORE CPU wake. Warm CPU resets are Wi-Fi-chip resets, not a Dell reboot.

`boot_irq_mapped.c` borrows the original exclusive IRQ owner and binds it to the
exact fourteen retained mappings and BAR. Its guard rereads PCI identity, D0,
MEM/BME/INTx and MSI/MSI-X capabilities plus chip/wake state. Boot polling also
remasks core MSI control after CPU reset. The original `boot_irq.c` no-DMA guard
is unchanged; mapped scope cannot restore host interrupts or enable DMA.

On warm failure/cancel, the adapter first attempts finite CE deassertion, then
quiesces boot IRQ, stops all engines and executes a bounded cold reset. Exclusive
warm ownership is cleared only after successful cold deassertion without a
sticky I/O error, fresh guarded PCI/wake identity, ROM-ready and all-eight-stop
proof. Loss of reset/PCI/ASPM/wake invariants is not automatically repaired here:
retain ownership instead. Irreducible failures enter RETAINED and prevent module
unload, unmap/free and PCI release. No automatic whole-machine reboot is allowed.

QPD14 is864bytes: existing main716 plus tail148, read via distinct diagnostic
service UUID9 and QIC1 extension184 (header4+SHA256 prefix32+tail148). Original
file service UUID1 is preserved. The reader/combiner require terminal stage5/6/7
or20 and an exact prefix hash. Hash binds reads, not device attestation.

The extra64bytes at800 are sixteen LE32 words: adapter phase/error, warm
phase/error/owned/CE-owned/CPU-reset-count/pipe-init-count, channels
phase/allocated/cleanup-cursor, verified-cold-recovery, cold phase/owned/ROM
indicator and mapped-guard error. Stage5 requires exactly two CPU resets and
pipe initializations, fourteen allocations and complete teardown/PCI/IRQ/link
restore. Stage20 means retained resources, not successful connection. Old
BMI/CE7 data regions remain zero in this profile and are rejected if populated.

`verify_init_profile.py` binds actual native entrypoint fixtures18scenarios,
channel27/mapped-IRQ36/adapter13 plus warm every-I/O/every-phase fault fixtures,
freestanding COFF, pinned upstream pack, split/decoder negatives, BLE loss
baseline/regression and actual normal/EMPTY UEFI city/ATT checks. QEMU has no
QCA9377 and tests the absent-device path only. `remote_check.py --profile init`
adds current-source two rebuilds and the unchanged live world package C checks.
`native_route.gates` requires these separate proofs and exact source/ABI hashes
before touching the owner key. Missing flags/subreports/hash bindings reject.


### Post-cold stop correction after physical26

Physical26 completed both CPU resets/channel configurations but timed out during
second ROM wait. Recovery reached cold DONE and ROM2 yet retained all resources:
its post-reset stopped-engine proof failed. Post-reset CE register values were
not captured; reset-cleared CE state is a hypothesis, not a proven physical cause.

Updated actual PCI fixtures now clear CE registers on cold deassertion. Original
code fails scenario13 (cleanup prohibited). Corrected recovery quiesces ROM boot
IRQ, performs another cooperative all-eight stop AFTER cold reset and ROM-ready,
and only then verifies guarded PCI/ROM/all-eight-stop before clearing exclusive
warm ownership and permitting cleanup. Sticky reset errors/ROM timeout/stop or
flush failure still retain mappings and prohibit unload. Added actual second
warm-ROM-timeout case17; all native entrypoint fixtures now18scenarios. Signing
requires post_cold_ce_stop and reset-cleared CE fixture proofs in both core and
entrypoint reports. This fix does not resolve or hide second ROM timeout itself.

Current physical26 remains RETAINED; the fix cannot be hot-swapped through its
blocked module unload. Only an owner-confirmed physical Dell reboot clears that
RAM ownership. Then validate fresh empty receiver and restore saved city through
an exact boot-recovery plan before further native trials. Never interpret RF loss
as reboot, silently reset counters, replay26, run native compilation on Mac, or
reuse old26 source-bound gates for changed source. Scene after26 still requires
owner observation. No automatic reboot or new signed packet during fix checks.


## Cached warm failure telemetry (QPD15)

Physical native28 confirmed warm timeout after two CPU resets and two pipe
configurations; post-cold re-stop/release now succeeds on physical Dell. The
next candidate changes observability only, preserving the reset sequence and
all PCI/DMA/IRQ ownership guards. It records cached core data at bytes864..887:
failure phase, last warm ROM indicator, elapsed microseconds within that phase,
first ROM polls, second ROM polls, last successful reset-control read (six LE32).
First failure is preserved through recovery; elapsed saturates at UINT32_MAX.
No extra MMIO read/write or DMA operation is introduced. Poll times describe
host observations; they are not device event timestamps. Success requires ROM2,
nonzero polls in both waits and no failure; faults require matching phase/error.
Poll counters bounded300 each by3s/10ms schedule. Existing QPD14 remains readable.

New diagnostic service UUID0A, main716bytes, QIC1 SHA256(prefix) +172tailbytes,
extension208bytes, joined888bytes. Decoder rejects active snapshots, malformed
length/hash/bounds and inconsistent failure/success. Actual native fixture17
forces second ROM timeout and verifies original failure phase11, zero last warm
indicator, elapsed>=3s and both poll counters survive successful cold cleanup.
This does not prove the cause of the timeout or successful Wi-Fi association.


## Cooperative wall-clock bound after physical29

QPD15 on Dell recorded second ROM failure phase11, indicator0, elapsed1175000us,
first polls4/second polls2. This is below that phase's3s deadline; global7s
TIMEOUT was reached while the per-phase budget remained. PCI guards, MMIO,
pipe configuration and gaps between native polls consume the global budget.
The new candidate changes ONLY overall warm bound7s ->20s, preserving each
ROM3s limit, I/O order, IRQ windows, DMA/BME policy and fault/cancel recovery.
Native entrypoint fixture18 uses600ms poll intervals; old7s baseline fails the
success assertion, new20s must pass with complete cleanup. Total scenarios19.
Slow/never-finishing pipe callback still times out at20s, with retained ownership
and bounded recovery; timer overflow guard uses the same20s. IRQ-window
source discrepancy is a separate later hypothesis, deliberately unchanged here.
