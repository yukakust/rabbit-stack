# Rabbit World Package v0

This experiment turns the owner's first ordinary-language world into a small,
target-independent binary package. It is the boundary between the future World Builder
and a reusable Rabbit Runtime.

```text
Russian intent
    -> reviewed interpretation
    -> portable semantic world
    -> deterministic compiler
    -> jump-stone.rabbit
    -> future Rabbit Runtime
```

The package records the exact semantic world and compact operations for the player,
arrow movement, timed jump, one relocatable solid stone, collision, and exit. It does
not contain x86 instructions, UEFI calls, QEMU settings, framebuffer addresses, USB
rules, or any Dell-specific fact. Those belong to a runtime and its Target Pack.

Build and verify without deploying anything:

```sh
cd ~/rabbit-stack/experiments/world-package-v0
python3 verify.py
python3 build_package.py \
  --output /tmp/jump-stone.rabbit \
  --report /tmp/jump-stone-package.json
```

The binary format starts with `RBTW`, version and payload lengths, plus the SHA-256 of a
canonical manifest. The manifest binds the portable world to the exact owner-reviewed
interpretation. A compact opcode stream follows. The verifier independently decodes the
stream and rejects tampering, truncation, stale approval, semantic drift, duplicate JSON
fields, and target-specific leakage.

This milestone is deliberately **PACKAGE-BUILT-NOT-DEPLOYED**. The existing UEFI image
still has the behavior compiled directly into x86-64 machine code. The next experiment
is a Rabbit Runtime that loads this same package and performs it. Only after that
boundary works will live package replacement—and later microphone/LLM input—avoid a
new USB image for every requested change.
