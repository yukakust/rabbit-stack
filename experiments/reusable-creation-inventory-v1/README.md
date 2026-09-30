# Reusable Creation Inventory v1

This experiment makes Rabbit components reusable before the first cat scene is executed.
It is target-independent: the catalog, Merge, provenance lock, and sharing package contain
no Dell, UEFI, ISA, framebuffer, MMIO, or QEMU fact.

## What exists

`catalog.json` contains versioned cards for:

- pixel cat and ball assets;
- clock, scene, frame-animation, 2D-physics, collision, and sprite-rendering capabilities;
- reusable cat-chase and bouncing-ball Anima;
- resource-budget, signed-package, and transactional-rollback policies.

Each card declares:

- stable component id and semantic version;
- kind, Creator, SPDX license, and plain-language meaning;
- typed input and output ports;
- exact dependencies and provided abilities;
- external authorities such as `display.draw` or `time.read`;
- bounded memory, persistence, object, pixel, and tick resources;
- one reviewed declarative implementation format.

`examples/cat-plays-with-ball.merge.json` connects thirteen cards into the first cat
blueprint. `examples/bouncing-ball.merge.json` forms a second Creation and reuses ten
of those exact component identities. Merge validation pins every component hash and
license into a provenance lock, checks every connection type, sums resources, and
requires authority grants to equal—not merely include—the requested effects.

## Sharing

`build_package.py` exports only the selected components, Merge, and exact resolved lock
into a deterministic package signed with Ed25519. `inspect_package.py` accepts it only
when given the already trusted raw public key. Carrying a public key inside a package is
not enough to establish trust; a package signed by another key is rejected.

The private-key file is supplied by the Creator and is never generated, copied, or
stored by this experiment:

```sh
python3 build_package.py \
  --merge examples/cat-plays-with-ball.merge.json \
  --private-key /secure/path/creator-ed25519-private.raw \
  --output /tmp/cat-plays-with-ball.rabbit-inventory \
  --report /tmp/cat-plays-with-ball.report.json

python3 inspect_package.py \
  /tmp/cat-plays-with-ball.rabbit-inventory \
  --trusted-public-key /trusted/path/creator-ed25519-public.raw
```

The test suite uses a deterministic test-only key in temporary storage. It must not be
treated as an owner key.

## Verification

```sh
python3 verify.py
```

Positive checks prove exact reuse, deterministic identities, typed Merge, provenance,
licenses, resources, authorities, and signed export/import. Negative checks reject
tampering, an untrusted Creator, a stale lock, hidden or unused authority, omitted
dependencies, incompatible ports, resource overflow, target leakage, native code,
malformed sprites, dependency cycles, and ambiguous JSON.

Expected terminal status:

```text
PASS: INVENTORY-V1-BUILT-NOT-EXECUTED
```

That phrase is deliberate. Inventory v1 proves reusable composition and sharing; it
does not yet claim that a scene interpreter has animated the cat on Mac, QEMU, Dell, or
another physical target. The next boundary is a hosted reference Scene/Anima v2 runner
that consumes this exact resolved Creation, advances deterministic ticks, and emits
reviewable frames before any native lowering or physical deployment.
