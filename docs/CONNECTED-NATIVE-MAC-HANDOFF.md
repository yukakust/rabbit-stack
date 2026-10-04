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

## 2026-10-04 — secondary signed-asset ATT channel, host/COFF gates

Added firmware_channel.c/h and firmware_gatt.c, preserving file handles1..7 and
diagnostic handles8..10 by explicit delegation. Secondary service suffix7 owns
11..17; control13/data15/status17. Existing server owns MTU/disconnect handling.
Channel receives one bounded signed chunk packet into caller-owned workspace;
BEGIN/resume binds exact packet SHA/length, DATA accepts only contiguous bytes or
exact prefix retries, COMMIT verifies transport hash then signed RAM acceptance.
Foreign BEGIN cannot erase active staging. Final receipts are idempotent; abort
does not clear accepted firmware chunks. Read/ReadBlob gives exact64byte receipts
even at MTU23, separating RAM acceptance/complete asset from hardware startup.
Pin guards reject channel writes/close until stopped consumer unpins. No owner
key, PCI/MMIO, allocation or hardware operation in this component.

Final Yukabox ASan/UBSan and both x86-64 UEFI COFF objects pass with all6 existing
RAM datasets, including exact751436byte official container/12chunks and2MiB/
32chunks. Tests exercise service/characteristic discovery, legacy delegation and
MTU ownership, long status/bad-offset rejection, foreign active session, abort,
gaps/UINT32_MAX offsets, truncated transfer, changed retry, lost ACK with exact
retry, matching BEGIN resume, repeated COMMIT, pinned close, and transport versus
signature rejection. Gate source/log hashes and underlying RAM gate hash match
the Mac source/evidence. Evidence under native-wifi-qca9377-v1/evidence/2026-10-04/
firmware-att-channel. This is NOT actual UEFI ATT execution or physical transfer.

Current native15 payload/source/session remains frozen and pending, native14
last confirmed installed. NEXT: obtain physical boot/BMI response, integrate
owner/target-bound RAM policy and allocation into an asset-capable native driver,
wire the ATT hook into its existing handler, add exact Mac receipt/resume sender,
then actual normal+EMPTY UEFI/current-world/owner gates before any physical send.
No chip firmware compatibility/upload/startup, radio/WPA/DHCP/reconnect proof yet.

## 2026-10-04 — Mac signed-chunk sender and portable receiver interop

Added firmware_sender_core.c/h and mac_firmware_sender.m with wrapper
send_firmware_chunk.py. No signing/private-key access. Exact64byte receipt parser
and pure controller stop foreign staging, prefix loss, aborted/poisoned state,
bad bitmap/ready flags and matching rejection. ACK alone never advances confirmed
prefix. Matching accepted RAM receipt finishes even if the complete asset is
already pinned by a consumer; no additional writes then. Atomically persisted,
fsynced checkpoint binds packet SHA, confirmed floor and attempted flag before
radio writes. Retry keeps identical packet/checkpoint; no ABORT/new generation.
Wrapper serializes with the current-world lock, blocks pending operations,
checks installed owner gate/public identity, packet signature/body hash, then
passes an immutable verified copy to the helper. Compile-only is the default.
Offline --preflight starts no CBCentralManager; physical radio requires explicit
--send or --query-only, service discovery and correct characteristic properties.

Final ASan/UBSan sender+actual RAM/transport core tests pass all6datasets, including
751436byte official container/12chunks and2MiB/32chunks. Tests ignore lost ACKs,
query exact progress, resume, detect receiver regression/foreign session, reject
malformed receipts/signature rejection, and check complete asset bitmap/ready.
Mac clang compile succeeds with warnings as errors. Offline Cocoa tests check
checkpoint atomic write/fsync, progress preservation, invalid/mismatched/fractional
values, malformed JSON and packet tampering (public TEST key only). No Bluetooth
manager or owner private key in those tests. Evidence under native-wifi experiment
evidence/2026-10-04/firmware-sender. Cocoa RADIO callbacks/physical signed-asset
transfer remain unverified; this is not firmware upload/startup or Wi-Fi.

Fourth native15 discovery query timed out before DATA/COMMIT; original signed
session remains pending, native14 last confirmed. Cached peripheral read-only
connection is a separate diagnostic attempt, not delivery or update success.
That cached query also reached its60second timeout; no receiver status obtained.
All query processes are terminal. Preserve pending native15 and wait for actual
Dell reachability; no DATA/COMMIT, abort, new nonce, reboot or media write.
NEXT: obtain physical native15/BMI facts, add validated RAM allocations and
owner/target asset policy to a separately gated native candidate, wire secondary
ATT handler, then normal+EMPTY UEFI/current-world gates before physical update.
Firmware compatibility, upload/startup, scan/WPA/DHCP/reconnect remain incomplete.

## 2026-10-04 — Mac RF/permission revalidation; physical Dell unavailable

Rabbit World app is running, AX shows world12 / operation needs continuation.
This is saved-controller state, NOT an observation of the Dell display. Its
CBCentralManager is only a permission/state checker; app source has no connection
or scanning ownership. No application/TCC reset, restart or security bypass.

New passive Mac probe compiles with warnings as errors. Actual20second unfiltered
scan: controller_state5(PoweredOn), authorization3(AllowedAlways),134advertisements,
no Rabbit service1/5/7 candidate, no connected file-service peripheral; known Dell
cached state0(disconnected). Other device names/identifiers were not recorded.
No connection, characteristic write, DATA/COMMIT, firmware or hardware update.
Evidence: native-wifi-qca9377-v1/evidence/2026-10-04/bluetooth-reachability.
This proves Mac RF reception/permission and absence of observed Rabbit services,
not Dell power state, screen state, distance or a diagnosis of its controller.

Same physical reachability blocker has persisted through four terminated
service queries and one terminated cached connection. Software preparation is
saved; continuing chip/firmware compatibility verification requires restored
physical Dell reachability. Owner city/tail + Mac proximity question remains
unanswered. Do not replace hardware proof with further mock success, reboot Dell,
alter USB/bootstrap or infer an unchanged receiver RAM epoch.

On owner return: inspect actual Dell screen/power and Mac proximity; re-query the
exact pending native15 session before DATA. If receiver loss/reboot is observed,
use existing reviewed recovery with fresh receiver state; never erase pending
session/counter based on assumption. Resume full original Wi-Fi goal, including
physical ROM/BMI, compatible firmware startup, scan/security, DHCP/two-way traffic
and reconnect with city/BT preservation. Goal is not achieved.

## 2026-10-04 — UEFI RAM adapter and native asset service wired; policy disabled

Added firmware_port.c/h. Before allocation require native-owned QPD7 clean BMI
success, exact Dell PCI identity, ROM-ready/no-crash, no reset/DMA/bus/IRQ claims,
and exact reviewed policy BMI type/version match. This is not firmware
compatibility inference. Owner/target policy cannot come from incoming packets.
Typed AllocatePool/FreePool callbacks, System/Boot headers and stable callback
pointers are checked. Allocate BootServicesData asset RAM plus65760byte workspace
cooperatively; pin prevents cleanup/unload, cancel zeroes asset before freeing.
NULL allocation errors unwind; non-NULL error/overflow/overlap retains opaque
ownership without dereferencing/freeing. Failed free keeps claim for retry.

11 ASan/UBSan host scenarios pass: both allocation failures, NULL success,
ambiguous outputs, overlap, both free failures/retry, changed callback/recovery,
and pinned complete signed751436byte test asset/cleanup. x86-64 UEFI COFF and
pinned iPXE header AllocatePool64/FreePool72/type4/SystemTable120 ABI gates pass.

asset_build.py wires adapter, poll, ATT delegation and stop/close/unload guards
into a separate native city+BMI candidate. Compiled asset policy is ZERO/DISABLED
because physical BMI/firmware compatibility is still missing. Exact twice-built
unsigned payload SHA256:
5ac507dfbadf542ccb52ec1e1f512e0baf46040d1d8cd130f973c72a317feaa0.
Actual normal+EMPTY UEFI city/BT/rejection/recovery tests pass. Actual UEFI asset
service11..17 discovery,64byte status/read-blob bounds and BEGIN denial pass via
mock USB ATT, QCA absent, no asset allocation. Host positive RAM/BMI identity is
synthetic, not a physical result or positive UEFI allocation test. Evidence under
native-wifi-qca9377-v1/evidence/2026-10-04/firmware-uefi-port.

No signing, new release/session, physical write, USB or reboot. Pending signed
native15 and saved native14/world12 remain unchanged. Native owner route does NOT
authorize this disabled-policy profile for delivery. NEXT: physical native15/BMI
facts; separately authorize exact firmware policy, test positive UEFI allocation
and full asset transfer/lifetime, then exact current-world/reproduction/owner
gates. Actual firmware upload/startup, radio/WPA/DHCP/reconnect still incomplete.

## 2026-10-04 — owner requested Bluetooth recovery; Mac power cycle verified

Owner reports everything powered on. Fresh passive scan observed97advertisements,
authorization3/controller5, zero Rabbit candidates or connected service; direct
read-only cached Dell query terminated at60seconds. Used System Settings Bluetooth
switch off/on with AX verification, then restored previous Appearance panel. Fresh
passive scan observed18advertisements and still no Rabbit; second cached read-only
query again terminated at60seconds. No DATA/COMMIT/ABORT, private-key access, Dell
reboot or USB/bootstrap change. Exact pending native15 session preserved. Both
query processes terminal. Evidence: native-wifi-qca9377-v1/evidence/2026-10-04/
bluetooth-recovery/report.json. Current Dell animation/screen and Mac proximity
requested; powered-on alone does not establish receiver liveness. Cause remains
undetermined. Need physical screen observation before further recovery; do not
claim Mac toggle restored Dell or infer unchanged receiver RAM.

## 2026-10-04 — owner confirmed moving cat; close-distance BLE retry failed

Owner confirms city visible and cat tail moving, Mac originally7m away; owner then
moved Mac nearby. Fresh20second passive scan saw137advertisements, no Rabbit service
and no connected Rabbit peripheral; Mac powered-on/allowed. Saved-peripheral
read-only query again reached60second timeout and terminated. No DATA/COMMIT/ABORT
or Dell reboot; native15 pending session unchanged. Evidence appended to
bluetooth-recovery/report.json. Distance alone did not restore the connection;
cause remains undetermined. Installed supervisor has Esc-to-stop but no separate
remote radio-reset command available without BLE; Esc would stop the scene.
Current whole-screen Dell photo needed to inspect visible diagnostics before
choosing a recovery. Existing city_recovery rejects native_pending and assumes
its own reviewed city profile; do not reboot expecting unconditional recovery or
clear native15 without fresh receiver evidence and a reviewed transition.

