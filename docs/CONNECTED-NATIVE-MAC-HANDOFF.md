# Mac agent takeover: first connected native engine update

## Request and vision

The Russian-speaking owner wants Codex to operate the Mac terminal directly,
not ask them to paste each command. Continue the already requested first wireless
native engine update, preserving the walking cat. Global vision: spoken/text
intent -> LLM candidate -> deterministic validation -> signed world/components
-> fast Bluetooth delivery -> visible effects on an OS-less Dell, without moving
the USB for ordinary world AND compatible engine/driver changes.

Read repository `AGENTS.md` and `HANDOFF.md`. This document supersedes older
PENDING statuses only where explicit latest physical observations are recorded.
Do not start an unrelated Wi-Fi/network runtime or graphics rewrite.

## Access boundary

The originating agent operates `/home/yuka2/rabbit-stack` on Linux. It has NO
access to the owner's Mac, Bluetooth, private key or physical Dell. A Linux
subagent inherits the same limitation. Run the following owner operations only
from a Codex session actually attached to the Mac repository and terminal.
First read-only check: OS, cwd, git status, required files and available space.
Never pretend Linux tests sent packets or observed the physical screen.

Owner Mac repository:
`/Users/yukakust/rabbit-stack`.
Working directory for commands:
`/Users/yukakust/rabbit-stack/experiments/x86-64-uefi-connected-supervisor-v1`.

## Current physical state and counters

- Dell OptiPlex3060, QCA Rome USB0CF3:E009 interface0, UEFI, no OS/internal drive.
  It DOES have RAM. Dedicated USB remains boot medium; do not remove/rewrite it.
- Owner installed the gated connected supervisor; synchronous interrupt-IN20ms,
  sole USB reader, root-owned staging, ABI3 combined Scene/radio driver.
- Current reported world: detailed ginger cat walking, RUP3 world counter2.
- Current assumed active driver: bootstrap driver1. No connected native update
  has been sent/applied in this boot. Native counter0; first release uses1.
- Confirm the owner has NOT rebooted Dell or sent another world/native release
  since the latest observation before proceeding. Ask one short question only if
  this is unclear; do not silently restore a world or infer current base by time.
- All downloaded worlds/drivers/counters are RAM-only. Reboot loses them and
  restores an EMPTY baseline. Do not reboot Dell as a routine troubleshooting step.

## Latest evidence

Owner previously received exact counter1 cat receipt and confirmed walking cat.
Next counter2 test deliberately stopped after receiver-confirmed8400/33381 bytes.
A new Mac process resumed SAME saved session at8400 and received exact applied
SHA256/session/counter receipt. Remaining transfer15.525s, NOT full-package timing.
This verifies controlled same-boot resume, not all unexpected failure recovery.
See `evidence/dell-connected-resume-owner-observed.json` under the experiment.
Receipts/UUIDs are correlated, NOT authenticated device attestation or encryption.

On Mac the owner pulled commit1cd1752 and ran
`python3 run_qemu.py --graphics-world` successfully. Actual UEFI loader/drivers
with MOCK USB observed TWO swaps, exact retry/no second apply, failed health and
bad signature retaining exact world/driver, then reviewed interrupts-enabled
hung-init watchdog return. Mac QEMU report:
`runs/q-aqcn0ciu/report.json`. This is emulator evidence, not a physical swap.

Owner then successfully PREPARED the following plan. It is NOT signed or sent:

