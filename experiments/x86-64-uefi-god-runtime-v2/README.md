# Rabbit God Runtime v2 — one runtime, wireless worlds

This experiment moves the extensibility boundary from firmware code to a bounded,
signed data package. The removable USB contains one x86-64 UEFI Runtime. Ordinary
world changes then arrive over passive BLE and live in RAM; they do not replace the
UEFI image.

## What a package may contain

- up to 16 RGB palette entries;
- up to 16 indexed sprites, each up to 16x16 pixels and 16 animation frames;
- up to 16 live objects;
- up to 16 Rabbit VM programs with 32 bytes per program;
- movement, edge bounce, chase, flee, animation, and bounded collision impulse;
- initial positions, velocities, targets, and a 160x90 logical scene.

The complete signed package is limited to 4096 bytes. It contains data and reviewed VM
instructions, never native x86 code. The Dell stages the entire package in RAM, checks
frame order and checksums, verifies the trusted Creator's Ed25519 signature, validates
all references and budgets, performs one health step, and only then replaces the active
world. Rejection or failed health leaves the previous world active. A successful commit
produces the existing bounded BLE ACK.

Transport v2 uses a 16-bit chunk sequence and six payload bytes per BLE UUID frame. It
therefore supports 4096-byte packages and is no longer limited by the old 255-frame
ceiling. It is deliberately slow and correctness-first; a connected or Wi-Fi transport
can later carry the same package contract faster.

## Verify and emulate

```sh
cd ~/rabbit-stack/experiments/x86-64-uefi-god-runtime-v2
python3 verify.py
python3 run_qemu.py
```

QEMU must show `RABBIT GOD RUNTIME v2.0` and fail closed because it has no Dell
`0CF3:E009` controller.

The verifier accepts fail-closed evidence bound to the exact generated source,
Runtime core, and Target Pack. EFI and disk-image hashes may legitimately differ
between the Linux and macOS cross-toolchains; each host build must still be
deterministic, and its own hashes are printed for physical review.

## Prepare, but do not write, the physical candidate

```sh
python3 prepare_physical.py
```

The command validates everything, creates the image in the host temporary directory,
lists removable physical media, and stops before any device write.

## Send a complete new world after the Dell boots v2

```sh
python3 send_package.py worlds/cat-chases-mouse.json --counter 1
```

Edit or generate another strict world JSON, increase `--counter`, and run the same
command. No USB movement or Dell reboot is required. A power cycle clears received
worlds because this version intentionally performs no persistent write; resend the
desired world after boot.

## Honest boundary

“One final image” means no reflashing for new worlds expressible by this package ABI.
Adding a new hardware driver, cryptographic primitive, VM opcode, larger budget, or a
fix to the Runtime itself remains a Runtime upgrade. This is the same stable-kernel /
dynamic-program boundary used by mature systems, made explicit and testable here.

## Text -> model -> validated world -> Dell

`ask_world.py` uses the OpenAI Responses API with a strict JSON schema. The model
receives your request, a base world, and the current VM instructions/budgets. It
returns a candidate, or an explicit unsupported result. A local independent schema
check, the existing package compiler, Ed25519 decoder, and transport round trip must
all accept the world before `--send` can start the existing Mac BLE sender.

Set `OPENAI_API_KEY` locally on the Mac (never paste it into chat or commit it).
For zsh, read it without showing or saving it in command history:

```sh
read -s "OPENAI_API_KEY?OpenAI API key: "
export OPENAI_API_KEY
```

Then, with the current v2 Runtime still running on Dell:

```sh
cd ~/rabbit-stack/experiments/x86-64-uefi-god-runtime-v2
python3 ask_world.py "Сделай кота розовым, пусть он бегает быстрее, мышку оставь прежней" --counter 2 --send
```

The default model is `gpt-4.1-mini`; override with `--model` or
`RABBIT_LLM_MODEL`. This makes one paid API request, with `store=false`, a 120-second
network timeout, and an 8000-output-token ceiling. Model credentials/access are
separate from this repository. No live API claim is made by the offline tests.

Without `--send`, the candidate is checked and saved without radio activity. Each
run saves intent, proposal, validated world, and a hash-bound report under ignored
`runs/world-*/`. For subsequent requests, use `--base runs/world-.../world.json`
to build on that world. The default base remains the checked-in cat/mouse example,
not an inferred copy of Dell's state. Increase counter beyond the last accepted
package in the current boot; this CLI cannot discover Dell's counter automatically.

The sender terminates on a matching ACK. Its failure/interruption records
`ACK-NOT-CONFIRMED`; a candidate passing local checks does not prove delivery.
The correlated receipt also does not independently prove the pixels or the semantic
accuracy of the LLM's interpretation. Existing development-key and receipt-authentication
limitations remain unchanged.

An externally generated proposal can enter the same checks without an API call:

```sh
python3 ask_world.py "Моё желание" --candidate /absolute/path/proposal.json --counter 2 --send
python3 verify_llm_world.py
```

Proposal format: `{"status":"ready","explanation":"...","world":{...}}`,
or `{"status":"unsupported","explanation":"...","world":null}`.
No generated code is executed. New sprites, objects, and reviewed VM behaviors
can change wirelessly; features outside this ABI return unsupported.
The text-builder profile also enforces the resident C core's nonzero resource ids
and 16-instruction tick limit, keeps movement magnitudes within 1..8, and declares
the existing fixed `121826` background rather than promising a palette-only change
to the background that this Runtime does not render.

API format reference: [OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs).
