# Offline persistent native bridge

This derives the checked `wmi-native-v3` CE3 path without editing that source.
It changes the actual native full-probe success path: after a real INIT TX
completion and validated WMI READY, it retains the same fourteen mappings,
firmware pin, PCI/wake/link/IRQ and adapter lifetime instead of automatically
ending the diagnostic. Each cooperative poll performs bounded fresh guards;
there are no sleeps or new allocations. No synthetic READY exists in production.

`persistent.c` binds these real objects to the earlier pure lifecycle policy.
The existing operating guard proves BMI0/1 and CE2; this bridge additionally
checks exact CE3/4 channel routes and both actual CE7 diagnostic routes,
descriptor addresses and sizes. A startup/operating guard failure immediately
revokes persistent admission even when the full probe already began cleanup.

An explicit local `qca_stop` blocks admission before running the existing
all-eight-engine stop and cleanup. Fresh BME-off/all-eight stop proof and IRQ
enable/cause readback establish the release gate. Release is observed before
the first unmap; final proof is observed after actual outer PCI closure and
firmware unpin. The bus field represents the retained adapter lifetime, not
the hardware bus-master bit. Once PCI is closed, no further hardware read is
attempted; the earlier verified stop is latched under sole-adapter ownership.

The unchanged full-probe stop path caches cancellation as stage6/error8448.
That is distinct from the already confirmed INIT and successful persistent
lifetime. The tests do not relabel cancellation as legacy diagnostic success.
Faulted lifecycle policy stays `RETAINED`; any later independent all-owner
release must use the existing adapter proof and a reviewed recovery policy.

## Scope and remaining gates

- There is no persistent RX/credit pump, station VDEV, scan, association, WPA,
  DHCP, RF transmission or credential access here. “Active” means retained and
  guarded radio ownership; it is not a connected station or command-complete
  station runtime. An RX pump is required before integrating station traffic.
- The derived source keeps the previous counter50/policy solely as an offline
  reference. There is **no assigned new generation, payload-signing route or
  hardware admission**. Do not sign or deploy this derivation as counter50.
- No full EFI payload, repeated EFI/QEMU/current-world checks or physical run
  is claimed. Freestanding COFF verifies the bridge and actual derived probe
  compile; the ASAN fixture exercises actual native entrypoints with simulated
  PCI/CE/DMA. Signing admission must add a reviewed new generation and exact
  source closure, repeated whole-driver builds, QEMU and current-world gates.
- Physical persistent status needs a separate read-only telemetry envelope and
  an authenticated stop path. Existing stage values alone cannot distinguish
  active radio from a diagnostic still in progress.
- Native unload must use actual all-owner proof. World-only updates need a
  separate persistent-owner state so a healthy radio does not block all world
  changes. Do not clear a retained owner state to bypass that requirement.

## Reproduce

Run `python3 verify_native.py` on Yukabox in the repository-shaped isolated
mirror. It uses the existing pinned compiler and pinned firmware. The fixed
test signing seed belongs solely to the simulated asset fixture; the real
owner key is never accessed. The mirror borrows existing Monocypher sources
read-only and never writes the main remote source tree.

Tests cover all22 actual startup outcomes, retain200 active ticks for each
successful INIT, explicit checked stop/all14 release, and five faults after
successful readiness: CE3 ring corruption, invalid payload mapping, poisoned
firmware, wrong CE3 route and clock rollback. Production guards must catch the
fault and revoke admission before the next operation.
