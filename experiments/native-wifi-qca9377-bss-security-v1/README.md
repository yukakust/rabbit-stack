# Copied BSS eligibility: legacy20 + WPA2-PSK/CCMP

Pure bounded adapter for actual owned/copied WMI MGMT_RX exports. Reuses unchanged
beacon_rx/beacon_info, and the exact hostap2.11 RSN parser bodies with TU-private
linkage, bounded input and copied output fields. No handshake/crypto/credentials,
RF, DMA/lifecycle operations, association, key installation or port authorization.
Candidate means eligibility for this narrow profile, never authenticated BSS or
network ready. An SSID/padlock never supplies security properties.

Context is externally verified current epoch/completion/start watermark, active
scan channel, reviewed frequency policy, target SSID and actual native legacy rate
mask. Digest/epoch equality checks are structural bindings, not authority proof.
The caller must supply the actual copied event provenance, not fabricated context.
The input/output and context/output cannot overlap; every rejection preserves output.

Supported/extended rates are extracted from actual IEs. Duplicate/malformed rate
IEs/values reject. Unknown basic membership selectors (including HT/VHT/HE/SAE-only)
reject legacy-only eligibility. Basic rates must fit the explicitly provided native
rate mask; actual advertised and selected native masks are kept separate. Raw ESS/
privacy/short-slot/preamble capability bits and channel are preserved, not guessed.

RSN must actually contain group, pairwise and AKM fields: no default selector may
substitute for absent advertisement. Duplicate IEs/suites, zero/oversize counts,
truncation/PMKID underflow or unexplained trailing bytes reject. Exact original RSN
and raw suite lists are retained alongside the mature parsed masks. Selection is
CCMP128 group/pairwise and PSK only. SAE-only/WPA3, enterprise-only, TKIP-only/group,
unknown ciphers and required PMF are unsupported. Real PSK+SAE transition is eligible
only when CCMP+PSK is explicitly offered and PMF is not required; PMF-capable optional
APs are accepted with selected_pmf0. No security downgrade or router change occurs.
RSNX is bounded/copied without pretending this adds SAE/RSNX negotiation support.

The core extraction is reproducible against every regular file of the pinned
wpa_supplicant2.11 release archive SHA912ea06f74e30a8e36fbb68064d6cdff218d8d591db0fc5d75dee6c81ac7fc0a.
HOSTAP-LICENSE.txt preserves copyright/license terms. This historical snapshot is
reference/parser reuse; deployment still needs the security-update/library/native
integration review required by security-plan-v1 before any credential use.

Independent oracle compiles the original upstream wpa_common.c parser, while tests
exercise complete copied MGMT frames/rate/capability/security/policy rejection under
ASAN/UBSAN and compare reused RSN results with upstream. Full16-bit PMF capabilities,
cipher/AKM combinations, transition cases, duplicate/truncated input, policy/epoch/
channel mismatch, immutable rejection and input mutation are covered. COFF required.
No physical/native admission or authenticated source authority is created here.
