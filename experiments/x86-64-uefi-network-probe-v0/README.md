# x86-64 UEFI network probe v0

This is the first concrete step toward sending live `.rabbit` packages to the Dell over
Wi-Fi. It does **not** connect to a network yet. It answers the two questions that must
come first without guessing:

1. Which network controllers are physically present, identified by PCI vendor/device
   and subclass numbers?
2. Does the Dell firmware already expose UEFI Simple Network or either standardized
   UEFI Wi-Fi protocol?

The probe boots without Windows or Linux, clears the UEFI text screen, prints protocol
availability, asks firmware for the handles of PCI devices that actually exist, filters
base class `02` (network controller), and displays
lines such as:

```text
UEFI SIMPLE NETWORK: YES
UEFI WIFI v1: NO
UEFI WIFI v2: NO

PCI NETWORK CONTROLLERS:
B=00 D=1F F=6 VEN=8086 DEV=15BC SUB=00
TOTAL: 01
```

The numbers above are only an example, not a prediction for the Dell. Photograph the
actual screen. `SUB=00` means Ethernet; `SUB=80` commonly identifies another network
controller such as Wi-Fi, but the vendor/device pair is what selects a concrete driver.

The machine code calls UEFI `LocateProtocol()` for Simple Network, Wireless MAC v1, and
Wireless MAC v2. For PCI v0.2 uses `LocateHandleBuffer()`, `HandleProtocol()`,
`EFI_PCI_IO_PROTOCOL.Pci.Read()`, and `GetLocation()`, then frees the temporary handle
buffer. It never probes absent buses, writes PCI configuration data, sends a packet,
joins Wi-Fi, reads storage, or changes firmware.

Verify and emulate first:

```sh
cd ~/rabbit-stack/experiments/x86-64-uefi-network-probe-v0
python3 verify.py
python3 run_qemu.py
```

QEMU includes an emulated Intel `e1000e` controller so at least one PCI network line is
expected. UEFI protocol availability depends on the bundled TianoCore drivers. Press any
key after recording the screen.

On 2026-09-22 the owner observed v0.1 under QEMU: `SIMPLE NETWORK: YES`, both UEFI Wi-Fi protocols as
`NO`, and the single emulated controller `8086:10D3` at `00:02.0`. This proves that the
original probe and its formatting worked under QEMU. On the Dell, however, v0.1 remained
on a dark screen for multiple minutes because it attempted every possible PCI bus.
Power-off and USB removal recovered safely; no inventory was claimed. v0.2 replaces that
algorithm with bounded firmware-handle enumeration and therefore requires a fresh QEMU
observation before another physical write.

Build the physical candidate without writing a device:

```sh
python3 build_image.py \
  --output /tmp/rabbit-network-probe.img \
  --report /tmp/rabbit-network-probe.json
```

Reviewed identities:

```text
program SHA-256: 1ee59aedd97ad54b02ceffb2422173fb831dcc83e5decea3aaefddc12c203abc
EFI SHA-256:     3711e4dac38dab0b9f7580da3f4166f5cc5fce31a3720eea6dedcb6e840820aa
image SHA-256:   d9718a582019fc7d82cd3f87048471138d450d62422ccbbf526910372a60ce5e
```

Status: **V0.2-BUILT-NOT-INSTALLED**. QEMU observation must be repeated. A physical USB
rewrite still requires fresh device identification and explicit authorization.
