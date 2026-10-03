# Connected bounded 3D actors

Extends the reviewed city driver with reusable coloured 3D primitives, sine
translation of individual parts and timed visibility. Roof-cat is a data model,
not a special branch in the renderer: 36 parts, dangling waving tail, first smile
after10 seconds, lasting1 second and repeating every10 seconds. Other figures can
be composed from ellipsoids, boxes and cones through the same strict planner.

## Boundary and limits

RUP5 retains signed RUP4 buildings/camera/sky/ground, then appends up to4 actors,
48 parts each,96 total, max6816 bytes. No code, network, filenames, meshes,
textures, physics, executable models or scripts in world data. Portable fixed-point
C validates signature, reserved bytes, length, IDs, geometry and timer bounds.
Names remain Mac metadata. Existing RUP4 and V3 histories stay restorable with NEW
monotonic world counters. Restore a compatible data world before an old engine.

Native profile sources are copied/transformed into ignored runs. Immutable installed
bootstrap, verifier, driver sources, USB and disk/firmware are untouched. Target-only
GOP access occurs after attach; the exact top-left crop agrees with the root's
unchanged480x270 presentation. Software rendering is800x450, enlarged to GOP size,
not native-resolution graphics. Mapped PE image, including BSS, is3887104 bytes,
within the immutable4MiB verifier limit. The first960x540 attempt exceeded that
limit, failed QEMU before signing and was never sent to Dell.

Target animation time uses x86 TSC calibrated with two UEFI50ms Stall samples on
attach, not frame count. init/trial have no clock/display access. This calibration
and real elapsed animation were exercised in QEMU; physical timing still requires
observation and is not guaranteed across all hardware/power management.

## Checks, signing and delivery

`python3 verify_actors.py` uses only public fixture keys, strict codec/planner
rejections, actual C rendering under ASan/UBSan and isolated smile/tail boundary
checks. No owner signature or radio. Connected controller tests exercise actor
addition preserving all buildings/camera/colors, history and two-stage recovery.

`actors_build.compile_city_driver` reproducibly builds the new profile.
`actors_gate.qemu_gate` executes the EXACT payload with real UEFI LoadImage/StartImage:
legacy V3 -> native actor driver -> city4 snapshot -> city5 actors -> city5 native
snapshot -> legacy data/engine rollback -> failed health and bad signature rejection.
It tests elapsed motion and fullscreen/crop agreement. Run both normal and empty
bootstrap fixtures before any owner signing. These use mock USB, not Bluetooth.

`actors_native.prepare_city` requires the installed owner identity/source gate,
exact payload QEMU evidence, current-world C health and two matching fresh rebuilds
BEFORE owner key access. RRT3 binds target, current payload, current signed world and
new native counter. `deliver_city` rechecks all bindings and uses the existing saved
paced Bluetooth session, separate COMMIT and exact receipt correlation.

Mac controller exposes actors5 only after that receipt. Its normal text/voice
requests compose checked reusable models or bounded new primitive data, validate
and sign a small RUP5 world and reuse existing Bluetooth delivery. City recovery
selects this profile and requires its exact EMPTY bootstrap fixture, explicit owner
reboot confirmation and fresh zero read-only receiver state before recovery signing.
The agent never reboots Dell or writes the USB. Physical reboot/recovery has not
been exercised for this profile.
