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


Owner follow-up: «сцена исчезла» after trial3 interruption. Scene loss is observed;
reboot/watchdog cause is NOT confirmed. Asked whether current display is Rabbit
empty baseline/diagnostics, Dell/UEFI, or black/no-signal, plus exact lines.
Read-only source inspection: root arms5s watchdog around radio poll and fatal()
prints failed stage then intentionally waits for watchdog. Bootstrap imports an
EMPTY RSS2 snapshot. This makes reboot-to-empty a plausible explanation, not a
physical diagnosis. Ordinary rg_disconnected resets MTU only, not root staging.
No further sender, world restore, timeout/watchdog change or USB action performed.


## Owner photo, read-only status and attempted world recovery — 2026-10-03

Owner photo preserved at connected evidence/dell-connected-native-trial-3-scene-loss-owner.png.
It shows blue blank scene area and live radio diagnostics/advertising, no visible
fatal/watchdog line. Do NOT call this proof of reboot or failed-health execution.

Agent added Mac-only `--query-only` (reads RFS without BEGIN/DATA/COMMIT/ABORT).
Actual status: same trial3 nonce, STAGING13440/36640, receiptcounter0/error0;
previous applied nativecounter2 is no longer retained by file service. Suggests
root state reset but does not authenticate boot identity or query active driver/world.
Then explicit `--abort-only` first verified exact nonce+length/STAGING, sent ABORT
only, read same-session IDLE/received0/length0. Actual query/abort logs archived.
No cancellation of PENDING/applied/rejected/foreign sessions is allowed.

Agent announced restoration, verified prior saved world2 bytes exactly match
cc545d03..., attempted SAME `/tmp/connected-cat-session-2.json` with no new signing
or counter. Timeout at1920/33381 then another phase0 disconnect; no reconnect,
COMMIT or final receipt. Agent stopped scanner (exit241). World recovery NOT
successful. Log archived as evidence/dell-connected-cat-world-2-recovery-interrupted.log.
All senders stopped. RSSI observations-80..-87; signal weakness is observed, not
proven cause of root state loss. Asked owner to move Mac within0.5–1m of Dell.

Next: read-only query of SAME WORLD2 recovery session when Mac is nearby; inspect
current screen/diagnostic text. Preserve both saved world2 and trial3 session files.
Continue exact world restoration only after actual current status is understood;
no native trial3 retry until world/base/native-counter state is established. No
USB/reboot/firmware operation authorized or performed in this recovery.

Mac sender compile passes and3 focused C/helper checks pass; CLI rejects conflicting
radio modes, missing bundles and staging-stop combined with query/abort before
radio. Actual query and exact abort confirm functionality; receiver/root/native
code and bootstrap/media bytes unchanged. Sender source8d87f4b2..., validator6793d285...,
helper modes documented in connected README. No claimed failed-init rejection.


## Nearby Mac cannot query receiver — 2026-10-03

Owner moved Mac nearby («рядом»). Read-only service scan discovered no Rabbit;
agent stopped scan without writes. Added optional query-only cached peripheral
UUID connection, retrieved known F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF, but no
connect/status callback arrived before60second query timeout. No BEGIN/DATA/COMMIT
or ABORT in either attempt; all radio processes stopped. Cause remains unknown;
old READY TO CONNECT text alone cannot prove current receiver liveness. Current
screen observation requested, no new owner response yet. Near scan/cached logs
are archived in connected evidence/dell-connected-cat-world-2-near-*-query.log.

Recovery plan is concrete: one OWNER-AUTHORIZED restart using unchanged installed
USB, observe bootstrap advertising baseline, Mac read-only query, then restore
SAME prior signed worldcounter2 package/session and require exact receipt plus
walking-cat observation. This is NOT authorized yet: initial request explicitly
forbade Dell reboot. Do not restart/reset/rewrite media or retry native modules
without that decision. No claim of successful restoration or failed-health test.

Mac query source07b09af8... compiled on Apple SDK,2 focused helper checks pass;
invalid UUID and cached query combined with send reject before radio. Cached
connection allowed only with --query-only; read-only queries bounded60seconds.
Receiver/root/native modules, installed image, keys and USB unchanged.


## Owner reboot and exact world2 recovery via smaller writes — 2026-10-03

Owner authorized/performed reboot («перезагрузил»), then Mac read-only query observed
IDLE/zero nonce/received0/length0/receiptcounter0. SAME old signed world2/default240
transfer reached receiver21600, timed out at sender24720, reconnected and observed
SAME nonce but prefix0. Sender stopped before COMMIT. This reproduces loss while
sending ordinary world on fresh boot, with no connected native COMMIT in this boot;
no proof of exact watchdog/error cause. No second manual reboot requested/performed.

Controlled sender-only100-byte DATA payload comparison after read-only query
confirmed SAME world2 STAGING0/33381/counter0. Exact original package and session,
no re-sign/new counter/nonce/media/receiver change. Actual run had no disconnect,
exact SHA256/session/counter receipt, exit0 and58.173s. Owner walking-cat/no-blue-line
screen confirmation requested and still PENDING. This was a new transfer from0,
not a nonzero retained resume; restores original world bytes, not lost live state.
Evidence: connected `evidence/dell-connected-cat-world-2-recovery.json` and four
associated reboot-query/default-loss/small-query/small-restore logs. One success
is NOT proof that smaller writes fix every fault or fragmentation is the cause.

After screen confirmation, SAME saved signed trial3 has been revalidated for
current bootstrap driver1/world2 and assumed nativecounter0 (owner reboot and
world-only operations). Do not re-sign or create new nonce/counter to hide failure.
RRT3 permits gaps previous<proposed; existing counter3 is still3 and valid from0.
Post-reboot review `/tmp/connected-native-trial-3-post-reboot-review.json`, SHA256
34bb8be3bf2a44e7ea185fc7884cfb6949825ceeb0fa4bdf8d9db0c9b985cb7b.
Current counter/base basis is chronological evidence, not authenticated device query.
Same release606594a7..., payloaddd229213..., base02e3a839..., worldcc545d03...,
no native retry yet. Expected deterministic rejected receipt counter3 with driver1/
cat retained; use100-byte writes for the next separate failed-init trial. No hung
fixture and no further swap/reboot. Physical rejected-trial outcome remains PENDING.

Optional `--chunk-bytes` bounds/conflicting modes checked before radio; Apple sender
sourcee08bc5f9... compiles;14 actual C world/GATT checks pass. Native/root/receiver/
USB unchanged. All radio processes stopped after exact world recovery receipt.


## Native3 smaller-write attempt stops before COMMIT — 2026-10-03

Owner reported «Код есть, синей линии нет.» after exact world2 receipt. Context
suggests cat present/no blue line; movement not explicitly reconfirmed. SAME
signed native3/session was checked against post-reboot review34bb8be3..., then
sent with100-byte DATA payloads. Four timeouts; retained resumes300/700/1400.
Sender stopped at bounded reconnect limit, exit1. Read-only query confirmed
STAGING1500/36640/error0/last file receipt counter2. No COMMIT, module did not
execute, failed-init rejection still NOT physically verified. Exact session ABORT
confirmed IDLE/received0/length0/counter2. All radio processes stopped.

Query-only now also reads connected RSSI before file status. Apple compile and
actual read-only query succeeded: connectedRSSI -84dBm, discovery -93dBm; IDLE
and retained filecounter2. Mac WiFi channel8/2.4GHz/20MHz, no network modification.
Shared-band interference is a hypothesis, not an established cause. Asked owner
whether5GHz or wired internet is available for a controlled comparison; answer
pending. Do not blindly resend or reboot. Logs/hashes and limits preserved in
connected evidence/dell-connected-native-trial-3-small.json and four archived logs.
No new signature/counter/nonce, receiver/module/bootstrap/media change.


## Controlled Mac pacing comparison and world recovery — 2026-10-03

Owner asked agent to investigate Bluetooth without waiting for alternate WiFi.
Read-only baseline now connectedRSSI -67 rather than prior -84dBm, without network
change. Both unpaced and50ms-paced same-native3 3000-byte prefixes succeeded.
Exact abort between short trials reset staging only and preserved worldreceipt2.
Long unpaced same-native3 transfer resumed3000, confirmed15300, disconnected at
sender17300, reconnected with receiver0. Read-only query showed filecounter0 and
connectedRSSI -61. Stronger signal alone did NOT prevent root-state loss. BEGIN
and disconnect do not reset filecounter in reviewed C; root reset/reinitialization
or corruption suspected, exact failure/watchdog stage still unproven. No COMMIT
or bad-init module execution. Exact partial-session abort confirmed IDLE/counter0.

SAME original signed world2/session with100-byte payloads and50ms delay staged
33000/33381 without disconnect; normal immediate sender resumed33000, sent381
remaining bytes and got exact applied SHA/session/counter2 receipt (finish1.282s).
World restored by receipt; owner walking-cat screen confirmation pending.
Then SAME signed native3/session from0 with100-byte payloads/50ms delay staged
35000/36640 without disconnect. Subsequent read-only query confirms retained35000
and previous world filecounter2, connectedRSSI -66. Still STAGING, NOT APPLIED.
All sender processes stopped; keep Dell powered. Do NOT re-sign/change nonce or
counter. Native rejected receipt remains pending; screen-motion confirmation
requested before continuing remaining1640 bytes and deterministic failed-init test.
No requested/manual reboot, network modification, USB/media writes or native COMMIT
in this comparison. Earlier root-state loss was observed, cause unproven.

