# Bounded lwIP TCP/DNS preparation

Software-only next-stage component, not a physical Wi-Fi/IP or HTTPS result.
Uses genuine lwIP2.2.0 at pinned commit
`0a0452b2c39bdd91e252aef045c115f88f6ca773`, preserving the hardened DHCP ingress
policy from frozen `network-nosys-v1`. Four additional TCP/DNS upstream source
files have exact URLs and hashes in `vendor/tcp-dns-upstream.json`.

NO_SYS single poll owner, IPv4, DHCP+ARP conflict check, selected DHCP ACK server
and transaction/MAC enforcement; one TCP PCB, eight segments, MSS1200,
window/send2400, 16KiB lwIP heap, eight1600-byte packet buffers, two DNS entries.
`wan_transport` owns one raw TCP stream and a caller-owned4096-byte cipher RX
arena. The send/receive callback convention matches Mbed TLS WANT_READ/WRITE.
It does not parse or authenticate TLS and must never carry a plaintext password.

Owned pbuf copies, bounded RX FIFO, TCP backpressure, duplicate suppression by
actual lwIP, epoch-bound callback context, volatile RX wipe and PCB abort on
explicit network revocation. A pending DNS request retains the singleton until
its genuine resolver completion/timeout; an old callback cannot acquire a new
epoch. There is no asynchronous thread or callback reentrancy.

`run_hardened.py` compiles actual lwIP+C fixture using ASAN/UBSAN and freestanding
COFF only on Yukabox. The fixture injects synthetic Ethernet packets: DHCP bad
server/xid/options/truncation/checksum, ARP conflict-probing/lease expiry,
wrong epoch, DNS wrong transaction/duplicate, TCP bad checksum/SYNACK/data
completion/duplicate, bounded send, stale BIO context, close/wipe and outstanding
DNS quarantine. Fixture RNG is explicitly synthetic, not production entropy.

Evidence records source hashes, compiler, actualC fixture result and COFF sizes.
Raw object section sums are not a reachable linked EFI measurement. No signature,
BLE, credentials, physical packets, Funnel exposure or frozen source change.

## Required integration before hardware admission

- Approved genuine entropy/DRBG with a lifetime covering all lwIP timers; no fake
  `random32` fallback. Current ops have no per-call error channel: platform must
  revoke before an unhealthy DRBG can enter this mature callback boundary.
- Authorization fields must come from actual current association+PTK/GTK install
  and controlled-port proof. They are coordinator authority, never UI booleans.
- Actual HTT owned Ethernet TX/RX with backpressure and generation/epoch bridge.
- Tick from monotonic single poll owner at<=100ms granularity independently of
  city rendering; call WAN poll and close on lease loss as well as radio loss.
- Place static lwIP heap/pools and cipher buffer in reviewed owned runtime arenas,
  then measure the full reachable EFI/file4MiB/262144 caps and all candidate gates.
- Mbed TLS certificate/name/trusted-time verification, fresh nonce HTTPS parsing
  and actual Dell→isolated Yukabox endpoint→Dell/serverlog correlation remain
  unimplemented here. Raw TCP success is not HTTPS or WAN success.
