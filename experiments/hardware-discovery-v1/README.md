# Hardware discovery v1 — read-only inventory and proposed USB plan

This experiment prepares U6 without touching physical hardware. It validates canonical
inventories, matches them against the first x86-64 UEFI USB Target Pack, and produces a
non-executable installation proposal.

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

This does not prove support for a real computer and does not create or write a bootable
image. When a candidate old computer is available, its facts must be collected read-only
and represented as a new inventory. Installation requires a later, separate authorization.