| Binding | Exact value |
|---|---|
| Plan file | `/tmp/connected-native-trial-1.json` |
| Reviewed plan SHA256 | `2b483eb704db585f5d3e841d4fcc787826b78465e8c4c3609c075abd43290835` |
| Installed report | `runs/owner-gate-s0bxi9d8/report.json` |
| Installed image SHA256 | `d9561b29d983a9ec09fe48e99c99c726597ec31d069f944c288f52ec2746a9a9` |
| Installed EFI SHA256 | `1736818811292d6af54e3f77cefee37b610b7a661a033fabd87283695d210378` |
| Baseline driver1 SHA256 | `02e3a839f5c4320754a7afa6fecc6ca626475d36c360f3ed66cdd6db30e7b4c3` |
| Payload | `runs/owner-gate-s0bxi9d8/driver-revision-2.efi` |
| Payload driver2 SHA256 | `0954cba928440d50716749e0c01306d7621bbdb52800e05cfa6c39c033ebd816` |
| Target SHA256 | `363d751288df7b47295f9c7a5250c3b41db24efd1a43a4bd348f00744c6bc7e9` |
| Active world file | `/private/tmp/connected-cat-world-2.rup` (`/tmp` alias) |
| Active world SHA256 | `cc545d03b210bd3ebdef2141368bd6daa90cc3ec966b7cfb357afc53d30d7645` |
| Owner PUBLIC file | `/Users/yukakust/.rabbit-owner/runtime.pub` |
| Owner public fingerprint | `58744820acd038de35d01eaf6afbad2aa4bb4e4022c8078d4e665270d41f36b4` |
| Private key location, NOT contents | `/Users/yukakust/.rabbit-owner/runtime.key` |
| World / native counters | `2` / proposed `1` (independent) |

Never recreate the plan, regenerate the key, rebuild the bootstrap or substitute a
freshly compiled driver to work around a missing/mismatched artifact. Stop and
report a mismatch. Public fixture keys cannot authorize physical native updates.
The private key must stay owner-local outside Git, owner-only regular file.
Never print/read its contents into conversation, copy it to Linux, or request upload.
Pass its path only to the reviewed local signing helper.

## Next actions for the Mac agent

1. Inspect live access and files read-only; preserve unrelated work. Verify plan
   SHA256 equals the reviewed value above. Check free space: Mac twice exhausted
   storage during this work. Do not delete user data to clear space automatically.
2. Explain expected effect and risk briefly: same walking cat/live state, blue
   line at scene bottom = engine2, intentional Bluetooth disconnect/reconnect.
   The owner requested implementation/testing; signing/send are scoped to this
   exact reviewed trial. Honor host permissions/approval UI. If takeover prompt
   doesn't authorize local owner-key signing and send, obtain that narrow approval.
3. Sign once on Mac with this terminal command (no send):

```sh
python3 prepare_native_trial.py \
  --sign-plan /tmp/connected-native-trial-1.json \
  --private /Users/yukakust/.rabbit-owner/runtime.key \
  --reviewed-plan-sha256 2b483eb704db585f5d3e841d4fcc787826b78465e8c4c3609c075abd43290835
```

   Helper rechecks installed image/report, production sources, owner fingerprint,
   payload and current world. It signs RRT3, independently verifies signature and
   saves create-only `/tmp/connected-native-trial-1.rrt` and
   `/tmp/connected-native-trial-1.session.json` (kind2/native counter1).
   If outputs exist, inspect them and preserve the session; do not erase/re-sign
   or silently create another nonce. Partial output/disk errors need diagnosis.
4. After valid signed outputs, operate the Mac terminal directly:

```sh
python3 send_file.py /tmp/connected-native-trial-1.session.json --send
```

   Capture sender output to an ignored run log using the tool/terminal's output,
   without leaking key bytes. Prefer read-only inspection of helper source before
   signing if needed. Avoid concurrent senders/managers. A write response/pending
   state/disconnect is NOT final application. Require exact final receipt.
5. Ask the owner only for physical-screen observation: still walking cat? blue
   bottom line? `OWNER DRIVER COMMITTED; RECEIPT RETAINED FOR RECONNECT`?
   They should not need to copy shell commands. Record receipt and reported
   appearance separately; do not call them authenticated attestation.
6. If transfer stops/times out, preserve the SAME session and Dell power. Query it
   again within bounded retry policy; do not regenerate session/increase counters
   to hide unknown outcome. Collect Dell diagnostic lines. A native swap closes
   the old radio, unloads old driver only after its callback returns, attaches new
   driver, and retains final receipt in immutable root across reconnect.
7. On rejected health, expect old world/driver retained. On uncertain radio close
   or attach/unload fault, watchdog may reboot and lose RAM. Stop, report actual
   state, do not assume cat survived/retry with stale base. Physical repeated
   controller-reset/reattach and Dell watchdog behavior remain unverified.
