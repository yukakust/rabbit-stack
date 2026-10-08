# Concrete adapter gaps and ordering

The current native scan/filter/VERSION path cannot yet call this a connected
station. Functions below are missing adapters, not fake success implementations.

| Required adapter | Actual source/input/result | Present preparation / precise gap |
|---|---|---|
| Native legacy-rate/cipher capability | Reviewed QCA9377 TX descriptor, key implementation and READY/service/resource profile | BSS selector requires source closure. Allocation pool and SEC_IND parser prove no TX/key capability; keep UNKNOWN. |
| VDEV start/peer lifecycle | Selected fresh BSS; actual WMI START response and HTT PEER_MAP | Existing PEER_CREATE bytes + new owned PEER_MAP parser; runtime START publication/response/order and peer deletion remain missing. |
| Management TX path | Actual MGMT_TX_WMI firmware service vs HTT3 TX_FRM policy; retained DMA descriptor + real completion | No native auth/assoc management serializer/publication or RF admission here. AP response CPU parser is implemented; TX/timeout/coordinator is missing. |
| Air auth/association | Actual selected BSSID/READY MAC/live channel; own posted request floor; response status/AID/basic rates | `sta_decode_mgmt`/`sta_observe` prepared. Actual request/post floor must come from reviewed TX owner. Model association inputs are explicitly synthetic. |
| WMI PEER_ASSOC / VDEV_UP | Actual AP AID/rates/caps; not an invented associated bit | Runtime configuration/response and legacy20 capability selection remain missing. PEER_ASSOC is firmware configuration, not air association. |
| EAPOL RX/TX | HTT ring owned descriptor/frame, exact decapsulation/address/EtherType0x888e; negotiated TX mode | Mature core's actual ether_send/RX calls are demonstrated only in hosted fixture. Native ring integration, TX serialization/completion/backpressure and bounded CPU frame lifetime remain missing. |
| Native `set_key` | Hostap CCMP16-byte key callback → actual WMI AES_CCM serializer/publication → fresh matching HTT SEC_IND | Only nonsecret request metadata/confirmation join is implemented. Real key bytes/provider, key serializer, synchronous bounded wait and native callbacks are missing. Never treat WMI TX DMA or debug-only INSTALL_KEY_COMPLETE as SEC_IND. |
| OS/entropy/eloop bridge | Actual reviewed bounded allocator, memory/string, monotonic clock, event/timer loop and approved RNG | Mature24 COFF units remain unlinked; partial native services elsewhere require individual integration proofs. No hosted clock or deterministic fixture RNG may become production fallback. |
| Controlled port | Actual mature COMPLETED + RX_TX callbacks, PTK+GTK SEC_IND, active same station/radio epoch and actual protected TX/RX | New software join and `sta_local_eligibility_live` inspect actual persistent owners/READY/RX epoch; fresh observation call site and encrypted native dataplane remain missing. `sta_local_eligibility` does not open hardware/firmware controlled port. |

Actual callers must use validated frozen62 HTT binding/version proof (IE6 op3,
major3/minor56); the raw decoder alone grants no version/epoch authority.
Each station object represents ONE association attempt bound to selected fresh
BSS and current acquired radio epoch; initialization takes actual request RX
floor. No object reset may erase attempted-key history while prior owners/keys
remain. Current module allows only first PTK and first GTK; rekey, key deletion,
reassociation, PMF, HT/VHT and cache/offload require new reviewed contracts.

While `set_key` waits synchronously, poll only the actual retained HTT/WMI owner,
archive/defer EAPOL and other events, and never reenter mature supplicant core.
Use the actual upstream bounded key wait (3seconds after send); any ambiguous
publication/timeout calls `sta_key_ambiguous`, never retries key installation or
resets packet numbers. SEC_IND does not cryptographically confirm key bytes or
carry a key index. Sole pending serialization + current peer/cast/cipher/floor
are the strongest source-supported confirmation available in this profile.

Immediately revoke eligibility on actual owner stop/fault/epoch change,
disconnect, peer-unmap, unsupported/ambiguous key events or mature core
disconnect. The hardware owner remains responsible for checked all-map cleanup;
this component neither unmaps nor releases anything. Prior physical scan evidence
does not grant RF association permission or encrypted credential provisioning.

Successful software proofs are not native admission, physical auth/association,
key-install proof, controlled-port-open proof, DHCP or WAN connectivity.