Sender-only --data-delay-ms1..100 is restricted to explicit --send plus staging
limit; default sends remain unchanged. Delay timers guarded by connection
generation/peer/characteristic/offset, so stale callbacks cannot resume a new
connection. Apple compilation and actual short/long pacing tests pass;2 focused
helper checks pass (existing staging-stop source assertion updated for scheduler
call);4 invalid diagnostic modes rejected before SDK/radio.18 mock USB checks
pass, NOT a physical USB fix. No receiver/root/native code change.
Evidence/log hashes: connected evidence/dell-radio-pacing-comparison.json and11
associated logs. Two long successes support a candidate mitigation, not proven
causation or general reliability. Precise reset cause needs physical diagnostics.


## Exact native3 rejection receipt retained — 2026-10-03

Owner confirmed walking cat («кот ходит») before final native3 COMMIT. SAME signed
release606594a7.../saved sessionfbf8c737... reverified against unchanged installed
gate, owner PUBLIC key and exact restored world2. No private-key access/signing.
Read-only query confirmed retained35000/36640/counter2; same-session normal100-byte
sender resumed35000, sent remaining1640, COMMIT, and exact REJECTED receipt
SHA/session/counter3/error2 (exit2, expected rejection,2.254s, no disconnect).
New connection read-only query independently reverified exact60-byte REJECTED
status: received=length36640, counter3, releaseSHA606594a7..., exact nonce.
Thus authenticated native trial was consumed and rejected; this is a physical
Dell result. Generic error2 does not attest which load/health callback failed.
Expected known fixture returns1 from scene_init; no hung fixture used.

Native counter3 is NOW consumed. Next fresh native release must use at least4
and current retained driver1/world2 basis, with refreshed review. Reusing the
same rejected receipt/session is idempotent; do not re-sign/relabel counter3.
Owner post-trial walking-cat/no-blue-line confirmation requested, PENDING.
All radio processes stopped; no USB/media/network change or manual reboot.
Evidence: connected evidence/dell-connected-native-trial-3-rejected.json plus
three archived final query/finish/requery logs; earlier failed attempts preserved.
Paced staging followed by small unpaced tail succeeded, but radio reset cause
and general reliability remain unproven. Sender source unchanged this turn.


## Owner confirms post-rejection scene — 2026-10-03

Owner: «ходит и линии нет». After exact native3 rejection and retained receipt,
cat continues walking and blue line absent. Physical rejection/scene preservation
trial complete; exact live frame/tick continuity unmeasured. Nativecounter3 consumed,
worldcounter2/current driver1 retained; next fresh native>=4. Evidence updated.
Next work: data-only text intent -> checked V3 candidate -> existing world authority
-> saved connected session -> paced staging/tail -> exact receipt -> current world.
World development authority remains distinct from owner-native key; do not silently
claim worlds are owner-authorized or change installed bootstrap.


## V3 text-world path ready for first physical intent — 2026-10-03

Added ask_connected_world.py: reuse existing subscription-only Codex runner through
generic propose_json; strict small objects/programs schema, unchanged V3 sprites/
palette/identity, exact current-world hash, deterministic Python bounds/signatures
and actual installed runtime C activation/240 ticks/render sentinels before radio.
world_check.py pins/rechecks crypto and gate runtime source; no owner-private key
access. Installed world authority remains PUBLIC development Creator, distinct from
owner-native. Do not silently claim owner-authenticated data worlds.

Persistent state initialized against exact current ginger-cat JSON/packagecounter2
and installed gate in ignored runs/text-world/state.json (pending=null). Saved
worldcounter and nativecounter are separate; nativecounter3 consumed, next fresh
native>=4. Proposal/delivery run saves exact package/session;100-byte/50ms-paced
whole-stream staging stops before COMMIT, next SAME-session call commits. Current
state advances only on exact applied receipt. Unknown delivery retains same pending
nonce/counter/bytes and blocks fresh intent; --resume --send. Never-sent drafts may
be explicitly discarded; ambiguous delivery cannot. Atomic save/single state lock.

6 new host flow checks pass, including actual C healthy speed edit and invalid MOVE
without boundary handling rejection, stale/extra/boolean proposal rejection,
unknown delivery/counter preservation, exact receipt gating and packet/session
substitution rejected before radio; only never-sent draft discard permitted.15 existing LLM tests pass after generic runner
refactor. Whole-stream STAGING/zero callbacks until explicit COMMIT tested in actual
C core/validator. No runtime/bootstrap/native source change.

Real local Codex smoke proposal: vx1->2 only; exact cat art/palette/program retained,
worldcounter3 candidate package d47182e6..., C240ticks checked. No radio; smoke
draft explicitly discarded with archive preserved in runs/text-world-smoke. Actual
Dell/current managed state staysworld2. Host evidence and saved proposal in connected
evidence/connected-text-world-host-ready.json and speed-proposal.json. Asked owner
which first text change to send (double speed, second same cat, or keep scene);
response pending. No physical text-intent orchestration claim yet. Missing mouse
art/background changes are currently unsupported, not fabricated. Voice and
Creation Inventory extension remain subsequent work.


## First text-to-art connected world receipt: cat wears red hat — 2026-10-03

Owner intent «давай коту наденем шапку» authorized graphic change/delivery. Used
imagegen skill/built-in tool: transparent red knitted beanie reference, then edit
original 2x2 cat walk source to wear same hat in4 poses. Copied both generated
source images into V3 assets; prompt/provenance saved. Existing import_cat.py does
RGBA format conversion only, no painted/keyed alpha; source1536x1024 RGBA, alpha0..254.
Imported4 distinct128x85 poses/shared256 palette/logical64x43, unchanged original
objects/programs/vx1. AI edit is visual preservation, not identical outside-hat
pixels. Local indexed PNG/GIF previews and user output copies saved.

Extended ask_connected_world.py with explicit --world-candidate for generated V3
art worlds; shared prepare_world uses same strict compiler/Python signature/pinned
C240ticks/render guards/session/counter/receipt gate. Small LLM patch schema remains
unchanged; no native fields accepted.6 existing flow checks pass after refactor,
plus added asset native-field/legacy-world rejection test passes (7 total).

Actual currentworld2 package binding checked; pre-send read-only status retained
old rejected native3 receipt, no active foreign staging. Hat worldcounter3 package
35017 bytes SHA8761fa34ce8af4365864f7b668cd66e5a3ecede02ac81a5a0edabbcbf37b71c3.
Saved session in runs/text-world/edit-0866els1. Entire35049-byte stream staged with
100-byte payloads/50ms delay, stopped before COMMIT. SAME session next connection
resumed35049 and got exact applied SHA/session/worldcounter3 receipt; commit
connection1.694s, no disconnects. Managed current state atomically advanced to
world3/current hat world, pending=null, only after exact receipt. Nativecounter3
remains consumed; next native>=4 must bind NEW active hat signed world.

Owner screen hat/walking-cat confirmation requested, PENDING. Evidence/log hashes
in connected evidence/dell-connected-cat-red-hat.json; generation provenance V3
assets/cat-red-hat-walk-v1.provenance.json. No USB/media/firmware/network changes,
manual reboot, owner-private key access or native update. Current world authority
remains public development Creator. Do not claim authenticated device attestation
or physical screen from preview. First text/art managed delivery receipt physically
observed; exact screen outcome still pending.


## Connected controller recovery and global roadmap — 2026-10-03

Owner authorized global reliability/common execution work («делай»), not another
scene modification. Added read-only preflight and exact receipt reconciliation to
ask_connected_world.py. Local lost COMMIT response can finish from exact saved
session/hash/counter/full-length applied receipt without replay. Saved confirmed
prefix survives across process invocations/partial logs; Mac sender receives a
minimum prefix before DATA/COMMIT to catch reset between query and BEGIN. Prefix
loss, foreign active session, exact rejection, application pending and unreachable
receiver remain explicit distinct statuses. At most two resumable attempts per
call; no new nonce/counter or reboot used to hide uncertainty. Locks inherited
through Python/native senders retain custody if a parent exits; competitor fails
busy. --status emits common local JSON; --status --query adds read-only receiver
state without promoting current state. Partial logs are archived even on timeout.

16 orchestration checks and16 C/native/transport host checks pass. Changed sender
compiled on actual Mac; real Dell returned retained exact applied hatworld3 receipt.
Separate local simulated lost-response fixture (current2/pending3) reconciled via
ONE real read-only Dell query to isolated current3/pending=null. No new world/native,
BEGIN/DATA/COMMIT/ABORT, media write, reboot, network change or owner-key access.
Managed runs/text-world/state.json remains byte-identical, actual hatworld3.
Do not call this an induced physical radio failure: local uncertainty was simulated.
Source hashes/logs/results: connected evidence/connected-world-control-recovery.json.
Radio reset cause and sustained reliability are still unproven. Common controller
supports bounded text data edits and supplied generated V3 asset worlds; automatic
artwork planning/native upgrades, voice and inventory integration remain unfinished.
Next global milestones and acceptance criteria: docs/CONNECTED-WORLD-CONTROL-PLAN.md.
Nativecounter3 separate/consumed; next new native>=4 bound to active hat signedworld.
Owner hat appearance confirmation supersedes older pending observation; movement
after hat update was not explicitly reconfirmed.


## Unified controller, Mac app and new physical trials — 2026-10-03

Owner expanded authorization to finish all five global steps, collecting required
human actions into one batch; USB rewrites authorized but no media write or Dell
reboot performed. New world_control.py/world_planner.py/engine_route.py combine
structured LLM plans, bounded original sprites, checked existing inventory/assets,
persistent journal/history, reviewed native background family and shared receipt
transport. Entire world candidate C gate precedes native private signing. Engine
source binds installed gate; exact payload deterministic PE/QEMU gate precedes
owner-key match/signing. Arbitrary generated native code remains unsupported.

