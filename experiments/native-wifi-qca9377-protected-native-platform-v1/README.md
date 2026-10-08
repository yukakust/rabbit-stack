# Protected native platform: concrete ABI/owner proof, not TLS deployment

New isolated software scope. All C, ASAN/UBSAN, COFF and linking ran on Yukabox.
4769 checks pass. Three actual COFF units link without DLL imports to a 12288-byte
mapped standalone EFI **link probe**, never launched. It is not a native63 update.

`protected_boot_api` obtains the existing platform's genuine BootServices callbacks:
SystemTable BootServices pointer at96, AllocatePool64, FreePool72, LocateProtocol320.
The actual pinned EDK2 oracle asserts the callback offsets; SystemTable120/offset96
also has an existing independent oracle in `production-memory-plan-v1`. Header
signatures, lengths, overflow and output aliases are checked before extraction.
This requires already valid, mapped, firmware-supplied tables with BootServices
still alive. These checks do not authenticate code/providers. No bootstrap change
is required to expose these methods; their physical presence/quality is unproved.

`protected_rng_inventory` invokes LocateProtocol/GetInfo only. It calls **zero
GetRNG methods**, exports only existing RNG-v2 GUID/count/status/CODE-hash whitelist,
and provides no sample/hash/private-key field. The unchanged RNG-v2 source is copied
and bound. Its official EDK2 baseline is
[fbe0805b2091393406952e84724188f8c1941837](https://github.com/tianocore/edk2/tree/fbe0805b2091393406952e84724188f8c1941837/MdePkg/Include).
An advertised algorithm is not entropy approval. Independent physical provider
provenance, callback lifetime and trusted firmware mapping still block private keys.

The arena owns one4096..2097152-byte BootServicesData pool. It has a generation epoch
and ONE exclusive stage loan (TLS/supplicant/network labels0..2 are identifiers only).
Live loans prevent cleanup. Return/cleanup wipes bytes. Error-returned/malformed
allocations and ambiguous FreePool outcomes remain uncertain owners, never retried,
dereferenced or cleared to claim release. Runtime RAM counts separately from EFI
SizeOfImage. No static multi-megabyte arena is introduced.

This module intentionally does not compose simultaneous allocators. TLS can remain
alive while the supplicant handles rekey and lwIP runs, so exclusive sequential
loans alone are insufficient. Future composition needs disjoint sized partitions
or separately bounded pools, real allocator high-water evidence and all-owner
inventory. Existing `production-memory-plan-v1` has the more mature singleton
holder/detach/16-byte-slack lifecycle and should be reused for native integration.
This proof does not replace that component or wire new native global owners.

## Actual size limits and remaining work

Native63 is exactly4194304/4194304 mapped bytes. Its `.text` has2928 bytes of page
slack; our full two-module text is3955 bytes and rdata64. Direct composition can
add a page and has **not** passed the immutable cap. Inventory-only dead-code
elimination or reclaiming inactive boot storage/code needs an actual complete EFI
composition; no cap growth or bootstrap modification is approved here. The link
probe size12288 cannot establish that the whole native image fits.

`integration.json` pins exact evidence for the remaining interfaces:

* MbedTLS3.6.7 TLS1.3: actual measured linked code, heap/stack peak and bounded BLE
  transport composition still needed. Require real RNG, full SPKI physical QR/pin
  confirmation, no0-RTT/resumption and authenticated completion before credentials.
  This scope does not implement or approve TLS, certificate keys or pairing.
* Mature supplicant-native-v2: real crypto and interop exist, but final freestanding
  link fails31 runtime/eloop/entropy/string APIs. Implement these actual services,
  then prove real EAPOL/driver key installation and local port admission.
* Hardened lwIP: 339 real-stack synthetic DHCP/ARP tests and COFF pass; code25520,
  BSS32361, data2/rdata2813 bytes. TCP/DNS are disabled; cannot pretend a UDP DHCP
  fixture provides TCP/TLS streaming. Real HTT Ethernet path, authorized association,
  key-install receipts and monotonic scheduling remain required.

No real credentials, private keys, Bluetooth, device, native state, counter,
signature, Funnel or native candidate operation occurred. Failed owner cleanup
must block any future physical release; it cannot be hidden in existing14 DMA slots.

Reproduce on Yukabox: `python3 verify.py --clang <pinned-clang> --lld <pinned-lld>`.
Native tools are guarded against execution on Mac. Artifacts are remote; public
source/report/log hashes are retained in `evidence/2026-10-09`.
