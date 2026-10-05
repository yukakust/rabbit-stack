# Bounded CE receive diagnostics, native44 candidate

Derived from unchanged native43. Same strict receive checks and all-owner teardown.
Read-only QWOP0002 status adds pre-consumption ring indices, descriptor bytes and
at most64 DMA data bytes. These are control/boot bytes only: no credentials,
keys, scan, association, WMI INIT or IP are transmitted. No guard is relaxed.

Not physically installed or admitted until deterministic and reproduction gates pass.
Physical native43 baseline: HTC READY, first CE1 receive rejected (error4),
zero outstanding DMA owners after teardown. Exact reason remains unproven.