Actual physical exact APPLIED: native4 background203050 payloadb5ece667..., native5
restored driver1 background121826 payload02e3a839..., world4 cat+mouse intentionally
stopped staging3000/35202 and resumed SAMEsession to application, world5 restored
initial hat. This is controlled physical staging stop, not unexpected RF failure.
Owner screen observation after these new trials pending. Current confirmed state
world5/native5. QEMU uses mock USB and is recorded separately from physical logs.

RabbitWorld.swift/build_control_app.py produce ignored local Rabbit World.app:
text, voice, resume, version restore and separate OS permission setup. Loopback
server requires ephemeral Bearer token0600; text/voice share same checked path.
12 new controller tests and16 transport checks pass, including actual C asset
checks, invalid-world-before-native, no-op, crash-after-receipt history recovery,
idempotency/pending session and authenticated loopback source routing. GUI built
and codesign verified. No tests masquerade as live microphone verification.

GUI text speed request saved checked world6; exact APPLIED still pending. Initial
child sender TCC abort due missing Bluetooth purpose fixed in Info.plist. Later
tccd AUTHREQ_PROMPTING for org.rabbit.world-control BluetoothAlways; read-only
queries time out before DATA. Pending exact sessiona817c934... retained; no new
nonce/counter/reboot used. Voice implemented but OS speech/mic permissions and
live utterance-to-receipt require owner. Russian recognizer on-device unavailable
in CLI diagnostic, falls back to Apple Speech service after permission.

One owner batch: allow app Bluetooth/speech/mic; resume saved text operation;
then speak a mouse request and observe physical scene. Do not mark full goal
complete before actual voice delivery and owner observation. Full hashes/reports/
logs/plans: connected evidence/world-control-2026-10-03/summary.json. Current world
authority still public development Creator; native uses owner key never logged.
Historical radio reset root cause and sustained reliability unproven. V1 inventory
exists; local V3 highres assets LicenseRef-Not-Assigned not shareable V1 cards.
Updated roadmap: docs/CONNECTED-WORLD-CONTROL-PLAN.md.


## GUI-created request world6 reconciled and applied — 2026-10-03

App service verified idle, exact pending request/session retained. Common CLI
resumed it from already Bluetooth-authorized Codex terminal, without replacing
package/session/nonce/counter. Physical exact APPLIED worldcounter6 package
b616a128f37e96add5478cb8196879ed9bc44d69d64df823bb7eaf2c9daf1d4e;
session SHAa817c934b65a11c957fe1105dc0e9f0f0242d0d2c5b6bb6b95be5f484a9c25c6.
World canonical SHAcf4c5e7695a567cdde11bfc01f57d850035abd409d0f204f8d45a98f8660a8f4,
catvx2, original hat/background retained in checked data. Nativecounter5 unchanged.
App AX shows Мир6/готов к изменениям and Применено; pending cleared. This proves
GUI-generated request plus common transport, not yet app's own Bluetooth access.
OS app Bluetooth/speech/mic permission and actual live voice/owner Dell observation
remain pending. User no longer needs to press resume. Evidence adds gui-world6-
applied/report.json preserving earlier pending reports separately. Goal active.


## Live voice, smooth mouse and general drawing route — 2026-10-03

Owner granted Rabbit World Bluetooth/speech/microphone, then spoke «Добавь коту ещё
пожалуйста мышку». Actual app request sourcevoice33465d109f924f4ab1d4ccaf66b6bc00
passed common C/signature/transport gates and physical exact APPLIED world7. This
supersedes pending live voice evidence; owner disliked pixel8x8 mouse. Two smooth
requests correctly returned UNSUPPORTED under former limited32x32/16color planner.

Added checked existing smooth128x128 mouse asset to planner catalog, and generic
created_drawings strict schema: bounded layered ellipses/rects/cubic/quadratic
curves, antialiasing3x with Pillow, max128x128/4frames, no executable XML, URLs,
files or scripts. New art is still portable indexed RGBA data, not native code.
Old plans remain compatible with absent created_drawings default[]. Replacement
uses new sprite id and prunes unreferenced old art; existing used colors retained.
14 tests pass including transparency/curve C gate, malformed/injected input
rejection, detailed mouse C gate and packet budget. Real Codex proposed an original
curved tree; rendered and passed actual C checker NOT SENT to Dell. This is not
image_gen quality for arbitrary generated curves and not a truecolor framebuffer.

App service restarted only after verified idle, binary/permissions unchanged.
Normal GUI request replaced existing mouse with smooth checked source40x40, y50.
Physical exact APPLIED world8; app AX shows World8 ready/APPLIED. Cat indexed
frames, every used color, object/speed and all programs byte-identical to world7.
Nativecounter5/background121826 unchanged. Mouse has one pose: moves with old VM
program, no separate anatomical paw cycle. Shared palette mapping recorded; source
license remains notassigned, not advertised as licensed Inventory v1 export.

Reused existing image_gen mouse PNG/prompt/provenance; no new image generation
this turn. Evidence/logs/plans/hash: connected evidence/detailed-art-2026-10-03.
No USB writes or Dell reboot. Owner visual confirmation of new smooth mouse and
continuing hat cat still pending; do not claim it from app receipt or host preview.


## 2026-10-03 — first fullscreen procedural 3D city on connected route

Owner requested to proceed with 3D. Added experiments/x86-64-uefi-city-v1:
portable signed RUP4 camera + max64 house/box/road records, fixed-point renderer
with depth buffer and near-plane clipping. Explicit privileged city Target Pack
binds checked GOP after attach; candidate init never writes physical display.
Active tick enlarges480x270 canonical frame and returns exact top-left crop for
unchanged root presentation. No immutable production source changes, USB writes,
Dell reboot or private-key output. This is simple flat-shaded software graphics,
not native-resolution detail, arbitrary meshes, textures, physics or measured FPS.

Actual physical receipts: owner-signed native6 payload
476b9977feaf74b988fb2f0f970590a4c08e93f755a996808ce2159892fc3535;
world9 first street; world10 GUI + real LLM add sixth house preserving ALL prior
buildings/camera; world11 GUI + real LLM camera forward200cm preserving ALL
buildings. Current world11/native6, no pending operation. Authoritative data,
camera/packages/history persisted Mac; app restarted and current city retained.
Physical fullscreen appearance/performance owner observation PENDING; asynchronous
question asked, no reply yet. Do not claim screen appearance from APPLIED receipt.

Controller accepts bounded city_world plans through same text/voice, C/signature,
shared paced Bluetooth100byte/50ms/COMMIT and exact correlation pipeline. Historical
V3 data remain restorable in city driver; restore V3 BEFORE rolling back to an old
V3-only driver. Block native background-only route while city capability installed
because that route would remove city snapshot support. City sky/ground are data.

New UI: city command examples and owner-confirmed Dell reboot recovery checkbox +
button. city_recovery first requires explicit owner reboot observation AND fresh
zero read-only receiver state, exact installed bootstrap + empty-boot QEMU gate,
rebuilds exact reviewed payload before owner signing against bootstrap1/EMPTY
world, then restores latest saved city using new monotonic native/world counters.
Never infer reboot from RF loss. Interrupted two-stage recovery retains sessions,
blocks edits and resumes via normal button. Physical reboot/recovery NOT exercised;
user/agent must first verify actual Dell appearance, then a separately coordinated
recovery trial. Yukabox sync/persistent Dell disk/automatic boot discovery not done.

19 host/controller tests pass, including no city before applied reviewed profile,
city add/camera/history restore, bounded/mixed-route rejection, owner+fresh reboot
guards, exact two-stage recovery resume keeping counters/sessions. Actual C120ticks
+16 adversarial max64 camera/geometry frames under ASan/UBSan pass. Exact same
native6 payload reproducibly built and executed in real UEFI QEMU both from a V3
world and EMPTY bootstrap: fullscreen outside old surface + coherent crop, city
application, legacy data/engine rollback, unhealthy/bad-signature rejection pass.
QEMU uses mock USB and public fixture keys; never physical Bluetooth evidence.
Source verifier experiments/x86-64-uefi-city-v1/verify_city.py (NO SIGN/SEND).
Evidence: experiments/x86-64-uefi-city-v1/evidence/2026-10-03; README there describes
loading/recovery and limitations. Binaries ignored runs, owner key stays local.

## 2026-10-03 — generic 3D actors, roof cat, physical native7/world12

Owner confirmed houses visible on Dell and requested a sitting roof cat with a
waving dangling tail and a1-second smile every10 seconds. Former city4 correctly
rejected this. Added separate reviewed `x86-64-uefi-city-v2` profile: portable
signed RUP5 actors, ellipsoid/box/cone parts, per-part sine translation and timed
visibility. Roof cat is checked reusable data (36 parts), not a renderer opcode.
Planner supports either checked actor_assets or complete bounded schema5 data.
Max4 actors/48 parts each/96 total; max6816-byte packet. Existing buildings/camera/
colors and actor data are preserved on unrelated edits; V3/city4 histories restore
with increasing counters. No arbitrary mesh/texture/physics support yet.