8. Only after first success, plan a second compatible live revision/return and
   a separately reviewed failed-health test. Do NOT send hung/unhealthy fixtures
   during this initial trial. No permission for arbitrary native code or media
   overwrite is inferred. Record evidence and update handoff, then scoped commit/push.

## Safety/architecture and implementation map

Root: owner verification, PE loader, exclusive dispatch, staging/receipt, GOP,
timers/watchdog. Combined owner-updatable driver: Scene VM/renderer/assets plus
HCI/ACL/L2CAP/ATT/GATT/UEFI USB. RRT3 binds target/base/payload/world, ABI3/state2,
domain-separated Ed25519 and native in-boot counter. Data worlds use a separate
development Creator key, which cannot authorize native code.
Health imports/exports RSS2 package/positions/velocities/frames/tick/world counter
on copied pixels. Failure retains previous driver/world. Privileged native code
is NOT sandboxed; signature/watchdog cannot guarantee recovery from memory
corruption, disabled interrupts/watchdog or arbitrary malicious owner code.
Immutable root/ABI changes may still require separately approved bootstrap work;
do not promise last-ever USB use. No internal storage/OTP/firmware settings writes.

Key files in `experiments/x86-64-uefi-connected-supervisor-v1/`:
`prepare_native_trial.py`, `send_file.py`, `release.py`, `build_image.py`,
`driver.c`, `loop.c`, `connected_abi.h`, `verify.py`, `run_qemu.py`, `qemu_test.c`.
Lower layers: `experiments/ble-connected-file-transfer-v1/`.
Signing-key safeguards: `experiments/runtime-update-contract-v1/owner_key.py`.

Latest Linux checks:13 owner/helper tests,28 actual world/GATT/link tests,18 mock
USB tests; ordinary and full-ginger QEMU swap/watchdog scenarios pass. Owner Mac
full-ginger QEMU and exact preparation pass. Actual connected native update is
still PENDING: no signed release/session/final native receipt reported yet.

Preserve unrelated Linux edits: `.gitignore`, root `README.md`, `BIB10.md`,
`experiments/x86-64-uefi-qca9377-network-runtime-v0/`. Do not commit them as part
of this takeover. Mac may have its own unrelated changes: inspect first.


## Mac-executed first native trial — 2026-10-03

Agent pulled main at 7e32a47 on the actual owner Mac. Owner confirmed same Dell
boot, walking cat and no intervening world/native update. Exact reviewed plan and
saved installed artifacts passed checks; 4.2 GiB free. Reviewed local helper signed
once, independently verified RRT3, and created the saved native counter1 session.
Private key contents were not printed or copied; no USB/reboot/storage operation.

Release SHA256: `d7f19e81d91c27f1a35f7f53aaf7e6dfcc1a70280e1a559cb2de00fa497a1def`.
Mac sender delivered 36640 stream bytes, disconnected after COMMIT, reconnected
and obtained exact SHA256/session/counter FILE APPLIED receipt. Exit0; elapsed
27.261 seconds including discovery/reconnect. This is actual Mac Bluetooth sender
evidence, not QEMU or authenticated device attestation. Physical screen confirmation
(cat motion, blue bottom line and committed diagnostic) is still PENDING.

Evidence: `experiments/x86-64-uefi-connected-supervisor-v1/evidence/dell-connected-native-trial-1.json`
and adjacent `dell-connected-native-trial-1-sender.log`. Preserve
`/tmp/connected-native-trial-1.session.json`; do not re-sign/re-send as a new trial.
Native counter1 now has an exact applied receipt; do NOT assume baseline driver1
or reuse the initial plan for another release. Second compatible transition and
separately reviewed failed-health physical test remain PENDING.

Owner subsequently confirmed the blue bottom line appeared («появилась»).
Explicit post-update walking-cat confirmation remains pending; do not claim
exact live positions/frames from screen observation alone.


## Exact return to driver1 — 2026-10-03

