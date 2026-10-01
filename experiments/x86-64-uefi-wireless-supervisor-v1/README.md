# Resident Scene/Anima + wireless native updater v1

Implemented candidate, **not installed or physically Bluetooth-verified**. The
installed Dell God Runtime v2 is unchanged and cannot acquire this supervisor
through its data-only VM. One separately approved bootstrap installation is still
required. This is not a promise of a last-ever flash rewrite.

## Ownership and authority

The immutable supervisor owns exact QCA RAM initialization, the single post-load
HCI reset, passive scanning, keyboard/Esc cleanup, 1500ms nonconnectable receipts,
physical GOP presentation, RAM staging, owner verification and driver lifecycle.
The resident boot-services driver owns Scene/Anima, world validation, sprites,
RGBA/RLE rendering and VM behavior. It receives only a 480x270 offscreen surface
through the reviewed ABI, not the hardware framebuffer. RUP2 and RUP3 world bytes
and their existing Mac world senders are unchanged.

Only separately owner-reviewed **native Scene drivers** can be replaced through
this ABI. The supervisor, root key, transport and hardware bootstrap remain
immutable; replacing those still requires another bootstrap version. No generic
claim of changing every driver, ABI or recovery mechanism wirelessly is made.

Native code is privileged, **not sandboxed**. It can defeat these cooperative
ownership rules, corrupt memory or disable interrupts/watchdog. An owner signature
authorizes exact bytes; it does not prove their safety. The LLM must not approve,
sign or send native releases autonomously. World releases still cannot execute
native code and use a different authority. Root-key rotation is not implemented.

## RRT2 is not a weakened interpretation of RRT1

The separately versioned `RRT2` / domain `Rabbit trusted runtime update v2\0`
binds target, base-driver SHA256, ABI 2, RSS2 state ABI, runtime counter, native
payload SHA256, **immutable active world-package SHA256**, and the owner's key.
Unlike RRT1, it does not externally sign every changing object position. Worlds
continue ticking throughout assembly. At the cooperative activation boundary the
supervisor exports an RSS2 live snapshot: signed package, object positions,
velocities, animation frames, tick and world counter. A new driver must import and
export the exact same canonical bytes before one health tick. A changed active
world revision rejects the release; migrating to another state ABI is unsupported.

The trial draws to a separate RAM surface. Failed init/health/unload validation
does not publish candidate pixels. Successful health swaps resident drivers,
publishes the trial frame and unloads the previous driver. Five-second firmware
watchdogs guard native entry/callback/unload calls. The older probe independently
observed an interrupts-enabled infinite-init reset; this integration has not
observed Dell recovery or arbitrary-corruption recovery. Failed authorized trials
consume their counter; exact latest retry returns a cached status without another
native effect. Incomplete world staging is discarded during engine replacement.

Everything is RAM-only. Power loss restores the compiled bootstrap, **not the
last downloaded driver or world**, and clears in-boot anti-replay counters. Cross-
boot freshness, persistence and cryptographically authenticated receipts remain
future work. Unauthenticated advertising is susceptible to interference/DoS.

## Transport and receipts

Worlds use existing RPv2. Native RRT2 uses actual supervisor RPv3 receive dispatch,
16-bit chunk sequence, six payload bytes, bounded 256KiB assembly and 32-chunk
checkpoints. Receipts remain sixteen-byte UUIDs with FNV checksum:

| Family | Meaning |
| --- | --- |
| RA / `11` | Existing world application or prefix receipt |
| RA / `22` | Native prefix assembled only; not authorized/applied |
| RA / `21` | Native driver committed, or exact cached committed retry |
| RA / `23` | Native rejection / failed trial; old driver retained |

Mac requires exact family, transfer, expected prefix/full FNV and receipt checksum.
Native final success is never inferred from a world or staging ACK. Receipt counters
carry the low 32 bits of the native counter and are informational, not authentication.
An ACK is correlation, **not authenticated Dell attestation**. Checkpoints can be
forged; the complete Ed25519 gate still prevents unauthorized native activation.

This remains slow advertising, not a fast file connection. The Linux reviewed
driver is approximately 25KiB; at 450ms/frame plus checkpoint waits its no-retry
minimum is about **35 minutes**. Mac sender prints the exact calculated budget and
has an overall bounded retry timeout. Improving throughput is a separate task.