Native7 exact APPLIED payload:
2c1bebad9394f3c46427767c063135980b599a7279a84a77dc68697097ab3a0c.
Mapped PE image3887104 bytes fits immutable4MiB bound. First960x540 prototype
exceeded that bound and failed QEMU BEFORE signing/sending; accepted version renders
800x450 and enlarges to checked GOP, returning coherent old-surface crop.
Target-only TSC clock calibrated by two50ms UEFI Stall samples on attach; candidate
init/trial do not access clock/display. Animation phase restarts on world/native
installation. Actual native/city4/city5 snapshots, clock motion, fullscreen/crop,
V3 data/engine rollback and unhealthy/bad-signature rejection passed actual UEFI
QEMU for both legacy-world and EMPTY bootstrap. Mock USB, never physical radio.

Native7 owner signing followed installed identity/source gate, current-world C
check, exact QEMU payload evidence and two matching fresh rebuilds. Immutable
production sources, USB, Dell disk/firmware and reboot untouched; no key output.

Normal app + real LLM request a83860a9190a4117b0c274b7527e8e19 composed schema5 with
roof-cat actor at620,510,600 yaw0 on house2 facing camera. Buildings/camera/sky/
ground exactly equal world11. Physical world12 exact APPLIED, app AX World12 ready.
World SHA fa5a3250633f2bbbd288d947be567c2c5db8e3395033da99b765edf0a0f5cc74.
Receiver receipt confirms application, not display appearance/timing. Owner visual
cat/tail/smile question pending; do NOT claim those observations from host/QEMU.

Mac app-launched helper initially waited for TCC and timed out before scanning:
existing Rabbit World Bluetooth toggle ON, but old granted cdhash8a40566... differs
from rebuilt city UI a5c5c74... . Same saved GUI request/session resumed through
agent CLI, exact receipts obtained; no new plan/package or reset. The existing
permission renewal in System Settings asks Touch ID; user action question pending.
App's own Bluetooth setup now reports available, but app-child helper revalidation
still needs checking after the pending system-auth sheet is resolved. Do not reset
TCC, weaken security, request/print a password, or infer that the toggle alone
proves the rebuilt app's helper can access Bluetooth. App binary not rebuilt here.

21 controller checks passed (existing19 plus actor add/history/preservation and
city5 two-stage recovery).6 actor codec/planner/actual C checks passed; ASan/UBSan
120 frames+16 adversarial camera/geometry frames. Isolated C smile boundaries
9999/10000/10999/11000/20000ms and tail frames250/850ms checked. Physical animation
accuracy and reboot/recovery NOT exercised. Recovery dispatches saved actor profile,
requires exact EMPTY fixture + explicit owner reboot + fresh zero receiver BEFORE
signing, and retains two-stage sessions. Current authoritative state Mac world12,
native7, no pending operation. Evidence: city-v2/evidence/2026-10-03. Profile runs
ignored; owner key remains local. Service was safely restarted after idle to load the final legacy-city-plan actor
preservation fallback. It currently runs from the already-authorized Codex agent
context; Rabbit World reconnected and AX shows world12 ready with full history.
App auto-launch after this service exits still requires completing/checking the
pending Rabbit World TCC renewal. No TCC reset or security bypass was performed.

## 2026-10-04 — Internet topology and isolated UEFI network receiver

Owner clarified Yukabox is in Poland, Dell and its monitor are in Georgia. The
image must travel over the Internet to the mini-PC Dell's existing video output.
Mac is command/control only. Owner explicitly authorized implementing the native
network receiver while preserving the old city. No cross-country display cable.

New source: experiments/x86-64-uefi-network-viewer-v1. Builds, fixture serving and
actual UEFI QEMU/sanitizer execution were done on Yukabox, not Mac. Pinned iPXE
Realtek driver includes physical10EC:8168 ID; test VM usesRTL8139 with no ROM.
Baseline firmware exposes neither SNP nor TCP4. Driver creates SNP, still no TCP4.
Small source adapter exposes existing asynchronous iPXE Download protocol and
cooperative DHCP instead of inventing TCP/IP. Pending operations progress via
Download.Poll; callbacks are bounded and closed before freeing/unloading.

Authenticated portable RPF1 RGB24/RLE frame contract: max640x360,1152128wire bytes,
Ed25519 over header+body, exact stream ID and increasing sequence. Entire frame
shape/signature validated before output/state writes. Production session/key
binding is not yet implemented; public zero-seed fixture has NO deployment power.
Remote image-signing key must never become owner executable-signing authority.

Real saved UE5.8.3 Radeon frame6e4f9de0... was fetched via DHCP/HTTP by the UEFI app,
decoded and presented in GOP; screenshot viewer region RGB hash exactly equals
FFmpeg-converted UE input. Green neighbouring fixture survives; it is NOT the
actual city. Bad signature/oversize/cancellation/replay preserve accepted state.
Config closes, driver unloads successfully, final SNP count0.293 real C checks
pass under ASan/UBSan. Evidence: network-viewer-v1/evidence/2026-10-04.

NOT a physical Dell or Poland→Georgia test; NOT live capture/video/FPS evidence.
Standalone app has test blocking waits, serial diagnostics and VM poweroff.
Not integrated into immutable-root city native profile, not signed or sent.
Need confirmed Ethernet to Internet router (owner question pending), reviewed
cooperative city+viewer profile, exact normal+EMPTY native gates/current-world
preservation, lifecycle/failure checks and reachable authenticated Yukabox endpoint.
Native7 mapped3887104bytes already nearly fills immutable4MiB; iPXE file303616bytes
leaves tiny margin. Account for parent PE, child code and bounded heap separately;
do not silently modify bootstrap limits. Production NIC binding must be restricted;
test ConnectController(AllHandles) is only in an isolated VM. See new README for
loading/recovery prerequisites and dependency source/licence pins.

No Dell reboot, USB/disk/firmware write, physical radio transmission, owner key
access/output/copy. Mac state remains native7/world12, no pending operation; city
map and snapshots retained. Loopback-only fixture stopped after verification.

## 2026-10-04 — owner chooses internal Wi-Fi, no Ethernet cable

Owner explicitly requested internal Wi-Fi after confirming no cable. Do not keep
waiting for Ethernet or infer an OS/disk installation. Current requested network
work supersedes the old unrelated-network warning scoped to the earlier trial.
New source: experiments/native-wifi-qca9377-v1. No working driver is claimed.

iPXE source has no ath10k/QCA9377 implementation; simply changing Ethernet PCI ID
cannot work. Pinned Linux ath10k PCI/CE/BMI/WMI/HTT reference sources and official
linux-firmware were downloaded on Yukabox; hashes/licence/notice provenance saved.
Implemented bounded host firmware/board TLV preflight and fail-closed exact board
selection.179 tests passed including real firmware/container database. Firmware
candidate751436bytes, WLAN.TF.2.1-00021-QCARMSWP-1, WMI-TLV4/HTT-TLV3, code swap
absent. Its compatibility with this physical revision remains unknown. Multiple
board calibrations include Dell1028:1810; never infer this Dell's subsystem from
the presence of that entry. Without exact physical identity selection rejects.

Next: read-only fresh PCI subsystem/revision/BAR inventory inside a separately
reviewed native profile, preserving city/Bluetooth. Then bounded PCI/DMA/CE/BMI
port, physical target identity, firmware RAM startup/WMI/HTT, scan/security/DHCP.
Mock tests and host container checks are not QCA9377 hardware emulation. Prove DMA
stop/callback cancellation/detach/rollback before owner-native gate. Existing4MiB
image bound needs explicit memory/asset-delivery design; don't append751KB to
native7 or modify immutable root limits silently. Reuse authenticated frame core
after a real packet interface exists, and separately establish WAN endpoint.

SSID/security-mode question pending; do not request password in chat. Future local
credential input, no credentials in LLM/evidence/Git. No credential consumer yet.
No firmware upload/execute, PCI/MMIO/DMA action, physical scan/association or new
native signature/transfer performed. Native7/world12 and old city remain unchanged.
Evidence: native-wifi-qca9377-v1/evidence/2026-10-04. Future native loading remains
subject to exact current-identity/normal+EMPTY QEMU/code/lifecycle gates; no USB,
disk, reboot, owner-key-copy or persistent-firmware changes implied.

Also implemented pure `pci_identity.c` decoding exact target/class/subsystem/
revision/32-or64bit BAR0, with unchanged output on rejection; positive fixtures
pass actual ASan/UBSan on Yukabox. Standalone typed UEFI PCI Read/GetLocation probe
was compiled and run in OVMF QEMU:6PCI handles, correct TARGET COUNT0 (RTL8139 VM).
No PCI write/MMIO/DMA/radio. This is an ABI/negative-branch test, NOT physical
identity evidence or a QCA hardware model. New pci-report/serial/host logs saved.
Before active city integration remove VM serial/poweroff harness; keep only the
bounded read routine and deterministic decode. Native identity/data lifecycle/
size gates are still required, and no physical profile has been signed or sent.

## 2026-10-04 — superseding status: physical PCI diagnostics applied, native9/world12

The preparation-only/native7 statements above are historical. Signed on Mac and
sent via the existing saved-session paced Bluetooth workflow: native8 and native9
both have exact correlated APPLIED receipts. Current payload SHA256
`18e271a20a61005bb67e15622177886446980777bf24eaaa207b0e03c3ca791b`, native counter9;
world counter12/packageSHA6414d1bae588acfef261d8c6befc8fc1edb96fb76892a33c47f8d3b2c05bb180
unchanged; native_pending=null. Installed bootstrap/owner gate still unchanged.
Mapped image3895296bytes within immutable4MiB. No reboot/USB/disk/firmware/OTP change.
Owner secret used locally only; never printed/copied to Yukabox.

