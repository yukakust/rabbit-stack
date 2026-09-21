# Capability negotiation v1 — intent to reviewed driver plan

This experiment inserts a deterministic capability resolver between the portable graph
and the U3 backends.

The world requests semantic effects, never target drivers:

```text
display.text  v1  required  ascii, at most 3 bytes
machine.exit  v1  required  status 0
light.emit    v1  optional  white, 50%
```

The two Target Packs advertise reviewed offers. Resolution produces different canonical
deployment plans:

```text
display.text -> qemu-virt-uart
display.text -> darwin-posix-write
```

Neither target currently offers a light, so the plan records `light.emit` as
`not-offered`. If the same request becomes required, resolution rejects deployment
before building an artifact.

## Trust boundary

The plan binds the exact semantic world hash, Target Pack hash, selected drivers,
constraints, limits, device bindings, authority effects, and remaining software layers.
Build and execution evidence additionally bind the plan and artifact hashes. A stale or
cross-target plan cannot be reused.

After validation, a small deterministic adapter translates the reviewed plan into the
already-tested U3 graph backend interface. The LLM does not select or approve drivers.

## Run

```sh
cd experiments/capability-negotiation-v1
python3 verify.py
```

Individual workflows:

```sh
python3 rabbit_capabilities.py world.json \
  --target targets/qemu-rv32i.json

python3 rabbit_capabilities.py world.json \
  --target targets/qemu-rv32i.json \
  --patch patches/add-bang.json \
  --plan /tmp/rabbit-plan.json \
  --report /tmp/rabbit-capability-report.json

python3 rabbit_capabilities.py world.json \
  --target targets/hosted-arm64.json \
  --patch patches/add-bang.json
```

On an Apple Silicon Mac, success ends with:

```text
PASS: complete U4 capability negotiation contract
```

This is still a small closed registry. It does not discover physical devices, install
drivers, contact a network, control a real light, or authorize new effects dynamically.