## 2026-10-04 — dedicated reboot recovery prepared; owner reboot NOT observed

Owner explained fullscreen city hides diagnostic text; do not request another
photo to read logs under that overlay. Owner authorized preparation of recovery.
Added dedicated reboot_recovery.py + verifier +7 controller transition tests.
Existing city_recovery is not compatible with pending diagnostic-native sessions;
use the dedicated route, including resumes. No GUI recovery integration in this
change. REBOOT-RECOVERY.md documents guards and limits.

On Yukabox: two exact plain actor driver builds (no QCA probe), actual normal and
EMPTY-bootstrap UEFI city load/snapshot/rejection/recovery gates with mocked radio;
exact saved world12 recompiled at counter13 checked in C ASan/UBSan,120frames,
roof-cat tail/smile timing and16adversarial camera frames.7 real-fixture-signature
controller tests pass, including no radio without reboot confirmation, nonempty
receiver refusal, immutable old packet, interrupted native/world resume and
restored world equivalence. Dependencies and exact evidence are hash-bound.
PayloadSHA256:0bd6291bb65312b8e33afeb5187839bb4da09cfb10069f2eba4837c9cc438f62.

Mac validated gates, owner identity, signed old pending native15/world12, current
controller/journal. Locally signed native16 against installed bootstrap1+EMPTY
world and saved world13/exact sessions at:
/Users/yukakust/rabbit-stack/experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/reboot-recovery-native16
Checked directory: experiments/native-wifi-qca9377-v1/runs/reboot-recovery-final.
Current native14/world12, native_pending pci-native-yhzzk0k_, all12history versions
and every old pending byte remain unchanged. Plan PREPARED-NOT-ACTIVATED; not
sent, no receiver writes, no Dell reboot or USB/bootstrap change. Actual Mac
restore invoked WITHOUT owner flag verifies guard rejects before any radio.
Evidence: native-wifi-qca9377-v1/evidence/2026-10-04/reboot-recovery.

NEXT requires OWNER actual reboot and observation of bootstrap, then agent runs:
python3 experiments/native-wifi-qca9377-v1/reboot_recovery.py restore --state experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json --directory experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/reboot-recovery-native16 --private /Users/yukakust/.rabbit-owner/runtime.key --dell-rebooted
This first queries exact zero/idle RFS; absent/nonzero response leaves old pending
native15 and state intact, no DATA/COMMIT. Only owner-confirmed reboot AND fresh
zero status allow atomic retired-native ledger+new recovery activation, preserving
old signed files/hashes. Existing packet15 is never sent against bootstrap.
Native16/world13 exact receipts drive promotion. Resume SAME command/directory
without --dell-rebooted after activation; do not regenerate packets/nonces.
After restoration require owner city/tail observation; this is not yet physical
recovery evidence or a Wi-Fi connection. Reboot may not cure the radio: if fresh
bootstrap cannot advertise, retain plan and diagnose physical radio. Full original
Wi-Fi goal remains incomplete.

## 2026-10-04 — owner reboot confirmed; physical recovery activated, delivery failed

Owner explicitly reported Dell reboot. Dedicated prepared native16 restore first
obtained actual fresh all-zero RFS idle response from known F45BFCB2 peripheral
(RSSI -81/-83); second read-only query also succeeded (RSSI -79/-82). Recorded
owner reboot plus fresh zero proof, atomically retired old native15 into controller
ledger (all original signed files/hashes preserved) and activated saved native16
recovery. This is an observed boot receiver response, not device attestation.

Native16 paced-stage helper connected at RSSI -77 but never completed service
discovery; disconnected phase0/offset0 of47904bytes with no error, then failed
300second timeout. Follow-up read-only query reached60second discovery timeout.
No BEGIN/DATA/COMMIT is observed in the logs; no APPLIED receipt or world delivery.
Dedicated route returned DELIVERY-NOT-CONFIRMED (CLI exit0 is NOT application
proof). All sender processes are terminal. No second Dell reboot, USB/bootstrap
change, new nonce/counter/packet or arbitrary pending clearing.

Controller still stores native14/world12 as last-confirmed saved versions; these
are NOT Dell's current RAM after reboot. recovery_pending points to the SAME
reboot-recovery-native16 directory, native_pending is None, engine_done/world_done
false. Native16/world13 bytes remain exact for continuation; old native15 is
retired, not deleted, and must not be delivered. Evidence plus full completed
query/stage logs: reboot-recovery/physical.

Asked owner what is currently on Dell screen and last BLE lines, and to position
Mac about0.5m beside Dell given weak signal (not a diagnosis). No reply yet. Old
fullscreen city hid text, but native16/world13 were not applied after this reboot.
Need actual current display diagnostic/photo before choosing another recovery.
Two successful boot queries prove transient reachability; loss after third
connection does NOT prove an RF, antenna, UEFI or host-state cause. Do not blindly
reboot again or claim restoration. Use dedicated same-session restore for resumes
only after receiver state is understood; never GUI's old city_recovery for this
new plan. Original Wi-Fi goal and physical city restoration remain incomplete.

## 2026-10-04 — photo diagnosis, isolated BLE recovery profile, native17 prepared

Owner photo shows valid disconnects for handles1/2 followed by advertising-ready,
then successful USB read5bytes `00 00 48 00 01` / EVENT LENGTH MISMATCH; later
valid `05 04 00 03 00 13` has no restart marker while USB polls continue. Source
reproduction: rl_event ignores the malformed input, remains RL_ADVERTISING, then
ignores Disconnect Complete because it only handles known RL_CONNECTED links.
Hardware can have auto-disabled advertising during an unobserved connection.
This explains a persistent state-machine failure; it does not prove why the
connection header was missing or rule out RF/firmware causes. Photo transcript
and image hash archived; room image not copied to Git.

Separate ble_recovery_build.py clones original HCI source in build workspace,
adds successful-untracked-disconnect restart while logically advertising, retains
known live peer on foreign disconnect, validates handle/status/pending/state. No
controller reset/ACL acceptance/file clearing is introduced by this transition.
Original hci_link/usb_port/bootstrap sources unchanged. Host ASan/UBSan reproduces
baseline silence and candidate recovery; malformed/foreign/error/stopped/fault/
pending-command cases tested. Two exact candidate native builds; actual normal
and EMPTY-bootstrap UEFI gates pass, EMPTY fixture injects observed malformed
input+unknown disconnect AFTER candidate attach. No event assembler added.
PayloadSHA256:0fb9fa6c1c307e8ca0fe51b4b29e3cd815c3e2881f9c1ceba6d01d80ce52b4ce.

Recovery can prepare successor above an unconfirmed signed recovery's counter,
without changing current state or old signed files. Dedicated restore validates
the predecessor reservation again before activation. Shared deliver_session now
optionally reuses the immediately preceding boot query once under SAME lock,
through normal status validation; defaults/resume/retries still query normally.
10controller tests and16connected-world regression tests pass on Yukabox. Actual
saved world13 C/ASan/UBSan+tail/smile/max-camera checks and two current-source
rebuilds/normal+EMPTY UEFI gates pass. Offline shadow-controller simulation using
actual native17 packet PUBLIC verification and MOCK radio proves replacement
native17/world13 receipts/counters/equivalence without canonical state changes
or owner private-key read. This is not physical success.

Locally signed NEW native17 against installed bootstrap1+EMPTY world, world13
unchanged city/cat. PREPARED-NOT-ACTIVATED, no new radio attempt. Directory:
/Users/yukakust/rabbit-stack/experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/reboot-recovery-native17
Checked: experiments/native-wifi-qca9377-v1/runs/reboot-recovery-ble17. Old
native15/native16 packets/files preserved; current controller STILL points to
unconfirmed recovery-native16, saved native14/world12; no promotion or erase.
The native16 old gate is now stale due recovery Python changes; DO NOT resume
its command or clear it manually. Next fresh-boot trial must use native17.
Evidence: native-wifi-qca9377-v1/evidence/2026-10-04/ble-disconnect-recovery.

NEXT needs a NEW owner-confirmed Dell reboot AFTER this preparation (the earlier
reboot does not authorize assuming a new receiver epoch). No USB/bootstrap write.
Then agent from repository runs:
python3 experiments/native-wifi-qca9377-v1/reboot_recovery.py restore --state experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json --directory experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/reboot-recovery-native17 --private /Users/yukakust/.rabbit-owner/runtime.key --dell-rebooted
Fresh zero receiver proof retires native16 with all hashes/bytes retained and
activates native17; reuse verified query prevents redundant third connection
before staging. Existing bootstrap still has old radio code until candidate is
applied, so this is not a guarantee of physical transfer. Native17/world13 exact
receipts then owner city/tail observation required. After activation resume SAME
17directory without --dell-rebooted, do not make a new nonce/counter/package.
Future Wi-Fi candidate profiles must retain this separately validated radio fix
rather than reintroduce original disconnect filter. Original Wi-Fi goal remains
incomplete; physical native17 recovery has NOT been attempted.

## 2026-10-04 — native17 + saved city world13 physically delivered

Owner confirmed a NEW reboot. Fresh read-only known-Dell RFS status was exact
zero/idle; canonical state then retired old native16 with hashes/files retained
and activated native17. Multiple bounded attempts retained the SAME packet/session
and resumed prefixes 3400,13200,19500,24700; receiver eventually confirmed full
47904 bytes. Bluetooth timed out repeatedly (RSSI roughly -75 to -93); no claim
that the new profile fixes all link instability. Commit disconnected on native
replacement; reconnect returned exact packet SHA256/session/counter17 APPLIED.
Saved city world13 (2128-byte package) then returned exact APPLIED receipt.

Current canonical counters are native17/world13; native_pending/recovery_pending
are null. WorldSHA remains fa5a3250633f2bbbd288d947be567c2c5db8e3395033da99b765edf0a0f5cc74;
12-version idle journal SHA unchanged. All prepared17 files and predecessor16
packet/session/payload/report hashes rechecked intact. Native15 also retained.
Physical malformed-event recovery itself is NOT proven by these normal receipts.
The city/tail display observation is pending owner's answer; receiver reports
are application receipts, NOT device attestation. No Wi-Fi connection established.

