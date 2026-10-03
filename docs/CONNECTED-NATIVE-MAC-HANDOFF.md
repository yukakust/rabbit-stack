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
