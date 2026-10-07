# Provisional native53: bounded persistent RX trial

This offline candidate combines the native52 minimum-prefix READY parser,
reviewed persistent ownership bridge and bounded RX pump. Public owner/target/
firmware identities are unchanged; the root reserved counter53 provisionally.
There is no signing/admission route here, and native52 physical success is not
assumed. Do not deploy merely because a host build passes.

After actual INIT TX completion and parsed READY, the trial retains all14 mapped
buffers and the firmware/PCI/IRQ/wake/link owners. It services RX1/RX2 for ten
seconds using cooperative bounded polls. Normal expiry calls the existing
checked `qca_stop` once; all-eight CE stop, BME-off, flush/unmap/free, IRQ/PCI
closure and firmware unpin remain prerequisites for release. Clock rollback,
ownership loss and malformed RX also request checked stop. A timeout alone
never proves release. There are no station, scan, RF, credential or IP commands.

The timer itself never touches hardware. Stop is requested by the derived
native entrypoint. Existing full-probe cancellation caches stage6/error8448;
new trial telemetry independently distinguishes successful READY, bounded
runtime, a normal expiry, retained faults and actual owner release. Faulted
lifecycle policy can remain RETAINED even after the existing adapter proves
every real owner released; recovery/admission must evaluate both facts.

## Read-only telemetry

UUID service `52414242-4954-4649-8000-000000000028`, characteristic ending0029,
ATT handles29..31. `QWRX0001` is192 bytes: eight magic bytes and46 little-endian
u32 values listed in `decode_profile.py`. It reports timer/lifecycle/RX phase,
errors, polls, FIFO/backpressure, actual owner counts, cached READY/TX completion
and the common credit ledger. Generation53 is a constant profile identity, not
device attestation. Reads have no MMIO or state mutation; writes are rejected.
There are no secrets, event payloads or credentials in this telemetry.

`actual_owners_released` is the actual adapter/port/pin inventory, distinct from
the pure lifecycle's logical state. A successful bounded trial requires normal
expiry, cached validated READY/TX completion, no timer/bridge/lifecycle error and
complete actual release. No receipt or QEMU result is a physical scene check.

## Verification and next admission

Run `verify_native.py` and `verify_candidate.py` only on Yukabox in the isolated
`parallel-persistent-profile-v1` repository-shaped mirror. Native host models
use only a fixed simulated signing owner; no real owner key is accessed.
The model covers normal ten-second expiry, timer clock rollback, earlier finite
expiry, five owner faults and13 RX cases, with actual native entrypoints and
all14 release. This remains simulated PCI/firmware evidence.

Whole-driver verification builds exact EFI bytes repeatedly, checks wire/mapped
bounds, runs the real supervisor in QEMU with normal and empty boot, preserves
city/GATT/restoration/rejection checks and validates the frozen world17 package
`47d63aa6e81b35fc355005cf65f889b9c43bc332443e37ddbba672b920c2fc2b`.
It records inherited source closure and exact derived compiler inputs.

Still required before hardware: actual native52 result and all-owner release,
reviewed counter53 admission and source closure on the Mac, deterministic
admission negative tests, exact local signing and delivery by the sole hardware
controller, then fresh QWBT/QWIN/QWRX observations plus physical city visibility.
RX dispatcher, station commands, regulatory/scan/association/WPA, HTT data,
DHCP/IP and confidential credential provisioning are not implemented here.
