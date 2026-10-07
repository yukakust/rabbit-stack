# City recovery after observed bootstrap context

No reboot command or claim of a user-confirmed manual reboot. The owner photo
shows the startup blue rectangle and BLE console. A fresh locked, known-peer
read returns the exact empty 60-byte RFS1. The cause of context loss is unknown.

`route.py` verifies actual APPLIED57, every saved firmware packet signature,
the last ten-chunk receipt, the preserved world18 and competing controller state.
It durably archives all original sessions, logs, photo and state before clearing
only the obsolete hardware-pending pointer. Counters remain57/18 at retirement.
The original signed sessions are retained unchanged.

The new recovery preflight runs only on Yukabox: repeated equal native builds,
ASAN/UBSAN city checks, normal and EMPTY-boot actual supervisor QEMU checks,
199 source hashes, and a checked world19 package. The plain-city payload equals
the previously applied56 payload, including Bluetooth disconnect recovery.

ROOT calls `guarded_prepare` with a fresh actual observation and activation
proof. It delegates to the unchanged original prepare, checks before the local
key boundary, and signs the new58 plan once. `restore_observed.restore` is an
isolated derivative preserving packet/signature/counter/receipt validation while
recording observed bootstrap context rather than a fictitious manual reboot.
On interruption, resume this exact saved plan only after its controller exits.
Never sign it again or replay native57 into the bootstrap.

Eight copied-state Python tests cover corruption, stale observations, competing
owners, archive-before-commit, the key boundary, and immutable resume evidence.
These tests and QEMU are not proof of physical Wi-Fi or visible city motion.

Actual controller and complete local durable archives live in ignored
`runs/actual-recovery58`. Public source/gate/evidence manifests are committed.
The historical `owner-reboot-city-recovery` packet-plan kind is an existing
compatibility tag; actual reports explicitly keep manual reboot unconfirmed.
