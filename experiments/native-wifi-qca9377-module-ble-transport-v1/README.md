# Native public signed-module chunk delivery

This NEW component stages one bounded public RABMOD01/RABRSN01 chunk (at most
65536+288 bytes), verifies transport SHA256 and defers admission to the native
loop after ATT callbacks return. Transport integrity never grants code
authority. The real private parent verifies owner/target/installed-parent file
assertion/epoch/counter/role/ABI, genuine child PE and code/arena lifetime.

Service UUID suffix33 uses handles20..26 and values34/35/36. It must intercept
ATT before the legacy firmware service's catch-all handles, preserves MTU247
and leaves every old native/firmware/diagnostic UUID and bootstrap unchanged.
Control B declares exact session8/length/SHA256. D carries exact session/offset
and at most231 bytes. C publishes PENDING, sole native mt_poll accepts the
owner-signed chunk; accepted chunk status is not module-load or Wi-Fi proof.
Status is80 public bytes. Saved same-session BEGIN and matching repeated data
are idempotent. No resign/reset on disconnect. Conflicting repeats, epoch,
time rollback,45s without byte progress or600s total fail and wipe staging.
Native polling cannot keep an idle transmission alive. Cross-epoch or closed
operations cannot execute callbacks. Borrowed callbacks prevent close/reentry.

There is one65824-byte staging buffer with explicit native lifetime, separate
from parent artifact262144-byte arena and from the city's external pool. Whole
image/child mapped caps must include it. It carries no TLS plaintext, password,
private key or secret provisioning request. Secure TLS provisioning is a
separate gated stream and must not be replaced by this channel.

Actual injected software checks use copied genuine Monocypher Ed25519 and the
frozen role2 artifact verifier: all288 signed header corruptions, signed body
hash mismatch, corrupted outer digest, max65536 body, duplicate exact data,
saved-session resume, conflict/epoch/alias/clock/deadline/wipe/reentry and ATT
discovery/paging/bounds. Firmware callbacks and native signer/device remain
absent. Native whole integration, Mac sender/session journal, installed parent
admission and actual BLE delivery are still required. No physical proof yet.

Reproduce verify.py on Yukabox only; scope-owned TMPDIR avoids shared/tmp.
