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