Owner explicitly confirmed the cat continued walking after the first engine2
update, authorizing continuation. First evidence now records motion plus blue line.
Agent extracted exact36352-byte driver1 from hash-verified installed image at
byte offset2207840 (SHA25602e3a839...), without rebuilding/substituting a module.
Reviewed return plan SHA256c5ad9e59bcefbfacc0c0b3c37ec22e1882f864b996e1304ba9658a8a29cc916a.
Signed and independently verified counter2, base0954cba9... -> payload02e3a839...,
unchanged world counter2. Release1f2ffb4e0ea0d413a435d9d57396308899d123c3bce793a58516710b5ef17c32.
Actual Mac sender observed timeouts with SAME-session receiver resumes10800/14400,
then deliberate native disconnect/reconnect and exact applied receipt. Exit0,
69.404s including reconnects. Owner screen confirmation of disappearing blue line
and continuing cat remains PENDING. Active base is now driver1/nativecounter2,
not driver2/counter1. Evidence and log: connected evidence/dell-connected-native-trial-2.*.
Preserve `/tmp/connected-native-trial-2.session.json`.

Separate deterministic failed-init test is prepared, NOT signed/sent:
`/tmp/connected-native-trial-3.json`, SHA256
 d065e518dffc2e88b3b090c9cccbbe128d831d703aef8818dba6745b18b850bb.
Exact driver3 SHA256dd22921330b2f3f577c858b37a67b7bdf4f0930bcfc379611d5f7de3a46c4bc0
was extracted from verified prior Mac full-ginger QEMU fixture image at2204032;
it matches installed gate module3 and its source returns1 from scene_init.
No hung fixture is used. Counter3 would be consumed on authorized health rejection;
active base should remain driver1. Screen/base confirmation precedes this send.
Mac-only sender now recognizes complete error2 rejection ONLY when exact
session/length/digest/counter match; explicit rejected output exits2, never applied.
Actual C file/GATT rejection and malformed-identity regression pass;14 connected
host tests and14 world/GATT host tests pass; Apple sender compiles. Receiver C,
installed image, native modules and file protocol are unchanged.


## Failed-init transfer interrupted before COMMIT — 2026-10-03

Owner confirmed blue line disappeared after return and authorized continuation.
Agent rechecked installed gate/source/world, reviewed separate counter3 failed-init
plan SHA256d065e518dffc2e88b3b090c9cccbbe128d831d703aef8818dba6745b18b850bb,
signed once with reviewed owner-local helper, independently verified signature and
saved SAME `/tmp/connected-native-trial-3.session.json`.
Release606594a7de56a8252eccf8759d45048851a4c79936a64f4eb7faf3662a0b62d6.

Physical transfer confirmed12960 bytes, disconnected at sender14160 with timeout,
then SAME session/UUID reported receiver offset0. Sender originally only warned and
continued from0; agent stopped exact Bluetooth process after noticing regression.
A second timeout occurred at13440 before stop. No COMMIT/phase3/final receipt appears
in complete sender log; deterministic unhealthy init was NOT executed/tested.
Sender exit241 reflects agent termination. Current screen/base/world/counter are
UNCONFIRMED after regression. Cause UNKNOWN; zero prefix is NOT proof of reboot.
No agent reboot/USB/key output. Evidence and log: connected
`evidence/dell-connected-native-trial-3.json` and adjacent sender log.

STOP before any retry: obtain current physical Dell scene/diagnostic observation.
Do not assume driver1/worldcounter2/nativecounter2 survived; do not silently resend
world, regenerate session or change counters. Preserve exact trial3 session and Dell
power. Check installed driver's root-owned staging reset path against observation.

Mac sender now fails closed immediately on receiver prefix regression instead of
silently restarting. Source SHA25635d2935b879b91de0eae0914a0764b21b14c68146255f3af17bb132499584b9f;
compile-only Apple check passed; no sender radio re-run after this edit. Installed
receiver/root/native module bytes unchanged. Failed-init physical rejection remains
PENDING, while first/return exact application receipts and visible line changes are
recorded separately. User has confirmed walking cat after first update only.
