# Pill v1 — intent-to-ARM64 baseline

There is no C source in this experiment. `pill.s` is handwritten ARM64 assembly for
Apple Silicon macOS. It uses the stable macOS C runtime functions `puts` and `getchar`
for terminal I/O; choice and branching are implemented directly in ARM64.

## Contract

| Input | Output | Exit status |
|---|---|---:|
| `r` or `R` | `Wake up, Neo.` | 0 |
| `b` | `The story ends.` | 0 |
| anything else / EOF | `Invalid choice.` | 2 |

## Build and verify on Apple Silicon

```sh
cc pill.s -o pill
python3 verify.py ./pill
```

Python is an independent test instrument, not part of the ARM64 program.
