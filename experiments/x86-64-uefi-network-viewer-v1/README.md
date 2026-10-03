# UEFI network viewer v1 — isolated prototype

Owner request: Yukabox in Poland renders Unreal; the mini-PC Dell in Georgia
receives the image over the Internet and presents it on its attached monitor.
Mac is the command point. Preserve the native city and its engine as a district.

Implemented: a bounded authenticated RGB/RLE frame decoder and a standalone UEFI
receiver using the mature iPXE Ethernet/DHCP/HTTP stack. Builds, fixture server,
UEFI QEMU and sanitizer tests run on Yukabox. No physical Dell installation,
owner signing, Bluetooth transfer, disk/USB/firmware write or reboot was performed.

## Evidence and falsifiable claim

Baseline: OVMF with RTL8139 and its option ROM disabled exposes no SNP or TCP4
service, even after ConnectController. Loading the pinned iPXE Realtek driver
creates SNP, but does **not** create TCP4. Its usual LoadFile method is a boot
entry, not a general HTTP client. Rabbit's small source adapter exposes iPXE's
existing asynchronous Download protocol plus a cooperative DHCP job on the driver
image handle. Each Download.Poll invokes one iPXE step; no new TCP/IP stack.

Claim: a real Unreal frame can reach an OS-free UEFI VM through that stack, be
authenticated/decoded and appear pixel-exactly in a separate rectangle, while a
neighbouring region survives; malformed input and cancellation preserve accepted
state; after close/unload the NIC service disappears.

Evidence in `evidence/2026-10-04`: actual QEMU serial log, checked report, build
hashes, server input/request log, screenshot and 293 C checks with ASan/UBSan.
The input is the already verified Unreal5.8.3 Radeon890M frame, SHA256
`6e4f9de0d26ce77975c08e40a6bbd8f599e1c8f930dc6e020af005b580b24e21`.
The left region is a green test fixture, **not the native city**. QEMU's NIC is
RTL8139, **not the physical RTL8168**. No physical display/Internet streaming,
continuous Unreal capture, FPS target, H264/WebRTC or shared 3D compositor is
claimed. This is a saved rendered frame, fetched multiple times with test counters.

## Portable frame contract

`RPF1`: 64-byte little-endian header, bounded pixel body, 64-byte Ed25519 signature
over the entire header+body. Header offsets:

| Offset | Field |
| --- | --- |
| 0 | ASCII RPF1 |
| 4 | version1, codec1 RGB24 or codec2 RLE |
| 6 | header size64, u16 |
| 8 / 10 | width / height, u16, each nonzero, max640×360 |
| 12 | body byte length, u32 |
| 16 | strictly increasing sequence, u64 |
| 24 | session stream ID,16 bytes |
| 40 |24 reserved bytes, all zero |

RGB24 is packed R,G,B. A run is nonzero u16 count followed by three RGB bytes;
runs must sum exactly to width×height. No padding/trailing data. Max230400pixels,
1152128wire bytes. Bounded wire+output staging needs2073728bytes, allocated by the
caller; `frame_core` has no allocator/static framebuffer. It validates the entire
body and signature before writing pixels or state. Errors preserve both.

Production stream ID/public key must be bound to a district/session by an owner-
checked profile, with fresh session identity on reset. A hash alone is not
authentication. This experiment uses an intentionally PUBLIC zero-seed fixture;
it has no deployment authority. A remote frame key must never become the owner
code-signing key. Image authority is limited to pixels; it cannot change city data
or authorize native executable updates. These limits still need implementation
in the integrated native profile; this standalone privileged app is not a sandbox.

## Reproduce on Yukabox

Copy this source directory to `/home/yuka/rabbit-world/dell-network-viewer-v1`.
Run there, in sequence:

```sh
python3 fetch_dependencies.py
python3 verify_host.py --output runs/host
```

Start the test server in a separate terminal; it binds only127.0.0.1:9783 and has
no world/control write API:

