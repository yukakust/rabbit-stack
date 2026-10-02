# Connected file transport v1 — host-verified core, NOT installed

This experiment is the connected-channel replacement for six-byte advertising
frames. It is NOT a working end-to-end Dell Bluetooth implementation yet. No image
or owner-native release is generated and no physical/radio action is performed.

Implemented:

- Portable, allocation-free bounded C file receiver (max 65,535 signed world bytes).
- Small fixed-channel ATT/GATT server: MTU exchange (23..247), primary service and
  characteristic discovery, acknowledged writes, status Read/Read Blob, errors.
- SHA-256, ordered offsets, exact duplicate acceptance, explicit abort, same-boot
  reconnect/resume, final receipt retry without repeating application.
- Exact signed RUP2/RUP3 world bytes. The apply callback MUST perform signature,
  counter, geometry/opcode bounds and health checks before atomic commit.
- Mac CoreBluetooth central source: connect, discover, acknowledged writes,
  offset resume and final SHA256/session/counter receipt comparison. Mac
  compilation and physical interoperability remain UNVERIFIED.
- Preparation-only Python adapter. It never sends or compiles a native release.

Twelve host tests call the actual existing freestanding C world validator, health
check and renderer, including the detailed four-frame cat. They check corruption,
signature and health rejection preserving the previous world, replay, disconnect,
idempotence, 3,000 deterministic malformed ATT PDUs and output/framebuffer guards.
These are host tests, NOT QEMU Bluetooth evidence or measured throughput.

## Lower link layer added — still not an installable supervisor

`hci_link.c` now implements sequential controller setup, connectable service
advertising, connection/disconnection events, real controller buffer queries
(including shared-buffer fallback), outbound ACL credits, bounded fragmentation,
inbound L2CAP reassembly and USB byte-stream deframing. ATT is routed through the
existing GATT/file core. Pairing is explicitly rejected, not silently enabled.
Host tests carry the exact 33,349-byte signed cat through simulated connected ACL
traffic into the actual C signature/health/renderer. No 450ms dwell is used.

`usb_port.c` is a candidate UEFI adapter: read-only exact USB identity/interface and
endpoint discovery, finite control/interrupt/bulk transfers, bounded output batches,
and shutdown requiring matching advertising-off/disconnection events. Failed
cleanup retains an unknown/bound state, never claims OFF. No asynchronous USB
callbacks are installed. Its MinGW object compiles; four mock-UEFI tests check
identity rejection, endpoint/ambiguity failures, handle release and cleanup proof.
The adapter must be called by the NEW sole-owner supervisor, with a monotonic clock
feeding `rl_elapsed`. It MUST NOT be launched alongside the old loop.

```sh
python3 verify_link.py  # 21 cases, including the 12 prior file/GATT tests
python3 verify_usb.py   # 4 mock-UEFI cases, no real USB
```

Owner approved one future bootstrap installation, NOT a write to an unidentified
disk. Do not install a fixed GATT-only image just to go fast: it would recreate the
current update boundary. Release gates required before that migration:

1. Sole-owner supervisor loop with validated module event/ACL/tx callbacks.
2. Owner-authenticated updates for combined engine/radio drivers, distinct from the
   public world signer; unhealthy trials retain old world and driver.
3. Callback quiescence, confirmed radio cleanup before unload, watchdog/Esc handling.
4. Two tested driver swaps, recovery baseline, deterministic owner-local build and
   exact local QEMU gate before any physical installation.
5. Mac compilation, Dell interoperability and measured throughput.

No bootstrap/native image is built by these tests, no measured speed is claimed.

## Installed supervisor integration boundary

The installed supervisor's assembly independently consumes USB HCI interrupt events.
Scene ABI 2 exposes only init/tick/frame/snapshot/receipt/counter and a pixel surface,
not an HCI event queue or an exclusive radio-owner handoff. Non-advertising LE events
(including connection/disconnection/ACL credits) are consumed and ignored by the
legacy loop. USB bulk ACL reads alone do not solve this event ownership problem.

Connecting a second event reader or installing an asynchronous interrupt transfer
without a tested takeover/cancel/cleanup mechanism is NOT a reviewed workaround.
This experiment deliberately supplies no such live adapter or send command. A
privileged module can access UEFI services, but this is not evidence that concurrent
ownership is safe or that rollback removes every callback or radio side effect.

The previously missing link/USB layers now have candidate code and synthetic tests,
NOT hardware evidence. Remaining: exclusive supervisor integration, complete
timeout/disconnect/Esc recovery, Mac compilation and Dell interoperability.
The existing owner-native updater replaces Scene drivers, not the immutable
supervisor/radio loop. A supervisor ABI change may require a separately approved
bootstrap installation; no "last USB ever" promise. Fresh medium identity, exact
owner build/QEMU/recovery gates and explicit write approval remain mandatory.

## Protocol

Service UUID `52414242-4954-4649-8000-000000000001`.
Characteristic UUIDs share that prefix, ending 2=control, 3=data, 4=status.
Fixed handles: 1 primary service; 2/3 control declaration/value; 4/5 data; 6/7 status.
This is a bounded experimental ATT subset, not a complete certified GATT stack.

| Operation | Value (all integers little-endian) |
| --- | --- |
| BEGIN on control | `01 01 01 00`, 8-byte session, 4-byte stream length |
| Data write | 4-byte offset, consecutive stream bytes |
| COMMIT on control | `02`, 8-byte session |
| ABORT on control | `03`, 8-byte session |
| Stream | SHA256 of signed package (32 bytes), exact signed package |
| Status (60 bytes) | `RFS 01`, session[8], received:u32, length:u32, state:u8, error:u8, zero[2], applied counter:u32, SHA256[32] |

States: 0 idle, 1 staging, 2 applied, 3 rejected. Errors: 1 SHA mismatch,
2 signature/bounds/counter/health/apply failure. ATT Write Response is NOT a final
application receipt. The Mac requires the exact final status identity. Read Blob
supports receipt reads even at default MTU. A disconnected bearer resets MTU but
retains staging in the same process/boot. Reboot loses it, with no hidden persistence.

At default MTU, each acknowledged write carries 16 useful stream bytes; MTU 247
permits 240. There is no artificial 450ms per-frame dwell. Actual throughput depends
on the eventual hardware adapter, negotiated link and round trips; no timing is claimed.
World integrity/authenticity is independent of link encryption. This version does
not implement pairing, confidential transport, owner authentication or native-file
execution; unauthenticated peers can still cause denial of service. Never use the
public development world signer as the owner-native key.

## Reproduce locally (no radio)

Python requires the repository's existing `cryptography`; C compiler required.

```sh
python3 verify.py
python3 prepare_transfer.py \
  ../x86-64-uefi-god-runtime-v3/worlds/ginger-cat-walk-v1.json \
  --counter 2 --output runs/cat-session.json
```

The saved bundle keeps a stable nonce for same-boot resume. Do NOT execute
`mac_file_sender.m` or start this candidate against Dell: the service is not installed.

Primary specifications used:
[Bluetooth ATT](https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Core-54/out/en/host/attribute-protocol--att-.html),
[Bluetooth GATT](https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Core-60/out/en/host/generic-attribute-profile--gatt-.html),
[UEFI USB protocol](https://uefi.org/specs/UEFI/2.11/17_Protocols_USB_Support.html),
[EDK II USB I/O definitions](https://github.com/tianocore/edk2/blob/master/MdePkg/Include/Protocol/UsbIo.h).
