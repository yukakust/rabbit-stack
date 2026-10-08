# Required real inputs and ownership

1. Actual taken beacon/current BSS selection supplies peer/READY MAC, SSID,
   interval/TIM DTIM, channel and AP basic rates. Unknown/missing TIM/native rates
   do not become a guessed DTIM1 or rate mask. Caller binds real policy and
   implementation source closures; regulatory power units are exact upstream
   half-dBm fields and antenna whole-dBm, not an inferred RSSI setting.
2. Firmware-selected legacy mode/rates must be genuinely implemented and match
   actual band. MODE11B cannot encode OFDM; MODE11GONLY cannot encode CCK. A
   successful byte/model proof is no native TX capability declaration.
3. Actual START response (requestor0/type/status) and HTT PEER_MAP must precede
   management startup. These runtime call sites/service fields are still not
   integrated here. Actual selected AP response supplies AID/caps/rates before
   WMI PEER_ASSOC and UP; source-bound parser state is required by caller.
4. ONE actual backend owns the immutable frame/page/descriptor and nonreused
   MSDU-id. Coordinator receives verified publication, DMA closure and owned HTT
   or WMI completion evidence with exact cookie/epoch/floor. Response may arrive
   before DMA; caller holds raw/metadata until both owners and status close.
5. Failures retain the owner facts until real backend stop/drain/all-map cleanup.
   No timeout returns a page to the pool, ACKs a frame or installs a key. Caller
   does not retry ambiguous auth/assoc under this one-attempt contract.
6. Single key publication requires fresh SEC_IND correlation and no reinstall
   guard. Pairwise/group flags are exact WMI0/1, cipher TLV4; HTT SEC_IND cipher6
   remains a different namespace. Nonzero GTK RSC needs genuine per-key/group/
   TID host replay ledger from owned descriptor/MPDU, which is a NEXT component.
   Key acknowledgement does not prove replay validation; no firmware PN flag
   may be invented. Initial RSC must survive in caller's ledger.
7. Current protected/encrypted RX in htt-data-path-v1 is explicitly quarantined
   until that key/PN authority exists. No controlled port, protected IP, DHCP,
   association or actual credential provisioning is claimed here.

Concrete remaining gaps: admitted native legacy-rate/regulatory/TX source,
actual START/peer management runtime bindings, management backend primary proof,
owned encrypted RX/key/initial-RSC replay path, real key/EAPOL/protected port and
secure credential delivery. No physical admission or counter reservation.
