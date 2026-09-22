# x86-64 UEFI network probe v0

This is the first concrete step toward sending live `.rabbit` packages to the Dell over
Wi-Fi. It does **not** connect to a network yet. It answers the two questions that must
come first without guessing:

1. Which network controllers are physically present, identified by PCI vendor/device
   and subclass numbers?
2. Does the Dell firmware already expose UEFI Simple Network or either standardized
   UEFI Wi-Fi protocol?

The probe boots without Windows or Linux, preserves the existing UEFI text screen, prints protocol
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
algorithm with bounded firmware-handle enumeration. The owner then reproduced the same
`SNP=YES`, Wi-Fi v1/v2=`NO`, `8086:10D3` result under QEMU with the exact v0.2 image.
On physical Dell, v0.2 still remained dark before even its title was visible. This moves
the suspected failure earlier than PCI enumeration. V0.3 removes `ClearScreen()` and
prints explicit `STAGE 1`, `STAGE 2`, and `STAGE 3` markers before each subsystem.
On 2026-09-23 the owner observed the exact v0.3 image in QEMU: all three stages were
visible, Simple Network was `YES`, both Wi-Fi protocols were `NO`, and the emulated
controller was `8086:10D3`. This opens the separately authorized physical diagnostic
gate; it does not yet identify the Dell controller or prove that `ClearScreen()` caused
the earlier dark display.

The exact v0.3 image was then written and verified, but the Dell again remained dark
before `STAGE 1`. Removing `ClearScreen()` therefore did not fix the physical failure.
Review exposed a concrete x86-64 UEFI ABI violation instead: `print_ascii` called the
firmware from a nested helper without reserving the mandatory 32-byte shadow space and
restoring 16-byte pre-call stack alignment. QEMU tolerated it; Dell firmware is allowed
not to. V0.4 adds `sub rsp, 0x28` / `add rsp, 0x28` around that nested firmware call.
This is a strong, testable cause hypothesis, not yet a confirmed physical diagnosis.

Build the physical candidate without writing a device:

```sh
python3 build_image.py \
  --output /tmp/rabbit-network-probe.img \
  --report /tmp/rabbit-network-probe.json
```

Reviewed identities:

```text
program SHA-256: ab444601b3976fc39764d7e25b8c464676f294eb62b0c65d601fe52e893d98de
EFI SHA-256:     2ef0a4b872e9879769090195792de840fc8a7f53282fd5931f13b5ccf48edd2c
image SHA-256:   cef4a46e3e3c73445f480cab1f19efc195163831f2423fb3aa7e63ed325614b4
```

Status: **V0.4-BUILT-NOT-INSTALLED**. It must pass a fresh QEMU gate because historical
v0.3 evidence cannot approve changed machine bytes. Another physical USB rewrite still
requires fresh device identification and explicit authorization.