Read-only `pci_collect.c` runs at driver attach. No VM UART/poweroff code is
included. Exact current-world/source/pinned-crypto double rebuilds, host sanitizer
checks and normal+EMPTY real UEFI city/fullscreen/clock/snapshot/rollback/rejection
gates ran on Yukabox. The exact VM candidate's PCI snapshot was read through mock
USB ATT (QCA absent in OVMF, not hardware emulation). Candidate preparation/signing
uses `native_route.py` and binds reproduction/source/evidence/session/base state.

Native8 added a fourth file-service characteristic; Mac still returned only its
old three and two diagnostic attempts failed. Native9 preserves file handles1..7,
adds primary service UUID ending0005 at8..10 and read-only characteristic UUID
ending0006 at10. `read_pci.m` successfully fetched QPD1/128bytes from the same
peripheralF45BFCB2-ABC2-AB4E-BB0F-310A54D424AF. No reader write API, no attestation.
Physical snapshot:16handles, one168c:0042, subsystem1028:1810, PCI revision0x31,
0000:02:00.0, 64-bit BAR0=0xd1000000, command0x0100 (memory and bus master disabled).
PCI revision is not SoC/BMI revision. Exact board-catalog match8124bytes,
SHA256b2713b77c725b0ff81af75c85c3aeba97885d0f40174f715b1e39d5a9d50f4e7;
still a candidate, not calibration upload authorization before SoC/BMI validation.

Initial port components `uefi_port.c`/`wake_core.c` and `wake-target.json` are
implemented. They exclusively claim PCI IO, check fresh identity/BAR descriptor,
allow memory-only enable and bounded allowlisted IO, cooperate with a monotonic
deadline, and retain ownership after ambiguous writes/failed cleanup. Wake clears
before attribute restoration and protocol close. Host ASan/UBSan mocks and COFF
ABI checks against pinned UEFI headers passed on Yukabox. These components are NOT
linked into native9 and have NOT performed physical PCI/MMIO writes. DMA/CE/BMI,
firmware startup/WMI/HTT/scan/WPA/DHCP remain unimplemented. Wi-Fi does not work yet.

Remote workspaces: `/home/yuka/rabbit-world/wifi-city-profile-v1` and
`wifi-city-profile-v2` (tracked source snapshot, no owner secret). Evidence under
`experiments/native-wifi-qca9377-v1/evidence/2026-10-04/diagnostic` contains exact
gates/reproduction, both delivery logs/reports, raw/decoded physical PCI,
failed first read attempts, board candidate and initial port checks. Original
native8 source variants are archived there; current source implements native9.

NEXT: owner screen/animated-tail observation pending (async question already sent).
Before physical MMIO bring-up finish a separately gated profile with validated BAR
extent, lifecycle cleanup/rollback/coexistence and SoC chip-ID telemetry, using the
initial port. Then build bounded DMA/CE and BMI get-target-info before selecting
and uploading firmware. Raw firmware751436bytes, xz476792bytes exceed262144byte
native transport cap: design owner-verified chunk assets in RAM; do not enlarge
immutable root limits. SSID/security-mode answer still pending; no password in
chat/LLM/evidence/Git. There is no credential consumer yet. Continue on Mac for
control/signing/Bluetooth, all builds/render/tests on Yukabox. Preserve old city.


## 2026-10-04 — native10 physical wake probe, identity still unresolved

Owner confirmed native9 city visible and roof-cat tail moving: «виден и двигается».
`bringup_build.py` integrates the port into a separately reviewed city profile.
One-shot attach claims exact1028:1810/PCI31, validates BAR, enables memory only,
requests wake, cooperatively polls for at most1second, reads chip-ID and clears
wake/restores attributes/closes PCI IO. Reattach cannot repeat hardware writes.
Candidate init/health stays hardware-free. Failed cleanup retains ownership and
blocks unload; it must not silently release a live device. No bus master, DMA,
chip reset, firmware/OTP, root/USB/disk changes or Dell reboot.

Yukabox passed15 ASan/UBSan production-code lifecycle scenarios, port ABI gates,
normal+EMPTY actual EFI city/snapshot/clock/restore/bad-update gates, two identical
rebuilds bound to current world12 and pinned crypto. OVMF QCA-absent coverage is
separate from physical evidence. BAR validation corrected before signing:
EDK2 GetBarAttributes AddrRangeMax can encode alignment; checked extent uses
base+AddrLen, with translation rejected. No physical operation used the old check.

Exact payload `a721f3fcab4749f4fda5ad98018cdf0fc2d2d6396a68991f07e372a1caabfe60`
was locally signed on Mac and delivered as native10, saved session
`pci-native-uis35sur`. Transfer staged53024bytes; COMMIT disconnected, then the
sender reconnected to the SAME session and obtained exact SHA/session/counter
APPLIED. State native_pending=null, world12 package unchanged. Secret stayed Mac.

Fresh physical QPD2/160-byte read from the same peripheral reports BAR extent
2097152, original PCI attributes0, stage3/error3 (chip-ID rejected), raw chip-ID0,
cleanup complete. The code reaches CHIP validation only after RTC state ON;
PCI open/BAR/memory-enable/wake therefore advanced to that point. Do NOT claim
supported chip revision, BMI version, firmware compatibility or association.
PCI config bytes were captured BEFORE the wake operation; cleanup status, not
those earlier bytes, reports restoration/close. This is Bluetooth telemetry,
not device attestation. Native10 city/tail visual observation is pending.

Pinned Linux uses qca6174_regs for QCA9377, RTC_SOC0x800 + CHIP_ID0xf0 =0x8f0.
Its normal probe reads identity AFTER chip reset, while ours deliberately does
not reset. Linux's supported-revision table permits revision0, but a zero raw
read here is kept inconclusive rather than treated as proof. Next: establish
PCI power/read/reset ordering and a bounded chip-only reset/recovery policy,
then CE/DMA/BMI get-target-info; do not blindly reclassify zero as verified or
upload guessed firmware. Preserve city/Bluetooth and exact loading/rejection
checks for every subsequent physical native candidate. Full Wi-Fi still needs
firmware RAM startup, WMI/HTT, scan/security and DHCP. Firmware asset chunk
transport is also required within unchanged native/bootstrap bounds.

Evidence: `experiments/native-wifi-qca9377-v1/evidence/2026-10-04/bringup`
contains gate/reproduction hashes, pre-update receipt/owner observation, full
saved-session delivery records, raw/decoded physical telemetry and a manifest.
Remote workspace: `/home/yuka/rabbit-world/wifi-bringup-v1/source`.


## 2026-10-04 — native11 power diagnostics, D0 confirmed; cleanup audit corrected

Full goal remains working Wi-Fi: verified chip/CE/BMI, exact firmware RAM loading,
radio scan/security, DHCP/two-way traffic and reconnect without city/BT failure.
Owner explicitly authorized continuing all these stages. Association remains false.

Read-only `power_build.py` profile reads conventional PCI config256 at attach;
`power_core.c` bounds capability traversal (48 aligned entries, loop/duplicate/
truncation rejection). QPD3/144 preserves file handles1..7 and diagnostic service.
Host sanitizer gates cover all255 capability pointers, D3, malformed/missing
chains and actual collector+ATT. Normal+EMPTY real UEFI city/snapshot/clock/
restore/rejection and current-world two-rebuild checks passed on Yukabox.
Locally signed and delivered native11 (`pci-native-y8kegeov`), exact correlated
APPLIED, world12 unchanged. No PCI/MMIO writes, power transition, reset or DMA
in this profile. Evidence under `evidence/2026-10-04/power`.

Physical: PM capability0x40, PMCSR0x0000 => D0; PCIe capability0x70,
LinkControl0x0143 => ASPM enabled. D3-to-D0 transition is NOT the next justified
step. Device/subsystem/BAR unchanged. PCI command now0x0102, bus master disabled.
This contradicts a stronger interpretation of native10 cleanup telemetry:
Attributes(Set0)/CloseProtocol returned success, but MEM command bit stayed on.
Do not describe API-success telemetry as proof that actual PCI settings restored.
The native10 log is retained as observed; this new finding supersedes its earlier
restoration conclusion. Before reset/CE add actual command capture/readback and
bounded16-bit fallback restoration (never32-bit write into W1C PCI status).
Failed readback must retain ownership and prevent unload. Preserve real initial
command rather than blindly trusting cached UEFI attribute flags.

NEXT: command lifecycle repair and adversarial API-success/stale-command tests;
then separately gated cooperative QCA-only cold/warm reset/readiness/SoC-ID using
pinned ath10k ordering. No PCIe accesses during reset settling intervals; recovery
must deassert/reset-settle before releasing ownership. Native11 city/tail visual
observation remains pending, distinct from exact Bluetooth receipt and telemetry.
SSID/security mode still needed before association; no password in chat/LLM/logs.
All native compilation/rendering/tests remain Yukabox; Mac control/signing/radio.


## 2026-10-04 — command lifecycle correction, host/ABI verified only

`uefi_port` now captures real original16-bit PCI Command, verifies actual
memory-only enable and real command restoration. Attributes(Set) success alone
is insufficient. On mismatch, Write16 restores exactly the captured command
without writing PCI Status W1C; a subsequent read must match. Failure/ineffective
write keeps claim and memory_attempted until successful retry; unload remains
blocked. Tests simulate stale-success attributes, config read/write errors,
successful-but-dropped config writes and an initially enabled MEM bit with cached
attributes0. Unrelated command bits/status remain preserved. ASan/UBSan and COFF
PCI Write ABI checks passed on Yukabox; evidence/2026-10-04/command-lifecycle.

