# Native Dell Wi-Fi: security and IP integration slice

Status: independent host work, not installed on Dell. No secrets were read,
no radio action was performed. Native49/CE3 repair and physical tests belong to
the coordinating agent. This folder does not modify their frozen inputs.

## Smallest supported first connection

Proposed first profile: infrastructure station, RSN/WPA2-PSK, AES-CCMP-128,
one BSSID, one vdev, one association at a time. This is a conditional profile,
not a claim about `SILK_56E35E_Plus`: an SSID and a padlock icon do not reveal
AKM/cipher/PMF requirements. The real beacon/probe RSN IE determines compatibility.
WPA3-only/SAE, enterprise EAP, required PMF, TKIP-only and unsupported ciphers
must return a specific unsupported result rather than downgrade security.
A WPA2/WPA3 transition BSS is usable only if it actually offers the supported
PSK/CCMP profile without a PMF requirement incompatible with this implementation.
No router setting change is part of this plan.

Reuse the mature wpa_supplicant RSN state machine and its crypto primitives,
with a small native adapter. Do not write a new four-way handshake or custom
cryptography. Porting the whole Linux nl80211 driver is unnecessary: its OS
interfaces are replaced by our already validated WMI/HTT boundary. The source
is a starting reference, not automatically a security-approved frozen release;
before deployment review upstream fixes/security advisories against the chosen
snapshot, preserve applicable BSD license notices, and prove the actual build.

The minimum supplicant adapter provides bounded allocation/free, strong random
bytes with failure propagation, monotonic timers, send EAPOL, install/delete
keys, association/disconnection notifications and authorized-port status.
`wpa_sm_rx_eapol` receives only an owned/copied immutable EAPOL payload from
the current association. Use `wpa_parse_wpa_ie_rsn` and its policy checks;
do not select a BSS by SSID alone or accept differing association RSN elements.
The checked framing helper here is not a substitute for these checks.

## Dependencies and acceptance gates

1. Physical INIT/READY and persistent radio lifecycle. The present bounded
   diagnostic destroys the operating radio, so no later handshake can run yet.
   Quiesce/reboot/fault must stop queues and release every actual DMA owner.
2. STA vdev/peer and management association. Regulatory/channel permission,
   selected BSSID/SSID and accepted RSN profile come from validated scan data.
   Firmware peer/vdev confirmations precede supplicant association notification.
   Standard open-system 802.11 authentication is part of WPA2 association; it
   does not mean an open, unencrypted Wi-Fi network.
3. Actual HTT transport. Negotiate observed HTT/firmware capabilities, RX ring
   configuration, bounded DMA buffers, TX descriptor/fragment completion IDs,
   RX descriptor format and payload decapsulation. The WMI event CE2 stream
   alone cannot carry ordinary IP traffic. EAPOL uses Ethernet EtherType 0x888e
   at the adapter boundary; account for native-Wi-Fi/SNAP/Ethernet formats from
   the negotiated firmware mode instead of assuming all RX is Ethernet.
   Keep management frame TX and ordinary HTT data TX separate.
4. Credential provisioning described below. Without this gate no real secret
   is loaded, sent, printed or written into a committed world/package/log.
5. Supplicant four-way/group handshakes. Mature core validates replay counters,
   MICs, ANonce/SNonce, selected AKM/cipher and RSN/KDE lengths. Secure RNG is
   needed for SNonce, not a timestamp or deterministic pseudo-random seed.
   PTK/GTK installation crosses the native key adapter into firmware and waits
   for genuine firmware completion or a bounded timeout. DMA completion of a
   key command is not key installation completion. Serialize pending installs;
   do not invent correlation fields that the firmware does not return.
6. Port authorization. Only after the supplicant and real key-install result
   succeed may IPv4 data cross the controlled port. Before authorization allow
   only required association/EAPOL traffic; DHCP must not start prematurely.
   Retransmitted message 3 must not reinstall the same PTK/reset packet numbers
   (the upstream `ptk.installed` guard is material, not an optional optimization).
   Rekey, disconnect, timeout, changed BSSID and native unload clear appropriate
   session state; encrypted RX replay handling/PN belongs to the proven
   firmware/driver path, not an EAPOL framing parser.
