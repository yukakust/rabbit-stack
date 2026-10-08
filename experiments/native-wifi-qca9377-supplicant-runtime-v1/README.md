# Mature supplicant freestanding platform runtime

New unsigned, software-only component. No frozen source, device, BLE, state,
counter, owner key or credential access. Native radio TX capability stays
UNKNOWN. This is a genuinely linked PE/COFF module, not a bootable/integrated EFI
candidate or physical WPA/IP proof.

The exact official-PMKSA-patched hostap2.11 core/internal crypto is retained.
The original31 unresolved platform symbols are implemented: bounded external
arena allocation/realloc/free with alignment and wipe, memory/string APIs,
monotonic/wall time providers, owned timeout queue, formatting/sorting and
fail-closed unsupported enterprise reauthentication. There are no libc success
stubs or default hardware/entropy callbacks. The formatter is the exact
[nanoprintf commit f25230e](https://github.com/charlesnicholson/nanoprintf/blob/f25230efb5882126b77337c3037d5944a60a1b3c/nanoprintf.h)
with integer/width/precision/size/large formats enabled, float/writeback disabled;
its upstream license and bytes are preserved.

Arena is caller-owned, aligned16,4KiB..1MiB, with128 live allocations. Freed
capacity and final arena are wiped. Metadata lives outside the arena. Invalid
free revokes instead of releasing another owner. A revoked runtime blocks new
allocations, RNG and callback work, but permits deinitialization/free/wipe.
Unbind requires zero live allocations/timers and not inside dispatch, invokes
mandatory external revocation, then wipes arena and metadata. These are CPU
arena operations, not an approved UEFI allocator, DMA pool or memory provider.

OS byte spans are capped1MiB, C strings4096bytes, diagnostic buffers8192bytes;
qsort supports at most256×256bytes and performs real insertion sorting. Invalid
hard preconditions revoke/trap, never return fabricated success. Standard C
primitives used by the formatter/host harness retain ordinary caller-owned
buffer contracts. Integer conversion has defined overflow clamping; errno/
locale/Unicode/float are outside this narrow native profile.

Timers:64 entries, exact context matching and ELOOP_ALL_CTX cancellation,
deadline/order stability, remove-before-call, actual monotonic guard, epoch
ownership and dispatch budget≤64. Nested dispatch rejects. Revocation cancels
every pending callback; later RNG, EAPOL/key or timer work cannot continue.
Native integration must call `rsn_runtime_poll` from its existing cooperative
owner loop; `eloop_run` is a bounded busy dispatcher used by hosted interop,
not a replacement for resident USB/HCI/CE timing or hardware polling.

Providers are explicit callbacks with provenance hash and mandatory revocation.
RNG has no fallback; missing/failed/revoked provider erases partial output and
revokes. The provenance hash does not approve entropy quality or device identity.
`os_get_time` requires a separate real wall-clock provider and fails if absent;
it never labels monotonic uptime as wall time. Timer/relative time comes only
from monotonic provider, rejects rollback.

`adapter.c` fills the genuine mature `wpa_sm_ctx`. EAPOL must be exact bounded
key framing to the selected peer; send provider must acquire its own copy before
return. Key callback admits only first-profile CCMP16-byte semantics and calls
the external actual-confirmation provider, never substitutes DMA completion.
Failed/ambiguous/missing provider closes/revokes. Protection/state callbacks
remain separate. The auth deadline is genuinely registered/cancelled; unsupported
PMKSA offload returns failure and unsupported enterprise reauth revokes. Key
deletion/reassociation/MLO/PMF/radio/data-plane support is not invented.

Verification is exclusively Yukabox: actual27-object COFF link (24 mature+3
platform units), no default libraries or OS import directory; actual compiled
size exports measure context storage. Separate ASAN/UBSAN tests cover allocator,
wipe, timer ordering/cancel/budget/revoke, RNG partial failure and providers.
All13 original mature supplicant/authenticator/internal-crypto scenarios run
with this allocator/timer platform; hosted libc printf and public fixture clock/
entropy/driver callbacks remain explicitly synthetic and unapproved for native
use. No key values are logged. Reports and compiled-source snapshots bind bytes.

Full radio+World/native image fit, approved DRBG/clock/memory providers, private
credential provisioning, actual HTT EAPOL/key transport and physical controlled
port proof remain separate required integration gates.
