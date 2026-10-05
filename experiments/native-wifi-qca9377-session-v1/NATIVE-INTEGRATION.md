# Next operating-profile integration

This is the remaining implementation boundary, not a physical connection proof.
Native41 only tests exact firmware startup and then closes all hardware owners.
The new pure protocol modules are not called by that installed image.

## Physical prerequisite

Native38's full asset was staged, but helper result3 stopped it before main.
Its session is historical and must not be replayed. Result3 compatibility and
post-cleanup legacy update delegation are fixed in applied native41. Finish the
existing signed `firmware-ram-ytrkhw7x` generation41 session. Read fresh QWBT and
save its actual phase/error/command counts/READY/closed-ownership fields. A full
RAM bitmap only proves staging. Require verified calibration, main upload,
BMI_DONE and actual HTC_READY before claiming firmware startup. Unexpected
board pointers or READY layouts need observed bytes and reviewed policy;
do not widen the current write guard based on a host fixture.

## Native operating lifetime

Derive a separately checked operating profile after this trial is released.
Use fresh setup/query and exact source/asset binding. Keep the adapter and RAM
asset pin while radio/DMA are active; do not run native41's automatic successful
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
operating WMI events. Route responses by endpoint and CE identity. Operational
WMI credits require a separate bounded ledger; the handshake codec alone does
not grant transmit permission. Stash WMI events that arrive while control TX
completion is still pending. Bound timeout/cancellation with monotonic time.

Validate service-ready ABI and memory requests. Derive all firmware host-memory
allocation sizes from a fixed resource profile, with overflow/budget/address
checks and retained-mapping lifetime tests. The info parser does not do this.
Send WMI init with exact mapped memory descriptions; require READY/status/MAC.
Create station VDEV0 and apply a checked regulatory/channel profile. Raw firmware
band limits are not a country/channel authorization table.

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
