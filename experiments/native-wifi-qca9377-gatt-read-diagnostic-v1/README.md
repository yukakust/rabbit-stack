# Known-peer GATT read diagnostic (Mac only)

Purpose: distinguish discovery failures from ATT read failures without changing
the frozen firmware sender, signed packets, Dell driver, or saved world state.
The helper connects only to the saved Rabbit peripheral UUID, discovers one
requested service, and reads one public value. It has no write, notification,
signing, key-loading, or firmware-activation API. Its timeout is 60 seconds.

Modes: `asset` (RAM receipt), `receipt` (ordinary file status), `prefix`
(prefix57 diagnostic status). ROOT must hold the existing `state.lock` across
each invocation and confirm all previous controllers have exited. Compile using
Foundation/CoreBluetooth and the existing FileSender-Info.plist. Generated
executables stay in ignored `runs/`.

Actual physical evidence is under `evidence/2026-10-07/physical57-handle-failure`.
Phase1 discovered all services; phase2 used targeted discovery. Both exact
source snapshots and raw callback logs are retained. Cached service lists do
not establish which driver currently runs on Dell.

Result: asset read failed with CBATTErrorDomain/code1 (Invalid Handle), ordinary
file status was a complete zero-session IDLE RFS1, and targeted prefix57 service
discovery found no service. Ten firmware chunks had been acknowledged earlier,
but continued same-boot RAM ownership is now unproven. Stop automatic retries;
preserve pending sessions and counters. A photo of the current Dell screen is
needed to distinguish a watchdog/reset screen from the expected live overlay.
No reboot, pending-session retirement, driver replay, or signature is authorized
by this diagnostic result. Wi-Fi/IP remain unconfirmed.
