# STA association: checked boundaries and first reusable wire block

This is host-only work, building on security-plan-v1 and supplicant-port-v1.
No radio access, candidate, credentials, signing, association or IP claim.
All reference files are hash-pinned to Linux commit
`6b5a2b7d9bc156e505f09e698d85d6a1547c1206`; references.json records exact
bytes, with upstream notices preserved in ignored runs/reference. No old source
or evidence was edited. This historical source is an architecture reference,
not a current security deployment endorsement.

## Concrete source findings

| Boundary | Pinned source and actual proof | Native requirement |
|---|---|---|
| HTT service | htt.c:ath10k_htt_connect, htc.h:ATH10K_HTC_SVC_ID_HTT_DATA_MSG | Separate HTC service 0x0300, actual CONNECT_SERVICE response endpoint; never reuse WMI endpoint by assumption |
| Protocol | htt.c:ath10k_htt_setup/ath10k_htt_verify_version, htt.h:htt_ver_resp | VERSION_REQ then actual VERSION_CONF, major 2 or 3 in this implementation; firmware HTT op-version selects T2H mapping independently of target major |
| Buffers | htt.c:ath10k_htt_setup, htt_tx.c/htt_rx.c | Version validation precedes fragment-bank/RX-ring config and aggregation config; real DMA owners, descriptors, fill/refill and drain are required |
| Peer creation | mac.c:ath10k_peer_create, txrx.c:ath10k_wait_for_peer_created/ath10k_peer_map_event | WMI PEER_CREATE publication followed by actual HTT PEER_MAP establishing vdev/BSSID/peer-id; CE3 DMA completion does not prove peer exists |
| Start | wmi-tlv.c:gen_vdev_start, wmi.c:event_vdev_start_resp | Validated actual selected BSS channel/SSID/beacon interval/DTIM; matching WMI VDEV_START response vdev/request/type/status, current epoch/watermark |
| Air association | mac.c:ath10k_bss_assoc | This callback already has mac80211 association state and AP-assigned AID. WMI PEER_ASSOC is firmware peer configuration, not an 802.11 authentication/association exchange |
| Up | mac.c:ath10k_bss_assoc, wmi-tlv.c:gen_vdev_up | PEER_ASSOC/rates/caps from actual AP association, then VDEV_UP with real AID/BSSID. Publication success is not AP acceptance or controlled-port authorization |
| Management TX | mac.c:ath10k_mac_tx_h_get_txpath, htt.h | Firmware feature/service MGMT_TX_WMI selects WMI mgmt path; otherwise HTT major >=3 uses TX_FRM, older uses HTT MGMT_TX. No universal guessed descriptor |
| EAPOL/IP | mac.c TX path, htt_tx.c/htt_rx.c, security-plan-v1/eapol_frame | Data travels HTT, using negotiated raw/native-WiFi/Ethernet mode and hardware RX descriptor/decapsulation; bounded EAPOL EtherType 0x888e delivery to mature RSN core |
| Key completion | mac.c:ath10k_install_key, htt_rx.c HTT_T2H_MSG_TYPE_SEC_IND | Actual HTT SEC_IND processing completes install_key_done. Validate current peer-id, cipher/type, unicast/group, epoch and sole pending install. WMI VDEV_INSTALL_KEY_COMPLETE handler in wmi.c is only debug logging |

The PEER_ASSOC_CONF enum and service bit exist, but the pinned TLV receive
switch has no handling case, and this STA association path does not wait for
that event. Do not invent a mandatory ACK from its name. If later firmware
requires/supports it, implement a separately proven service-specific contract.
Likewise SEC_IND has no invented command nonce: serialize key installation,
require fresh receive watermark and peer/security matching, and quarantine an
ambiguous timeout instead of retrying keys or resetting packet numbers.

## Smallest implemented block

peer_wire.c serializes only PEER_CREATE: WMI command 0x6001, TLV tag 97,
16-byte body: vdev-id, padded eight-byte MAC, peer-type DEFAULT (0).
The upstream STA path initializes DEFAULT, not BSS (1). The API accepts only
the currently configured four-vdev resource budget (ids 0..3), nonzero unicast
BSSID, 24-byte capacity and non-overlapping output/input with integer bounds.
Invalid calls leave output untouched. It neither authorizes RF nor chooses an
AP; caller must bind actual BSS/RSN, target, active radio epoch and policy.

The verifier extracts actual packed upstream structs/enums and generator
assignments into an independent oracle. Native tests compare 1000 BSSID/id
variants, output canaries, every undersized capacity, invalid ids/MACs,
aliases, NULL and overflowing address ranges. ASAN/UBSAN and freestanding
COFF compile are performed exclusively on Yukabox. Reports bind all source,
references, oracle and log hashes. This pure block is not native integration.

## Deterministic implementation order

1. Finish actual passive scan/export evidence. Select a real matching BSS and
   parse bounded RSN/supported rates/channel; enforce WPA2-PSK/CCMP and PMF
   policy already specified by security-plan. Current beacon parser alone is
   insufficient for association capabilities. Do not infer RSN from SSID.
2. Next smallest runtime step: HTC HTT service CONNECT plus version request/
   response parser, bounded retained event FIFO and actual CE routing. Bind
   firmware TLV HTT op-version, negotiated endpoint/max-message and supported
   target version. Fail closed on unknown versions; no RF transmission needed
   to learn protocol version. Extend all-owner inventory before adding maps.
3. Add exact QCA9377 PCI HTT DMA RX ring/fragment/TX setup, decoded current
   hardware formats and bounded completions. Prove actual HTT peer-map,
   security-indication and packet decapsulation with replay/length/owner tests.
   Runtime WMI RX2 pump is not an HTT data-plane implementation.
4. Implement bounded management authentication/association state machine or
   reuse mature mac80211-equivalent logic; actual AP response/status/AID and
   timeout/disconnect rules. Start/peer/rate/up configuration must follow that
   state, not an assumed synthetic association. First narrow profile can use
   legacy 20MHz rates when genuinely supported, never fictitious HT/VHT caps.
5. Join mature RSN core using its required synchronous key callback: poll
   actual HTT SEC_IND while deferring EAPOL, no reentrant supplicant calls.
   Require no-reinstall guard, real crypto/RNG/timers and controlled-port state.
   Complete encrypted authenticated credential provisioning separately;
   signatures and BLE advertising do not supply confidentiality/device identity.
6. Only after association and RSN authorization: actual data-plane packets,
   DHCP/ARP/IP and internet exchange with Yukabox. All failures retain owners
   until proven checked stop; no DMA completion becomes protocol success.

This intentionally implements one exact serializer rather than speculative
whole connect. WMI START/UP/PEER_ASSOC/key serializers, HTT transport, RSN/BSS
parser, management association, key confirmation and port authorization remain
unimplemented here. The preceding reusable supplicant slice stays authoritative
for real core dependency and key no-reinstall tests.

Reproduce on Yukabox with verify.py --clang <pinned-clang> --reference
<hash-matched-reference-directory> --output <owned-output-directory>.
