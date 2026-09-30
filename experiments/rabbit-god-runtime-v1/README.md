# Rabbit God Runtime v1

This experiment starts the stable resident runtime that will eventually let the owner
describe a world on the Mac and replace the running Dell world without moving the boot
USB. It is a contract and deterministic hosted transaction model, not yet a new physical
UEFI image.

The portable core does not know Bluetooth, Dell, UEFI, or framebuffer addresses. It
accepts only a trusted Creator's signed Reusable Creation Inventory package, checks the
resolved component graph, authorities and resource limits, and uses two logical slots:

```text
active world -> receive into staging -> validate -> provisional
             -> health succeeds -> commit + receipt
             -> health fails    -> restore previous active world
```

The separate Dell Target Pack binds semantic package receive/receipt operations to the
already demonstrated QCA Rome passive BLE advertisements and bounded non-connectable
ACK. The first transport budget permits 32 KiB packages in at most 4096 eight-byte
payload frames. This is sufficient for the current 20,329-byte signed Cat Creation,
though it is a correctness-first transport rather than the eventual fast path.

Run:

```sh
cd ~/rabbit-stack/experiments/rabbit-god-runtime-v1
python3 verify.py
```

The verifier transports the exact signed Cat package through all frames, commits only
after a successful health check, rejects corruption, missing/reordered chunks, an
untrusted signer, stale replay counters, authority escalation, oversized packages and
Target Pack escalation, and proves health failure restores the previous world.

Current status:

```text
GOD-RUNTIME-V1-CONTRACT-HOSTED-VERIFIED-NOT-PHYSICALLY-INSTALLED
```

The next boundary is implementing this exact core inside one combined Dell UEFI image:
Scene/Anima interpreter + package staging + validation + BLE receive/receipt. Until that
new image passes QEMU and Dell gates, the existing cat-and-ball USB remains untouched.
