# x86-64 UEFI USB / Bluetooth probe v0

This experiment decides whether a nearby Bluetooth link can become Rabbit's first live
wireless transport without assuming that the Dell exposes a usable Bluetooth controller.
It boots without Windows or Linux and uses only the standard UEFI USB I/O protocol to:

1. enumerate at most 64 firmware-present USB interfaces;
2. read each device and interface descriptor;
3. display vendor/product IDs and device/interface class triples;
4. label standard Bluetooth class `E0/01/01` as `BT=YES`.

The implementation follows UEFI 2.10 `EFI_USB_IO_PROTOCOL` and TianoCore's `UsbIo.h`.
It calls only `UsbGetDeviceDescriptor()` and `UsbGetInterfaceDescriptor()`. It contains
no USB bulk/interrupt/control data-transfer call, port reset, Bluetooth HCI command,
pairing, radio transmit, configuration write, storage read, or persistent mutation.

References:

- <https://uefi.org/specs/UEFI/2.10/17_Protocols_USB_Support.html>
- <https://github.com/tianocore/edk2/blob/master/MdePkg/Include/Protocol/UsbIo.h>
- <https://github.com/tianocore/edk2/blob/master/MdePkg/Include/IndustryStandard/Usb.h>

Verify and emulate first:

```sh
cd ~/rabbit-stack/experiments/x86-64-uefi-bluetooth-probe-v0
python3 verify.py
python3 run_qemu.py
```

QEMU contains a USB keyboard for a negative classification check. It does not model the
Dell's Bluetooth hardware, so `BLUETOOTH CANDIDATES: 00` is acceptable there. The screen
must show at least one described USB interface and must not label the keyboard as
Bluetooth. Photograph the screen, then press any key.

Build the physical candidate without writing a device:

```sh
python3 build_image.py \
  --output /tmp/rabbit-bluetooth-probe-v01.img \
  --report /tmp/rabbit-bluetooth-probe-v01.json
```

Reviewed identities:

```text
program SHA-256: 1a716bd0f4f7a9eeee3b2b5cdcca2b1ecc460933d02bc33c8802d04bc142a0ce
EFI SHA-256:     9c143212037c6368187f4daecf09b360a8f6d1689146a1e2c7ef7ae9706c1c34
image SHA-256:   15bc2c6e19236bbb0a1f2823eda0ab89f55a93b51b682d81e53e85db8e5d69a2
```

Status: **BUILT-NOT-INSTALLED**. A QEMU observation is required before any fresh device
identification, explicit physical-write authorization, or Dell execution.

The result is a routing decision, not Bluetooth support. `BT=YES` opens a staged BLE
bridge path; zero candidates sends the project back to the observed QCA9377 Wi-Fi path.
