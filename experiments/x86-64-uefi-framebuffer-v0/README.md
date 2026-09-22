# x86-64 UEFI framebuffer v0

This experiment changes the physical effect from firmware text to pixels. The portable
world requests one solid orange `256 x 256` rectangle at `(100,100)`. Its x86-64 Target
Pack binds that meaning to the UEFI Graphics Output Protocol (GOP).

The application uses UEFI only to locate GOP and obtain its already configured linear
framebuffer. It then reads `FrameBufferBase`, resolution, stride, and pixel format and
writes all 65,536 pixels with reviewed x86-64 store instructions. It accepts the two
standard packed 32-bit RGB/BGR formats, waits for one firmware key, and returns success.
It never calls UEFI Simple Text Output and contains no `HI` string.

Build and verify without touching physical media:

```sh
cd ~/rabbit-stack/experiments/x86-64-uefi-framebuffer-v0
python3 verify.py
python3 build_image.py --output /tmp/rabbit-framebuffer.img --report /tmp/rabbit-framebuffer.json
python3 run_qemu.py
```

Expected QEMU screen: one solid orange square, 256 pixels wide and high, beginning 100
pixels from the top and left. Press one key to return to firmware, then close QEMU.

This is a pre-physical artifact. It does not authorize writing a USB device. UEFI still
loads the PE32+ application and exposes the framebuffer; Rabbit owns the individual
pixel writes but does not yet initialize the GPU or display controller from reset.

Reviewed identities:

```text
world SHA-256:  41ba583c46803a3cce864524b68fe553983db066d1f193720915f83ce7667b05
target SHA-256: 4288e3f93f6a30ca6ec177e5683a3e0e4d2bce3523e1ec5fb8a0bb917d5bd474
EFI SHA-256:    e8806bf1f3f922c53125c24f2cab3c0a2c1df869983f4a1d0ff2cc3c10006836
image SHA-256:  43e1998c7e60d49096d9980cbed77f8e4dc5a3abbc41dff48a5b94ee7ca50c77
```