This correction is NOT loaded on physical Dell yet. Current native11/world12
is the read-only power profile. Next separately gated native reset profile must
include this correction and fresh D0/resource/identity checks; no extra native
probe sent merely to repeat the same zero chip-ID. Native11 confirmed MEM0102,
so preserve the actual starting command rather than claim historic0100 restored.
Full Wi-Fi goal remains active and incomplete. SSID/security and post-update
city/tail observation questions are pending; password stays out of chat.


## 2026-10-04 — cooperative cold-reset core host gates passed

Previous goal turn was concrete progress: physical native11 D0/ASPM evidence
changed the next action and actual PCI command cleanup was corrected/tested.
Current continuation revalidated native11/evidence/current sources. Added
`reset_core.c/h`, `reset-target.json`, adversarial `reset_test.c` and
`verify_reset.py`. Based on pinned ath10k PCIe-local GLOBAL_RESET0x80008,
assert and deassert each require20ms without accesses to the claimed Wi-Fi
PCI device. Target minimum extent is0x8000c, not wake-only0x80008.

Errors on reset writes are ambiguous: ownership starts before assertion and is
not released until deassert readback confirms clear after settling. Poll has
bounded3-attempt recovery; a stuck asserted bit, error/all-ones readback, or
ineffective clear retains ownership. Explicit recovery retries deassert/verify,
never another assertion. Reverse-clock and expired-deadline cases still require
safe cleanup. Host mocks test no early access, ambiguous assert/clear, stuck bit,
read failure/all-ones, retries, repeated poll and invalid inputs. ASan/UBSan and
freestanding x86 COFF passed on Yukabox with source-bound evidence/reset-core.
A successful write is NOT proof that reset asserted; current component proves
ordering/recovery in mocks, not physical reset or useful post-reset identity.

NEXT concrete implementation: native reset adapter/profile. Fresh exclusive
PCI/D0/BAR identity and actual Command checks first; safely wake without treating
zero chip-ID as already verified. Gate allowlisted GLOBAL_RESET RMW, retain the
PCI claim through reset settling and recovery. After reset revalidate actual
PCI configuration/resources/memory-only state before further MMIO; do not trust
pre-reset cached flags. Observe FW indicator and repeated chip-ID. Integrate
reset lifetime into close/unload and candidate rollback, preserve city/BT, run
normal+EMPTY/current-world/source/native size gates before signing. Include the
command lifecycle correction; hardware-free candidate health/init stays so.
Native11/world12 remains physically installed; NO reset profile has been signed,
sent or executed yet. No DMA, firmware RAM upload, scan/association/DHCP yet.
Full original Wi-Fi/reconnect goal stays active. SSID/security-mode and post-
update city/tail observation pending; they do not block independent port work.


## 2026-10-04 — native12 physical reset/identity verified, chip revision1

Previous goal continuation was progress (reset component code/host+COFF gates).
This turn integrated that component and actual Command lifecycle correction into
`reset_probe.c`/`reset_build.py`, preserving city and existing file service.
Fresh exclusive PCI/identity/BAR/D0 checks precede wake/reset; post-deassert20ms
checks revalidate PCI identity/BAR/no bus master and memory decode. If reset
clears MEM, memory-only enable is repaired and read back before further MMIO.
Close during either reset settling window cancels forward work, retains claim,
finishes deassert/settle and then verifies Command restoration. Failed clear
or readback retains ownership. Explicit close can request bounded cleanup retry
without another assertion. Reattach never repeats one-shot hardware work.

Eleven actual generated-production host scenarios passed ASan/UBSan (UBSan halt):
normal/zero-before-reset/unsupported chip/D3/no target, stuck clear/ambiguous reset
write, post-reset memory loss, zero-after-reset, and cancellation during either
settling window. Port/component gates and normal+EMPTY real UEFI city/fullscreen/
clock/snapshot/rollback/rejection gates passed on Yukabox; current-world/pinned-
crypto two rebuilds matched. Earlier host test fixture failures were corrected
before this exact profile was signed; no failed fixture profile was sent.

Exact payload99463fa0068204926a2d4988e2d5dfe62c5f2ed2f22ed96a3f36dfc50ea8c67e
signed locally Mac, delivered saved session `pci-native-23kicu1u` (56096bytes).
COMMIT disconnected/reconnected to SAME saved session and exact APPLIED. Fresh
query confirms native counter12/session matches. World counter12/package remain
unchanged; native_pending=null. No root/USB/disk/OTP/Dell reboot or key copy.

Physical QPD4/196 read: stage5/error0, chip-ID003821ff, supported SoC revision1,
reset DONE/error0/owned=false, original/readback GLOBAL_RESET0, D0/PMCSR0,
BAR extent2097152, original/active Command0102, original attrs0200, no revalidation
error, cleanup complete. Actual Command restoration is verified by corrected
port before CloseProtocol; this preserves the real initial0102, not historical
0100. Bluetooth remains responding. Physical city/tail observation after native12
is pending; previous owner observation was native9, do not silently extend it.

Immediate FW indicator read was0. This is NOT a timed readiness failure and NOT
firmware-ready proof. No firmware, CE/DMA, BMI target version, scan, association,
DHCP or reconnect implementation verified yet. NEXT: bounded ROM-ready wait and
CE/DMA/BMI get-target-info; bind actual target type/version before selecting/
uploading exact firmware/board chunks in RAM. Known revision1 is a completed
physical identity substep, not completion of the original Wi-Fi goal. Keep full
original goal active. SSID/security mode question pending; password never chat.

Remote exact workspace `/home/yuka/rabbit-world/wifi-reset-v1/source`.
Evidence/2026-10-04/reset-profile contains source-bound gates/reproduction,
full saved-session logs/raw+decoded telemetry/current receipt and manifest.


## 2026-10-04 — CE ring core implemented, host/COFF gates only

Previous goal turn was physical progress: native12 cold reset yielded supported
chip revision1, with command/cleanup and saved-session receipt evidence. This
continuation revalidated current sources/physical handoff; native12/world12
remains installed. Implemented `ce_ring.c/h`, `ce_ring_test.c`, `verify_ce_ring.py`
and separate `ce-target.json`. Pinned ath10k32-bit descriptor8bytes (address32,
length16, flags16), qca6174 metadata0xfffc/shift2, gather/byte-swap flags. Native
world data does not contain these target facts.

Core implements bounded power-of-two rings2..32, one reserved entry, explicit
little-endian descriptor bytes, descriptor/buffer32bit address/end bounds, cookies,
TX gather publication and queued-versus-published completion invariants. Ownership
/bookkeeping is recorded before an ambiguous doorbell. Invalid hardware indices,
changed descriptor address/oversized length or doorbell errors fault the ring but
retain its mapping. Zero RX length is a valid transient after DRRI advances:
return WAIT, preserving ownership, until descriptor update (as pinned ce.c).
Close calls adapter stop before clearing any descriptors; failed stop retains
ownership and blocks free/unmap. Hardware stop callback must actually verify CE
quiescence, bus-master-off and DMA flush: mock success is NOT hardware proof.

5000 fill/wrap cycles across sizes, gather publication, RX update race, hostile
length/address/index, 32bit overflow, invalid sizing/metadata and failed publish/
stop retry passed ASan/UBSan (halt_on_error) on Yukabox. Freestanding x86 COFF
compiled. An initial host UB in descriptor zero-fill shifting a32-bit zero beyond
31bits was caught and fixed before successful gates; no physical code was sent.
Evidence/2026-10-04/ce-ring hashes bind exact tested source/log. No Mac native
build, no owner signing or physical transfer this continuation.

NEXT: UEFI coherent DMA allocation/Map/Unmap/Free adapter and exact CE MMIO setup/
stop with actual-command verification and flush. Enforce32bit device addresses,
retained resources on ambiguous enable/stop/unmap and no callback after release.
Then bounded ROM-ready wait and BMI get-target-info on physical Dell. Current
ring core alone does NOT implement DMA mapping, CE MMIO, BMI, firmware loading,
scan/association, DHCP or reconnect. Full original goal remains active/incomplete.
SSID/security and city/tail observation pending; no password in chat/LLM/evidence.


## 2026-10-04 — UEFI DMA lifetime adapter implemented, host/ABI gates only

Previous goal turn was progress (CE ring code and tested bounds/lifetimes).
Current native12/world12 evidence and current sources revalidated before work.
Added `dma_buffer.c/h`, adversarial tests and `verify_dma.py`. PCI IO
AllocateBuffer(any pages/BootServicesData/attributes0), Map(CommonBuffer2), Unmap,
FreeBuffer and Flush typed method offsets verified against pinned UEFI headers.
Full mapped length, page alignment and32bit device-address/end bounds required;
no physical address truncation. Successful Map with NULL token still records a
mapping and passes the returned token to Unmap. EDK2 Map can fail after returning
a token (IOMMU SetAttribute failure); retain/unmap that token before free.
No bus-master enable or CE MMIO is implemented by this adapter.

`dma_users` now guards PCI close/reopen until buffers are released. Exposure is
marked before any future CE/doorbell/BM write. Close starts irreversible-to-reuse
closing state: no new exposure after a failed close. For exposed buffers, adapter
stop callback must verify CE engines stopped; then actual PCI Command must show
bus master off, Flush succeeds, Unmap succeeds, then FreeBuffer. Errors retain
remaining resources/claim; no free-after-failed-Unmap or early protocol close.
Ambiguous allocation error with nonnull output is quarantined, never guessed
safe to free. Limits16pages/buffer and64buffers are explicit Rabbit policy.

