# Rabbit Wireless Program Loader v0

This experiment turns the Dell OptiPlex 3060 USB image into a long-lived loader for
small bounded Rabbit VM programs. A complete scene program
chooses a square or triangle, arbitrary RGB, position, size, movement step, and whether
the arrow keys control it. These are runtime program bytes, not choices compiled into
the USB image.

Each 16-byte BLE service UUID transports one frame:

```
RP | version+type | transfer | sequence | 7-byte payload | FNV-1a-32
```

The Mac repeats `BEGIN`, four `CHUNK` frames, and `COMMIT`. Dell keeps the previous
scene alive until all 24 bytecode bytes arrive in order and both frame and program
checksums pass. FNV is only a corruption check, not authentication. This version
remains bounded because its interpreter exposes no native-code execution, arbitrary
memory write, storage write, pairing, or connection. Dell transmission is limited to
one non-connectable, hash-bound acknowledgement advertised for 1.5 seconds after a
valid commit; passive receive resumes afterward.

## Pre-physical gate

```sh
cd ~/rabbit-stack/experiments/x86-64-uefi-ble-program-loader-v0
python3 verify.py
python3 run_qemu.py
```

QEMU must show `TARGET NOT FOUND; NO DEVICE WRITE SENT`, because it does not
contain the exact physical QCA controller.

The exact v0.2 image reached `STAGE 5` on the Dell, then stopped before the chained
runtime title. That observation localized the failure to the first UEFI call: the
expanded `0x700`-byte frame inverted Microsoft x64 stack alignment because the runtime
is entered by `JMP`. V0.3 changes only that frame to `0x708`, preserving the larger
workspace and restoring the proven 8-mod-16 pre-call relationship.

The v0.3 physical loader proved complete program transfer, four-direction movement,
and hot replacement. V0.4 added the bounded Dell-to-Mac acknowledgement. Its first
physical ACK was received by CoreBluetooth with the correct program hash and counter,
but transfer id `00`: v0.4 had cleared transfer state too early. V0.5 preserves the
transfer id until it is copied into the ACK. Fresh v0.5 QEMU mismatch evidence is now
recorded, so `python3 prepare_physical.py` creates `/tmp/rabbit-vm-loader-v05.img` without writing
any device.

Once installed and booted on the Dell, arbitrary colors can be sent without
moving the USB stick or rebooting:

```sh
python3 send_program.py triangle --rgb 3366FF --x 400 --y 240 --size 96 --step 16
```

Wait for `PROGRAM APPLIED` on the Dell. Dell then advertises the exact program receipt,
the Mac prints `ACK RECEIVED` and exits automatically. Press `Esc` on the Dell to
disable the passive scan and exit the loader.

The Mac sender inserts a quiet 1.8-second receive window after every complete six-frame
transfer. During diagnostics it prints the CoreBluetooth scanner state and every visible
128-bit service UUID, so a missing receipt can be separated from a decoding mismatch.
