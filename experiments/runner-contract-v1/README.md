# Runner Contract v1 — hosted, native, and bridge

This experiment runs the unchanged U4 semantic world and patch through one explicit
Runner Contract with three execution envelopes:

- `native`: RV32I guest bytes loaded into QEMU `virt`;
- `hosted`: ARM64 assembly compiled and executed as a Darwin process;
- `bridge`: a simulated device in a separate child process reached through framed stdio.

Every runner declares its transport, authority, remaining layers, temporary mutations,
startup/execution timeouts, recovery method, persistent-write policy, and whether it is
a simulation. Runner contracts have independent canonical identities.

## Bridge protocol

The bridge uses canonical JSON with a four-byte big-endian length prefix. Its request
binds the plan and artifact hashes. The response echoes the request hash and observed
result. Evidence contains independent request, response, and complete transcript hashes.

`bridge_device.py` is only a deterministic protocol simulator. It is not physical
hardware and does not claim USB, serial, network, light, phone, or appliance access.

## Run

```sh
cd experiments/runner-contract-v1
python3 verify.py
```

Individual patched workflows:

```sh
python3 rabbit_runners.py ../capability-negotiation-v1/world.json \
  --target targets/native-qemu-rv32i.json \
  --patch ../capability-negotiation-v1/patches/add-bang.json

python3 rabbit_runners.py ../capability-negotiation-v1/world.json \
  --target targets/hosted-arm64.json \
  --patch ../capability-negotiation-v1/patches/add-bang.json

python3 rabbit_runners.py ../capability-negotiation-v1/world.json \
  --target targets/bridge-simulator.json \
  --patch ../capability-negotiation-v1/patches/add-bang.json
```

The complete suite has passed on the learner's Apple Silicon Mac and ends with:

```text
PASS: complete U5 three-envelope Runner Contract
```

## Verified result

Hosted Darwin ARM64, native QEMU RV32I, and the simulated framed bridge all observed
exact `HI` and patched `HI!` with status `0`. Runner identities, plan/artifact bindings,
bridge transcript hashes, recovery declarations, replay/timeout rejection, and all three
documented CLI workflows passed.
