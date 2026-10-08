# Filter64 component

This new derived component changes timing policy only; frozen filter-barrier-v1
bytes are not edited. Body serializers and exact ECHO validation remain the
same. New timing policy: command-stage3s, ECHO3s from actual POSTED, overall12s.
The caller's existing TX2s timeout and actual DMA/credit/epoch proofs are retained.

`deadline` is the effective minimum of stage/reply and overall cap. A stage reset
requires the preceding actual DMA completion; unrelated credits do not extend
it. ECHO publication records its real sampled time before another RX/refund
pump. All arithmetic is checked/capped without wrap. At-deadline input faults;
there is no retrospective approval of queued packets. Terminal diagnostics
remain stable. Exact ECHO and actual final DMA are both required for success.

The clock ledger records observed start, stage, post, DMA, ECHO and timeout times
and maximum filter poll gap. A last-DMA timestamp must be interpreted with the
current-command DMA boolean; it may otherwise refer to an earlier command.
These are not hardware-arrival timestamps and do not explain physical63 latency.

Yukabox-only ASAN/UBSAN regression140125 plus timing11 checks and5 COFF objects
passed. Evidence/2026-10-09/report.json binds code, test, dependencies, object and
log hashes. The producer copies these exact C/header bytes; its compiler adds
only a scoped diagnostic wrapper for inherited GCC indentation warnings.
No memory allocation, register access, credit writes, physical radio operation,
credentials or signing is implemented by this component.
