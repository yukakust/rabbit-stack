# Filter deadline origin and physical63 order review

Pinned primary source is Linux ath10k commit
6b5a2b7d9bc156e505f09e698d85d6a1547c1206. `references.json` binds the three
public upstream files. This is a read-only review, not a producer64 implementation.

## What physical63 proves

The full firmware upload and boot succeeded. Filter posted three commands and
observed two DMA completions. Its last-command `tx_completed` boolean is zero.
The checked-release capture retains a credit-only record7 and exact ECHO record8
on pipe2 after publish floor6, with argument0x63000001. It proves firmware replied
and the sole RX owner copied the reply. It does not prove the third DMA completed,
or when ECHO arrived relative to a deadline. All fourteen owners were released.
No HTT VERSION or scan began. Current completed firmware session is not replayed,
cleared or resigned by this scope.

## Primary source versus our origin

`core.c:2840..2867` submits dummy STA CREATE/DELETE, then invokes WMI barrier.
`wmi.c:26` defines the barrier wait as3*HZ. `wmi.c:9110..9120` reinitializes the
completion, successfully submits ECHO, then begins the three-second completion
wait. It is not a three-second limit starting before CREATE. Independently,
`wmi.c:1944..1959` bounds each WMI command's credit/send retry wait by3*HZ.
These Linux timings are a design reference; no Linux is installed on Dell.

Frozen filter v1 begins one3,000,000us deadline before CREATE and checks it in
every API. Native63's qca_hardware_poll first pumps the combined persistent RX.
Its filter pipeline then calls qca_filter_poll before polling CE3 completion or
taking queued RX. Thus at an expired overall clock, copied ECHO and pending DMA
are intentionally not processed. This is consistent with the physical snapshot;
physical arrival timestamps are missing, so it is not proof ECHO was timely.
The separate TX owner also checks its2,000,000us request deadline before reading
CE3 DMA completion. That guard must not be silently bypassed.

## Minimal next-component proposal

Create a NEW derived component only after Root review. Keep wire serializers,
READY/MAC, epoch, monotonic clock, credit serial/outstanding, immediate-POSTED
observation, exact request/byte counts, completion floor, argument, duplicate
ECHO rejection, immutable credit ledger and final real DMA proof unchanged.

Use a3s command-stage deadline for CREATE, DELETE and ECHO submission phases,
with a new stage beginning only after validated prior-command DMA completion.
Arm a separate3s ECHO-reply deadline only on the actual ECHO POSTED observation.
Set an independent12s overall cap at begin (3 command budgets plus3s reply),
with checked addition/overflow and no sliding resets from unrelated RX/credits.
This is a conservative component policy inspired by upstream separate waits,
not a measured Dell firmware latency or a promise it will solve every timeout.
Keep the existing sole TX owner's2s request timeout and all DMA/refund guards;
it can still abort sooner. A new component cannot manufacture DMA completion.

Every receive/completion admission must have observed_now strictly below its
applicable deadlines and overall cap. At or beyond a deadline, retain diagnostic
raw without granting success. Do not drain queued records first to resurrect an
expired proof. Poll ordering alone cannot supply the missing arrival timestamp.
Before a valid timeout decision, the existing nonexpired owner pump/CE3 poll and
bounded owned RX consumption must run at coherent sampled monotonic times;
immediate POSTED must still be reported before any extra RX pump/refund.

Recommended bounded diagnostics are begin/stage/post/ECHO/DMA observation times,
last poll gap and effective deadline. These are host observation timestamps,
not hardware arrival timestamps. Their ABI/storage/whole EFI cap must be measured
in a new producer before signing; final63 already maps the full4MiB cap.

## Required actual-C integration models for the next producer

1. Slow coherent polls: CREATE/DELETE consume more than3s in aggregate, each
   within its own stage/request budget; posted ECHO then exact owned reply and
   actual DMA3 arrive within their respective budgets. New proof may pass.
2. Same schedule with missing DMA3: exact ECHO alone never passes; real TX timeout
   still faults and retains owners/raw. Refund is not DMA completion.
3. Exact ECHO before DMA3 and DMA3 before ECHO both require both observations.
4. At-deadline and one-us-late ECHO/DMA always fail; no accepting old queued frames.
5. Clock regression, epoch mismatch, wrong/stale/duplicate ECHO, forged byte counts,
   missing credits and fast-refund-before-POSTED all retain existing fail-closed
   behavior. Unrelated credits/unknown events never extend any budget.
6. Overall12s cap wins even if stages appear individually progressing; bounded
   archives and full fourteen-owner release remain required on every failure.

`timing_test.c` compiles the exact frozen filter/credit/wire sources on Yukabox.
It reuses captured physical ECHO bytes with explicitly invented synthetic timing:
expired-global poll rejects before consume; in-budget ECHO plus modeled DMA3
passes; ECHO before expired/unproven DMA does not pass. It changes no production
state/deadline and does not implement or validate the proposed component64.
