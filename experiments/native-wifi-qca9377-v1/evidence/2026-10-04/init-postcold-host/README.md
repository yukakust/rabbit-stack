# Post-cold stop correction — 2026-10-04

Physical native26 remains RETAINED, with second ROM timeout and uncertified
cold recovery. No new owner signature, native session, Bluetooth send, reboot or
USB/bootstrap change in this fix stage. Scene/tail after26 awaits owner observation.

Hypothesis: cold reset clears CE halt/register state, so pre-reset stop proof is
not valid afterwards. Exact post-cold physical registers were not captured.
Updated real PCI fixtures clear those registers on cold deassertion. The original
native adapter611f7ee fails actual native entrypoint scenario13 with held resources
(baseline-failure.log). The corrected adapter re-stops all eight engines AFTER
cold reset/ROM-ready, then certifies guarded ROM/PCI/all-eight-stop before
releasing warm ownership or mappings. Cold I/O ambiguity/ROM timeout/stuck stop/
flush failures continue to retain. The second warm ROM timeout is still unresolved.

Yukabox full gate PASS: ASan/UBSan/core COFF, channels27/mapped IRQ36/adapter13,
actual native entrypoints18 (including second-ROM-timeout/cleared-CE recovery),
strict QPD14 split/decoder negatives, BLE baseline/regression, actual normal and
EMPTY UEFI city/ATT, two rebuilds, unchanged live world package C/sanitizer checks.
QEMU proves absent-QCA path/city behavior only. No physical fix success claimed.
Source closure273files, payload SHA256:
b6f108f7a91e1786f31bc2db08922e100fd2667b4d360bab24c6d4867da891de.

Mac native_route gate validates exact reports/current-world/source/ABI, and
rejects missing post_cold_ce_stop before owner key access. No signed packet yet.
Current counter26/world13/package unchanged; all pending slots remain empty.
An owner-confirmed physical reboot is needed to clear retained native26 ownership;
then fresh-empty-receiver proof and an exact city recovery plan are required.
Do not replay26 or reuse its source-bound gates after the correction.