Evidence: experiments/native-wifi-qca9377-v1/evidence/2026-10-04/ble-disconnect-recovery/physical-native17
includes exact boot/stage/reconnect/commit logs, both receiver receipt reports,
sessions/plan and summary. Private key remains local; no USB/bootstrap writes.
Do NOT rerun reboot recovery: it is complete at receiver level. Next requires
owner city/tail observation, then prepare a new Wi-Fi diagnostic above native17
against the CURRENT world/payload, retaining the separately tested BLE recovery
profile. Retired native15/16 are historical and must not be delivered.

Owner subsequently confirmed «виден»: city visible on physical Dell. Tail motion
is not implied by that reply; separate observation requested.

## 2026-10-04 — native18 physically applied; ROM ready, BMI exchange timeout

Owner confirmed recovered city visible (tail observation separately requested).
New BMI profile uses ble_recovery_build.link_source instead of baseline HCI;
normal+EMPTY actual UEFI fixtures now inject the malformed-event/unknown-handle
sequence. Baseline/fixed link ASan/UBSan and34 integrated Wi-Fi scenarios pass,
all port/reset/CE/BMI/DMA component gates pass. Two fresh native builds match,
248 source hashes and actual saved world13 C validation bound in reproduction.
Mac gate accepts exact profile and rejects missing BLE-recovery evidence before
signing/radio. Native route now requires that evidence on boot-IRQ profiles.

Locally owner-signed native18 against native17/current world13. Packet70432bytes
resumed from confirmed57600 after bounded disconnects, then exact SHA/session/
counter18 APPLIED receipt after replacement/reconnect. Directory:
experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/pci-native-8j0d1wek
PayloadSHA256:00324a1214b556ef23e406993a905700e9beba3b7152b041e557f475346aea51.
Current native18/world13, no pending operation; same city content/12-version journal.
No Mac native compilation; only Mac Bluetooth sender/reader compilation/signing.
Original USB/bootstrap/HCI sources and retired native15/native16 files unchanged.

Fresh physical280byte QPD7: chip003821ff/rev1, Dell1028:1810, D0. ROM indicator
00000002 / rom_error0 FIRST observed ready, unlike native14 indicator0 timeout.
Combined boot-IRQ/post-reset-ASPM profile is a positive result, not proof of which
change independently caused it. Post-reset LinkControl0140; restored0143/error0.
BootIRQ10MMIO writes; original enable0/core8688 restored, pending cause0, ownedfalse.
BMI exchange reached3-second timeout(error5, overall0x805/stage6), target version/
type remain0: NO BMI reply/firmware compatibility/startup/association success.
Cleanupcomplete, DMA held0/mask0, bus_ownedfalse, reset_ownedfalse; PCI Command
restored0100. Do not describe this as no DMA attempt: production path passed
ROM and attempted the bounded CE0/CE1 exchange before safe cleanup. Completion
indices/TX/RX details are not retained in current QPD7, so exact failure is unknown.
Owner city/tail observation after18 pending; no physical animation claim.
Evidence: native-wifi-qca9377-v1/evidence/2026-10-04/bootirq-ble-profile-native18,
physical subdir has exact receipt/logs/raw and decoded QPD7/hash summary.

NEXT: preserve city and BLE recovery; record CE0 TX/CE1 RX completion flags and
initial/final hardware/ring indices BEFORE cleanup, plus bounded descriptors/
request/response snapshot. Compare pinned ath10k BMI transport configuration and
DMA publication/metadata with these observations. No speculative firmware upload,
no unbounded wait/bus-master change or blind repeated reset. Fresh deterministic
host/lifetime + actual normal/EMPTY city/BLE + two-rebuild/current-world gates
before next locally signed profile. Physical firmware/scan/WPA/DHCP/reconnect and
Yukabox video transport remain incomplete; original full Wi-Fi goal incomplete.

## 2026-10-04 — native19 CE snapshot applied; early memory-enable mismatch

Owner confirmed city visible after18; tail motion is not implied. QPD8 extends
280 to356bytes with an immutable76byte pre-cleanup exchange snapshot. Existing
BMI polling records initial/last observed hardware indices; snapshot captures
completion flags, software indices, mapped addresses, original descriptor slots,
request/response bytes. No extra MMIO read/write or changed timeout/order. Capture
occurs before stop/unmap/free, once; maps/registered bounds checked, acquire fence;
indices are last observations, not simultaneous fresh hardware reads. Contract
CE-SNAPSHOT-CONTRACT.md.35 production-code integrated sanitizer scenarios include
neither/TX-only/full completion and persistent snapshots after release; actual
mock snapshots decoded and malformed flags/mask/index/address rejected. Component
and normal+EMPTY real UEFI city/BLE/malformed-link/rejection gates pass, two builds/
248 input hashes/actual current world13 C checks pass. No QEMU physical claim.

Locally signed/delivered SAME native19 packet71456bytes through many bounded link
timeouts/resumptions, exact SHA/session/counter19 APPLIED after replacement.
Payload4385750e67ec8362638cdaa80db9837dd4c111befa09213173c7d3f213959d0b.
Directory experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/pci-native-99fzp6dy.
Native19/world13, no pending; fresh physical QPD8 obtained. It stopped EARLIER:
error0x10b00 (port step11 actual MemoryEnable Command readback), original cached
UEFI attributes0x200, original/restored actual PCI Command0100. No chip reset,
ROM wait, DMA allocation or BMI attempt; snapshot absent, cleanupcomplete.
This does NOT establish TX/RX failure: no exchange was reached. Native18's prior
ROM-ready observation remains historical valid evidence. New19 physical city/tail
observation not received. Evidence ce-snapshot-native19/physical includes exact
receipts/raw+decoded data and ORIGINAL19 uefi_port.c/port_test.c preserved separately
before the next correction; their baseline source comes from b13c198.

Next correction targets a reproduced cached-Attributes Enable no-op. If fresh
actual Command is exactly original (MEM still off), explicit Write16 of only
original|MEM, then exact readback. Unknown Command changes/error/dropped writes
fail closed, no MMIO until verified; memory_attempted retains ownership before
ambiguous writes, original Command/attributes restoration still required. No
bus-master/StatusW1C/USB/bootstrap/reboot/firmware change. Four additional port
cases cover success/drop/ambiguous-applied/foreign command with original PCI
Status preservation, no MMIO before success and cleanup retry. Current19 signed
session is complete; do not resume it after source correction. Next new update
must be above19, preserve city world13 and BLE recovery, and pass NEW exact gates.

## 2026-10-04 — native20 exact memory-enable repair prepared, transfer incomplete

Four added production port cases and all component/sanitizer/COFF/35 integrated/
normal+EMPTY UEFI city/BLE/malformed-link gates PASS on Yukabox. Two exact new
native builds/current world13 C/248source reproduction PASS. PayloadSHA256:
9bd99b42aded22e3b55bff9d8eaf5799f35776f6b2a26376690f94b3aa06eeaa.
Locally owner-signed NEW native20 against exact applied19 and city13. Directory:
experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/pci-native-_g6coe4s.
Private key not printed/copied; no Mac native compile/USB/bootstrap/reboot.

Physical radio attempt: fresh query of native19's exact final receipt, staged
native20 from0 to700, next same-session attempt reached1400/71456; final3
reconnections BEGIN-confirmed1400 then timed out without advancement. No COMMIT
attempt, no APPLIED20 receipt, no post20 chip read. Report DELIVERY-NOT-CONFIRMED;
canonical saved engine remains19/world13, native_pending points to SAME20directory.
All radio processes terminal. Source-bound20 gates remain current (no source edit
following checked builds). Preserve packet/nonces/counters/current19/20gatefiles.
Evidence cached-memory-native20 (gates/rebuild/source hashes) and physical subdir
(exact session/report/all radio logs/pending summary). Do not confuse tested repair
with a physically successful repair or CE exchange. Wi-Fi remains incomplete.

Async owner question asks whether Mac is still next to Dell, or can be brought to
30-50cm from Bluetooth adapter; no answer yet. Very weak RSSI/repeated timeout
observations do NOT establish an RF/antenna/firmware cause. Before another long
retry obtain updated proximity/physical scene observation; no forced radio reset.
Resume same packet via:
python3 experiments/native-wifi-qca9377-v1/native_route.py deliver --state experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json --private /Users/yukakust/.rabbit-owner/runtime.key
Then exact20 APPLIED -> fresh read-pci + QPD8 decode -> owner current city/tail.
No fresh preparation, signed21, reboot flag, pending clear or old19 resume.
If current20 now reaches BMI, inspect immutable snapshot before choosing changes.
Pinned Linux pci_host_ce_config_wlan/ce.c init_src_ring/init_dest_ring configure
host-side queues; our current all-engine halt/zero clears both halves. This is a
source difference worth examining with fresh observations, NOT a proven physical
cause or authorization to skip DMA/stop/lifetime gates. Capture target-side initial
configuration before any speculative ring changes. Full Wi-Fi/Unreal transport
not achieved; firmware upload/scan/WPA/DHCP/reconnect still pending.

## 2026-10-04 — SAME native20 applied; memory repair physically passes, CE idle

Owner replied «рядом» to proximity request. Exact saved20 resumed from receiver-
confirmed1400/71456. Two timeouts reached2000 then a long connection staged full
71456; COMMIT/reconnect exact SHA/session/counter20 APPLIED. Same nonce/counter/
packet, no preparation or reboot. Current native20/world13, native_pending null,
12-version idle journal/world content unchanged. All radio helpers terminal.
No USB/bootstrap/owner-key-copy/Mac native build. Reachability improved during
this trial; this does NOT establish a lasting RF fix or cause of earlier timeouts.

Fresh physical QPD8 from known F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF: cached attributes
200 / original+restored PCI Command0100, active snapshot0102, chip003821ff/rev1,
D0/reset/revalidation good. Memory-enable repair crossed the prior step11 failure;
ROM indicator2/ready, then BMI3second timeout5/overall0x805. NEW persisted snapshot
captured: initial TX/RX0/0, last observed hardware0/0, software reads0/0/writes1/1,
TXdone/RXdone false; request08000000 at mappedb1d07000, response12zeros atb1d06000,
TXdescriptor0070d0b10400fcff, RXdescriptor0060d0b100000000, received bytes0.
This proves posted request/response and no observed completions; it does NOT
prove why hardware failed to advance or claim a fresh simultaneous register read.
No BMI version/type/firmware upload/startup/scan/association/DHCP success.
DMA held0/mask0, busownedfalse, resetownedfalse, cleanupcomplete, ASPM0140->0143
and bootIRQ/Core8688/enable0 restored. Physical city/motion after20 requested,
answer pending; do not turn gate snapshots into physical animation observation.

