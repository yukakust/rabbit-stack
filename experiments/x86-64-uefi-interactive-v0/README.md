# x86-64 UEFI interactive v0

This is Rabbit's first interactive physical-world candidate. The portable world contains
one orange `128 x 128` object at `(100,100)` and rules saying that arrow-key events move
it by 16 pixels without leaving the visible screen. Escape exits successfully.

The x86-64 Target Pack binds those meanings to two UEFI facilities:

- GOP supplies an already configured linear framebuffer;
- Simple Text Input supplies standard UEFI scan codes for arrows and Escape.

The reviewed machine bytes clear the visible framebuffer to black, draw the object with
direct pixel stores, poll for a key, erase the old rectangle, update and clamp `(x,y)`,
and draw the next frame. There is no operating system, process, window system, graphics
library, event framework, compiler, assembler, or linker in the generated artifact.

Build and test without writing physical media:

```sh
cd ~/rabbit-stack/experiments/x86-64-uefi-interactive-v0
python3 verify.py
python3 run_qemu.py
```

Expected behavior:

1. the firmware display becomes black;
2. an orange square appears at `(100,100)`;
3. each arrow press moves it 16 pixels;
4. it stops at screen boundaries;
5. Escape returns from the application.

On 2026-09-22 the owner ran the exact image under QEMU 11.1.1 and manually confirmed
all four arrow directions, 16-pixel movement, erasure without an orange trail, clamping
at every screen edge, and successful return on Escape. The observation is bound to the
exact world, target, EFI, and image in `evidence/qemu-macos-arm64-observed.json`.

This remains physically `BUILT-NOT-INSTALLED`. USB installation requires another exact
device check and explicit authorization.

Reviewed identities:

```text
world SHA-256:  f6d22aa19f64ff36e6057b9904624e2fb4d551e75234aa59d774a82b539462b9
target SHA-256: bbec78f05b18422021999adf8e6fbafd34695cf6c6fb8ef1235c858245b7f9ac
EFI SHA-256:    b633e0aa48f850bd350d2d1d55bb7e431b83f43f7f1b783e84864e10ede7ef84
image SHA-256:  be2d4ba213672e1ce11879c5b644976a59edad924cfffd6237643e0afa65e06f
```
