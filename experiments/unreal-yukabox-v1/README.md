# Unreal executor on Yukabox — first GPU frame verified

Unreal5.8.3 is installed on Yukabox. The C++ smoke project builds and captures a
1280x720 Vulkan frame on the actual Radeon890M, then exits normally. Evidence:
`evidence/2026-10-03/installation.json`, `build.log`, `smoke-report.json`, `frame.png`.
This is an executor baseline; the connected district/cat/portal are still planned.

Owner decision, 2026-10-03: Yukabox runs the editor, build tools, rendering and
district. Mac is only the command point. The existing Dell district remains on its
native executor; this experiment sends no Dell package and does not replace it.

Remote workspace: `/home/yuka/rabbit-world/unreal-yukabox-v1`. Subdirectories:
`engine` (official installed Linux build), `projects`, `cache`, `logs`, `snapshots`.
Downloads, engine binaries, derived data and credentials do not belong in Git.
The local owner signing key is never copied to Yukabox.

## Reproducible preflight

Copy `probe_target.py` to the remote workspace, then invoke it through SSH:

```sh
ssh yukabox 'python3 /home/yuka/rabbit-world/unreal-yukabox-v1/probe_target.py --root /home/yuka/rabbit-world/unreal-yukabox-v1'
```

The probe is read-only and enumerates actual Vulkan hardware separately from
llvmpipe. It does not claim Unreal works based on device enumeration. The captured
initial report is in `evidence/2026-10-03/target.json`.

Installed using Ubuntu repositories: vulkan-tools, xvfb and missing XCB dependencies;
existing runtime libraries were retained. No OS upgrade or reboot performed.
RADV enumerates Radeon890M on Ubuntu26.04; Xvfb reports no DRI3 presentation.
Actual Unreal Vulkan offscreen rendering now works without Xvfb or a desktop.
The screenshot shows the expected three basic blocks, ground, shadows and engine
default pawn sphere. This does not benchmark a detailed city or validate every
feature on Ubuntu26.04. Last probe detected no physical monitor on Yukabox. Owner
selected the Dell monitor on2026-10-04; direct monitor input vs network through
the Dell mini-PC is pending clarification. Native Dell currently has no stream
receiver. Historical physical network inventory found no firmware SNP protocol;
do not assume Pixel Streaming can already display there. Direct input switching
would be an intermediate display test, not shared city composition.
Final builds use `-NoUBA` (local build without the accelerator listener).

## Next gates

1. DONE: owner signed into Epic; official Linux5.8.3 downloaded directly on Yukabox.
   SHA256 recorded, all300132 ZIP members extracted with CRC checks. Browser cookies
   and owner keys were not copied. No agent EULA acceptance was performed.
2. DONE for this baseline: actual C++ build, Vulkan Radeon890M device creation,
   inspected1280x720 frame and runner exit0. No `-NullRHI` or CPU llvmpipe used.
3. Create a small neighbouring district with a versioned Rabbit data adapter. Keep
   the old district snapshot and its engine hash immutable. LLM produces checked
   data/commands, not arbitrary remotely executed Python/C++.
4. Import a detailed rigged cat with recorded source/license and bounded assets;
   verify the requested tail and smile timing. A primitive placeholder does not
   complete this gate.
5. Add a visible portal, then shared composition and district attachment according
   to the city roadmap. Separate scenes/engine launch do not prove this works.

`city-map.json` is a stored placement proposal: the old district references an exact
world12 snapshot, the new district is explicitly `planned`. Positions use centimetres
and Y-up. An Unreal adapter must map Rabbit `(x,y,z)` to UE `(z,x,y)` and verify yaw;
there is no running importer, portal or combined view yet. Old snapshot bytes are
backed up on Yukabox, but that is not a full backup of old binaries/history.

Official references:
- [Linux installed build](https://dev.epicgames.com/documentation/en-us/unreal-engine/linux-development-quickstart-for-unreal-engine)
- [Linux requirements](https://dev.epicgames.com/documentation/en-us/unreal-engine/linux-development-requirements-for-unreal-engine)
- [Offscreen launch and streaming](https://dev.epicgames.com/documentation/unreal-engine/unreal-engine-pixel-streaming-reference)

Pixel Streaming is a possible later display transport, not installed here. Its
encoder and receiver must be tested separately; an AMD Vulkan device does not
prove AMF encoding support. The display destination remains to be chosen, without
making the Mac a rendering/execution host.

## GPU smoke project

`project/` is a C++ baseline with only engine-owned basic meshes, a directional
light and fixed camera. It is a graphics test, not the new city or a detailed cat.
`run_smoke.sh ROOT` builds and executes it on Linux, with a fresh log directory
and screenshot request. `install_archive.py` records SHA256/build version and
checks archive member paths before extracting an official 5.8.3 installed build.
The smoke frame and selected Vulkan GPU must be inspected together; file creation
alone is insufficient. Actual compilation and graphical execution passed. First
runner failed its final shell parsing because the script was updated in place
while bash was reading it; frame was already saved. The corrected stable script
was rerun successfully. Never replace the active runner file while it executes.

Reproduce from the command point:

```sh
ssh yukabox 'bash /home/yuka/rabbit-world/unreal-yukabox-v1/run_smoke.sh /home/yuka/rabbit-world/unreal-yukabox-v1'
```

Each run writes a fresh remote trial directory. Inspect that run's frame/device
log; do not mistake the historical evidence image for a newly observed result.
