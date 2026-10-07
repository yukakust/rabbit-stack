# EFI RNG boundary: offline adapter only

Hypothesis: a bounded native ABI adapter can discover EFI_RNG_PROTOCOL, enumerate algorithms, and obtain bytes only from an explicitly reviewed provider and advertised standard SP800-90 HASH256/HMAC256/CTR256 algorithm. Absence, warnings, malformed lists, unknown/raw-only selection, stale review, changed callback, failed RNG or ambiguous resource release fail closed. There is no timer, MAC, default-algorithm, or random-seed fallback.

The trusted caller supplies already validated BootServices callbacks and a fresh acquisition epoch; `RngReview` must come from independent provider provenance approval. A nonzero hash is a structural policy binding, not an authenticity proof. Provider presence, an advertised GUID, and a nonzero sample do not prove entropy quality. The adapter does not approve any physical Dell provider. It has not been integrated into firmware and has made zero physical RNG calls.

`rng_discover` uses LocateProtocol and a bounded two-call GetInfo sequence, with at most one pool of 256 bytes/16 GUIDs. It rejects duplicate algorithms. `rng_fill` uses explicit GetRNG only after review, obtains at most 256 bytes in scratch memory, and leaves the caller output unchanged on failure. Scratch and local pending bytes are wiped; output is copied only after successful scratch release. A failed FreePool remains an actual retained owner. A failed allocation that returns a pointer is quarantined as uncertain and never dereferenced or freed by this adapter. The future native all-owner inventory must explicitly include this additional pool; current Wi-Fi cleanup slots do not account for it.

`rng_diagnostic` exports only phase/error/status/counts, protocol/algorithm GUIDs, and a caller-supplied hash of CODE. It excludes pool/provider pointers, random samples, sample hashes, and private keys. No random diagnostics are implemented.

The ABI oracle uses official EDK2 commit `fbe0805b2091393406952e84724188f8c1941837` (edk2-stable202502), pinned Protocol/Rng.h, Guid/Rng.h and Uefi/UefiSpec.h. It checks the real RNG structure/GUID macros and real BootServices ordering (AllocatePool64, FreePool72, LocateProtocol320). Native compilation, 557 meaningful mock failure/boundary/zeroization cases under ASAN/UBSAN, and freestanding x86-64 COFF compilation ran exclusively on Yukabox. Evidence is in `evidence/2026-10-07`.

This bounds call count and memory, not wall-clock duration of synchronous firmware methods. Trusted valid, disjoint buffers and BootServices pointers remain caller obligations. A physical provider discovery/provenance review, complete owner integration and secure provisioning protocol review remain necessary before using bytes for private session keys.

Official sources: https://github.com/tianocore/edk2/tree/fbe0805b2091393406952e84724188f8c1941837/MdePkg/Include ; https://uefi.org/specifications . No credentials, private keys or random samples were read or exported.
