# Mature RSN core: bounded native-port feasibility slice

This branch uses the already inspected official hostap 2.11 archive, SHA256
`912ea06f74e30a8e36fbb68064d6cdff218d8d591db0fc5d75dee6c81ac7fc0a`.
It tests synthetic temporal-key bytes only; no actual password, PMK, owner key,
BLE packet, driver state or device access. No installed Dell code changed.
Hostap 2.11 is a pinned research reference, not a claim of a currently
security-approved deployment baseline; upstream fixes must be reviewed before
deployment. See preserved upstream `HOSTAP-LICENSE-README.txt` and source notices.

## Actual completed work

* Unedited `src/rsn_supp/wpa.c` compiled on Yukabox with the actual upstream
  headers, `CONFIG_NO_STDOUT_DEBUG`, `CONFIG_NO_WPA_MSG`, `CONFIG_NO_TKIP`,
  optimization and per-function/data sections. The resulting host ELF object
  has 29624 text bytes and 47 direct unresolved symbols. This is not a linked
  core, freestanding COFF port or final deployment size.
* The verifier extracts the exact unedited bytes of
  `wpa_supplicant_install_ptk` and `wpa_sm_get_auth_addr` from pinned `wpa.c`.
  The small test compiles those functions with actual upstream `wpa_sm`,
  `wpa_sm_ctx`, key/algorithm types and upstream cipher helpers from
  `wpa_common.c`. Its rekey-timer stubs abort if reached; timers are disabled
  in these fixtures. No substitute handshake or install algorithm is used.
* 1038 ASAN/UBSAN cases pass: confirmed initial success and TK erasure;
  1000 repeated calls which make no additional driver install;
  definite simulated driver failure preserves uninstalled state/TK;
  subsequent definite success; every TK length 0..32; no-cipher and invalid
  cipher branches. The callback validates actual CCMP algorithm, key length,
  address, zero receive sequence, key flags and synthetic key bytes.
  This directly tests the mature no-PTK-reinstall boundary, **not** an M3
  packet replay, complete four-way/group handshake, RX packet-number behavior,
  actual firmware key installation or native radio lifecycle.

Every regular reference file is compared with the hash-pinned archive before
compilation; reports bind test/verifier source and exact upstream excerpts.
Public report/log live under `evidence/2026-10-06`. Binaries and extracted
upstream source remain in ignored remote runs. All native compilation happened
only in `/home/yuka/rabbit-world/parallel-supplicant-v1` on Yukabox.

## Concrete direct dependency inventory

The report records all 47 symbols from `nm -u wpa.o`. They fall into:

| Boundary | Actual direct examples | Native responsibility |
|---|---|---|
| Allocation/libc | malloc/free, memcpy/memset/bcmp, os_zalloc/os_memdup, snprintf | Bounded allocator and freestanding libc shim; not host glibc |
| Secret lifetime | bin_clear_free, forced_memzero, os_memcmp_const | Reuse mature non-optimizable erase/constant-time helpers |
| Timers | eloop_register_timeout, eloop_cancel_timeout | Monotonic polling scheduler with cancellation/lifetime guarantees |
| RNG | random_get_bytes | Proven strong platform entropy; propagate failures |
| Crypto | aes_unwrap, rc4_skip, wpa_eapol_key_mic, wpa_pmk_to_ptk | Mature implementations, known-answer tests and strict allowed-profile checks |
| RSN parsing/generation | wpa_parse_wpa_ie_rsn, wpa_parse_kde_ies, wpa_compare_rsn_ie, wpa_gen_wpa_ie, wpa_gen_rsnxe | Actual upstream common/wpa_ie modules with matching profile |
| Capability/cipher mapping | wpa_cipher_*, wpa_mic_len, wpa_use_* | Retain checked upstream dispatch; no accidental unsupported negotiation |
| PMKSA cache | pmksa_cache_init/deinit/add/get/flush/list/reconfig/etc. | Compile actual cache with bounded storage/timers, or explicitly reviewed removal; no success stubs |