## Reproducible checks (no physical writes)

From this directory:

```sh
python3 verify.py
python3 run_qemu.py --archive
python3 run_bootstrap_qemu.py --test-key-only --headless \
  --ovmf-code /usr/share/OVMF/OVMF_CODE_4M.fd \
  --ovmf-vars /usr/share/OVMF/OVMF_VARS_4M.fd
```

Host tests exercise C/Python signatures and profile separation, stale counters,
owner authority, PE acceptance, byte-exact live snapshot import, RUP2/RUP3 graphics
with guarded framebuffer bounds, unhealthy retention, lost checkpoint retry,
sender family checks and create-only reviewed signing / dry-run sending. QEMU
actually loads resident Scene drivers, commits two native replacements in one boot,
keeps world identity/counter and moving state, loses/retries receipts without
re-execution, retains exact state on failed health and rejects a tampered signature.
The **test harness substitutes embedded canonical frames for radio**, and is never
linked into the Dell bootstrap. Repeat driver, harness and bootstrap builds match.
Source/target/EFI/image/firmware and observations are archived under `evidence/`.

The real receiver separately displays `TARGET NOT FOUND; NO DEVICE WRITE SENT`
without the exact QCA device in QEMU. Its actual headless screenshot requires visual
confirmation; that script does not automatically certify screen text. Linux evidence
does not certify a different Mac-built EFI. MinGW and hash-pinned Monocypher are the
same existing toolchain; QEMU tests take explicit CODE/VARS paths on other hosts.

`diagnose_gate.py` emits QEMU-only entry markers and register/screenshot diagnostics;
its instrumented public-test-key image is never a production/physical candidate.
Early captures with the legacy assembly string helper showed only firmware startup;
instrumentation changed that observation, so timing alone was not accepted as an
explanation. The initialization caller-frame helper is replaced with bounded
supervisor-owned UTF-16 conversion/ConOut. The receive helper
is retained from the prior receiver. The unmodified selected bootstrap reached
the expected fail-closed screen. Headless capture waits 25 seconds and still requires
visual confirmation; no early screenshot is promoted to passing evidence.

## Owner provisioning and release workflow (not installation instructions)

The owner creates a random private key **on their Mac, outside the repository**:

```sh
mkdir -p "$HOME/.rabbit-owner"
python3 ../runtime-update-contract-v1/owner_key.py generate \
  --private "$HOME/.rabbit-owner/runtime.key" \
  --public "$HOME/.rabbit-owner/runtime.pub"
```

Never paste or commit `runtime.key`; raw private files are unencrypted and require
owner-controlled protection/backup. Generation refuses overwrite and creates the
private file owner-only. Public test keys are forbidden for production bootstrap
builds and physical sending.

Build the owner-provisioned candidate and reviewed visible engine revision:

```sh
python3 build_image.py --owner-public "$HOME/.rabbit-owner/runtime.pub" \
  --output /tmp/rabbit-wireless-supervisor.img \
  --module-output /tmp/rabbit-scene-revision-2.efi
python3 run_bootstrap_qemu.py --owner-public "$HOME/.rabbit-owner/runtime.pub"
```

These commands never unmount, erase or write USB. Before installation require exact
local observation, fresh device identity, owner approval and confirmed recovery.
No physical installer is provided here; the public test artifact is never installable.
After a separately gated installation and world delivery, reproduce its **exact**
JSON/counter package bytes using `save_world.py WORLD.json --counter N --output
/tmp/active-world.rup`. Use the world actually delivered, not a guessed scene.

`sign_runtime.py` requires private key, payload, active `--world-package`,
`--target-sha256`, `--base-runtime-sha256`, separately checked
`--reviewed-payload-sha256`, fresh native `--counter` and create-only `--output`.
Target/base/module identities come from the bootstrap report, then the previously
committed release. It never sends. `send_runtime.py RELEASE.rrt` requires public key,
the same world/target/base and `--minimum-counter`; default is **verified-not-sent**.
Only explicit `--send` compiles CoreBluetooth on Mac and advertises. Runtime and
world counters are independent. Key bytes never enter advertising.

Still pending: actual Mac Objective-C compilation, live QCA assembly/checkpoint/
application/rejection receipts, two engine swaps preserving a moving Dell world,
Esc cleanup, Dell watchdog recovery, and physically verified owner provisioning.
