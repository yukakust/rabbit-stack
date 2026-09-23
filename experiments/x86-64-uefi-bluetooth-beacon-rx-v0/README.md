# x86-64 UEFI Rabbit Bluetooth beacon receiver v0

This is the first Rabbit experiment that deliberately uses radio. The Mac advertises
one exact 128-bit service UUID:

```text
52414242-4954-4C45-8000-000000000001
```

The physical Dell enables **passive** Bluetooth LE scanning for at most 20 seconds and
accepts only that UUID. Bluetooth Core specifies that passive scanning only receives
packets and does not transmit scan requests. This experiment does not pair, connect,
advertise from the Dell, exchange ACL data, or write persistent state.

## Exact authority

The Dell image permits this fixed five-command sequence:

1. `0x0C01` — expose the LE Meta event;
2. `0x2001` — expose only LE Advertising Reports;
3. `0x200B` — configure scan type `0x00` (passive), 10 ms interval/window;
4. `0x200C` — enable scan;
5. `0x200C` — disable scan before displaying the result.

Budgets are 8 events while awaiting each Command Complete, then 100 receive attempts of
200 ms and at most 80 bytes per event. Recovery is power-off and USB removal. Active
scan, radio transmit, pairing, connection, controller reset, firmware download, and all
persistent writes are rejected by the Target Pack and verifier.

## QEMU fail-closed gate

```sh
cd ~/rabbit-stack/experiments/x86-64-uefi-bluetooth-beacon-rx-v0
python3 run_qemu.py
```

QEMU has no `0CF3:E009`; it must display:

```text
TARGET NOT FOUND; NO HCI COMMAND SENT
```

No scan is started in QEMU. On 2026-09-23 QEMU 11.1.1 on the Apple Silicon Mac displayed
that exact result for v0.1. The owner-reviewed observation remains bound to the exact
v0.1 identities. V0.2 independently reproduced the same fail-closed result, bound to
its new identities, so `prepare_physical.py` is open for read-only media inspection.

## Mac sender

`run_mac_beacon.py` compiles the reviewed Objective-C source with Apple `clang` into a
temporary executable with an embedded Bluetooth permission description, then advertises
only the exact Rabbit service UUID through CoreBluetooth. Objective-C deliberately
avoids coupling this experiment to the separately versioned Swift compiler and SDK:

```sh
python3 run_mac_beacon.py
```

macOS may request Bluetooth permission for Terminal. Keep the process running while the
Dell boots and scans; stop it afterward with `Ctrl-C`.

Expected Dell success:

```text
RABBIT BEACON RECEIVED
UUID=52414242-4954-4C45-8000-000000000001
NO PAIR; NO CONNECT; NO RADIO TRANSMIT
```

## Physical v0.1 result and v0.2 diagnostic

The physical Dell accepted the complete bounded passive-scan sequence and disabled the
scan after 20 seconds, but did not match the Rabbit UUID. V0.1 did not expose whether
zero advertisements arrived or advertisements arrived without the expected UUID, so it
cannot distinguish sender visibility from parser mismatch.

V0.2 preserves the same five-command authority and adds one bounded diagnostic line:

```text
RX/LE/ADV (HEX)=00/00/00
```

The fields count successful scan-window USB events, LE Meta events, and LE Advertising
Reports. They are two-digit hexadecimal counters (`64` means 100). No packet contents,
addresses, pairing, connection, or new radio authority are added. V0.2 requires its own
QEMU fail-closed observation before physical preparation opens.

Reviewed identities:

```text
program SHA-256: 1df246ea4d9d269603e07510027b8ff0f1d2754fe88eb8fff8123359c5d13aed
EFI SHA-256:     18a098c4168b1679c3d4d11a59d67c0d4ecb917a2f0720e21741bddbb62bc30d
image SHA-256:   bd15cc66ee6340bd0225a4394bd6d754f0b31115b52b4ee6d98a513ac8e90df2
```

Status: **V0.2 QEMU-OBSERVED; NOT PHYSICALLY INSTALLED**.