These are direct dependencies only, not a complete transitive port manifest.
`CONFIG_NO_TKIP` still leaves a direct `rc4_skip` symbol in this compiled core;
simply setting that macro does not prove removal of every legacy algorithm.
The full `wpa_common.c` object also refers to mature HMAC-SHA1/SHA256, MD5,
AES-CMAC and PRF implementations, beyond the cipher helpers retained by the
small test's linker garbage collection. A deployment build must resolve real
dependencies and prove unsupported profiles cannot execute legacy paths;
do not fill crypto/cache/RNG dependencies with dummy success functions.

## Required adapter and the discovered synchronous-key constraint

`struct wpa_sm_ctx` supplies set/get state, deauthenticate/reconnect,
`ether_send`, bounded EAPOL allocation, selected-BSSID/RSN lookup,
auth-timeout cancellation, config/network context and `set_key`.
The higher-layer driver/controlled-port state must implement authorization;
`wpa_sm_ctx` itself has no `set_supp_port` member. Its optional `store_ptk`
callback may remain absent when no caching is requested; it must never log
key material. Do not confuse optional callbacks with required lifecycle work.

Most importantly, upstream **expects synchronous `set_key`**:

1. It calls the adapter with the TK/algorithm/flags.
2. On callback success it erases TK and sets `ptk.installed` and `tk_set`.
3. Further calls observe the installed guard and avoid reinstallation.

Thus returning 0 when a WMI descriptor is merely queued is incorrect.
The adapter must return 0 only after a genuine firmware key-install completion,
with bounded timeout and correct current association/vdev/session. One minimal
approach is bounded backend polling during this callback: the radio owner
continues servicing required CE/HTT completions, copies arriving EAPOL into a
bounded deferred queue, and prevents reentrant entry into the supplicant until
the callback returns. It must not recursively run supplicant timers/callbacks,
free borrowed DMA input, or publish unrelated native/world changes. Return
failure on definite rejection and propagate the resulting disconnect/error.
An asynchronous adaptation is also possible but requires explicit upstream
state-machine changes and separate ordering tests; it cannot be faked by a
success return followed by a later error.

The failure/retry fixture models **definite not-installed failure**. A firmware
timeout after ambiguous publication may have installed the key; preserve actual
owners, quarantine the association and prove teardown/definite state before
retrying. Blind retry could reset encryption packet numbers. The fixture is not
permission to retry uncertain hardware key installation.

## Next bounded tasks before deployment

1. Resolve/compile mature core + common/wpa_ie + PMKSA + real crypto + native
   platform adapter under a pinned freestanding configuration; measure final
   image/RAM budget and current upstream fix coverage.
2. Exercise synthetic M1..M4/group exchange with a mature authenticator and
   genuine crypto: MIC, replay, altered RSN, duplicate M3, rekey, failures,
   timeouts and controlled-port authorization. Current 1038 cases do not do this.
3. Join the persistent-radio/STA/HTT branch: exact real RX decapsulation,
   association notifications, synchronous confirmed key adapter and bounded
   queue/lifetime behavior. No connection until these exist.
4. Join physically authenticated encrypted credential provisioning from the
   security-plan branch. Real secrets remain exclusively on Mac until that
   path is implemented and verified; synthetic tests can proceed independently.

Reproduce on Yukabox:

```text
python3 verify.py --clang <reviewed-clang> --reference <pinned-reference-directory> --output <ignored-output-directory>
```

Primary source: [official hostap release](https://w1.fi/releases/wpa_supplicant-2.11.tar.gz),
particularly `src/rsn_supp/wpa.c:wpa_supplicant_install_ptk`, `wpa.h:wpa_sm_ctx`,
`wpa_i.h:wpa_sm_set_key`, `src/common/wpa_common.c` cipher helpers.
For native firmware completion semantics see pinned
[ath10k ath10k_install_key](https://github.com/torvalds/linux/blob/6b5a2b7d9bc156e505f09e698d85d6a1547c1206/drivers/net/wireless/ath/ath10k/mac.c).
