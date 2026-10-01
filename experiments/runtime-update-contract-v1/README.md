# Runtime update contract v1 — HOST REFERENCE ONLY

The owner prioritized wireless runtime updates over installing graphics v3. This
experiment implements the signed envelope, ordered transport and a NON-EXECUTING
transaction model. **It is not a deployable UEFI supervisor. Do not send its frames
to the current Dell or install another image yet.**

Run in a terminal from the repository root:

```sh
python3 experiments/runtime-update-contract-v1/verify.py
```

## Separate authority

Runtime modules are target-specific trusted code, not portable worlds or LLM proposals.
The future supervisor needs a separately provisioned owner public key. The publicly
known development world key is explicitly rejected. The key in `verify.py` is also
public, test-only, and must never be installed. `owner_key.py` now generates random
owner-local keys and explicitly signs reviewed bytes; rotation/recovery remain pending.

A signature establishes authorization, not memory isolation, termination, driver
correctness or absence of disk/firmware writes. Native execution would expand the prior
no-native-code policy; the owner approved this option on 2026-10-01, retaining separate
release review/signing. A capability table alone is not a
sandbox for privileged machine code on this UEFI target.

## Exact RRT1 envelope

192-byte little-endian header (`<4sHHIIIIQ32s32s32s32s32s`), nonempty opaque payload,
64-byte Ed25519 signature. Signature input is domain
`Rabbit trusted runtime update v1\0` followed by exact header and payload.

| Field | Bytes | Meaning |
|---|---:|---|
| magic/version/flags | 8 | `RRT1`, version 1, reviewed-runtime flag exactly 1 |
| total/payload lengths | 8 | Exact sizes, complete envelope at most 262144 bytes |
| supervisor/state ABI | 8 | Exact accepted versions; migration unsupported |
| counter | 8 | Positive uint64, monotonic within a boot |
| target SHA-256 | 32 | Separately reviewed Target Pack |
| base runtime SHA-256 | 32 | Exact active runtime before replacement |
| payload SHA-256 | 32 | Exact complete candidate bytes |
| state SHA-256 | 32 | Immutable quiescent state snapshot |
| owner public key | 32 | Must equal externally provisioned key |

The model additionally requires a separately reviewed exact payload SHA-256. It cannot
establish how review was conducted, classify bytes as executable, validate PE/module
ABI or prove safety. Those are future backend gates. State export must happen at a
quiescent boundary; a changing live state cannot silently stand for this fixed snapshot.

## Model transitions, NOT fault recovery

`SupervisorModel.stage()` validates the candidate before recording a pending trial.
Old active bytes/state remain untouched. `resolve()` takes a correlated boolean health
result from a future trusted backend: success replaces active bytes; failure retains
the exact prior bytes/state. No candidate code runs and no health observation is produced.
Failed authorized trials consume their counter. Exact latest completed retries return
the same receipt without repeating activation. Receipts are marked unauthenticated.
Owner reboot restores the immutable bootstrap and clears volatile replay history.
Cross-reboot replay protection and persistence are not claimed.

A saved RAM copy cannot recover a native hang or corruption of supervisor memory by
itself. Actual execution needs a reviewed isolation/watchdog/fallback boundary and
observed fault tests. `reboot()` here is an owner-reset model, NOT automatic recovery.

## New reference transport; installed receiver unchanged

RP **version 3**, 16-byte UUID frames, six payload bytes, uint16 chunk sequence.
BEGIN carries little-endian uint32 length plus two zeros; CHUNK carries ordered bytes,
with canonical zero padding at the end; COMMIT carries whole-envelope big-endian
FNV-1a32 plus two zeros. Per-frame checksum follows the existing shape.
Checksums detect accidents; complete envelope signature grants authority.
Installed RP version 2 receivers cannot consume this protocol.

This supports up to 256KiB, not faster delivery: at six bytes per 450ms, 100KiB takes
about 128 minutes before receipts/retries. Streaming/checkpoint progress and measured
throughput remain required work. No Bluetooth calls or extra radio effects are added.

## Required continuation

1. The owner chose privileged reviewed native modules. The data-only world's
   no-native-code policy remains separate and unchanged.
2. Implement a resident supervisor owning QCA, transport, framebuffer and input, plus
   a real module ABI and RAM budgets. Avoid recursive full runtimes independently
   reinitializing/resetting the same controller.
3. Add streaming/checkpoints, separate receipts and quiesce/export/trial/resume.
4. Observe malformed images, failed initialization, hung trials and fallback in QEMU.
5. Gate an exact bootstrap image with an owner-local key. Current v2 lacks an updater,
   so its initial addition requires one separately authorized bootstrap installation.
6. Prove two successive runtime updates on Dell without USB movement, followed by a
   world update and power-off return to the unchanged bootstrap.

No last-ever flash promise: RAM updates vanish at power-off. Changes to the resident
supervisor/ABI may still need a separately reviewed recovery installation.

The first actual execution/recovery probe is now
`experiments/x86-64-uefi-runtime-supervisor-v1/`: signed native driver A -> B in RAM,
ordinary failure retaining B, and a watchdog-reset observation in QEMU. That sibling
probe is still not a physical Bluetooth updater.
