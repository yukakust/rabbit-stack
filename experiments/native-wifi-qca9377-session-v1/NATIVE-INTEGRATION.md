# Next operating-profile integration

This is the remaining implementation boundary, not a physical connection proof.
Native42 tests exact firmware startup and then closes all hardware owners.
The pure operating-protocol modules are not called by that installed image.

## Physical prerequisite — completed on 2026-10-05

The exact generation42 session `firmware-ram-pwg6_pnz` delivered all twelve
immutable packets (bitmap4095). Fresh QWBT observed all3114 BMI commands complete,
plan20/error0, calibration result3 under the exact firmware feature policy, and
actual HTC READY:20bytes,2credits,1792-byte credits,4endpoints. A subsequent read
confirmed native stage5/error0, adapter12,cleanup14,DMA0 and asset pin0. The
controller cleared hardware_trial_pending only after this actual cleanup.
Evidence: native-wifi-qca9377-v1/evidence/2026-10-05/native42-firmware-ready.
This proves the physical startup diagnostic, not a retained operating lifetime,
scan, association, lease, encrypted traffic or WAN. Visual city/tail observation
remains separate and pending. The retired partial41 session must not be replayed.

## Native operating lifetime

Derive a separately checked operating profile after this trial is released.
Use fresh setup/query and exact source/asset binding. Keep the adapter and RAM
asset pin while radio/DMA are active; do not run native42's automatic successful
teardown at HTC_READY. Add distinct operating telemetry so READY, scan, router
association, lease and WAN traffic cannot be confused with a closed diagnostic.

The existing `QcaChannels` already owns seven directions and fourteen mappings:
CE0 TX/control, CE1 RX/HTC+HTT, CE2 RX/WMI, CE3 TX/WMI, CE4 TX/HTT and CE7 TX/RX
diagnostics. Each direction currently has one data page and an eight-entry
descriptor ring. Never post the same data buffer twice while DMA can own it.
Retain existing IRQ/link/PCI/BM guards and completion fences. Posting RX,
processing a validated completion and reposting require a single explicit owner.

Drive `htc_session` with the observed READY and verified CE0/CE1 completions.
Open WMI/HTT services, keep assigned endpoints, and post CE2 receive before
operating WMI events. Route responses by endpoint and CE identity. The pure `htc_credit` ledger now reserves WMI credits including the HTC header,
commits them before descriptor publication, and restores them only from bounded
firmware credit reports. It cannot identify a replayed RX completion: the actual
CE owner must consume each completion once. `htc_control` coordinates the
endpoint-zero handshake and retains a validated early response until its exact
TX completion; it does not queue early WMI service events or drive hardware.
Both are host-checked with ASAN/UBSAN and COFF on Yukabox, not installed on Dell.
The handshake codec alone does not grant transmit permission. Stash WMI events that arrive while control TX
completion is still pending. Bound timeout/cancellation with monotonic time.

Validate service-ready ABI and memory requests. Derive all firmware host-memory
allocation sizes from a fixed resource profile, with overflow/budget/address
checks and retained-mapping lifetime tests. The info parser does not do this.
Send WMI init with exact mapped memory descriptions; require READY/status/MAC.
Create station VDEV0 and apply a checked regulatory/channel profile. Raw firmware
band limits are not a country/channel authorization table.

## First native control candidate — host/QEMU checked

`native-wifi-qca9377-operating-v1` now integrates the protocol coordinator with
actual CE0/CE1/CE2 code and native entrypoints. The bounded20-second trial retains
the adapter/pin during connect-WMI/connect-HTT/setup and SERVICE_READY receipt,
then uses existing actual stop/cleanup.17 ASAN/UBSAN hardware-model scenarios,
COFF, two byte-identical full UEFI builds, normal/EMPTY QEMU and current-world
reproduction pass on Yukabox. Payload147456bytes, generation43 candidate only.
No physical signing/delivery/admission yet. Actual controller remains42.
The candidate is not a persistent radio and does not send WMI INIT or scan.
Next: exact physical admission and observation, then retained host memory/init.
See that candidate's README for binding and replacement boundaries.

## Discover and connect

Use the passive scan codec only after those prerequisites. Correlate scan IDs,
feed bounded validated RX frames to the host-checked beacon/probe-response
SSID/BSSID/channel/opaque-RSN parser (it does not validate security), and
select the explicitly requested `SILK_56E35E_Plus`. Passive scans alone may not
reveal a hidden SSID. Do not infer the router's security from a lock icon or from
an unidentified current Mac connection. Unsupported security must be reported
without silently downgrading to an open network.

Implement management receive/transmit and HTT data queues before association.
Keep credentials in Mac owner-only storage; implement authenticated confidential
delivery before transmitting a password or equivalent derived key. Packet
signatures alone do not make the current GATT channel confidential. Do not
ship credentials to Yukabox for builds or into repository/session evidence.

Router authentication needs the appropriate RSN/key handshake and firmware key
installation. An association event alone is not proof that encrypted data flows.
Require actual protected transmit/receive evidence.

## IP and Yukabox

The existing network-viewer experiment already has an iPXE DHCP/HTTP adapter,
tested with a virtual RTL8139 NIC in QEMU. Prefer assessing reuse over a second
handwritten IP stack. That EFI build is394240bytes and is not an installed Dell
Wi-Fi driver; loading/size/ABI/owner checks still need a concrete integration.

Require a real DHCP lease, ARP/router exchange and packet counters. Yukabox's
observed addresses are private IPv4 plus a Tailscale overlay, not a directly
reachable public endpoint for an ordinary Dell router lease. A WAN route/relay
or supported overlay transport is still required; do not treat Mac's existing
SSH access as Dell connectivity. Verify a nonce-bearing request/response
originating on Dell before enabling graphics streaming.

## Replacement and evidence

The current resident loader calls the native close callback once. An active
adapter cannot be unloaded while cleanup still needs polling. Provide explicit
authenticated quiesce plus a receipt that every actual DMA/PCI owner was
released before permitting a native replacement. Preserve the world and old
districts. RAM firmware staging may need retransmission after replacement;
do not assume cross-module asset ownership exists.

Test the actual derived native entrypoints through every allocation, RX/TX,
timeout and cancellation boundary with ASAN/UBSAN, then COFF, current-world
QEMU, two identical rebuilds and the physical gates. Archive host and physical
evidence separately. No USB/bootstrap writes, autonomous reboot, flash/OTP
programming or owner-key export is part of this operating profile.