Evidence cached-memory-native20/physical refreshed with all exact receipt/radio
logs and raw+decoded QPD8/hash summary. Prior incomplete-transfer summary retained
as initial-pending-trial-summary.json. Git evidence session representations are
metadata/hash only; exact binary/session files stay ignored under local runs.
DO NOT rerun native20 delivery or reuse retired19/15/16. New profile counter>20
must bind actual current20/world13 and retain BLE recovery/MemoryEnable repair.

NEXT independent investigation: capture each CE source/destination base,size,
control/command and indices AFTER ROM ready BEFORE our first all-engine stop/zero.
Our current stop zeroes both queue halves; pinned ath10k ce.c init_src_ring and
init_dest_ring set only host-configured halves. This is a reviewable source
mismatch/hypothesis, not physical proof of peer configuration or cause. Read-only
bounded/cooperative snapshot first; never blindly preserve unknown DMA/ring state
or bypass all-eight quiescence, bus-master-off, Flush/Unmap/Free ownership gates.
After owner scene check, gate/sign/send that separately reviewed diagnostic and
compare before/after queue configuration to locate CE transport failure. Full
original Wi-Fi/Unreal-to-Dell goal remains incomplete; no credential consumer yet.

## 2026-10-04 — native21 applied: initial CE queues are already empty

Owner authorized the bounded pre-halt diagnostic («делай»). QPD9 retains QPD8's
exchange snapshot and adds264bytes of read-only register telemetry,620bytes total.
After ROM-ready/IRQ restoration/fresh identity and bus/access init, stage13 reads
one CE engine per poll before any halt/zero, with bus mastering off and no DMA
allocation. Source/destination bases/sizes, control/command/read indices are raw
values only, never dereferenced or reused. Original teardown/lifetime gates remain.

Yukabox gates:38 ASan/UBSan integrated scenarios including synthetic nonzero
initial queues, pre-halt read failure/all-ones/cancellation, immutable snapshots;
invalid decoder masks/data; existing port/reset/CE/BMI/DMA/Bluetooth recovery;
actual UEFI normal+EMPTY diagnostic three-part Read/ReadBlob with offset621
rejected; two rebuilds/current-world C check. Missing pre-halt gate explicitly
rejected before signing/radio. No native driver compilation on Mac.
Checked local runs/bmi-profile-native21; payload SHA256
4eb51e4d8559bb244bcde4f1e1453c5a11e501147cd1f662d756b1c423610a61.
Owner-signed exact saved session pci-native-iody16yf resumed across SIX delivery
route invocations and repeated bounded reconnections,0->3100->26200->40300->65500
->65600->71456bytes, then COMMIT/reconnect exact SHA/session/counter21 APPLIED.
Current native21/world13, native_pending null, idle12-version journal unchanged.
All radio processes terminal. No physical USB/bootstrap write, Dell reboot or key
print/copy. Mac current Wi-Fi2.4GHz/channel8 was observed; optional owner5GHz
switch question unanswered. No network switch made and no RF cause established.

Fresh physical QPD9 from known F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF:
valid255/failed0, all EIGHT queues before first halt have source/destination base
and size0, read indices0, command0, control80. Thus clearing existing configured
queues is NOT supported as the cause in this trial. Do not preserve unknown DMA
state or skip halt/lifetime protection on that hypothesis. Chip003821ff/rev1,
D0/reset/revalidation good, ROMindicator2/ready, BMI timeout5/overall805 persists.
QPD8 retained portion again has softwarewrite1/1, hardwarelastobserved0/0,
request08000000, response12zeros, no TX/RX completion. DMAheld0/mask0, bus/reset
ownership false, cleanupcomplete, ASPM0140->0143 and IRQ/Core8688/enable0 restored.
No BMIidentity/firmwarecompatibility/upload/startup/scan/WPA/DHCP/network success.
Owner post21 city/tail observation requested, still pending at record time; never
claim physical animation from exact receipt or QEMU tests.

Evidence: experiments/native-wifi-qca9377-v1/evidence/2026-10-04/pre-halt-native21,
gates/reproduction, physical exact receipt/all logs/raw+decoded QPD9/hash summary.
Session evidence metadata only; exact saved packet/session/binaries stay ignored.
DO NOT replay completed21 or retired20/19/15/16. Future native>21 must bind current
21/world13, preserve cached-MemoryEnable repair and Bluetooth recovery.
NEXT: compare pinned ath10k BMI descriptor/publication, CE reset/run/clock/wake
sequence and actual bus-master/DMA access. Add separately bounded observations
where required before changing behavior; chip ready does not imply BMI ready or
firmware compatibility. Await owner city/tail check before another hardware
candidate. Full Wi-Fi and Unreal/Yukabox-to-Dell streaming goal remains unfinished.

## 2026-10-04 — owner confirms native21 city; pre-BMI sequence audit

Owner replied «виден»: city visible after21 confirmed; do not infer tail movement.
No new radio delivery or chip writes in this audit, current21/world13 unchanged.
Pinned pci.c/hw.h hashes checked again on Yukabox. QCA9377 dispatch selects
qca6174_chip_reset (cold+warm), qca6174 CPU-to-CE translation. hif_power_up order is
chip_reset -> init_pipes -> init_config -> wake_target_cpu. init_config uses
CE7 diagnostic target reads/writes: interconnect state, target pipe configuration,
service-to-pipe map, PCIe flags, early allocation(9banks), EARLY_CFG_DONE; then
CORE_CTRL CPU_INTR2000. Current probe performs cold reset/ROM-ready -> host CE0/1
configuration -> direct BMI. It omits that target initialization handoff and warm
reset. Request command8/4bytes, receive-before-send and metadata3fff match reviewed
BMI descriptor publication; no evidence yet that changing these fixes the timeout.

Evidence pre-bmi-sequence-audit/reference.json retains bounded pinned pci.c
excerpts with hash/line numbers; summary binds current probe/source findings.
This confirms a SOURCE SEQUENCE GAP, not the physical cause or working solution.
Next narrow trial: implement/host-gate bounded read-only CE7 diagnostic transfer,
then read the fixed QCA9377 host-interest interconnect pointer. Validate target
address translation/range, mapped host buffers, cancellation/timeout/all-eight
teardown before physical trial. Returned pointers must not grant arbitrary read/
write authority. Only afterward add separately gated target configuration and
CPU notification; do not set EARLY_CFG_DONE or load firmware prematurely.

## 2026-10-04 — native22 applied, CE7 response bytes arrived before first poll

Implemented fixed read-only CE7 for QCA9377/rev1 word4008f8. No arbitrary target
address or pointer chase/write API. Translation CORE_CTRL low11bits<<21 must match
fresh PCI BAR; register extent covers target window; active Command exact0106,
registered nonoverlapping DMA/rings, RX before TX, flags/metadata0. Successful
CE7 would all-eight stop/flush/close/reuse rings before old BMI. Failure suppresses
BMI and enters existing guarded teardown. QPD10/700bytes persists CE7 snapshot.
Contract CE7-DIAGNOSTIC-CONTRACT.md and pinned diag-target.json. Fresh downloaded
primary targaddrs.h/core.h/pci.h checked by hashes on Yukabox (no Mac native build).

48 sanitizer integrated scenarios + component/Bluetooth recovery/normal+EMPTY
actual UEFI mock long diagnostic bounds/invalid snapshot fixtures pass. Current-
source two rebuilds/current-world check pass; missing fixed_ce7_read_only gate
rejected before local owner signing. Exact22 payload
be1c663e6651eca986170397a86c7c9b726179a0c4aed24559d3c751d013d19f
saved pci-native-q_oei4o_. Single stage connection0->74528bytes without interruption;
COMMIT/reconnect exact SHA/session/counter22 APPLIED. This is a better trial,
not a proven lasting Bluetooth/RF fix. Current22/world13, native_pending null,
idle12-version unchanged journal. All radio processes terminal, no USB/bootstrap,
Dell reboot, private-key output/copy or firmware/early-config write.

Fresh physical QPD10 from known F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF:
CE7 phaseFAULT3/error7 timeout100ms/overallD07; initial indices0/0, lastobserved
BOTH NULL (mask0): timeout happened before the first hardware-index polling pass.
TX softwarewrite1 / RXwrite1, source target4008f8->d11008f8 using CORE8688,
Command0106. TXdesc f80810d104000000; RXdesc0050d0b104000000 at mappedb1d05000.
Response changed from prezeroed0 to00401ee0; RX descriptor length changed0->4.
This is observable mapped-memory write evidence consistent with a CE7 reply,
NOT a completed/correlated diagnostic read and not pointer access authority.
Do NOT call it a DMA-no-response trial or immediately change descriptor encoding.
BMI was not started (QPD8 exchange absent/bmi_error0). ROMready2, chip003821ff,
reset/revalidation good; DMA held0/mask0, bus/reset ownership false, cleanupcomplete,
ASPM0140->0143, IRQ/Core8688/enable0 restored. Owner post22 scene check requested,
pending; do not infer animation. Full Wi-Fi remains incomplete.

Evidence ce7-native22 gates/reproduction/physical receipt/raw+decoded/hashes; session
metadata only in Git, exact binary packet/session remain ignored. Completed22 must
not be resent. NEXT: change diag poll to observe completion before declaring wait
timeout,3second cooperative budget and first/last elapsed/poll-count telemetry.
Gate and sign NEW23 against exact current22/world13. Only confirmed CE7 read plus
validated target ABI permits later bounded initialization configuration. Re-read
fresh physical diagnostics and obtain owner scene observation after new application.


## 2026-10-04 — native23 physical CE7 completion confirmed

Native23 fixes premature timeout: observe both hardware completion indices before
testing elapsed wait budget, use3seconds, and latch first/last poll delay and count.
QPD11/716bytes retains QPD10 and adds16bytes. Decoder assumes no polling frequency.
52 ASan/UBSan host scenarios, normal/EMPTY exact UEFI city/ATT checks, two source
rebuilds/current-world C check passed on Yukabox. Missing completion-before-timeout
gate is rejected before local signature/radio. Mac only built control reader/sender.

Locally signed23 exact current22/world13. Saved session pci-native-dlu8d1sa,
74528bytes staged in one uninterrupted connection, then COMMIT and exact correlated
SHA/session/counter APPLIED after reconnect. Current native counter23, payload
99af1e47e32c2e416f807a56420be812b95e9e3ceaf9c65ae5c9342acfdc4342;
world13/package unchanged, journal idle12versions, all pending slots empty.
Do NOT replay completed22/23. No USB/bootstrap write or Dell reboot.

