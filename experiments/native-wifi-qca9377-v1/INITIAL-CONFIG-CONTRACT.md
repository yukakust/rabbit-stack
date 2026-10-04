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