```sh
python3 frame_server.py --image /home/yuka/rabbit-world/unreal-yukabox-v1/logs/smoke-nah3Obxq/frame.png --output frame-server-evidence
```

After `FIXTURE READY`, build/run from the source directory:

```sh
python3 build_efi.py --source efi_receiver.c --out receiver.efi
python3 run_probe.py --efi /home/yuka/rabbit-world/dell-network-viewer-v1/receiver.efi --output /home/yuka/rabbit-world/dell-network-viewer-v1/runs/receiver --receiver
```

The runner uses a temporary virtual FAT directory, private OVMF variable copy,
QEMU slirp and QMP screenshot. It never opens a physical device. It checks receipt
markers, exact displayed RGB hash, neighbour pixels, cancellation/replay and NIC
removal; process exit0 alone is insufficient. Stop the fixture server afterwards.
The fixed build timestamp is0; no fresh-clean dependency reproducibility claim yet.
UE's installed Linux Clang/LLD is used for COFF. Binaries/vendor/generated headers
remain ignored. Source adapter patches are idempotent and reject unknown edits.

Dependencies: [iPXE](https://github.com/ipxe/ipxe) commit
`6262f1081fe185564e8ec8365a1d23597ec6e6f5`, Realtek driver containing10EC:8168 and
10EC:8139 IDs; [EFI driver build target](https://ipxe.org/appnote/buildtargets).
iPXE driver/adaptations use GPL2-or-later; keep upstream COPYING and source patch.
EFI imported headers carry their BSD/BSD-2-Clause-Patent notices. Monocypher4.0.3
is pinned/hash-checked by `crypto-provenance.json`, BSD2 or CC0; retain fetched
`vendor/monocypher-LICENCE.md`. No proprietary engine source/binary is distributed.

## Loading, recovery and remaining integration

Current load/recovery is **VM only**: EFI receiver loads the child driver from its
own bytes using the parent's device path, connects it, polls DHCP, fetches bounded
frames, authenticates before GOP presentation, aborts stalled transfer before
freeing callback buffers, closes configuration, unloads driver, verifies SNP gone.
Test blocking waits/COM1 diagnostics/poweroff are not a native runtime integration.
The source adapter also retires completed upstream download allocations after
callbacks return; long-running memory/timing and failure-injection remain unproved.

Before physical use:

1. Confirm Dell has Ethernet to an Internet router. Historical inventory is not a
   live link check; bare UEFI has no proven Wi-Fi stack. No OS is installed on Dell.
2. Integrate a separate reviewed city+viewer profile: all candidate init/health
   paths stay offline; after active attach, poll cooperatively alongside Bluetooth
   and city rendering. Restrict NIC binding, URL/session and authenticated region.
   Network loss disables that region and leaves native city/USB reader running.
3. Fit the immutable4MiB mapped-image bound (native7 already3887104bytes; iPXE
   file303616bytes leaves almost no code margin). Do not change immutable bootstrap
   bounds silently. Account for separately loaded driver and bounded heap too.
4. Test exact integrated payload from saved city and EMPTY in normal native QEMU
   gates: world snapshot preservation, city animation, crop/fullscreen coherence,
   network fail/close/rollback, rejected code updates and both driver lifecycles.
5. Establish an authenticated read-only Internet endpoint on Yukabox. The present
   loopback fixture and QEMU10.0.2.2 are not reachable from Dell in Georgia; a private
   Tailscale address alone is not a native UEFI client. Measure reachability/bandwidth.
6. Rebuild exact integrated bytes twice, check current receiver/source identity,
   sign locally on Mac and send via existing Bluetooth. Owner key stays on Mac.
   Save physical receipt and owner screen observation separately from VM evidence.

Old city/map/snapshot/native7 and authoritative world12 remain unchanged. No
physical loading or recovery path has been tested for this new receiver yet.