Fresh physical QPD11 from known F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF:
CE7 DONE2/error0, TX/RX indices0->1, four received bytes, fixed4008f8->d11008f8
returned00401ee0. First/last polling390000us, one poll, within new3s budget but
after old100ms deadline. Confirms premature native22 timeout. Device completion
time unknown. This proves bounded CE7 read, not arbitrary pointer authority or
full Wi-Fi connection. Raw response matches native22 observational bytes.

First read caught stage11 BMI still active; preserve it separately. Later fresh
read is terminal stage6/error805: CE0/1 BMI timeout, both observed indices0,
response12bytes allzero, request08000000. CE7 snapshot persists across reused
response DMA page and BMI cleanup. Four DMA buffers released, heldmask0,
bus/reset ownership false, cleanupcomplete. PCIe ASPM restored0143 and IRQ/core
restored8688/enable0. No firmware upload, target initialization write, association,
WPA or DHCP. Owner subsequently confirmed post23 city visible; tail movement
was not explicitly confirmed.

Evidence: experiments/native-wifi-qca9377-v1/evidence/2026-10-04/ce7-poll-native23.
Gate reportSHA a10dd7855267d7be2d95401f8f9d8d3e1c6a934be2d8adf5dff9df8398e39972;
reproductionSHA909a9060a279828f1770632f1fe00a3deadf4c9e7f66136e122ea697df577db4.
Only session metadata goes in Git; exact packet/session remain ignored.

Next initialization boundary:
1. Extend narrow read-only CE7 Target Pack to validate PCIe-state layout and
   bounded config destinations. Physical4008f8 returned401ee0; treat as data until
   alignment/range/nonoverlap/length checks. Never chase arbitrary pointer.
2. Pinned pci.h pcie_state is9 LE32words: pipe_cfg_addr+0, svc_to_pipe_map+4,
   MSI fields+8..24, power_mgmt_method+28, config_flags+32. Read it and fixed
   hi_early_alloc400900/hi_option_flag24008cc before designing writes.
3. Host-check exact target-side pipe/service tables for QCA9377, including
   qca6174 override. Ensure all advertised channels have owned host resources.
4. Follow pinned qca6174/QCA9377 cold+warm-reset ordering and safe CE lifecycle.
   Write/read back only validated bounded RAM destinations, clear PCIeL1 mask0x1,
   early_alloc magic6d8a in high16bits with9IRAM banks. EARLY_CFG_DONE mask0x10
   is last commit marker; set only after verified configuration, then CPUwake2000.
5. Fresh signed candidate>=24, saved Bluetooth session/exact receipt, fresh
   diagnostics, complete teardown and owner scene check. BMI/version/firmware
   gates still separate; successful CE7 alone does not authorize firmware loading.

Reason for separate initialization phase: CE7 now proves the memory transport,
while physical target config layout/contents and the missing warm/CPU handoff
sequence are not yet verified. Do not claim CE7 timeout fix solved BMI timeout.


## 2026-10-04 — native24/25 initialization reads, transport fixed, QCA9377 spans checked

Implemented finite CE7 configuration reads authorized only after completed HI
word4008f8 equals401ee0: fixed pcie_state401ee0/36bytes, early_alloc400900/4,
optionflag24008cc/4. Three successful reads copied into immutable telemetry
before reuse. No arbitrary pointer chase, RAM writes, CPU wake or firmware upload.
60 host ASan/UBSan scenarios include wrong HI value, each read timeout, partial
completion, invalid36byte response length, cancellation and all-ones table pointer.
Actual normal/EMPTY UEFI city/ATT, current-world checks and two rebuilds passed.

Native24 exact APPLIED at saved pci-native-o97jwm4t,75552bytes. Physical Mac
reader rejected800byte QPD12: returned738bytes(3*246) without NSError, missing62.
No padding or acceptance of incomplete configuration. Exact UEFI QEMU four-chunk
pass was not presented as proof of physical Mac read. Underlying limit cause
not proven. Evidence init-read-native24 has receipt, rejected raw prefix, gates,
and six-file source overlay/full manifest to recover24 from final25 tree.
Completed24 must not be replayed.

Native25 fixes transport: distinct diagnostic UUID8/service8..12, original file
service1..7 retained. Read-only UUID6/handle10 main716bytes; UUID7/handle12 QIC1
120bytes(header4+SHA256 main32+tail84). Reader requires terminal stage5/6/7 and
hash match before assembling QPD13/800bytes. Independent combiner rejects partial
parts, bad hash/header and correctly hashed active probe. Actual UEFI tests read
main+extension and verify hash/bounds. Missing split gate rejects before signing.
SHA binds two reads, does not attest device. Physical read now succeeds.

Native25 exact APPLIED saved pci-native-y9dcccyr,76064bytes, staged one connection,
COMMIT/reconnect correlated SHA/session/counter receipt. Current native counter25,
payload4f4303fd5be75c7146b93ee1339b729b5ec62b56a1b85dbf6bb7cc5a7baee564,
world13/package unchanged, journal idle12versions, all pending slots empty.
Do NOT replay25 or use its old source-bound gates for a new payload.

Fresh known F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF QPD13: configuration DONE4,
error0/mask7. pcie_state words:
404d90,404e50,8,0,0,0,0,3,1. Early_alloc0, optionflag20. CE7 four-byte HI
read still completed, config last4byte read firstpoll390ms, both completion
checks passed. Pipe address404d90, service404e50. BMI remains timeout805 with
ROMready2; complete cleanup, DMAheld0, bus/reset unowned, ASPM0143 restored.
Owner subsequently confirmed post25 city visible; tail movement was not explicitly
confirmed. Native23 city visibility was also confirmed previously.

Important source correction: initial HOST preflight incorrectly assumed10 target
records from generic pci_target_ce_config_wlan and rejected physical overlap.
No hardware writes were enabled or sent. Pinned core.c maps QCA9377 to
qca6174_values; hw.c defines ce_count8 but num_target_ce_config_wlan7. hw.h
NUM_TARGET_CE_CONFIG_WLAN resolves that chip-specific field. Correct write span
is7*24=168bytes, not240 or192. Service map17*12=204bytes. The192byte pointer gap
is available layout space, not proof that eight records should be written.
CE7 diagnostic entry is not part of target's seven configuration records.
Pinned QCA6174 override: record5directionOUT2/max2048; service record15pipe1.
Pinned pci.c QCA9377 uses9IRAM banks.

New init-target.json pins core.c/ce.h plus original hw/pci/targaddrs hashes.
verify_init_pack.py independently checks source mappings/counts/record sizes,
service count, bank count and override; Yukabox primary check passed.
Corrected init_preflight.py passes exact physical25 receipt/current-state/raw
checks, checks conservative400000..410000 spans/alignment/nonoverlap/reserved
regions and flags, and runs10negative cases. Pipe168bytes404d90..404e38;
service204bytes404e50..404f1c. Planned values: config_flags401f00 1->0;
early_alloc400900 0->6d8a0009; optionflag24008cc remains0 until last commit.
Tables not generated, warm-reset sequence not yet verified, target writes disabled.
Physical field/destination validation is not full firmware compatibility.

Evidence init-read-native25 has full physical raw/decoded/spans, primary source
check, host reports, receipt/session metadata and old host-preflight source overlay.
That overlay preserves the source-bound25 build input before corrected preflight;
its generic10record host mock pass is not the corrected physical span gate.
No generated binaries/session stream/private keys in Git. No USB/bootstrap write,
Dell reboot or initialization RAM write performed by agent.

Next hardware candidate>=26 after post25 scene observation: pin new init pack and
verifier in source snapshot; implement QCA9377 cold+warm ordering and bounded
CE7 config writes/readback with owned host channels matching advertised target
tables. Only then EARLY_CFG_DONE0x10 as last marker and CORE_CTRL wake0x2000,
then BMI/version query. All cancellation/error paths retain safe DMA ownership
and guarded teardown. Firmware/WPA/DHCP/streaming remain later steps.

## 2026-10-04 — initialization table candidates independently verified

After owner confirmed city visible, added init_tables.py: exact seven LE32 pipe
records/168bytes and seventeen service records/204bytes. verify_init_pack.py
independently parses pinned pci.c/ce.h/htc.h, applies source-checked QCA6174
override and compares every encoded byte. New htc.h hash pinned in init-target.
Yukabox report passes,42 negative resource cases reject unowned/unmapped,
duplicate/missing/unsupported channels and malformed rings/buffer capacities.
Optimized Python explicitly rejected to keep source assertions enabled.

Important host CE5 detail: upstream override disables its host queues and moves
HTT RX service15 to CE1. Do not invent an extra CE5 host TX queue merely because
target CE5 direction is OUT. CE6 target-autonomous. Required active host channels
are0TX/1RX/2RX/3TX/4TX/7TX+RX. Current native25 has only0/1/7; live resources are
still incomplete. Pure synthetic inventory checks are not live DMA proof and
are not integrated into native_route signing or runtime write authorization.

Verifier also pins exact cold+warm call order and warm BAR offsets/masks from
primary pci.c/hw.c/hw.h. This checks upstream sequence, not our native execution.
Native cooperative warm-reset implementation, added live channels, finite CE7
write/readback/commit and CPU wake remain pending. INITIAL-CONFIG-CONTRACT.md
records the boundaries, loading and guarded recovery requirements.

Evidence init-tables-host includes primary-source/table report and new host
span check against exact physical25 receipt/current state. No new physical
probe, payload signature, Bluetooth send or USB/bootstrap write. Engine remains
native25/world13, pending slots empty. Old25 gates cannot cover these changes;
future candidate must snapshot init_tables.py/new verifier/pack with full gates.

## 2026-10-04 — warm-reset and full-host-channel C components checked

Owner authorized continuing. Added warm_core.c/h, channels_core.c/h and their
host fixtures/verify_init_core.py. Warm reset now exists as cooperative C code,
with two CPU resets, SI0/CE timing, bounded ROM waits and a cooperative pipe
callback. Guard/clock/I/O/cancellation failures retain exclusive ownership.
CE ownership precedes ambiguous assertion; recovery can only deassert after10ms
and verified clear, never restart or silently release an errored operation.

Full channels allocate14 pages/57344bytes for0TX/1RX/2RX/3TX/4TX/7TX+RX.
Each registered mapping and ring is owned; live preparedness checks current PCI
command and actual hardware bases/sizes. CE5 host disabled and CE6 autonomous.
Data RX1/2 posts after explicit start; diagnostic RX7 only per exchange. Reuse
retained mappings after all-eight stop; cleanup one guarded buffer per poll.
Duplicate DMA maps reject; aliased host allocations retain ambiguous ownership.

