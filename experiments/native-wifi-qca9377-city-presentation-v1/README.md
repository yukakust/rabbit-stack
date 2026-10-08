# Cached city presentation and cooperative network service

NEW unsigned projection of the frozen owned-city parent. It preserves world19, the cat, both pixel formats, legacy cropping and drawing geometry. Two precomputed coordinate maps replace per-pixel divisions. Presentation and raster loops offer a QCA-only service slice, guarded against reentry and gated at 4 ms. A clock rollback disables extra frame polling. No Bluetooth operation occurs inside drawing.

Bounded maps accept 480–3840 by 270–2160, validated stride/format and caller buffers; close wipes maps. The original city pool remains explicitly owned. Network readiness, entropy and trusted wall time cannot be inferred from the frame clock or these callbacks.

Yukabox evidence: 105 ASAN/UBSAN/COFF checks; 20 original/derived world19 frames byte-identical including legacy copying, 17 animated changes and 26651 synthetic service opportunities. Three identical unsigned EFI builds: 213504-byte file, 2224128-byte mapped image. Real OVMF normal/EMPTY LoadImage/StartImage/current-world/replacement/rollback checks passed with synthetic USB/QCA fixtures. These are software checks, not physical Wi-Fi or signing admission.

`check.py` verifies pinned sources and evidence offline. Native generation and verification scripts run only on Yukabox. The frozen predecessor, bootstrap and signed64 are unchanged. Persistent radio, TLS and association still require separate integration and physical proof.
