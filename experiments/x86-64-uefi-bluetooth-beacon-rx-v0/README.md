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
that exact result. The owner-reviewed observation is bound to the exact probe, target,
program, EFI, and image identities. `prepare_physical.py` is now open: it builds and
inspects the removable target without writing it.

## Mac sender

`run_mac_beacon.py` compiles the reviewed Swift source into a temporary executable with
an embedded Bluetooth permission description, then advertises only the exact Rabbit
service UUID through CoreBluetooth:

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

Reviewed identities:

```text
program SHA-256: 0aa77e83498e57bb3dc6554e9e5750ec9a12b42f5fa0a4d76f6c9c86ccf0465f
EFI SHA-256:     8b9df03b61e21319c1d0329d185b080d17962a1b3763424ddb0d6ddc98c62840
image SHA-256:   0fa4c4ce888d9a2ba916898f1ab43f579b92b52553d7f6a96b44fabddc2dd50c
```

Status: **QEMU-OBSERVED; NOT PHYSICALLY INSTALLED**.