Yukabox ASan/UBSan and freestanding COFF gates passed.27 real-component channel
fixtures plus warm every-I/O/every-phase cancellation/guard faults, second ROM
and pipe failures, timeouts/clock/recovery tests passed. Joint warm/channel fixture
performs both pipe initializations using identical14 retained pages, no BME-on
or unmap/free during reset. Source and transitive ABI identities checked before
and after gates. Evidence init-core-host, not physical/QEMU proof.

Critical integration boundary: bmi_probe.c/bmi_build.py remain native25 profile,
not linked to new cores. Existing boot_irq.c forbids polling with dma_users>0;
do not weaken that check to combine mapped channels with warm ROM polling.
Need separately gated mapped/BME-off boot-IRQ adapter, actual native lifecycle,
bounded verified cold recovery for warm faults, latched telemetry/split decoder,
integrated faults and exact normal/EMPTY UEFI/current-world/two-build gates before
signing candidate>=26. Warm owned flag must never be cleared merely to unload.
INITIAL-CONFIG-CONTRACT.md has detailed loading/observability/recovery boundary.

No new signature, session, Bluetooth send, USB/bootstrap write or Dell reboot.
Physical receiver remains applied native25/world13, all pending slots empty.
Target RAM initialization writes, CPU wake, firmware, association and network
streaming remain unperformed. Owner last confirmed city visible, not tail motion.

## 2026-10-04 — native26 physical warm/full-channel trial, retained recovery

Integrated separate init_probe/init_adapter/init_build profile, mapped IRQ scope
with original no-DMA boot_irq guard preserved, and QPD14 split diagnostic UUID9.
Yukabox host fault/ASan/UBSan/COFF, actual17 entrypoint fixtures, normal/EMPTY UEFI
city/ATT, two current-source rebuilds and unchanged world C gates all pass.
Source snapshot273files;11 bad signing prerequisites rejected before key access.
Native26 exact APPLIED: pci-native-wg2f6n8n,76064bytes, payload
 d8a6dd6805c3862e201b43a05cdf860e71895227b6c94f471af391c33f4cd583.
World13/package unchanged, all pending slots empty. Do NOT replay26.

Fresh known Dell QPD14/hash split: stage20/adapter13 RETAINED, warm error2
(second ROM wait timeout, CPU resets2/pipe initializations2), fourteen pages
held, BME never enabled. Recovery cold phase3/unowned, ROM2, mapped guard error0,
IRQ quiesced; recovery_verified0. All-eight-stop proof after cold reset failed,
so warm/PCI/IRQ/link ownership remains held. This is not a warm success or full
cleanup. City/tail after26 requested, not yet observed by agent. Evidence:
evidence/2026-10-04/init-warm-native26 (exact gates/source/receipt/raw/decoded).

Code recovery currently stops CEs BEFORE cold reset, then checks stopped state
AFTER reset. Hypothesis: cold reset clears halt/register state. Existing mocks
kept CE registers across reset and missed this. Need explicit reset-cleared
register fixture, post-cold all-eight stop and verified recovery proof, with
finite retries and no release until proof. Actual post-cold CE values were not
captured, so cause is not yet physically proven. Retained resources prevent
module replacement; only owner-authorized physical reboot can clear current
state. Prepare/verify fix before requesting reboot; never force-clear owned flags.
No target RAM writes, CORE wake, firmware/association/DHCP or stream was performed.

## 2026-10-04 — post-cold stop fix checked, not signed or sent

Native26 trial/evidence committed and pushed611f7ee. Reproduced retention in
actual native entrypoint fixture: cold reset now clears CE registers. Original
adapter fails scenario13 cleanup assertion (saved baseline failure). Corrected
adapter quiesces IRQ on ROM-ready, then re-stops all eight CEs AFTER cold reset,
rechecks guarded PCI/ROM/all-eight-stop and only then marks recovery verified,
clears warm ownership and begins guarded one-page cleanup. Sticky reset errors,
ROM timeout, stop/flush failures still retain. Second warm ROM timeout itself is
not resolved; actual post-cold physical registers were not captured.

Added second-warm-ROM-timeout scenario17; actual entrypoints now18scenarios.
Signing requires post_cold_ce_stop plus cold_reset_clears_ce_fixture in both core
and actual entrypoint reports. Full Yukabox ASan/UBSan/COFF/pinned pack/normal and
EMPTY UEFI city/ATT/BLE/decoder gates pass,273 current sources/two identical rebuilds
and unchanged world13 C checks pass. Corrected payload SHA:
b6f108f7a91e1786f31bc2db08922e100fd2667b4d360bab24c6d4867da891de.
Mac exact native_route.gates passes and rejects missing new post-cold flag.
Evidence evidence/2026-10-04/init-postcold-host. No fix signature/session/radio send.

Physical engine remains26/d8a6dd..., world13 unchanged, all pending slots empty;
retained14 mapped pages, BME off, module unload prohibited. Owner city/tail after26
question remains pending. Need owner-confirmed physical Dell reboot, then fresh
empty receiver and exact signed boot-city recovery before new physical native
trial. NEVER infer reboot from RF loss or force-clear warm/map ownership.

Recovery integration caveat: generic city_recovery.py chooses last_release_report
and compiles native city on Mac; do not use it for this diagnostic profile or
violate Yukabox-only native builds. reboot_recovery.py has proper remote preflight
but prepare currently expects pending native/recovery, whereas26 completed and
all slots are idle. Add/check explicit completed-current reservation or equivalent
strict idle boot-recovery plan; do not fabricate a pending slot or reuse consumed26.
Plan must bind exact completed26 receipt/base/counters, saved world and owner key;
validate fresh empty boot only after owner confirms reboot. Restore counter>26 and
world counter>13, then rerun current-world binding for the fixed native candidate.
Preserve city/cat/history and immutable USB/bootstrap. Owner key stays Mac-local.

## 2026-10-04 — completed26 offline boot recovery READY

Supersedes the preceding recovery integration caveat. reboot_recovery.py now
supports idle completed diagnostics explicitly: verifies APPLIED predecessor26,
correlated session/counter/hash/current-world and owner public signature; preserves
its files and reserves27 without fabricating native_pending. prepare remains
strictly offline; activation still requires explicit owner-confirmed actual reboot
AND exact fresh-empty receiver before any write.15 signed-fixture controller
cases pass on Yukabox, including completed full restore/resume and mutation guards.

Yukabox current-world/roof-cat C+sanitizer checks, two equal BLE-recovery city
builds, normal and EMPTY UEFI gates passed. Checked directory on Mac:
experiments/native-wifi-qca9377-v1/runs/idle26-city-recovery-mac.
City recovery payload0fb9fa6c1c307e8ca0fe51b4b29e3cd815c3e2881f9c1ceba6d01d80ce52b4ce,
Wi-Fi probe disabled. Source/crypto/world evidence gate verifies locally.
Owner key used only locally after gates; exact offline native27 and world14
sessions are prepared at absolute directory:
/Users/yukakust/rabbit-stack/experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/reboot-recovery-native27.
Plan PREPARED-NOT-ACTIVATED, old_pending_kind=completed, reserved_counter26,
world13 semantic city/cat preserved at future world14. No plan27 radio transmission.
Actual restore WITHOUT --dell-rebooted rejects before radio; state byte-unchanged.
Evidence evidence/2026-10-04/idle26-recovery-plan, no packet streams/binaries/keys.

NEXT: ask owner to physically reboot Dell and report completion. Until explicit
confirmation do not execute recovery writes. Once confirmed:
python3 experiments/native-wifi-qca9377-v1/reboot_recovery.py restore --state experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json --directory /Users/yukakust/rabbit-stack/experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/reboot-recovery-native27 --private /Users/yukakust/.rabbit-owner/runtime.key --dell-rebooted
Use same directory/sessions on interruption; never recreate/resign unless a new
strict reservation is required. Runtime27 then world14 require exact receipts,
then owner city/tail observation. No Mac native compilation or USB write.
After recovery, rebuild full fixed init profile/source+world binding on Yukabox
before signing a later counter28+ trial; prior f91204d fix gates bind world13 and
old recovery-helper source and cannot authorize changed world14/current inputs.
Physical second warm ROM timeout still unresolved. Capture more diagnostics;
do not claim that post-cold fix solves initialization/firmware/WPA/DHCP.
Current actual state remains native26/world13, retained Wi-Fi ownership/BME off,
all pending slots empty. Owner observation after26 is still pending.

## 2026-10-04 — owner reboot confirmed, recovery27/world14 APPLIED

Owner explicitly said 'перезагрузил'. Executed exact prepared native27 recovery
under controller lock; initial read-only query on known Dell F45BFCB2-ABC2-AB4E-
BB0F-310A54D424AF returned exact zero/EMPTY receiver. Only then activated plan.
Native27 staged47904bytes, committed/reconnected and returned exact correlated
APPLIED receipt. Then world14 staged2128bytes and exact APPLIED receipt returned.
No new nonce/packet/replay, key export, USB/bootstrap write or Mac native build.

Current runtime27 payload0fb9fa6c1c307e8ca0fe51b4b29e3cd815c3e2881f9c1ceba6d01d80ce52b4ce,
world14 semantic SHA unchanged fa5a3250633f2bbbd288d947be567c2c5db8e3395033da99b765edf0a0f5cc74,
package46f7cc5f1ad67d32a53d7328bfe1a68324eab7c1757f3ec96468787b3a7f1fac.
Recovery/world/native pending slots empty; completed26 evidence preserved in
retired_native_sessions. Recovery directory reboot-recovery-native27 completed:
do NOT replay it. Wi-Fi probe disabled in recovery city profile.
Physical city/tail after recovery27 has been asked through async question and
is pending; do not infer screen behavior from APPLIED or QEMU.
Evidence: evidence/2026-10-04/idle26-recovery-applied27.

Independently rebuilt fixed init profile on Yukabox with CURRENT recovery-helper
source. Full host fault/COFF/normal+EMPTY UEFI/BLE/decoder gates pass, payload
b6f108f7a91e1786f31bc2db08922e100fd2667b4d360bab24c6d4867da891de.
Fresh273 source hashes + two rebuilt payloads + exact current world14 C/sanitizer
checks pass; Mac native_route.gates verifies updated report/reproduction/world.
Checked directory experiments/native-wifi-qca9377-v1/runs/init-profile-native28.
No native28 key signature/session/physical send yet. Physical post-cold fix is
still unverified; second warm ROM timeout unresolved. After owner confirms city/
tail, sign fresh28 against actual runtime27/world14, send exact saved session and
read hash-bound QPD14 on known Dell. Check recovery/cleanup as well as timeout;
never clear ownership flags or imply firmware/association success.

