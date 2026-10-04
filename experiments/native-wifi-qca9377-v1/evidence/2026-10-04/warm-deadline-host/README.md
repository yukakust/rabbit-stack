# Warm cooperative global deadline — host checks

Candidate payload39d66beb7a05b7919eca5f162c230ac057d95a229cf2d55eeb0db9a7317daa60.
Changes ONLY global warm bound7s ->20s, each ROM wait3s unchanged. DMA, I/O
order, IRQ window, target RAM/firmware policies and recovery stay unchanged.

Actual native fixture18 delays only WARM adapter polling to600ms intervals;
outer cold reset, allocation and cleanup retain normal polling. Old7s source
from1a14172 produces stage6/error5122 during second pipe configuration;
new20s source produces success stage5 with two CPU resets/two configurations,
14 pages freed and all resources restored. Identical fixture SHA bound in
old-7s-baseline.json; no overlapping ASPM fault selector remains in case18.
Initial attempted fixture had an obsolete fault selector and slowed outer cold
reset too; those failed setups are NOT accepted baseline evidence.

All19 actual native entrypoint scenarios, channels27/mappedIRQ36/adapter13,
warm each-I/O/cancel/20s stuck callback/overflow, sanitizer/COFF, split decoder
negatives, BLE baseline and normal/EMPTY UEFI city/ATT pass on Yukabox.
273 current source hashes, two identical rebuilds, exact world14 C/sanitizer
checks pass; Mac signing gate passed before local signature. Physical result
must be recorded separately. No binary/packet streams/key export in evidence.

Reproduction: baseline-recipe.py is the exact baseline command used, with a
Linux-only guard. Run from the copied repository root on Yukabox after
verify_init_probe generated runs/init-probe-host, preserving old checked29
sources at runs/init-profile-applied29 (or export1a14172 warm_core.c there).
It builds the same current fixture against only the old warm core, asserts
TIMEOUT5122 and records exact source/fixture hashes. It never signs/sends,
loads a key, writes target hardware or deletes gate results. Then the regular
verify_init_profile.py/remote_check.py produce the checked new20s profile.
