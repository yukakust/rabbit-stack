# x86-64 UEFI Bluetooth HCI identity v0

This experiment crosses exactly one new boundary after the physical USB inventory:
it sends one local informational HCI command to the exact Dell controller `0CF3:E009`
and receives its Command Complete event. It does not scan the room, advertise, pair,
connect, download firmware, reset the controller, or send Bluetooth radio data.

The sole opcode is `0x1001`, **Read Local Version Information**. The returned fields are
HCI version/revision, LMP version/subversion, manufacturer, and status. They describe
the local controller, not nearby devices.

The implementation follows:

- [Bluetooth Core 6.2 USB transport](https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Core-62/out/en/host-controller-interface/usb-transport-layer.html): HCI commands use endpoint 0 with `bmRequestType=0x20`; events arrive on interrupt-IN;
- [UEFI 2.10 USB support](https://uefi.org/specs/UEFI/2.10/17_Protocols_USB_Support.html): `UsbControlTransfer` and `UsbSyncInterruptTransfer`;
- [TianoCore UsbIo.h](https://github.com/tianocore/edk2/blob/master/MdePkg/Include/Protocol/UsbIo.h): exact protocol layout and call signatures;
- [Linux btusb](https://github.com/torvalds/linux/blob/master/drivers/bluetooth/btusb.c): independent `0CF3:E009` QCA Rome classification.

## Authority and limits

- exact USB target: `0CF3:E009`, interface `00`, class `E0/01/01`;
- at most 64 USB interfaces and 8 endpoint descriptors per interface;
- exactly one allowed HCI command, opcode `0x1001`;
- at most 8 interrupt events of at most 64 bytes while seeking its response;
- no controller reset, firmware download, bulk data, scan, advertising, pairing,
  connection, ACL traffic, internal-disk write, or firmware write.

## One-command QEMU gate

```sh
cd ~/rabbit-stack/experiments/x86-64-uefi-bluetooth-hci-identity-v0
python3 run_qemu.py
```

The command first runs all deterministic positive and negative checks and only then
starts QEMU. QEMU has a USB keyboard but no `0CF3:E009`, so the required screen is:

```text
TARGET NOT FOUND; NO HCI COMMAND SENT
```

This proves the image fails closed on a different machine. It cannot prove the physical
HCI exchange. Photograph the QEMU screen and press any key.

Reviewed identities:

```text
program SHA-256: 63c54bfbc690a5af5094c5cc393fadbd1626071a5cc104cec215784bf01702aa
EFI SHA-256:     b7da72b8fa450e047c9f6d69c0879c394aa7274ba28b8643813885186d9485fe
image SHA-256:   c5658d3edf41028089f72d2be324c12dddbaad1b3f0c037930a1d81bd91ec8de
```

Status: **BUILT-PRE-QEMU**. `prepare_physical.py` remains locked until exact QEMU evidence
is added. Physical USB replacement will still require a fresh removable-device identity
and explicit owner authorization because this artifact introduces one real USB command.
