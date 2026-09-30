# Scene/Anima v2 hosted reference runner

This experiment is the first executor for the exact target-independent `Cat Plays With
Ball` Creation from `reusable-creation-inventory-v1`. Inventory remains the declarative
blueprint. This runner supplies reviewed meaning for ticks, integer 2D physics, edge and
cat/ball collision, state-machine behavior, frame animation, a two-entity scene, and
bounded sprite composition.

## What the cat does

The 240-tick reference story starts with the cat looking at a moving ball. The Cat Anima
then cycles through `look`, `chase`, `pounce`, `bat`, and `wait`. A bat changes the
ball's integer velocity; the ball also reflects from all four scene edges. The two
eight-by-eight sprites and their palettes are read from the reusable catalog rather
than copied into the runner.

There is no random number, floating point value, wall-clock timestamp, network input,
or external visual asset in the trace. Repeating the same Creation and runner contract
therefore produces the same trace and raster identities.

## Run it

In a terminal:

```sh
cd ~/rabbit-stack/experiments/scene-anima-v2-runner
python3 verify.py
python3 run_hosted.py
open /tmp/rabbit-cat-scene-v2/preview.html
```

`preview.html` is a convenient offline visualization of the already generated trace;
it is not the evidence oracle. `trace.json`, `report.json`, and the final RGB raster are
the inspectable artifacts. Generated artifacts stay outside Git.

To choose a different empty output directory or a shorter reviewed run:

```sh
python3 run_hosted.py --output /tmp/my-rabbit-scene --ticks 120
```

## Trust boundary

The runner first invokes the Inventory v1 validator and accepts only Creation identity
`c6e1def6497769bbaa3917a8dacba099b01676af459358d7e6551fb6fa82eab8` with exactly
the reviewed thirteen component identities and exactly `display.draw` plus `time.read`.
Changing a sprite, Merge, authority, component, runner bound, or Creation revision is a
hard rejection before execution.

The status is:

```text
SCENE-ANIMA-V2-HOSTED-EXECUTED-NOT-PHYSICALLY-DEPLOYED
```

The cat really executes in the hosted reference runner and can be viewed on the Mac.
`../x86-64-uefi-scene-anima-v2/` now supplies the separately reviewed Dell Target Pack
and a QEMU-observed bounded AOT lowering of this exact trace. The portable Creation and
its component identities did not change. Physical Dell observation remains pending.
