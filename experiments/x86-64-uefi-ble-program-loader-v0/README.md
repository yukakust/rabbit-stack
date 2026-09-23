# Rabbit Wireless Program Loader v0

This experiment turns the Dell OptiPlex 3060 USB image into a long-lived,
receive-only loader for small bounded Rabbit VM programs.  The first VM has one
instruction: `SET_SQUARE_COLOR(red, green, blue)`.  The color is data supplied
at runtime; it is no longer one of two values compiled into the USB image.

The 16-byte program is transported as a BLE 128-bit service UUID:

```
RBVM | version=1 | opcode=1 | R | G | B | 000000 | FNV-1a-32
```

FNV is only a corruption check, not authentication.  This version remains safe
because its interpreter exposes no native-code execution, arbitrary memory
write, storage write, pairing, connection, or Dell radio transmission.

## Pre-physical gate

```sh
cd ~/rabbit-stack/experiments/x86-64-uefi-ble-program-loader-v0
python3 verify.py
python3 run_qemu.py
```

QEMU must show `TARGET NOT FOUND; NO DEVICE WRITE SENT`, because it does not
contain the exact physical QCA controller.

After the QEMU evidence is recorded, `python3 prepare_physical.py` creates
`/tmp/rabbit-vm-loader-v01.img` without writing any device.

Once installed and booted on the Dell, arbitrary colors can be sent without
moving the USB stick or rebooting:

```sh
python3 send_program.py set-square-color --rgb FF0066
```

Wait for `PROGRAM APPLIED: SET_SQUARE_COLOR` on the Dell, stop the Mac sender
with `Ctrl-C`, and send another program. Press `Esc` on the Dell to disable the
passive scan and exit the loader.