## 2026-10-04 — native28 applied; physical post-cold cleanup PASS

Owner said 'виден' after27: city visible; tail motion not confirmed. Sent exact
gated native28 against runtime27/world14; staged76064 then exact correlated APPLIED
receipt after COMMIT/reconnect. Saved session pci-native-ifvdvbiy; do NOT replay.
Current native28 payload b6f108f7a91e1786f31bc2db08922e100fd2667b4d360bab24c6d4867da891de,
world14 unchanged, all pending slots empty. First read rejected still-active probe;
next read fresh known Dell F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF QPD14 hash split.

Physical stage6 failed-but-cleaned: warm timeout2, CPU resets2/pipe inits2;
adapter CLOSED12, channels CLOSED6, allocated14/cleanup cursor14, no held pages,
cold recovery verified/ROM2/unowned, IRQ/link/PCI restored, no retained ownership,
BME off. This verifies post-cold stop/release fix on Dell. Warm initialization is
still NOT successful; firmware/association/DHCP/streaming remain unperformed.
City/tail after28 async observation pending. Evidence under
experiments/native-wifi-qca9377-v1/evidence/2026-10-04/init-postcold-native28.
No autonomous reboot, USB/bootstrap writes, target RAM writes or key export.

Next offline candidate adds QPD15 cached warm failure phase, last indicator,
phase elapsed microseconds, first/second ROM poll counts and last reset read.
No additional MMIO operations: reads only already cached core values. Full gates,
source/current-world reproduction and local signing gate required before sending.
New UUID0A avoids cached GATT envelope; main716, QIC1 extension208, total888.
Read-only Mac helper /tmp/rabbit-read-pci15; old14 remains supported. Do NOT use
old28 gates with changed telemetry sources to sign a new packet.

QPD15 full offline gates now PASS on Yukabox, payload
11a9df2059578ca8f2b6c7046a61e211672ddda3f5ab065660038fb99190db3e.
18 real native fixture scenarios; second-wait case17 explicitly asserts phase11,
indicator0, elapsed>=3s and both ROM polls preserved through recovery. Existing
warm operation traces pass. Split/decoder negatives, normal+EMPTY UEFI/ATT/BLE,
273 current sources, two identical rebuilds and exact world14 C/sanitizer all pass.
Mac native_route.gates read-only gate passes: report9a9b1c0683ef6fba38838f9bb818ce4a081d09312749d82497687835c1b24dbf,
reproduction5d5ab08dcd0b63256188abb505269a4c95f1fc593ac8ba9ec844ab6b7708db9a.
Checked directory runs/init-profile-native29. No29 signature/session/send yet;
physical runtime28 and world14, no pending. Mac readonly helper compiled and19
historical physical reports decode. Evidence warm-failure-qpd15-host is HOST ONLY.
NEXT: obtain owner scene/tail observation after28 (asked async), then current
bindings/sign counter29/send saved session/read QPD15 with /tmp/rabbit-read-pci15.
Physical post-cold cleanup28 passed; exact warm failure cause still unresolved.


## 2026-10-04 — native29 applied; GLOBAL warm deadline identified

Owner said 'все видно, продолжай' after28: city visible (tail not explicit).
Sent exact QPD15 native29, session pci-native-aqp0dyyt,76064bytes, exact APPLIED
receipt; world14 unchanged and no pending. Fresh known Dell QPD15 split confirms
stage6/adapter CLOSED12;14 pages freed, verified cold recovery/ROM2, PCI/link/IRQ
restored, no retained ownership. No autonomous reboot/bootstrap/key export.

Failure phase11 SECOND_ROM, last warm indicator0, elapsed1175000us, polls4/2,
last reset read33000800. This is below per-wait3s, so global7s bound exhausted
first; do NOT claim a complete second3s wait or blame chip boot performance yet.
Physical evidence warm-failure-native29; host prerequisites warm-failure-qpd15-host.

Pinned pci.c audit separately found IRQ-window discrepancy: upstream disables/
clears IRQ before warm and after each ROM wait; ours enables across reset. Saved
warm-irq-sequence-audit, hypothesis only. Do NOT combine it with deadline test.
Next candidate changes ONLY total warm deadline20s (each ROM stays3s). Actual
native fixture18 with600ms calls reproduces old7s failure and must pass with20s;
19 scenarios total, source/signing gates require slow cooperative fixture proof.
Full current-source/current-world gates underway on Yukabox before any signing.


## 2026-10-04 — native30 PHYSICAL warm/channel PASS

Full gates19 native entrypoint scenarios, slow600ms WARM-only calls and old7s
source failure baseline passed on Yukabox; two equal rebuilds/current273 inputs/
exact world14 C+sanitizer, normal+EMPTY UEFI city/ATT/BLE/decoder passed. Local
signing gate accepted exact profile; only global warm bound7s->20s changed (ROM
waits remain3s). No IRQ-window/DMA/target RAM/firmware change. Host evidence
warm-deadline-host, checked runs/init-profile-native30. Initial failed fixture
setups (obsolete ASPM fault selector/slowed outer reset) are NOT baseline proof.

Signed/sent session pci-native-3skn7pxs counter30,76064bytes staged then exact
APPLIED receipt on reconnect. Current payload39d66beb7a05b7919eca5f162c230ac057d95a229cf2d55eeb0db9a7317daa60,
world14 SHAfa5a3250633f2bbbd288d947be567c2c5db8e3395033da99b765edf0a0f5cc74,
package46f7cc5f1ad67d32a53d7328bfe1a68324eab7c1757f3ec96468787b3a7f1fac.
No pending slots; do NOT replay30. Fresh known Dell QPD15 split: stage5 SUCCESS,
root/adapter/warm errors0; warm DONE12, CPU resets2/pipe inits2, ROM polls4/4,
last warm indicator2/failure phase0. Adapter CLOSED12/channels CLOSED6,
allocated14/cleanup14, no held buffers/ownership, IRQ/link/PCI restored, BME off.
No extra cold recovery needed. Physical evidence warm-deadline-native30.

Global deadline really blocked prior trial; increasing it alone allowed complete
physical warm initialization. IRQ-window hypothesis remains a source discrepancy
but is NOT a required next fix after this success. Never claim association,
firmware compatibility/upload, DHCP or video. Owner confirmed city visibility
after30 (видно, го дальше); tail motion was not explicitly confirmed. No autonomous reboot,
USB/bootstrap write, owner key export or Mac native compile.

NEXT: implement and gate full-channel initial-config CE7 exchange with fresh live
host-interest/table destinations, bounded reads/writes/readback, last config-done
marker, CPU wake and BMI version before firmware. Existing init_preflight/synthetic
inventory does NOT authorize physical writes; must connect real14-map/ring proof,
PCI/D0/wake/IRQ + BME scope + recovery in native adapter. Current30 unload safe.
Keep Mac control/signing/BLE only, builds/sanitizer/COFF/UEFI on Yukabox. Retain city/
cat/world14 and earlier history. No firmware unless exact board/image/license and
safe loading/observability/recovery are verified separately.


## 2026-10-04 — native31 PHYSICAL full-channel CE7 fixed-read PASS

Source contract: experiments/native-wifi-qca9377-v1/FULL-READ-TRIAL.md.
Full warm/channel initialization followed by ONE fixed read4008f8, expected401ee0.
All14 retained mappings reused, CE7 ring callbacks rebound to diagnostic transport,
IRQ quiesced before BME-on. Fresh ACTIVE guard validates PCI/MEM/BME/D0/wake,
ASPM/MSI/MSIX, chip identity, core BAR and device IRQ each poll. Original BME-off
guard preserved. Adapter cancellation/close takes teardown before idle-ring check.
No target RAM writes, BMI query, firmware upload, association/DHCP/video.

Yukabox full gates25 native entrypoint cases including slow-poll completion before
timeout, no reply, TX-only, bad length, wrong word and lost BME; previous warm/cold/
retention cases preserved. Core27channels/36mappedIRQ/13adapter, ASan/UBSan, COFF,
pinned pack, normal+EMPTY UEFI city/ATT/BLE/decoder and current279source/current
world14 two rebuilds passed. Host evidence full-channel-read-host.
Payload9832bcd8d0e43ab9f419686eeb3124643aba03c35db8850522c707d8b9329e35.

Local owner signing AFTER exact gates; saved session pci-native-k6ly_0c1, native31,
80672bytes. Paced100bytes/50ms, staged then COMMIT with correlated exact APPLIED
receipt after reconnect. Current native31/world14, no pending slots. Do NOT replay.
Fresh read-only known Dell QPD16 (UUID0B, prefix716 + SHA-bound extension244)924bytes:
stage5, warmDONE12/error0, CPU2/pipe2, ROM polls4/4; CE7DONE2/error0,
word00401ee0/bytes4, TX+RX complete/mask3, polls1, observed elapsed393000us.
This is HOST observed completion time, not measured device execution latency.
AdapterCLOSED12/channelsCLOSED6, allocated14/cleanup14, all DMA/PCI/IRQ/link/wake
released/restored. Physical evidence full-channel-read-native31. No reboot needed.
Owner city/tail observation after31 asked and pending; do not invent confirmation.

NEXT: expand this exact full-channel read scope to fresh fixed PCIe-state36bytes
at401ee0, early_alloc400900 and option_flag2 at4008cc, after the same warm init.
Validate fresh table destinations/spans/flags; old QPD12/13 values are historical
evidence only. Then separately gate bounded config writes/readback, done marker
LAST, CPU wake and BMI version before firmware. Source-pinned tables/synthetic
inventory alone do not authorize target writes. Preserve city/cat/history, Mac
control/signing/BLE only, Yukabox builds. No autonomous Dell reboot/USB changes.


## 2026-10-04 — native32 PHYSICAL fresh full-channel config reads PASS

Contract CONFIG-READ-TRIAL.md. Retain exact warm14/HI proof, then fixed reads
401ee0/36bytes,400900/4,4008cc/4 through same CE7. No pointer-following/target
writes. Snapshot parsed data before reusing response page. QPD17 reuses legacy
config bytes716..799 alongside full14 HI proof888..923; size924, prefix716 +
SHA-bound244 extension, fresh service UUID0C. File serviceUUID1 preserved.

