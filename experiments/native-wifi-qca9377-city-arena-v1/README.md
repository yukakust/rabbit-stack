# Bounded city buffers: unsigned integration preparation

Depth800×450 (1,440,000 bytes) and the legacy480×270 picture (518,400 bytes)
share one real BootServicesData pool:1,958,415 bytes including16-byte alignment.
The frame buffer, world19 package, geometry, projection, pixel format and animation
remain unchanged. The pool owns the actual pointer holders. Rendering enters an
exclusive bounded reader; detach clears both holders before volatile wipe/free.
Allocation errors returning a pointer or failed frees quarantine ownership;
neither is converted into a safe release. No callback may render after detach.

`native_projection.py` derives NEW files from the retained47-resource prototype.
It acquires the city pool from validated SystemTable/BootServices interfaces after
registration validation, before scene init, and closes it only after radio and
phase-owner retirement. The immutable bootstrap and frozen64 are not modified.
The Connected ABI already permits only one root callback loop; this is not a
general concurrent-renderer allocator.

The original47 feasibility prototype required a CLOSED runtime even when QCA was
absent and its runtime ledger had never been used. Full QEMU exposed refusal to
unload at same-driver replacement. The NEW projection permits this unused case
only when every runtime ledger byte is zero. Acquired/nonzero owners still need
the original CLOSED proof and the existing guarded phase detach and RNG cleanup.
The old prototype is unchanged. Failed QEMU attempts remain in ignored remote
runs; added fixture markers locate failure without removing original assertions.

Evidence, all native C/COFF/QEMU only on Yukabox:

- 21 ASAN/UBSAN allocator/alias/epoch/reader/wipe/error-ownership checks.
- 20 original-versus-pointer renderer frames of the exact signed world19,
 byte-identical, with17 frames differing from time0 due to animation; exact
 legacy buffer copy.
- Three identical whole EFI builds:212,480 file /2,195,456 mapped bytes.
- Normal and EMPTY real OVMF LoadImage/StartImage gates, world19 target-clock cat
 animation, same-driver replacement, rollback and absent-radio diagnostics.
 Radio/USB inputs are synthetic; these are not Dell observations.

The projection is unsigned, has no reserved generation or signing admission,
and is not installed. It does not add RX-ring publication, radio association,
TLS, RNG authority, IP or WAN. The extra graphics pool is external to SizeOfImage;
the47 DMA owners and phase pool remain separately counted, not hidden in the cap.
Further composition must preserve exact resource/lifetime and aggregate-image
limits. Firmware64 delivery is unrelated and must remain the sole BLE controller.

`verify.py`, `verify_renderer.py`, `native_projection.py`, then
`verify_projection.py` reproduce the respective stages on Yukabox. Fixture
world/crypto/source hashes are pinned by the renderer verifier; generated native
sources and imported prototype generator are bound by the native report.
