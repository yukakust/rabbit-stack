# Mature RSN linked host proof — synthetic only

Frozen host-only comparison of unmodified hostap 2.11 supplicant and authenticator with real OpenSSL 3.5.5, compiled and executed on Yukabox. The pinned archive SHA256 is `912ea06f74e30a8e36fbb68064d6cdff218d8d591db0fc5d75dee6c81ac7fc0a`; upstream license information is retained in HOSTAP-LICENSE-README.txt. Reference archive and byte-identical source snapshot remain at `/home/yuka/rabbit-world/parallel-security-v1/reference/`. This scope adds a synthetic integration harness; no upstream files are modified.

The final proof is `evidence/2026-10-08/report.json` (SHA256 `ab6d3fc62a2ff757c40f20088f28b160a929ae63b1c66aa12467eecbfdbd6bb2`). It binds 18 mature compilation units, 311 actual header/runtime dependency files, compiler, objects, executable and saved logs. ASAN/UBSAN passed all ten bounded scenarios:

| Mode | Actual tested exchange or rejection |
| --- | --- |
| 0 | Successful WPA2-PSK/CCMP M1–M4, matching installed PTK/GTK |
| 1 | Corrupted M3 MIC rejected by supplicant |
| 2 | Duplicate M3 answered without PTK/GTK reinstall |
| 3 | Modeled installed-key callback timeout quarantines association; replay cannot retry installation |
| 4 | Definite key-install failure keeps local data closed |
| 5 | Genuine upstream timer-driven GTK rekey, duplicate group G1 without GTK reinstall |
| 6 | Corrupted M2 MIC rejected by authenticator |
| 7 | Stale M3 replay counter rejected |
| 8 | Malformed M3 key-data length rejected |
| 9 | Wrong public fixture PMK rejected by real MIC check |

Both mature state machines and crypto are real. Key storage, EAPOL transport and confirmed/ambiguous driver results are explicitly synthetic models. RNG uses public deterministic fixture bytes through an explicit `os_get_random` linker wrapper; it cannot qualify native entropy. Timers use the unmodified upstream eloop and actual host time APIs. The executable has no user credential interface. Logs contain public counts/status only, no derived keys or fixture secret values. Cleanup erases modeled key buffers.

## Required local controlled-port boundary

Upstream sends M4 before its local `set_key` callback finishes. In modes 3/4 the authenticator can already report authorized while local key installation fails. The harness keeps local data closed unless `state == WPA_COMPLETED && sta_ptk == 1 && sta_gtk >= 1 && protection && !quarantined && !deauth`. This is a tested synthetic admission predicate, not a firmware completion proof. Native admission requires exact peer/vdev/cipher/epoch confirmation from actual HTT SEC_IND, plus independent local controlled-port enforcement; ambiguous completion requires quarantine. No remote AP deauthentication or hardware cleanup is claimed by the model.

## Remaining deployment blockers

The actual full-core freestanding COFF attempt failed on missing `stdlib.h`, recorded in COFF-attempt.log. This scope proves linked Linux interoperability, not a freestanding image. Native work still needs allocator/zeroization, bounded timer/time, reviewed entropy, actual EAPOL data-plane and synchronous confirmed-key adapters, and a reviewed crypto backend. Dynamic host imports and core ABI inventory are retained. Linux/OpenSSL objects cannot be copied directly into EFI.

The historical 2.11 security baseline is explicitly not approved: official advisory 2026-2 requires PMKSA network-context and AKMP validation; no patch or upgrade is applied here. See security-baseline-review.json. Production credentials remain inadmissible. Existing native61 has only 16 KiB mapped-image headroom; this host proof gives no native size/owner-lifetime fit. Actual association, encrypted credential provisioning, DHCP/IP and physical connectivity are not tested here.

## Reproduction

Run `verify.py` only on Yukabox with `--reference /home/yuka/rabbit-world/parallel-security-v1/reference --clang <pinned clang path from report> --output /home/yuka/rabbit-world/parallel-supplicant-linked-v1/runs/<new-name>`. The script verifies the entire extracted archive before compiling, enforces its isolated output directory and records source/dependency/log hashes. Final outputs remain in remote runs/checked-final; local evidence retains public logs and report. No Bluetooth, signing, owner-key reads or native state operations occur.
