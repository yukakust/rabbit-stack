# Native61 historical advertisement eligibility — not association authority

This new independent scope leaves native61, receiver UUIDs, drivers, HCI/timers,
`bss-security-v1` and every signed/frozen input unchanged. `copied-pin.json`
binds nine byte-identical mature parser/header/license copies to their original
repository sources. The existing source-extracted hostap2.11 RSN parser, beacon
parser, rate/RSN/PMF validation and upstream license are reused exactly.

`bridge.py` is a pure host translator over the pinned scan61 observer decoder.
It requires three identical QSCN snapshots, two identical110-page raw export
passes, exact reviewed policy/generation, released ownership, terminal state,
Root-supplied epoch/status comparison data and the accepted owned slot16 WMI
beacon strictly after START floor and before terminal completion. It preserves
`live_frequency:0` and reports the beacon's own `observed_frequency` separately.
The raw copied payload and its hash are carried without modifying UUID layout or
mistaking cached fixture data for physical provenance. Root must independently
establish actual receipt/owned-copy authority: matching supplied comparison fields
alone proves no physical observation. The translator never creates association,
controlled-port or native-rate authority.

`historical.c/h` validates the externally supplied historical context and copied
MGMT payload before using the frozen mature BSS grammar. The frozen API's internal
`live_frequency` and `native_rates` fields were designed for live callers. Here,
private parser-only operands explicitly translate observed-channel equality and
the actual known advertised rate bits into that existing grammar contract. This
is **not** an assertion of active radio frequency or hardware capability. The
public input/output keeps live0, native capabilities UNKNOWN/unproved and fresh
live revalidation mandatory. The old output's `selected_rates` is explicitly
cleared0, preventing grammar operands from leaking as native selection.

Positive output means only a historical advertisement offers the narrow
WPA2-PSK/CCMP profile with PMF optional rather than required. It retains raw
capabilities/rates/basic requirements and mature parsed RSN information. It does
not authenticate the AP, select a live association, perform a handshake, install
keys, access credentials or authorize IP. The actual native legacy mask is never
guessed. `qca_historical_native_rates` optionally compares an independently
caller-proved mask with advertised basic requirements, but that structural
comparison neither updates proof authority nor removes fresh-live revalidation.
Without such actual driver proof, native basic-rate compatibility is UNRESOLVED.

The C context's policy/epoch comparison fields are structural bindings; actual
signed generation, reviewed policy, acquired epoch, completion ownership and
checked release must be established by Root outside this pure grammar. For a
future association, obtain a fresh live BSS, revalidate channel/security/basic
rates against actual native capabilities and supply local STA key/controlled-port
proofs through the separately reviewed supplicant bridge.

## Validation

All C execution/ASAN/UBSAN/COFF happened only on Yukabox in
`/home/yuka/rabbit-world/parallel-bss61-historical-v1`. TMPDIR is the scope's
`runs/checked`; no C runs on Mac. `verify_remote.py` reproduces it.7194 synthetic
checks and five production COFF units passed: wrong generation/epoch/floor/
terminal/policy/channel; nonquiescent, active frequency or retained owner;
truncation/padding/malformed/duplicate rate and RSN data; SAE/TKIP/required-PMF
negative profiles; optional PMF; every4096 structural native-mask combination;
and immutable rejection outputs. Pure Mac Python tests cover six host bridge
cases including terminal live0, immutable export passes and Root comparison
mismatches. Every positive fixture is explicitly SYNTHETIC-NOT-PHYSICAL.

Copied profile plus adapter object-section sums are8613 bytes text,644 bytes
rdata and0 BSS. This is not a measured final EFI SizeOfImage or native admission.
No actual61 capture was consumed, no current hardware state/key/credential/BLE
session was touched, no RF/DMA/USB/native operation ran and no package was signed.
No current-world or physical Wi-Fi result is claimed by this scope.
