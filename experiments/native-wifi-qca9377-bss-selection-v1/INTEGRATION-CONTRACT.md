# Integration contract

1. Single owner runs the actual persistent RX poll, then `qca_rx_take` once for
   the real completion. Input to this module is that CPU-owned copy, never a
   borrowed CE buffer. Preserve unknown/error records in the existing archive.
2. Coordinator supplies actual current lifetime epoch, scan RX start floor,
   negotiated WMI endpoint, READY MAC, active live scan frequency and policy
   digest/allowed 2.4GHz channel frequencies. Do not relabel historical frozen
   scan exports as current live observations. The frame carries no epoch by
   itself: epoch authority is the caller's actual retained acquisition.
3. Derive `native_rates` and PSK/CCMP capabilities from reviewed native TX/key/
   crypto/rate implementation. `capability_source[32]` records its source closure,
   not a firmware claim, arbitrary boolean or signature. Current allocation-only
   `htt-persistent-runtime-v1` does not prove these capabilities. Until supplied,
   pass UNKNOWN (zero capabilities/rates); selection fails closed.
4. Choose an explicit freshness TTL and monotonic CPU timestamps; offer during
   current scan, select while actual persistent radio remains ACTIVE. Refresh
   owners before using the result. Expired/released/faulted observations never
   authorize subsequent association. Selected BSSID/channel/security/rate/raw
   snapshot must be bound into a separately reviewed station/auth transaction.
5. Call the live adapter with current production persistent object; it checks
   READY, owner booleans/count consistency, session endpoint, actual RX completion
   ceiling and epoch. Current source joins existing fourteen-map ABI without
   imposing a fake count on the future external HTT ledger. The runtime owns
   resource accounting and cleanup; this module releases nothing.
6. Selected snapshot is eligibility, not authenticated AP identity or permission
   to transmit. Authentication, association, key derivation/install, protected
   port, DHCP and WAN proof remain independent later gates.

Concrete remaining blockers: reviewed native legacy rates/PSK+CCMP capability
source, live coordinator call site/TTL decision, actual compatible owned beacon,
and separately reviewed station/key/data path. This component is not integrated
into frozen64 and does not reserve any generation or packet counter.