18 ASan/UBSan scenarios passed: full success/order, allocation failure/ambiguous
allocation, failed Map with/without token, short/above32bit/misaligned/overflow
mapping, successful NULL-token mapping, failed stop/still-enabled BM/Flush/
Unmap/Free/config read, invalid host alignment and multiple-buffer ownership.
Freestanding x86 COFF and ABI Map72/Unmap80/Allocate88/Free96/Flush104 checks pass.
Existing port tests reran after dma_users guard changes. Source-bound evidence
under evidence/2026-10-04/dma. All builds/tests Yukabox; no physical DMA activation,
owner signing or new Bluetooth native transfer this continuation.

NEXT: actual CE MMIO setup/stop adapter (halt verification, interrupt masking,
ring base/size/indices, doorbell ordering) and real bus-master lifecycle. Bind
CE ring+DMA lifetime to that adapter, then ROM-ready wait and BMI get-target-info.
Stop callback is MOCK ONLY at this stage; it does not prove physical CE quiescence.
Do not physically enable bus master until the complete stop/recovery/native gate
exists. Native12 remains physically installed; firmware upload/WMI/HTT/scan/WPA/
DHCP/reconnect remain incomplete. Full original Wi-Fi goal stays active. Pending
SSID/security mode and city/tail observation do not block independent port work;
no password in chat/LLM/logs. EDK2 references are technical implementation context,
not evidence of this Dell's actual Map behavior.

Reference: https://raw.githubusercontent.com/tianocore/edk2/master/MdeModulePkg/Bus/Pci/PciBusDxe/PciIo.c
(PciIoMap/Unmap/AllocateBuffer/FreeBuffer/Flush); pinned iPXE headers remain the ABI
reference, and actual physical mapping still needs separate evidence.


## 2026-10-04 — CE MMIO and PCI bus-master lifetime, host/COFF gates

Added ce_hw.c/h, ce_uefi.c/h and ce_bus.c/h. Fixed QCA6174-family CE bases
and register masks are recorded in ce-target.json and checked against pinned
Linux hw.c SHA256. Halt requests are owned before ambiguous writes; bounded
cooperative polling requires HALT request + ACK. After halt, mask interrupts,
clear ring addresses/sizes and read them back. Configure only while halted,
verify configuration readback, preserve supported control bits, clear W1C status
without treating readback as a value register, seed software ring indices from
hardware and publish with release ordering. Primary-source review caught swapped
watermark halves before physical deployment: high threshold occupies bits15:0,
low threshold bits31:16. Exact watermark assertions now cover this.

PCI IO adapter restricts engine/register access, requires retained exclusive PCI
claim/MEM/awake/BAR lifetime, and validates descriptor windows against registered
mapped32bit DMA buffers. Exposure is recorded before writes, including ambiguous
failures. Resume/doorbells reject closing or unmapped regions. Zero-size disabled
queues accept only zero indices while halted. Halting/zeroing still works after
DMA close has set closing, so failure recovery remains possible.

Bus lifecycle controls ALL8 engines, including inactive pipes. Before bus-master
activation mark every registered descriptor/data buffer exposed, resume configured
engines and write only16bit PCI Command, then require exact readback. Failed enable
retains ownership; an ambiguous error cannot authorize free. Stop requests every
engine, cooperatively verifies halt and zero addresses/sizes, disables bus master
with actual16bit readback. On failed halt, attempt disabling DMA capability but
retain ownership. DMA close callback requires completed stop plus FRESH all-eight
halt/zero-ring and bus-master-off reads, then existing adapter Flush/Unmap/Free.
No callback dereferences a released PCI protocol. All caller operations must be
serialized with native unload, and all DMA buffers must be registered.

Evidence: experiments/native-wifi-qca9377-v1/evidence/2026-10-04/ce-hw.
21 actual core/UEFI/bus scenarios pass ASan/UBSan on Yukabox: ambiguous enable,
dropped enable/readback, failed disable, missing halt ACK, corrupt stop readback,
failed config reads, closing buffers, failed Flush/Unmap and safe retained-resource
recovery. All3 production components compile freestanding x86 COFF. Updated ring
core passes5000 wrap cycles and seed-at-nonzero tests; updated source-bound report
and log are included alongside CE gate evidence. Mock completion is NOT physical
CE/DMA/BMI success. No owner key, signing, radio send or native update in this turn.
Saved state still identifies native12 payload99463fa0... and no pending operation;
this is saved receipt state, not a fresh physical observation.

NEXT: integrate cooperative ROM readiness and CE0/CE1 BMI get-target-info into a
native profile, bind DMA/ring/bus lifetimes to its stop/unload gate, pass exact
normal+EMPTY city/BT and rebuild gates, then owner-sign/send and obtain physical
telemetry. Firmware chunk upload, radio/WMI/HTT, scan/WPA, DHCP/two-way traffic and
reconnect remain incomplete. Original full Wi-Fi goal remains active.


## 2026-10-04 — cooperative ROM readiness and first BMI exchange

Added rom_ready.c/h and bmi_transport.c/h, BMI target facts, integration tests
and verify_bmi.py. ROM wait reads only validated PCI IO firmware indicator at
0x3a028, at10ms intervals with3s deadline; all-ones is never interpreted as ready,
crash bit takes priority over initialized bit. Handle clock reversal, near-UINT64
clock overflow, protocol release and PCI IO errors without blocking a city tick.
Caller must first complete reset and fresh PCI/D0/wake validation.

First transport query is ONLY BMI_GET_TARGET_INFO (LE32 command8), with12byte
reply length/version/type retained. CE0 source and CE1 destination use actual
ring/CE/bus/PCI IO production components. Verify empty seeded rings match live
hardware base/size and registered descriptor memory; refuse unmapped/closing
buffers, descriptor/data aliasing, parallel exchanges and clock overflow. Post
response before request, use BMI transfer metadata0x3fff, and require both TX
and RX completion. RX hardware-index-before-length race remains WAIT. Bad length,
address, cookie/index or zero/all-ones identity faults retain rings/mappings for
explicit bus stop. Ring close callback requires fresh all-engine halt/zero rings,
bus-master-off AND successful PCI IO Flush before zeroing descriptors. Actual
DMA close still owns Unmap/Free ordering. No firmware-write/execute/done command.

11 integration scenarios pass ASan/UBSan on Yukabox, each also exercising ROM
ready/all-ones/crash/timeout/clock/IO/lifetime gates. Includes nonzero seeded
indices, RX-before-TX publication order, delayed descriptor update, invalid reply
length/oversize/address/index/version, failed RX doorbell, close only after stop,
rejected descriptor aliases and unmapped input. Freestanding x86 COFF for both
new production components passes. Exact source/log and pinned reference hashes
in evidence/2026-10-04/bmi; tests use synthetic target version/type, NOT Dell data
or firmware-compatibility proof. Native profile integration/physical ROM ready/
physical BMI response are explicitly false in report. Saved native12 unchanged,
no Bluetooth send/signing/new physical observation in this turn.

NEXT: integrate this first query into reset profile with4 coherent DMA pages
(TX descriptors, RX descriptors, request, response), fresh PCI/D0/reset/ROM gates,
all-eight bus stop/start and unload retention. Allocate1page at a time, register
all4 buffers, initialize8entry rings before configure, seed from hardware, then
start bus and query. On success/error/cancel cooperatively stop all engines,
close both rings, close all buffers, then port/wake; any uncertain allocation or
failed stop/unmap retains native ownership and blocks unload. Include telemetry
for ROM/BMI raw reply/error and resource cleanup, preserve city/BT normal+EMPTY
QEMU gates and exact reproducible owner-bound package before physical delivery.
Full firmware RAM chunks/radio/scan/WPA/DHCP/reconnect goal remains incomplete.


## 2026-10-04 — native13 applied physically; ROM-ready timeout before DMA

Added bmi_probe.c/bmi_build.py/verify_bmi_profile.py and delivery/reproduction/QPD5
support. Full profile links production reset, ROM,4coherent DMA buffers,8CE bus
lifetime, seeded CE0/1 rings and BMI transport; one allocation/cleanup per poll.
Stop/cancel retains reset/CE/DMA ownership until cooperative cleanup completes,
blocks unload on failed halt/Flush/Unmap/Free, supports cleanup retry after errors.
17 integrated hardware-mock scenarios including D3/unsupported/absent, reset
ambiguity/cancel, ROM timeout, above32bit mapping, malformed reply, BMI timeout,
ambiguous bus-master enable and Flush failure pass ASan/UBSan on Yukabox. Exact
normal+EMPTY UEFI QEMU city/BT/rejection/recovery gates pass; QCA absent in VM.
Same native bytes rebuilt twice against current actual saved city package with
sanitizer world checks. QPD5 is240bytes, fits247byte ATT MTU; decoder distinguishes
raw BMI reply from firmware compatibility, and rejects invalid DMA hold masks.
All native compilation on Yukabox; Mac only control/Bluetooth/reader/signature.

Owner-authorized exact native13 payload SHA256:
ec846096da49cc5eea9b118405e9024cfcbe6ee0be190df60564d072a1abb362.
Signed locally (key never printed/copied) and66848byte session sent over Bluetooth.
Staging timed out at29000bytes; same nonce/session resumed from receiver-confirmed
29100. COMMIT disconnected as expected on module replacement; same session then
received exact SHA/session/counter APPLIED. Saved engine native13, city world12,
no pending operation. Fresh pre-native13 QPD4 proves previous cleanup/chip identity;
post-native13 actual QPD5 obtained after applied receipt and Bluetooth recovery.
Session: runs/text-world/pci-native-7e7wgk_a under connected supervisor experiment.

