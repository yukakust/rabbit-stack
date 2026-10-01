# Signed native runtime supervisor v0.1 — QEMU ONLY

The owner chose separately reviewed privileged native runtime updates. This is the
first **executing** native update/recovery slice, not another world VM model. It does
not yet update the installed Dell over Bluetooth. **Never install this probe:** its
Target Pack forbids physical installation and it contains a public TEST key.

## Implemented

The unchanged supervisor assembles RP v3 frames in bounded 256KiB RAM, independently
checks RRT1 Ed25519/SHA-256/target/base/state/ABI/counter, and validates a restrictive
x86-64 PE32+ driver profile. The separate owner signature authorizes the signed payload
identity; the owner-local signer requires its explicitly reviewed hash. No per-payload
allowlist is compiled into the loader. This cannot prove a human performed a good
semantic safety review. It uses UEFI
`LoadImage` with a RAM `SourceBuffer`, then `StartImage`. The module is a boot-services
driver returning registered ABI v1 callbacks, not a full application that terminates.
Callback addresses must lie inside the loaded image's executable sections.

Initialization and one health tick run against a copied 16-byte fixture state.
Failure retains the exact prior state/driver; success commits and unloads the prior
driver. An exact latest completed retry returns a cached result without repeated
native effects. Trial callbacks and driver unload use a five-second firmware watchdog
in this QEMU Target Pack. The test module ABI is NOT yet the full Scene/Anima ABI.

`run_qemu.py` actually observes:

1. Baseline -> signed native A -> signed native B without reboot.
2. Exact B frame retransmission returns receipt-only; tick count remains unchanged.
3. Signed failed initialization modifies trial state, but B's identity, handle and
   exact state are retained.
4. Tampered signature and stale counter reject before `LoadImage`.
5. Signed incompatible module ABI leaves B active.
6. Signed initialization emits `NATIVE HUNG INIT ENTERED` and enters an infinite loop
   with interrupts enabled. Firmware watchdog resets QEMU; unchanged bootstrap returns,
   with no automatic relaunch of volatile updates.

No real radio traffic or physical device participates. Guest probe uses no persistence,
internal-disk, firmware-setting, radio or `ExitBootServices` API. QEMU disk snapshot mode
and a disposable OVMF variable store protect host originals. Firmware itself can mutate
that emulated variable store during boot; all-firmware write-freedom is not claimed.

## Run in the terminal

```sh
python3 experiments/runtime-update-contract-v1/verify.py
python3 experiments/x86-64-uefi-runtime-supervisor-v1/verify.py
python3 experiments/x86-64-uefi-runtime-supervisor-v1/run_qemu.py
```

Requires Python `cryptography`, host C compiler, MinGW GCC/objdump, QEMU and compatible
OVMF. Other hosts pass explicit `--ovmf-code` and `--ovmf-vars` paths. Crypto sources
use the same hash-pinned Monocypher fetcher as God Runtime v1. SHA-256 has independent
`hashlib` differential tests. Nine host tests cover signatures, unsafe/wrong PE
profiles, world-key rejection, key permissions/no-overwrite, C frame loss/checkpoint/
retries, large ordered transfer and SHA block/padding boundaries. The earlier model's
ten tests remain unchanged. The QEMU runner additionally repeats complete image builds
and refuses nondeterministic artifacts. Logs/screenshots and source/contract/target/
EFI/image/firmware identities are bound into ignored run reports and archived evidence.

## Security limits

Native modules are privileged trusted code, **not sandboxed**. Signatures and callback
checks cannot stop native code from corrupting the supervisor, disabling interrupts or
watchdog, or directly using firmware/storage. Observed watchdog recovery covers the
explicit infinite-loop fixture, not arbitrary malicious native faults. Reset loses
RAM updates/worlds and returns to bootstrap, not the latest in-RAM world. Migration,
authenticated receipts and cross-reboot replay protection are not implemented.

Only fixture keys are used here; no production owner key was generated/provisioned.
`runtime-update-contract-v1/owner_key.py` can generate random owner-local private keys
(raw, unencrypted, mode 0600, outside Git), refuses overwrite/unsafe permissions, and
signs only explicitly supplied reviewed payload identities. It neither sends nor
executes code. Account/disk protection, backup and key rotation remain owner concerns.
The LLM may propose code but must not approve or sign native releases by itself.

## Remaining Bluetooth / Dell work

- Actual Mac/QCA frame adapter and bounded checkpoint/result advertisements. C framing
  is implemented; live radio handover is not.
- Scene/Anima resident module ABI, framebuffer/input/QCA ownership and quiesce/resume.
  Existing v2/v3 full EFI applications are not drop-in modules for the fixture ABI.
- Measured throughput improvement: six bytes/450ms means about 128 minutes per 100KiB
  before retries. Enlarged framing is not faster transport.
- Owner-local key provisioning, exact Mac QEMU gate, separately authorized bootstrap
  installation, observed Dell watchdog support, and two actual wireless native updates.

Unsupported watchdog must reject trials before native execution. Initial updates stay
RAM-only and vanish on power-off. No last-ever USB promise, no persistent-write authority,
and no physical installer is provided. Working Dell remains unchanged on God Runtime v2.

Primary reference: [UEFI boot services](https://uefi.org/specs/UEFI/2.10/07_Services_Boot_Services.html)
for image loading/lifecycle and watchdog semantics.
