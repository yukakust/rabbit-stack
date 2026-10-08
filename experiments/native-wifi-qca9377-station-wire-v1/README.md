# Exact station WMI bytes / management coordinator

Unsigned CPU-only preparation. No RF admission, device calls, credentials,
signatures, deployment counter or frozen-source changes. Native capabilities
remain UNKNOWN; source hashes in caller bindings do not grant radio permission.

Pure serializers emit exact START/UP/PEER_ASSOC/CCMP INSTALL_KEY bytes from pinned
Linux `6b5a2b7d9bc156e505f09e698d85d6a1547c1206` generators, using source-bound
fresh BSS epoch/floor, exact `iPhone (9)`10, selected legacy/basic rate masks,
actual AP AID/capabilities and explicit regulatory power/channel inputs. The
caller must obtain those inputs from owned current RX/native capability/policy,
never fabricate them from SSID or a positive model. Peer association requires
AP auth/association proof and PEER_MAP in the real caller; bytes are not proof.

CCK bit7 in WMI legacy rates is derived from actual ath10k conversion and is
distinct from the over-air supported/basic-rate bit. Narrow peer flags are
AUTH|NEED_PTK4WAY for pure RSN; upstream GTK2WAY flag comes from legacy WPA IE,
not simply from having a GTK. HT/VHT/QoS/PMF/high-rate capabilities are not
invented. Management requests advertise only legacy rates and chosen pure
WPA2-PSK/CCMP RSN, open-auth algorithm0/transaction1, bounded sequence/listen
fields; no reassociation or downgrade path is present.

Key bytes are copied only from the explicit caller buffer into its output;
scratch is wiped, no values are logged. Exact upstream key arg/generator does
not encode RX sequence/RSC. Nonzero supplied sequence is therefore rejected
until genuine owned descriptor/key/RX replay integration exists; this is a
component integration limitation, NOT a claim that target only supports zero.
Sequence remains caller-owned and must never be silently discarded/reset.

`coordinator.c` retains immutable auth/assoc proposals. Actual backend publication
cookie/MSDU-id, current RX floor/epoch, real DMA closure, status0 and matching
owned AP response must all join before advancing. DMA alone does not establish
ACK/AP success. NO_ACK/DISCARD/error statuses are retained; failures retain
publication/owner facts, and late actual DMA closure remains observable. One
association transaction has explicit local overall10second bound, monotonic
guard and no automatic retry. This bound is a local profile, not a vendor timing
claim and does not alter resident/HCI/USB timers.

Backend contract must prove either actual service-selected WMI MGMT or HTT3
MGMT pkt_type3/ext_tid17/direct packet paddr. Raw data pkt_type0 is not a
substitute. NEW htt-data-path-v1 management proof is external/unadmitted until
its own primary/producer proof passes; this coordinator performs no submission.
Controlled-port/EAPOL/private keys and replay admission remain external.

Tests compile ORIGINAL upstream generator bodies in an explicitly synthetic
hosted fixture (real calloc storage only, no kernel/device success), compare
bytes under ASAN/UBSAN, then COFF-compile production slices only on Yukabox.
References/upstream notices and source/copy/oracle hashes are retained.
