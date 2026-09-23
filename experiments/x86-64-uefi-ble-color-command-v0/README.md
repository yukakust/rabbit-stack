# UEFI BLE color command v0

This is the first Rabbit runtime whose visible state can change from the Mac without
moving the boot USB or rebooting the OS-less Dell.

The Dell boots once, initializes the exact QCA Rome `0CF3:E009` controller in volatile
RAM, draws a centered yellow `128 x 128` square through UEFI GOP, and opens a bounded
passive BLE receive window. It recognizes exactly two service UUIDs:

```text
BLUE   52414242-4954-4C45-8000-000000000002
YELLOW 52414242-4954-4C45-8000-000000000003
```

Everything else is ignored. The receive window lasts at most 120 seconds and closes
early after both commands have been observed. Scan disable is mandatory. The Dell does
not actively scan, advertise, pair, connect, or transmit radio data. It writes no disk
or firmware state; QCA setup exists only in controller RAM until power-off.

## Mac gate and candidate preparation

```sh
cd ~/rabbit-stack
git pull --ff-only
cd experiments/x86-64-uefi-ble-color-command-v0
python3 verify.py
python3 run_qemu.py
```

Expected QEMU result: `TARGET NOT FOUND; NO DEVICE WRITE SENT`, because QEMU does not
have the exact physical QCA controller. Close the QEMU window, then prepare the physical
candidate and inspect the exact external disk identity:

```sh
python3 prepare_physical.py
```

This creates `/tmp/rabbit-ble-color-command-v03.img` but does not write any device.

## Physical interaction

After the reviewed image is installed on the dedicated Rabbit USB, start one sender on
the Mac before booting the Dell:

```sh
python3 run_mac_command.py blue
```

Boot `UEFI: KingstonDataTraveler Duo`. When Dell reports `COMMAND BLUE RECEIVED`, stop
the sender with `Ctrl-C` and immediately run:

```sh
python3 run_mac_command.py yellow
```

Expected physical result: the square changes yellow → blue → yellow, then the Dell
reports that both commands were verified and disables scanning. No USB movement or Dell
reboot occurs between the two commands.
