# x86-64 UEFI Bluetooth local capabilities v0

This experiment performs the next bounded step after the physical HCI identity result.
One boot sends three local informational commands to the exact Dell controller
`0CF3:E009`:

1. `0x1002` — Read Local Supported Commands (64-byte command bitmap);
2. `0x1003` — Read Local Supported Features (8-byte BR/EDR feature bitmap);
3. `0x2003` — LE Read Local Supported Features (8-byte Bluetooth LE bitmap).

These commands inspect the controller itself. They do not scan the room, advertise,
pair, connect, reset the controller, download firmware, or send Bluetooth radio data.
The Bluetooth Core specification defines all three as local-information commands; the
LE command has been part of the mandatory LE controller interface since Bluetooth 4.0.

## Authority and limits

- exact USB target: `0CF3:E009`, interface `00`, class `E0/01/01`;
- at most 64 USB interfaces and 8 endpoint descriptors per interface;
- exactly three allowed HCI opcodes: `0x1002`, `0x1003`, `0x2003`;
- at most 8 interrupt events per command and 80 bytes per event;
- no controller reset, firmware download, bulk/ACL data, scan, advertising, pairing,
  connection, radio traffic, internal-disk write, or firmware write.

The 80-byte event buffer is intentional: the `0x1002` Command Complete packet contains
a 64-byte bitmap plus the HCI event envelope and therefore does not fit the earlier
64-byte identity buffer.

## QEMU fail-closed gate

Run on the Mac:

```sh
cd ~/rabbit-stack/experiments/x86-64-uefi-bluetooth-local-capabilities-v0
python3 run_qemu.py
```

The command runs every deterministic positive and negative test before starting QEMU.
QEMU has no `0CF3:E009`, so the required result is:

```text
TARGET NOT FOUND; NO HCI COMMAND SENT
```

After that observation is exact-hash-bound, `prepare_physical.py` will verify, build,
hash, and inspect removable media in one command. It will still stop before writing any
device; a fresh exact-device review and explicit authorization remain required.

Reviewed identities:

```text
program SHA-256: 4ad4b42f4a9805a4363d9f36f33e76a4f9ae658c68a2f2e5bdf64300ca80e142
EFI SHA-256:     23ffeb7474d03cec04d139fa18be5e91737c40d254e6411ac8f93a54a45e6b5e
image SHA-256:   006ed8b12843b7d91712764cc4b42462c1e192924d8a1ddb6ae05fa3232336ea
```

Status: **PRE-QEMU; NOT PHYSICALLY INSTALLED**.