7. IP stack and router evidence. Prefer an existing small TCP/IP stack such as
   lwIP in NO_SYS mode to another homemade DHCP/ARP/TCP implementation. Provide
   `netif` Ethernet RX/TX, `sys_now`, bounded pbuf pool and timer polling. Give
   the stack ordinary owned pbuf data, never a dangling CE/HTT DMA pointer.
   DHCP Discover/Offer/Request/ACK must match transaction, client MAC and bounded
   options; validate the lease/netmask/router, perform address-conflict handling
   and lease renewal, then actual ARP and packet exchange with the router.
8. WAN is a separate gate: an IP/lease does not prove reachability to Yukabox,
   which needs a chosen reachable relay/overlay path and a real Dell-origin
   nonce exchange. Video decode/Unreal is subsequent work.

Work that can run concurrently: supplicant platform-port compilation/fixtures,
credential crypto transport prototype with synthetic inputs, lwIP polling-port
host harness. Physical RF/firmware testing is serial under one device owner.
The security path joins the station/HTT path at gates 3 and 5; IP joins at gate 6.

## Confidential credential delivery

Current BLE packet signatures authorize the sender and package; they do not
encrypt credentials or authenticate the recipient. BLE peer UUID, target ID and
claimed receipt are public identifiers, not proof a secret will reach this Dell.
Do not put the existing credential file or its derived PMK into plaintext BLE,
world assets, signing logs, Yukabox, test fixtures or this directory.

Diskless RAM-only Dell has no established persistent device secret. A workable
first enrollment therefore needs an out-of-band binding to the physical screen:

* Reviewed native code creates a fresh recipient key from a proven strong RNG
  (verify actual UEFI RNG availability/failure behavior; don't assume it exists).
  It displays a QR containing the full recipient public-key fingerprint and
  boot/session challenge. A human verifies/imports the screen value on the Mac.
  A short numeric hint alone is not a full-key authentication scheme.
* A mature library implements an authenticated encrypted channel. Candidate:
  TLS 1.3 through a bounded BLE byte-stream adapter, with Mac pinning the
  physically obtained Dell SPKI fingerprint. Self-signed temporary identity
  is usable only through that explicit pin, not by disabling authentication.
  This is an architecture candidate, not an implemented TLS/UEFI library port.
  A pinned library version, crypto known-answer tests, real randomness, code
  size/RAM budget, fragmentation/backpressure and failure behavior are gates.
* Inside the encrypted channel Dell accepts an owner-signed provisioning request
  bound to recipient key fingerprint, challenge, boot/native identity, exact
  SSID bytes, negotiated security profile, fresh session counter and expiration.
  Its pinned owner public key already exists; private owner key stays on Mac.
  Signature verification plus TLS recipient pinning cover different directions.
* Provision once per fresh boot/session, acknowledge without secret material,
  keep only necessary secret in Dell RAM, erase on replacement/teardown/fault.
  For the narrow WPA2 profile Mac could send a 32-byte PMK derived by mature
  PBKDF2-HMAC-SHA1 implementation from exact SSID/password, reducing raw password
  exposure. PMK still grants access to that network and needs the same secrecy.
  It is not a WPA3 credential strategy and does not bypass EAPOL/key installation.

An alternative standard HPKE envelope (RFC 9180) still needs physical recipient
authentication, sender authorization, replay/context binding and a proven
freestanding library. It is not permission to hand-roll X25519/HKDF/AEAD.
Existing Bluetooth LE Secure Connections could be considered only after its
pairing/authentication stack is genuinely present and tested; current advertising
and GATT connection are not proof of encrypted/authenticated pairing.

No enrollment UI action or user question was performed in this branch. The
physical-screen step is a future requirement arising from absent device identity,
not a request to pause the current CE3/INIT diagnostic.

## Concrete artifact in this folder

`eapol_frame.c/.h` provide a bounded, allocation-free EAPOL-Key frame view for
the conditional WPA2 profile: 802.1X versions 1..3, packet type 3, descriptor
type 2, descriptor version 2, fixed 16-byte MIC field, exact outer and key-data
lengths, borrowed nonce/MIC/key-data spans, big-endian replay counter. Maximum
4096 is an explicit local admission budget, not a protocol-wide maximum.
Ethernet headers/padding must be removed before calling; no truncation or
unvalidated borrowed buffer lifetime. Output stays untouched on rejection.

Success means framing only: no MIC/replay policy/RSN checking, no decryption,
no M1/M2/M3/M4 classification, no key installation or authorization. It accepts
key-info flags structurally so the mature state machine can apply semantic
policy. It neither implements WPA3 nor makes malformed authenticated packets
acceptable. Call it only after AKM/cipher profile selection.

201477 host checks passed under ASAN/UBSAN on Yukabox, including every 16-bit
outer length and key-data length for a fixed fixture, every key-info value,
version/type/descriptor mutations, all short lengths, allowed size boundaries,
big-endian replay decoding, immutable-on-failure and null inputs. Independent
offset/size oracle compiles the actual upstream `wpa_eapol_key` and 802.1X
header. Freestanding x86-64 Windows COFF compilation also passed. No binary is
committed; public evidence is secret-free and labels the absence of device proof.

Reproduce on Yukabox with `python3 verify.py --clang <reviewed-clang> --reference
<reference-directory> --output <ignored-output-directory>`. The reference holds
the official archive and its extracted tree; verifier checks every regular
extracted reference file against the pinned archive before compiling.

## Pinned primary references

* [Official hostap release archive](https://w1.fi/releases/wpa_supplicant-2.11.tar.gz),
  SHA256 `912ea06f74e30a8e36fbb68064d6cdff218d8d591db0fc5d75dee6c81ac7fc0a`.
  `src/common/wpa_common.h` size/offset/AKM definitions;
  `src/common/wpa_common.c:wpa_parse_wpa_ie_rsn` RSN parsing;
  `src/rsn_supp/wpa.c:wpa_sm_rx_eapol,wpa_supplicant_install_ptk` mature handshake
  and no-reinstall guard; `src/drivers/driver.h` adapter boundaries.
* Linux commit `6b5a2b7d9bc156e505f09e698d85d6a1547c1206`:
  [ath10k mac.c](https://github.com/torvalds/linux/blob/6b5a2b7d9bc156e505f09e698d85d6a1547c1206/drivers/net/wireless/ath/ath10k/mac.c)
  `ath10k_install_key` command plus real completion wait;
  [htt_tx.c](https://github.com/torvalds/linux/blob/6b5a2b7d9bc156e505f09e698d85d6a1547c1206/drivers/net/wireless/ath/ath10k/htt_tx.c)
  descriptor IDs/ownership and native-Wi-Fi/Ethernet modes;
  [htt_rx.c](https://github.com/torvalds/linux/blob/6b5a2b7d9bc156e505f09e698d85d6a1547c1206/drivers/net/wireless/ath/ath10k/htt_rx.c)
  RX allocation/ring fill and decapsulation.
* [RFC 2131](https://www.rfc-editor.org/rfc/rfc2131) DHCP leases/transactions;
  [lwIP NO_SYS](https://www.nongnu.org/lwip/2_1_x/group__lwip__nosys.html) polling
  stack port proposal (not implemented or version-pinned in this branch).
* [Mbed TLS entropy port guidance](https://mbed-tls.readthedocs.io/en/latest/kb/how-to/add-entropy-sources-to-entropy-pool/)
  platform RNG requirement; [RFC 9180](https://www.rfc-editor.org/rfc/rfc9180)
  standard HPKE alternative (not implemented).

Full content hashes of downloaded source references are in `references.json`.
