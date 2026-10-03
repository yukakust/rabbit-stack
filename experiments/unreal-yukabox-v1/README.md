# Unreal district on Yukabox — preparation

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
RADV enumerates Radeon 890M on Ubuntu26.04; Xvfb reports no DRI3 presentation.
Initial Unreal trial therefore uses Vulkan offscreen rendering, with explicit
frame evidence before declaring success. Performance and Ubuntu26.04 compatibility
are still unverified. No full desktop or publicly accessible control endpoint added.

## Next gates

1. Obtain the official Linux `.zip` after the owner signs into Epic. Accepting an
   EULA requires the owner to review/accept or explicitly confirm that exact step.
   Download directly on Yukabox; do not send browser credentials or owner keys.
   Record engine version, artifact hash and the actual installed path.
2. Verify an actual editor/GPU launch and captured frame; reject llvmpipe as evidence
   of GPU rendering. Do not use `-NullRHI` to claim a successful graphical trial.
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
