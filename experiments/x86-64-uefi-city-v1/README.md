# First procedural 3D city

Hypothesis: an owner-reviewed connected ABI3 driver can render a portable city
and present it fullscreen without replacing the installed bootstrap or its radio
protocol. Baseline: signed V3 cat world in a 480×270 top-left viewport.

Result: exact UEFI candidate gates pass, including fullscreen pixels outside the
old surface, city data application, legacy world/engine rollback and unhealthy or
bad-signature rejection. Physical Dell returned correlated APPLIED receipts for
native6, initial city9, LLM-added house10 and camera movement11. Physical screen
appearance and performance remain owner-observation pending. See evidence.

## Portable data and target boundary

`city_world.py` defines schema4 JSON and bounded Ed25519-signed RUP4 packets:
32-byte header, 1–64 32-byte building records, 64-byte signature. Coordinates and
dimensions are centimetres. Camera yaw is 0–255 around a complete circle; 0 looks
along +Z, 64 along +X. Houses, boxes and low road volumes are procedural geometry.
World id and building names are Mac metadata; exact packet reconstruction binds
the visible parameters. Public development Creator authority is unchanged and
is distinct from owner native authority.

`city_core.c` uses fixed-point perspective, near-plane triangle clipping and a
depth buffer. Geometry is true 3D; this is an intentionally simple flat-shaded
software renderer. The internal image remains 480×270 and is enlarged to the
physical display, so this does not promise native-resolution detail, textures,
arbitrary meshes, physics, characters, or measured 30fps.

`city_display.c` is the privileged x86 UEFI Target Pack. Only after driver attach
does it bind the checked GOP buffer. Candidate init/trial never writes GOP. An
active tick enlarges the canonical surface and returns its exact top-left crop
to the old root, whose final presentation therefore agrees with the full frame.
This is an owner-reviewed privileged driver, not a native-code sandbox. Display
bounds: 480–3840 by270–2160, RGB/BGR, checked stride and buffer size.

`build_city.py` asserts immutable source anchors and creates local transformed
driver/runtime copies; installed bootstrap sources remain unchanged. The driver
retains V3 rendering and RSS2 snapshot ABI. Before reverting to a V3-only driver,
first restore V3 data; an old driver cannot restore a city4 snapshot.

## Commands, history and recovery

Rabbit World uses the existing strict planner, C/signature gates, shared paced
Bluetooth transport, exact session receipt correlation and increasing counters.
Try «добавь дом справа», «камера вперёд на два метра», «поверни налево» or «сделай
небо темнее». Complete city data candidates preserve unrelated buildings and
camera. Text and final voice transcripts use the same path. Saved V3 and city
versions remain available through the history selector.

The authoritative city, camera, packages, journal and history are saved on Mac.
They survive Mac app restarts. Dell still holds its active driver/world in RAM.
The new recovery UI requires the owner to tick «Dell был перезагружен», then
«Восстановить город на Dell». It first reads fresh zero receiver state, validates
the installed bootstrap and exact empty-boot candidate gate, rebuilds the exact
payload, signs a new owner release bound to bootstrap1 + empty world, then sends
the saved city with a new increasing world counter. It never infers reboot from
Bluetooth loss. Interrupted recovery keeps exact native/world sessions for
«Продолжить передачу»; normal edits are blocked during recovery.

Recovery is tested with actual empty-boot UEFI execution plus host two-stage
resume checks. Physical Dell reboot/recovery remains untested; no reboot or USB
write was performed for this milestone. Yukabox synchronization, autonomous boot
discovery and persistent Dell disk storage are separate future work.

## Reproduce

Run `python3 experiments/x86-64-uefi-city-v1/verify_city.py` on Mac with the existing
compiler/QEMU tools. It uses PUBLIC fixture native keys, actual portable C with
address/undefined-behavior sanitizers and adversarial camera bounds, then exact
UEFI LoadImage/swap/fullscreen/restore/rejection gates both from a V3 world and
from an empty bootstrap. Mock USB is explicitly not physical Bluetooth evidence.
No owner signing, radio, media write or hardware purchase is performed.

Run the connected `verify_world_control.py` for controller/planner/history,
recovery guards and exact two-stage recovery session/counter preservation.
Generated binaries and images stay in ignored runs. Real owner signing belongs
only to the separately reviewed `city_native.py`/`city_recovery.py` paths.
