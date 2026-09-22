# Hardware discovery v1 — read-only inventory and proposed USB plan

This experiment validates canonical inventories, matches them against the first x86-64
UEFI USB Target Pack, and produces a non-executable installation proposal.

The real read-only inventory in `inventories/dell-optiplex-3060-observed.json` records
the firmware screens reviewed on 2026-09-22. It contains no Service Tag or Express
Service Code. The machine has an x86-64 Core i5-8500T, 8192 MiB RAM, UEFI, working HDMI
firmware output, working USB keyboard input, enabled USB boot, enabled front/rear USB,
and no installed M.2 storage. Secure Boot was enabled and the purchased USB device was
not inserted during discovery.

The reviewed v0 target therefore rejects this exact snapshot with two explicit reasons:

```text
secure-boot-state-unsupported
suitable-removable-media-missing
```

This is successful discovery, not a failed experiment. No firmware setting was changed,
no device was written, and the matcher did not silently weaken the boot policy.

The proposal is deliberately marked:

```text
status: PROPOSED
installation_authorized: false
executable: false
writes_performed: []
artifact.status: UNBUILT
```

It permits only a named removable device, explicitly forbids discovered internal disks,
contains no firmware or security changes, and recovers by powering off and removing USB.

Run the simulated conformance suite:

```sh
cd experiments/hardware-discovery-v1
python3 verify.py
```

This does not prove physical execution and does not create or write a bootable image.
Building an artifact, identifying the removable device on the Mac, authorizing its
erasure, and changing any boot-security setting belong to later, separate U7 decisions.