PHYSICAL RESULT: chip003821ff/SoCrev1, D0, verified cold reset clear and PCI original
Command0102 restoration. ROM indicator remained0 for bounded3second wait;
stage6/error0x504 (ROM error4 timeout). BMI was NOT sent; DMA was NOT activated or
allocated. Bus phaseIDLE/ownedfalse, buffer count/held-mask0, port cleanup complete.
No firmware/radio/WPA/DHCP success. Exact evidence under
experiments/native-wifi-qca9377-v1/evidence/2026-10-04/bmi-profile, including gate
reports, source-bound reproduction, physical receipt, raw/decoded diagnostic and
physical-summary.json. QEMU PASS must not substitute for this physical timeout.
Async owner observation city/tail after native13 remains pending; no visual claim.

NEXT: account for native PCIe bringup differences. Pinned ath10k hif_power_up
saves and disables LinkControl ASPM BEFORE reset; our fresh prior physical power
probe found LinkControl0143 (both ASPM bits enabled) and current profile does not
change those bits. Implement bounded reversible16bit LinkControl save/disable/
readback/restore under exclusive PCI claim (never32bit write touching LinkStatus),
with retained ownership on ambiguous failure and cleanup before port release.
Then repeat ROM wait physically in next owner-checked profile. Also inspect
ath10k wait_for_target_init's legacy-INTx workaround (repeated interrupt-enable
writes with readback) and QCA6174 cold+warm reset ordering. Do not blindly enable
host interrupts or claim either hypothesis as established; no further physical
writes until matching deterministic gates. Full original Wi-Fi goal remains active;
firmware RAM chunks/radio/WPA/DHCP/two-way traffic/reconnect remain incomplete.


## 2026-10-04 — native14: reversible ASPM tested physically; ROM still times out

Added pcie_link.c/h. Under exclusive validated PCI claim, decode fresh256byte
capability list and require D0 + matching Dell QCA identity + PCIe endpoint cap.
Save LinkControl; clear only ASPM bits0:1 using PCI IO Write16 and exact readback.
Own before ambiguous write. Restore exact saved word with fresh cap/identity/D0
check, no DMA users/BM; adjacent LinkStatus is never written. New port link_owned
blocks close/reopen until verified restore. Cleanup failure retains native/PCI
ownership and supports explicit retry. Full integrated gate extends to21host
scenarios: rejected capability, ambiguous/drop disable, failed/drop restore and
retry, with original reset/DMA/BMI failures. DMA gate rerun for new port guard.
QPD6 is246bytes (full Read response247 fits ATT MTU); adds saved/last LinkControl
and ownership/error, preserves pre-reset active snapshot at182. Decoder gates
ownership/size and distinguishes restoration from firmware readiness.

Exact21host sanitizer + component host/COFF/ABI gates, normal+EMPTY real UEFI QEMU
city/BT/rejection/recovery gates and two fresh native/current-world rebuilds pass
on Yukabox. Candidate payload SHA256:
50e1d3d34a76d6adbfa930474b6bedd7ebdf93ff4daa0f278963bb8dd6ecb54a.
Locally signed exact native14,67872byte Bluetooth session staged fully; same session
COMMIT/reconnect got exact SHA/session/counter APPLIED. Saved native14/world12,
no pending operation. Receipt session runs/text-world/pci-native-_pexlbhw.
No owner key output/copy, Mac native build, USB/bootstrap change or Dell reboot.

PHYSICAL QPD6: LinkControl0143 -> verified0140 BEFORE reset -> restored0143,
ownedfalse/error0. Chip003821ff/rev1 and D0/cold-reset checks remain good. ROM
indicator0 after3s, stage6/error0x504; no BMI response, no DMA allocation/activation,
held resources0 and cleanupcomplete. Evidence under native-wifi experiment
/evidence/2026-10-04/pcie-rom-profile includes all source-bound reports and raw
physical receipt/diagnostic. Active link snapshot is BEFORE reset, not a separate
measurement during ROM wait: this experiment does not prove ASPM stayed disabled
through cold reset. Do not overstate a ruled-out hypothesis. Owner visual
city/tail observation remains pending; Bluetooth restoration is observed.

NEXT: augment fresh post-reset PCI snapshot with LinkControl and ensure/reapply
ASPM-off before ROM polling if reset changed it. Pinned ath10k
wait_for_target_init repeats PCIE_INTR_ENABLE at SOC_CORE_BASE+offset with
firmware|CE masks for legacy INTx boot race and flushes posted write via readback;
current profile does not perform that step. Add a reversible boot-IRQ adapter,
with host INTx disabled and MSI/MSI-X state validated before device IRQ enable,
actual-command/target-register readback and cleanup/port-close ownership guard.
Never blindly enable an unhandled host interrupt. All writes need matched mock,
COFF, exact normal/EMPTY city/BT, reproduction and owner gates before next send.
Another source difference is Linux pci_claim enables bus mastering BEFORE reset/
ROM wait, while ours leaves it off until ROM-ready. If IRQ ordering is insufficient,
plan a DMA-lifetime-aware earlier master enable only after all8CE quiescence and
reviewed mapped empty rings, retaining mappings across reset and revalidation.
No DMA activation, firmware compatibility/upload, scan/WPA, DHCP/two-way traffic
or reconnect success yet. Full original Wi-Fi goal remains active/incomplete.

## 2026-10-04 — native15 boot IRQ candidate checked and signed; delivery pending

Added reversible boot_irq.c/h with pinned target facts. Validate fresh identity,
D0 and MSI/MSI-X disabled before owning legacy bootstrap registers; mask host
INTx with PCI Command Write16 before any device interrupt writes. Clear only the
CORE_CTRL firmware MSI mask0x800, repeatedly enable firmware/CE mask0x7fc00 during
bounded ROM wait, verify every write. Cleanup disables and clears device IRQs,
checks pending causes, restores the saved core bit and host command; ambiguous
writes or cleanup errors retain ownership and prevent unload. No host IRQ handler
is enabled. Recheck/reapply ASPM-off after reset, preserving original LinkControl.

QPD7 is280bytes with boot ownership/error/register snapshots and post-reset link
measurement. Actual UEFI QEMU gates test bounded ATT Read/ReadBlob, including
invalid offset, with QCA absent.34 host sanitizer failure/recovery scenarios,
component gates, normal+EMPTY UEFI city/rejection/recovery, and two exact rebuilds
with current world pass on Yukabox. Payload SHA256:
0beeb5450db864eba62710cfe7df7e0ba3d19594d9e480b6b50129f99225b4a6.
Evidence: native-wifi-qca9377-v1/evidence/2026-10-04/boot-irq-rom-profile.

Exact owner-signed native15 session is saved on Mac at
connected-supervisor runs/text-world/pci-native-yhzzk0k_. First read-only Bluetooth
query timed out before any DATA/COMMIT; diagnostic reader also disconnected.
Second same-session read-only query also reached its60second timeout. Both sender
processes are terminal; no DATA/COMMIT attempted. Mac Bluetooth controller is on.
Delivery report and both query logs are archived alongside the gate evidence.
Native14 remains the last confirmed installed release; native15 is NOT a physical
success. Resume the SAME pending session after reaching Dell; do not regenerate a
nonce, clear staging or increment the counter. Observe current sender process
before retrying. City/tail and proximity question is pending. No USB/bootstrap,
reboot, firmware upload or Wi-Fi connection performed or inferred. Full original
goal remains active, including firmware RAM chunks, radio/WPA/DHCP/reconnect.

## 2026-10-04 — signed firmware RAM assembly core, host/COFF only

Added firmware_chunks.c/h, pure firmware_chunk_format.py, sanitizer harness and
verify_firmware_chunks.py; contract in FIRMWARE-CHUNKS-CONTRACT.md. Independent
of the frozen native15 candidate and its saved signed session. No Dell update,
production owner signing, firmware upload or identity/compatibility inference.

Packets have224byte signed/hash-bound headers and up to65536byte bodies, fitting
the262144byte transport budget. Reviewed external policy binds owner, target,
whole hash/length, exact generation, physical BMI type/version and asset kind.
Accepts shuffled chunks/exact retries; rejects context/owner/signature/hash/bounds
errors before RAM writes. Full assembly hash and a second hash before consumer
pin are required. Pin blocks replacement/cancel; unpin requires stopped consumer
and DMA. Cancel zeroes the asset. Maximum2MiB/32chunks, caller-owned RAM.

Yukabox final ASan/UBSan and x86-64 UEFI COFF gates pass for1,65535,65536,65537,
2097152bytes and the exact reviewed751436byte official firmware container
(12chunks, max packet65760bytes). Tests cover all truncated headers, tampering,
real Ed25519 checks, valid signatures under wrong key/context, shuffled/retried
delivery, pin/cancel lifetime and corruption before/after complete assembly.
Evidence: native-wifi-qca9377-v1/evidence/2026-10-04/firmware-ram-chunks.
Signatures are TEST FIXTURES with synthetic BMI identity, never owner uploads.

NEXT: retain pending native15 and obtain its physical boot/BMI evidence first.
Integrate this RAM core into a separately framed native-owned Bluetooth asset
service with exact receipts, validated UEFI allocations and unload guards;
preserve existing file-service handles and native/world update meanings.
Actual firmware compatibility, extraction/calibration, BMI memory writes,
firmware startup, radio/scan/WPA/DHCP and reconnect remain incomplete.
