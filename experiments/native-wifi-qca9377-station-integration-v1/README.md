# Station/supplicant integration preparation

New software-only scope. Frozen supplicant-native-v2, native64, BSS selector,
signed packets, state and hardware remain untouched. No credentials, owner keys,
BLE controller, generation reservation or native deployment.

`station.c/h` implement bounded CPU parsers and one-association joins:

* Actual owned `QcaRxEvent` is re-decoded with the unchanged HTC codec. HTT pipe1
  event is zero; WMI pipe2 event equals the actual normalized payload word.
* HTT TLV PEER_MAP is12 bytes; PEER_UNMAP4; SEC_IND28. Packed upstream structs
  independently generate model wire bytes and prove offsets/lengths. Reserved
  fields remain raw in caller input; unknown envelopes are not converted into
  authority. Production bound API additionally checks actual parsed major3 /
  minor56, firmware IE6 op3 binding and negotiated endpoint/message limit.
* MGMT_RX uses actual tag44/40-byte header + tag17 owned frame and zero padding,
  status0 and current live 2.4GHz frequency. Only ordinary addressed management
  frames from selected BSSID to READY MAC are eligible; fragments/protected/
  ordered/DS variants are unsupported. Open-auth algorithm0/transaction2 status
  and association response status/AID/rates are parsed from actual AP bytes.
  Successful AID requires reserved high bits and1..2007. Association rates/basic
  rates must fit the separately reviewed native legacy-rate implementation.
* Peer mapping joins vdev/BSSID/id/current completion and rejects peer ids≥2048
  using the pinned ath10k RX-descriptor limit; out-of-range raw metadata is
  retained as diagnostics rather than indexed into an invented peer table. Authentication and actual
  association response establish state; WMI PEER_ASSOC publication never does.
* One serialized pending PTK or GTK request must already have been committed by
  the real caller. SEC_IND must be newer than that request's actual RX floor,
  match peer-id, CCMP security type6 and unicast/group. The pending caller index
  supplies index0 for PTK /1..3 for GTK. SEC_IND itself has NO key index, nonce,
  command cookie or key-byte confirmation. Its cookie is solely local diagnostic
  identity. Wrong pending indication, ambiguity, disconnect/unmap or attempted
  reuse closes/quarantines this join. Key material never enters this component.
* Mature `set_state(WPA_COMPLETED)` and `mlme_setprotection` callbacks are separate
  inputs. Intermediate RX protection is retained accurately; only final RX_TX
  plus association, peer, confirmed PTK+GTK, current epoch and no pending/fault
  grants **software eligibility**. AP authorized is independent. Disconnect
  after keys revokes state permanently; an old completion cannot reopen it.

`verify.py` runs the actual C parser/coordinator against exact primary packed
definitions under ASAN/UBSAN, exhaustive peer ids, raw mutation/length tests and
COFF. `verify_interop.py` separately links the real official-PMKSA-patched hostap
2.11 core + actual internal crypto + upstream hosted eloop with new callback
joins. Its public synthetic fixture models native publication/SEC_IND; actual
radio acceptance and firmware keys are not simulated as physical proof. Modes
0/2 complete handshake and duplicate-M3 no reinstall; modes1/9 reject MIC/PSK
faults; modes3/4 keep local eligibility closed after ambiguous/failed installs,
even while the synthetic AP authorized bit is1. No values of fixture key
material are logged. Hosted libc/time/eloop and deterministic fixture entropy
are still present. Native freestanding supplicant linking remains incomplete.

Primary reference is Linux commit `6b5a2b7d9bc156e505f09e698d85d6a1547c1206`
[ath10k](https://github.com/torvalds/linux/tree/6b5a2b7d9bc156e505f09e698d85d6a1547c1206/drivers/net/wireless/ath/ath10k)
and its [802.11 definitions](https://github.com/torvalds/linux/blob/6b5a2b7d9bc156e505f09e698d85d6a1547c1206/include/linux/ieee80211.h).
This exact historical source is an interface oracle, not a current deployment
security endorsement. Upstream notices remain in copied references.

`sta_local_eligibility_live` also inspects actual persistent ACTIVE owners,
READY MAC/session endpoints/RX epoch before exposing software eligibility;
closed/replaced/faulted owners reject without mutating them. This still does not
implement a firmware controlled-port operation.

Native capability remains UNKNOWN: parsing metadata or passing synthetic
handshakes does not implement or authorize native legacy rates, RF TX, firmware
key installation or the protected dataplane. See INTEGRATION-CONTRACT.md.
