# Universal graph v1 — patchable typed module graph

This experiment replaces World v0's fixed pair of modules with the first explicit
portable event graph. The base graph is:

```text
start.started
    -> letter-h.trigger   (emit H)
    -> letter-i.trigger   (emit I)
    -> exit.trigger
```

`patches/add-bang.json` does not edit either backend or any existing module. It adds one
`console-byte` module, removes the `letter-i -> exit` connection, and inserts:

```text
letter-i.done -> punctuation.trigger -> exit.trigger
```

The observable result changes from `HI` to `HI!`.

## What is explicit

`world.json` contains:

- imported, versioned module types;
- a versioned graph-core dependency;
- declared capabilities;
- module, connection, and output budgets;
- modules and typed port endpoints;
- event connections;
- the observable contract.

The validator owns the reviewed port signatures. It checks direction and type, requires
one start and one exit, rejects cycles and unreachable nodes, follows event order, and
derives output from the graph rather than trusting the claimed contract.

## Run

```sh
cd experiments/universal-graph-v1
python3 verify.py
```

Individual workflows:

```sh
python3 rabbit_graph.py world.json --target targets/qemu-rv32i.json
python3 rabbit_graph.py world.json \
  --target targets/qemu-rv32i.json \
  --patch patches/add-bang.json
python3 rabbit_graph.py world.json \
  --target targets/hosted-arm64.json \
  --patch patches/add-bang.json
```

The QEMU backend emits 40 bytes for `HI` and 48 bytes for `HI!`. The Darwin backend
emits deterministic ARM64 assembly and temporarily links it with Apple `clang`. Both
Target Packs are graph-v1 revisions because variable-length output replaces World v0's
fixed 32-byte image contract; the proven World v0 files remain unchanged.

On non-Apple-Silicon development hosts the verifier checks the ARM64 artifact but skips
its execution. U3 is complete only after the same verifier ends with
`PASS: complete U3 universal module graph contract` on the learner's Mac.

This remains a deliberately linear, stateless graph. Branches, queues, persistent state,
dynamic loading, and hot patches are not implemented yet.
