# x86-64 UEFI network probe v0

This is the first concrete step toward sending live `.rabbit` packages to the Dell over
Wi-Fi. It does **not** connect to a network yet. It answers the two questions that must
come first without guessing:

1. Which network controllers are physically present, identified by PCI vendor/device
   and subclass numbers?
2. Does the Dell firmware already expose UEFI Simple Network or either standardized
   UEFI Wi-Fi protocol?

The probe boots without Windows or Linux, clears the UEFI text screen, prints protocol
availability, scans PCI segment 0 for base class `02` (network controller), and displays
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
Wireless MAC v2. For PCI it writes only the configuration **address selector** port
`0xCF8`, then reads data from `0xCFC`; it never writes configuration data, sends a packet,
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

On 2026-09-22 the owner observed `SIMPLE NETWORK: YES`, both UEFI Wi-Fi protocols as
`NO`, and the single emulated controller `8086:10D3` at `00:02.0`. This proves that the
probe and its formatting work under QEMU; it says nothing yet about the Dell's physical
controllers. Exact-bound evidence is in `evidence/qemu-macos-arm64-observed.json`.

Build the physical candidate without writing a device:

```sh
python3 build_image.py \
  --output /tmp/rabbit-network-probe.img \
  --report /tmp/rabbit-network-probe.json
```

Reviewed identities:

```text
program SHA-256: da81a6f725fcc259403e3658c6c4d1f6b5b7b6fecceebf6d88711cbad2add831
EFI SHA-256:     d48db92f82e10642f980906379d4dd11db20f51754d46886f3ca35cb9b8efd8f
image SHA-256:   a6a34c676d6772cfd378397e312f4d99faf4a233b8a20307420503864fc35598
```

Status: **QEMU-OBSERVED-NOT-PHYSICALLY-INSTALLED**. A physical USB rewrite still
requires fresh device identification and explicit authorization.