Yukabox gates30 actual native entrypoint ASan/UBSan cases, three per-location
no-response faults, bad length, BME loss, legacy warm/cold/cleanup retained cases;
core27channels/36mappedIRQ/13adapter, pinned pack, COFF, normal+EMPTY UEFI city/
ATT/BLE/decoder, current285sources/two exact rebuilds/world14 C passed. Initial
fixture found post-HI BME loss must be recorded as CONFIG fault; fixed. Decoder
now also rejects complete-mask7 paired with active config phase. Gate attempts
before these fixes are not physical authorization evidence.
Payload1e72c4ffcc3ff6da53785032ac7f682b1080af83d8d8593ec72b9379fa7d51fc.

Local owner signed AFTER gates, saved session pci-native-zgv75kje/counter32,
81696bytes. Paced transmission resumed same session after disconnect at70200;
COMMIT/reconnect gave exact APPLIED receipt. Current native32/world14, no pending
slots. Do NOT replay. Known Dell read-only QPD17/writes0, stage5/errors0: warm
DONE12/CPU2/pipes2/ROM4+4, HI401ee0 completed, configDONE4/error0/mask7.
State words404d90,404e50,8,0,0,0,0,3,1; early_alloc0; option_flag2 **0** (old
pre-warm QPD13 value20 is historical and cannot authorize fresh writes). Span
preflight +10negative cases passes: pipe404d90/168bytes, services404e50/204bytes.
All14 maps cleaned, adapter/channels closed, PCI/IRQ/link/wake/DMA released.
Evidence full-channel-config-read-host and full-channel-config-read-native32.
Owner city/tail after32 asked and pending, never invent physical observation.

Firmware preparation (NO upload): pinned linux-firmware commit
f9b926a6e1d67e09e54adc329c4e76be5f24a895 material hashes and license/notice checked
on Yukabox; container WLAN.TF.2.1-00021-QCARMSWP-1,751436bytes, SHA
8f8b002fccfe81d42238f27dd1f56d189604f180bd4772c7c8e75ae1fef16f01,
image727125bytes, RAM OTP image24193bytes, no code swap. PCI board CANDIDATE
1028/1810 exact catalog match8124bytes SHA
b2713b77c725b0ff81af75c85c3aeba97885d0f40174f715b1e39d5a9d50f4e7.
Hardware compatibility NOT proved; fresh BMI identity/board variant pending.
Public audit and exact table/flag candidate in firmware-preparation-native32.
No firmware binaries/private key in Git. Candidate not signed/sent.

NEXT: connect source-pinned table writes/readback to full14 live adapter, fresh
fixed reads/spans in SAME warm/BME/IRQ scope. Done marker LAST, CPU wake, bounded
BMI info query, safe all-eight teardown/retention. Then exact BMI/board variant
and signed asset receiver integration before firmware RAM upload/startup.
Existing firmware_port accepts old QPD7 only: do NOT bypass it with fabricated
telemetry; port the policy to fresh native-owned live proof and test separately.
Preserve city14/cat/history. Mac control/signing/BLE, native builds on Yukabox;
no autonomous reboot, USB/bootstrap, permanent OTP/firmware changes. No Wi-Fi
association/DHCP/video yet.


## 2026-10-04 — native33 PHYSICAL config writes/readback + FIRST BMI PASS

Contract SETUP-BMI-TRIAL.md. New finite setup profile repeats the exact full14
warm/HI/config read proof in SAME live scope. Native policy rejects invalid
completed-exchange owners/buffers, table alignment/range/overlap, early-alloc
signature and already-done flag. Writes are never authorized by old JSON.
Source-pinned native table arrays independently checked against init_tables.py
and pinned upstream. Five paired operations: pipe168, services204, config_flags
bit0 clear, early_alloc OR6d8a0009, option_flag2 OR10 LAST. Exact byte readbacks
required; done submission requires all prior write/readback masks15.
Only then core control OR2000 and existing idle CE0/CE1 BMI_GET_TARGET_INFO8.
CPU bit can self-clear, other core bits must match. BMI observes completion
before3second timeout. No firmware write/execute/done command or image in payload.

QPD18 remains924/prefix716 + SHA-bound244 extension, serviceUUID0D/fileUUID1.
Setup280..355 replaces unused legacy CE snapshot region; config716..799 and
HI888..923 preserved. Explicit bounded write/readback/cpu/BMI masks and attempts;
decoder rejects false/out-of-order success. Historical route manifest kind
native-read-only-pci retained for compatibility; THIS profile declares
target_ram_writes=true/firmware_upload=false and gates those independently.

Yukabox65 actual native entrypoint ASan/UBSan cases: previous warm/cold/CE7/config
faults, ten IO timeouts, five bad readbacks, five unsafe span/flag cases, ten
operation cancellations, BMI timeout/bad length/zero version/BME loss and delayed
BMI completion>=3s. Fixed mock setup-cache timing and seed flag0 matching fresh
native32. New phase280=1 is a valid cancellation snapshot, so old legacy-region
negative mutation was replaced with invalid setup phase6, not relaxed decoder.
Core27channels/36mappedIRQ/13adapter/pinned tables/COFF/normal+EMPTY UEFI city/
ATT/BLE/decoder/current292sources/world14/two equal rebuilds passed. Host evidence
config-setup-bmi-host. Payload
70ab49fb8d08690152c698fc93e76de4603ff06a039359dbffe073e7aa285da5.

Local owner signing AFTER exact gates. Saved pci-native-f73i7q5r/native33,
86816bytes, paced100bytes/50ms stage then COMMIT/reconnect exact APPLIED receipt.
Current native33/world14; no pending slots. Do NOT replay. Fresh known Dell
read-only QPD18/writes0: stage5/root+adapter+warm+setup errors0, warmDONE12,
CPU resets2/pipes2/ROM polls4+4, fresh configDONE4/mask7. SetupDONE4/op10,
write mask31/readback mask31/attempts5, CPU before8688/readbacka688.
**FIRST physical BMI reply**: DONE2/error0, version05020001, type8, length12,
12bytes, TX/RX complete, polls1/host-observed elapsed392000us. Fixture type7
is synthetic; physical policy must bind actual type8, never borrow fixture data.
AdapterCLOSED12/channelsCLOSED6,14maps cleaned, all HOST DMA/PCI/IRQ/link/wake
resources restored. Target RAM/CPU state intentionally changed and NOT restored
by this teardown. No reboot needed; owner city/tail after33 asked and pending.
Evidence config-setup-bmi-native33. World14 hashes remain unchanged.

Fresh hardware audit on Yukabox matches05020001 to
QCA9377_HW_1_1_DEV_VERSION/qca9377 hw1.1, PCI dev0042, firmware directory
ath10k/QCA9377/hw1.0, calibration8124bytes. core.c/hw.h exact pinned hashes
checked. Public evidence firmware-preparation-native33. This resolves hardware
version/directory, NOT firmware startup or exact board variant compatibility.
Previous pinned container/license/PCI board candidate in native32 preparation
remain relevant; fresh board-variant selection and live policy integration pending.

NEXT: integrate signed bounded firmware asset receiver with native-owned fresh
setup/BMI proof (actual05020001/type8), exact owner/target/asset generation/hashes,
and cancellation/lifetime policy. Existing firmware_port takes OLD QPD7 only;
do NOT fabricate an old snapshot or trust client-supplied diagnostic JSON.
Keep new live setup owner valid across the receive/load phase or separately
reinitialize and revalidate before each hardware phase; no historical receipt
authorizes future writes alone. Validate exact board variant/calibration before
RAM image load/startup, then WMI/HTT/scan/security/DHCP. Need signed chunks because
751436byte container exceeds immutable262144byte native transfer limit.
Retain prior city/cat/history; Mac control/signing/BLE, native builds Yukabox.
No flash/OTP programming, autonomous Dell reboot, USB/bootstrap change.
Firmware not uploaded; Wi-Fi association/DHCP/video still unverified.


## Continuation: fresh setup proof and relocated firmware receiver (host only)

Current physical baseline is STILL native33/world14, no new signing/session/send.
Firmware has NOT been uploaded or started, Wi-Fi association remains unverified.

Added qca_fwp_start_setup: accepts native-owned completed setup/BMI cache only
AFTER adapter CLOSED and full DMA/PCI/IRQ/link/wake teardown. Requires setup
phase4/op10/masks31/31/attempts5, BMI12bytes/length12/DONE/error0/TX+RX complete,
version/type matching separately reviewed policy. Checks exact adapter/bus/access/
ring/buffer relationships, same SystemTable, zero errors/ownership and all14
buffers released. No freed DMA response dereference. RAM-only staging; cached
proof does NOT authorize future device writes or a later firmware startup.
Legacy qca_fwp_start(QPD7) remains for previous isolated fixtures; do not synthesize
QPD7 from physical QPD18. Policy MUST be trusted native configuration, never a
client packet/report. Physical BMI type8 differs from synthetic fixture type7.

Firmware GATT base is selectable: old11..17 or full-diagnostic-safe13..19 using
QCA_FC_BASE=13; same serviceUUID7/characteristicUUID8/9/A, all lower handles
explicitly delegated. No overlap with existing file1..7/diagnostic8..12.
Yukabox ASan/UBSan tests: six sizes including full751436byte/12chunk container,
both GATT bases/resume/duplicate receipt/corruption/signature rejection;11 pool
allocation/free/pinning/ambiguity scenarios;143 invalid fresh proof states and
successful two-allocation/two-free staging; COFF/UEFI pool ABI gates. Public
reports/logs/source hashes under firmware-setup-receiver-host. These tests are
NOT physical native driver integration or physical Bluetooth firmware transfer.

NEXT: integrate fresh setup gate plus base13 GATT into a dedicated native profile,
with exact installed owner/target and reviewed asset digest/size/type8/version/
generation. Cooperative polling/close must retain uncertain ownership and block
unload while RAM asset is pinned. Check integrated actual entrypoints, normal and
EMPTY UEFI city/Bluetooth gates, two equal rebuilds and current world before
local owner signing. Then stage exact signed chunks and verify physical receipts.
Separately establish board variant/calibration before main runtime firmware load/execution.
Pinned core.c checks SMBIOS BDF extension and BMI board/chip IDs before board
selection; PCI1028/1810 candidate alone is not a fresh exact board-variant proof.
Upstream reads BMI IDs by loading a bounded OTP helper IMAGE into RAM and
executing a GET_EEPROM_BOARD_ID query. This is distinct from programming
permanent OTP; if needed, it requires its own exact RAM helper/query gate.
Native33 historical source-bound evidence belongs to commit2f2ca2c; it does NOT
authorize a new build from these changed sources. Do not replay applied33.
Preserve city/cat/history; no autonomous reboot, flash/OTP programming, USB change.
