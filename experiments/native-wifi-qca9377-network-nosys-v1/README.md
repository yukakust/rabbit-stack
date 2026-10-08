# lwIP NO_SYS next-IP preparation — synthetic, not a Dell update

Pinned upstream: [lwIP2.2.0 release](https://github.com/lwip-tcpip/lwip/releases/tag/STABLE-2_2_0_RELEASE),
commit `0a0452b2c39bdd91e252aef045c115f88f6ca773`.
`vendor/` contains unmodified selected upstream sources, all upstream headers and
COPYING. `upstream-pin.json` binds181 files to this commit. The upstream
[DHCP implementation](https://github.com/lwip-tcpip/lwip/blob/0a0452b2c39bdd91e252aef045c115f88f6ca773/src/core/ipv4/dhcp.c)
is the actual parser/state machine used in these tests.

`network.c/h` provides a single-thread, bare-metal NO_SYS netif adapter with
ARP/address-conflict detection, IPv4, UDP and DHCP. No OS, threads, sockets, TCP,
DNS, IPv6, malloc-backed memory, IP fragmentation or actual network traffic.
Memory is fixed:16KiB lwIP heap, eight1600-byte packet buffers, two UDP PCBs,
eight timeout objects, one static DHCP/netif state, one1518-byte output scratch.
Input is copied into bounded owned pbuf storage. The output callback must consume
or copy borrowed Ethernet bytes synchronously; it cannot retain the scratch
pointer. A real HTT adapter must map these Ethernet frames into its own proven
TX/RX owners and respect completion/credit/backpressure; that is not implemented.

Before any DHCP/ARP/IP, `rabbit_network_start` requires externally proved RSN
controlled-port authorization, verified key installation, nonzero generation and
association epoch, and explicit entropy/output callbacks. These are internal
proof inputs from the supplicant/driver, not UI permissions or user-set booleans.
They do not establish Wi-Fi authentication themselves. EAPOL is rejected by IP
input and remains on the separate supplicant path. Every ingress requires the
current association epoch. `revoke` clears IP and closes the local adapter. Real
link loss must call it. Only synthetic deterministic RNG is used by fixtures;
production RNG validity/entropy is an external prerequisite.

Call `tick` from one owner with monotonic elapsed milliseconds, each at most100ms
(the ACD timer resolution); late/gapped scheduling must be handled by the future
persistent driver. There is no asynchronous reentrancy or scheduling thread.
`rabbit_network_ip` returns lwIP's network-order IPv4 word, only while authorized.

## Verification

C compilation, execution and ASAN/UBSAN/COFF were performed only on Yukabox in
`/home/yuka/rabbit-world/parallel-network-nosys-v1`; TMPDIR is the isolated scope's
`runs/checked`, never `/tmp`. `run_remote.py` is the reproducer, not a Mac command.
No frozen driver, HCI/USB path, BLE connection, real state, key or credential was
read or changed. No package was signed or sent to Dell.

The real stack passed16 synthetic DHCP/ARP/controlled-port checks: blocked start,
EAPOL separation, wrong transaction ID, missing OFFER server-ID, stale epoch,
truncated IPv4, invalid option length, corrupt IPv4 checksum, valid OFFER/REQUEST,
wrong ACK transaction ID, valid ACK with ARP conflict probes, duplicate ACK,
renewal and lease-expiry transitions, and revocation. These are packet fixtures,
not a router, DHCP server or physical Dell result.

All17 production C units compile to freestanding x86_64 COFF. The declarations
under `freestanding/` are compile shims, not a complete runtime implementation.
Final integration must resolve libc-like helpers/panic/RNG/sys_now against the
existing bare-metal ABI and verify no unsupported imports. Object section sums:
24,519 bytes text,32,361 bytes BSS,2 bytes data and2,813 bytes ordinary rdata,
plus small individual string sections. Final EFI SizeOfImage is **not measured**.
This does not fit native61's16KiB remaining mapped allowance as a direct addition.
A future scoped composition must free memory/remove inactive bootstrap storage or
otherwise fit the existing cap; this scope does not enlarge any cap.

## Explicit integration blockers

A separate real-stack ASAN fixture confirms an upstream behavior gap: during
REQUESTING, an ACK with matching MAC/xid but mismatched option54 server-ID is
accepted. The upstream source matches MAC/xid and dispatches ACK without enforcing
the selected OFFER server-ID. Missing OFFER server-ID is correctly rejected.
This scope preserves upstream unmodified and records the gap; it does not claim
strict ACK-server validation or authorize production signing. A narrow new
validated admission/filter design is required before using this client for the
physical IP milestone. DHCP does not authenticate the server in any case.

Also pending: final EFI/link ABI and mapped caps; real RX/TX ownership bridge;
actual RSN/key/RNG proofs and persistent timer owner; real DHCP lease evidence;
router reachability; protected end-to-end Dell/Yukabox exchange. No physical
Wi-Fi/IP/Yukabox claim is made.

## New hardened adapter — separate from the preserved initial baseline

`network_hardened.c` and `dhcp_policy.c/h` compose the same pinned unmodified
upstream with a new bounded ingress policy. `run_hardened.py` reproduces this
separate version; its proof is `evidence/hardened/`. The initial upstream-gap
report above remains immutable and describes the unfiltered baseline only.

The policy checks IPv4/UDP/container bounds, rejects fragmented input, validates
DHCP cookie and bounded TLVs including option-overloaded `file`/`sname`, rejects
ambiguous duplicate type/server/overload options, and requires one server-ID on
ACK. During REQUESTING and RENEWING it requires that ID to match the selected
server. REBINDING and INIT-REBOOT do not inherit that restriction. After actual
lwIP acceptance transitions REBINDING→BOUND, the adapter adopts the new ACK's
server-ID for subsequent renewal. A checksum/xid/MAC failure leaves lwIP in
REBINDING and cannot change that server binding.

Primary basis: [RFC2131 client behavior](https://www.rfc-editor.org/rfc/rfc2131.html#section-4.4)
and [reacquisition](https://www.rfc-editor.org/rfc/rfc2131.html#section-4.4.5)
select one server initially and permit another server during rebinding;
[RFC2132 overload/message-type/server-ID](https://www.rfc-editor.org/rfc/rfc2132.html#section-9.3)
defines the relevant wire encodings. RFC2132 describes ACK server-ID as optional:
Rabbit's mandatory ACK-ID, END-marker and duplicate-option rejection are an
explicit stricter fail-closed interoperability profile, not a universal RFC
requirement or proof of server authentication. Routers omitting ACK-ID would be
rejected and need a separately reviewed interoperability decision.

Hardened verification:339 synthetic real-stack ASAN/UBSAN checks and all18 COFF
production units passed. This covers every truncated frame length, invalid
option length, missing/duplicate/wrong ACK server-ID, fragment rejection,
selecting/renewal correctness, permitted rebinding with a new server and actual
new-server adoption, lease expiry, and a pure valid-overload policy fixture.
It does not claim a physical router or exhaustive packet-parser verification.
Hardened object sums:25,520 bytes text,32,361 bytes BSS,2 bytes data,2,813 bytes
ordinary rdata plus small individual string sections. Final EFI mapped budget,
bare-metal libc ABI, timer/RNG and HTT/RSN integration remain pending; no cap was
enlarged and production signing remains false.
