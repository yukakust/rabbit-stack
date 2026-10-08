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


## Continuation: integrated signed RAM receiver, physical native34

Native34 was locally owner-signed after current-source gates, sent through the
saved RRT session pci-native-ch3zpq7f and confirmed by an exact APPLIED receipt.
Payload SHA256 4aca12f49f34cac0b679928b7c594c7f2c4c34ab610a2caac0527d50cdb1a856,
92672bytes. World14 is unchanged; no world/native/recovery operation is pending.
Do NOT replay applied34 or reboot Dell during this volatile RAM trial.

receiver_build integrates firmware_port/channel/GATT/chunk signature checking
with the actual native init/poll/stop entrypoints. Trusted embedded policy binds
installed owner/target, generation34, physical BMI type8/version05020001 and the
exact 751436byte firmware-6.bin container digest
8f8b002fccfe81d42238f27dd1f56d189604f180bd4772c7c8e75ae1fef16f01.
ATT handles13..19 preserve existing file1..7/diagnostic8..12. RAM allocation starts
only after completed native setup/BMI and complete host-resource teardown.
Normal adapter close sets cancelled=1 as a close request; this is required by
the fresh proof gate, together with error0 and exact completed setup masks.
A RAM pin blocks unload; cooperative close retains ambiguous allocations.
No firmware image write, execute, BMI_DONE or association command is included.

Yukabox actual-entrypoint sanitizers cover65 cases, including full signed
12chunk staging and pinned-unload refusal. Fresh-proof port tests cover143
invalid states and11 allocation/pinning/lifetime scenarios. Normal and EMPTY
QEMU preserve city/animation/legacy BLE and check new ATT discovery/status plus
absent-target rejection. Two equal native builds and the world14 gate passed.
These are host/QEMU checks, distinct from physical receipts.

Fresh physical QPD18 after34: setupDONE4/op10/masks31/31/attempts5; CPU8688->a688;
BMI DONE2/error0/version05020001/type8/length12/bytes12, TX+RX complete,
1poll/390000us. AdapterCLOSED12/channelsCLOSED6, all14 allocations released;
DMA/PCI/IRQ/link/wake restored. Target configuration RAM changed intentionally.
Visual city/tail confirmation after34 was requested and is still pending.

Immutable owner-signed firmware RAM session firmware-ram-y_iygsqw was prepared
only after this fresh diagnostic and all gates. ALL12 chunks are now confirmed
on physical Dell: bitmap4095/ready1, exact full751436byte container in HOST RAM.
Every chunk is owner-signature/hash/target/policy checked by native34; the final
receipt confirms the complete container hash. No firmware started or Wi-Fi
association. Session status EXACT-FULL-FIRMWARE-CONTAINER-IN-RAM.

Controller corrections: one outer lock with a directly invoked compiled helper,
skip all previously accepted chunks during a partial transfer, re-query only the
last chunk after full completion, and persist each sender attempt before launch.
Windowed writes use at most240bytes/peer budget, status after4096bytes,50ms delay;
only RFCS receipts advance durable confirmed floors. A10ms trial ended in a
connection timeout;50ms also had a timeout, so pause causation is not proven.
Bounded timeout resumes retained the exact signed packets and accepted chunks.
No re-signing or ABORT. Offline controller tests cover partial/full resume and
durable timeout; public actual controller sources and radio logs are archived.

RAM belongs to the current native driver's lifetime. A future unpinned driver
close frees staging allocations; a pin blocks unload. A subsequent chip loader
must deliberately arrange asset ownership or re-stage assets under its own
checked profile; historical RAM readiness alone does not authorize chip writes.
Do not replay applied34 or recreate this completed signed RAM session.

NEXT after exact full-container receipt: separately establish exact board
variant/calibration, then gate the RAM helper/query and chip-image loader.
The container in Dell HOST RAM is not firmware running in Wi-Fi-chip RAM.
Wi-Fi association, DHCP and Yukabox video are still unverified. Preserve city,
cat and history; no autonomous reboot, flash/OTP programming or USB change.

Final verification: current-source full native/QEMU profile rerun and two equal
Yukabox builds passed after the host-only asset_route fix. Native bytes remain
4aca12f4...; no new signing or native installation. Explicit gate_updates retain
the original proof and the refreshed proof. Final repository asset_route deliver
performed ONLY one --query-only of chunk11, exit0, bitmap4095/ready1, no data
or COMMIT writes. Completed RAM session remains firmware-ram-y_iygsqw. Public
summary, physical reports/logs/checkpoints and host/controller proofs are under
evidence/2026-10-04/signed-ram-receiver-native34. No binaries, private material
or RRT wire/session blobs are checked in. World14/native34; all pending slots
null. Wi-Fi remains disconnected; chip-image execution has not been attempted.

## 2026-10-04 native35 board helper: physical outcome UNKNOWN

Base commit e6353ab was native34/world14 with full signed751436byte container
in host RAM. At turn start a query-only of the final chunk confirmed that state.
New bounded board helper profile passed73 actual native entrypoint fixtures,
SMBIOS/core ASan+UBSan/COFF, normal+EMPTY city/ATT QEMU and two equal Yukabox
PE builds/current-world checks. Payload117248bytes SHA
654629798fd72bc5a6e2d9d645e3bd6323d35436d0cbace9bc77e5167e0e8e77; installed-owner signing occurred
locally only after gates. No private key output/export.

Saved native35 session pci-native-0iphq475 received all117536 stream bytes;
300s staging timeout resumed the identical packet from80500. On COMMIT the
radio timed out; reconnect found same session received0 and no exact APPLIED
receipt. Controller status RECOVERY-REQUIRED-RECEIVER-LOSS, native_pending
retained; last confirmed native34 is historical, not current physical authority.
DO NOT replay/resign native35 or advance counters by assumption.

Independent read-only query afterward: stateSTAGING1, received0/117536,
receipt_counter0, same session. Board service20 absent. QPD reader got cached
716byte QPD18 prefix, then ATT invalid-handle on extension: cache is rejected,
not a fresh chip observation. These observations are consistent with volatile
receiver loss/bootstrap, but reboot/fault cause is not established. User scene/
tail observation is pending. Full firmware/helper execution and board identity
were NOT physically confirmed. Wi-Fi still disconnected.

All public host/protocol/failure logs and selection rules:
experiments/native-wifi-qca9377-v1/evidence/2026-10-04/board-helper-native35.
Native helper policy is query-only GET_EEPROM_BOARD_ID0x10, no permanent OTP
write/main start. Candidate PCI board catalog hashb2713b77... is NOT selected;
require completed physical SMBIOS/BMI identity. Old native34 RAM is owned by
that image lifetime; after this uncertain swap do not claim it still exists.

A standalone BLE-recovery city preflight is being prepared on Yukabox under
runs/native35-city-recovery. It preserves semantic world14 and proposes world
counter15/native36, reserving failed35. Recovery execution is gated by
reboot_recovery.py: explicit owner confirmation of an actual Dell reboot and
exact fresh-zero RFS receipt. No autonomous reboot, USB/flash changes or ABORT.
Continue host diagnosis while awaiting the owner scene observation; if recovery
is needed, finish the checked packet before requesting that physical action.

Main load/start remains pending: fresh proven board selection, signed staging
under loader ownership, calibration/main stream, BMI_DONE and valid HTC_READY.
None may be claimed from QEMU tests or historical host-RAM receipts.

Recovery preflight completed: two equal Yukabox builds, current saved world/
roof-cat timing and normal+EMPTY QEMU passed. Signed local recovery plan
text-world/native35-city-recovery-plan is PREPARED-NOT-ACTIVATED: native36 and
world15 are saved, no radio write from recovery, controller native35 pending
remains intact. Public gates/plan reports archived under recovery-preflight;
RRT/session/base64 blobs and private keys excluded. Await actual screen state
before deciding recovery. No owner-confirmed reboot has occurred in this turn.

2026-10-05 owner observation: city NOT visible; owner reports "выключилось"
and now a small empty surface plus text. This supports volatile world loss,
but does not establish a manual reboot or exact fault cause. Recovery plan/
current controller/both saved sessions/source gates revalidated offline;
47616byte standalone city driver disables Wi-Fi probing. Request one owner
reboot to discard stale staging; restore only after confirmation and fresh-zero
read-only receipt. Do not replay35 or activate recovery against current staging.

## 2026-10-05 physical city recovered, native36/world15

Owner explicitly confirmed "перезагрузил". Prepared recovery plan rechecked and
activated only after exact fresh-zero receiver query. Standalone Wi-Fi-disabled
BLE city driver native36 and restored world transport15 both have exact
SHA/session/counter APPLIED receipts. Recovery report APPLIED/engine_done/world_done;
all pending slots null. Semantic world hash remains
fa5a3250633f2bbbd288d947be567c2c5db8e3395033da99b765edf0a0f5cc74.
Native36 payload0fb9fa6c1c307e8ca0fe51b4b29e3cd815c3e2881f9c1ceba6d01d80ce52b4ce,
47616bytes; world15 packagec347d5541494979eab0467933d0953102d0ad94b07f309b85c13488e21dea0f7.
The native36 COMMIT disconnected normally; reconnect obtained exact APPLIED.
Saved native35 remains preserved/retired, never replayed; owner private key
never printed/exported. Physical city/tail confirmation requested, pending.
Evidence: experiments/native-wifi-qca9377-v1/evidence/2026-10-05/native35-city-recovered36.
Wi-Fi remains unconnected; no physical board/helper/main execution proof.
Do not reuse native34 staging after reboot. Diagnose/isolate native35 failure
before another probe; current recovery driver deliberately has no Wi-Fi probe.

2026-10-05 owner replied "да все видно" to city/tail confirmation. City recovery
is now physically visible as well as protocol-confirmed. Code audit found
native34 receiver qca_stop calls cooperative qca_fwp_close once; that frees
workspace only, retains memory and returns1. Resident runtime_update invokes
active.close once and treats that as fatal, before candidate.attach. New
regression reproduces this exact unpinned full-container close boundary; no
new hardware write while diagnosing. Main helper execution remains unconfirmed.

Receiver single-call close regression fixed and host-gated: actual full signed
container baseline fails at one unpinned qca_stop; fixed wrapper performs at
most2 release steps.65 scenarios+normal/EMPTY QEMU pass. Pinned/fault retention
remains. Evidence:2026-10-05/receiver-single-close-fix. Current native36 has
no receiver buffers. Fresh board-query native37 gates are being regenerated
against saved world15 before signing/radio. No physical probe from fix checks;
never deploy generation34 fixture artifact or replay failed native35.

## 2026-10-05 native37 physical board helper query PASSED

Fresh gates bind current world15/new source closure. Native37 session
pci-native-wqsvjyjg, payload654629798fd72bc5a6e2d9d645e3bd6323d35436d0cbace9bc77e5167e0e8e77
117248bytes; EXACT APPLIED after normal COMMIT disconnect/reconnect. First
staging timed out300s; same saved packet resumed from80500 and completed.
Old35 was never replayed. Native36 has no receiver buffers, so its single-close
completed; this differs from the reproduced native34 receiver close ABI bug.

Read-only QBDI observations progress12commands/2728bytes ->83/20336 ->
phase5/error0/submitted101/padded24196/polls101/result00000000. Exact helper
loaded to chip RAM and executed GET_EEPROM_BOARD_ID0x10 successfully.
SMBIOS state2/error0, no BDF suffix; BMI version05020001/type8. Final adapter
CLOSED12/cleanup14/users0/rootstage5/error0. Fresh complete QPD18 independently
confirms exact PCI168c:0042/subsystem1028:1810/revision31, masks31/31/5writes,
all14 DMA released, host IRQ/PCI/link/wake restored. Native37/world15, pending
null. Owner city/tail confirmation after37 requested and still pending.

Zero board ID is unusable BMI identity; pinned upstream selection uses exact
PCI name without variant. Unique group0 board-2 record SELECTED:
bus=pci,vendor=168c,device=0042,subsystem-vendor=1028,subsystem-device=1810
8124bytes SHAb2713b77c725b0ff81af75c85c3aeba97885d0f40174f715b1e39d5a9d50f4e7.
Selection manifest binds physical raw QPD/QBDI hashes, source commits, complete
cleanup, full catalog hash and exact record. This is board selection proof,
NOT calibration/main image startup. Evidence:2026-10-05/board-helper-native37.

NEXT: owner visual confirmation, then implement/gate a complete loader with
its own signed-RAM asset ownership, exact chosen board/calibration/main LZ,
BMI_DONE and valid HTC_READY. Native37 owns no reusable main-image staging;
old native34 RAM is gone after reboot. Do not use former RAM receipt as current
load authority. Main firmware not started, Wi-Fi not associated. No USB or OTP
programming changes. Future receiver profiles must include the one-call close
fix, fresh policy generation and full current-source/world gate.

## Continuation: exact boot core and HTC_READY (2026-10-05; host only)

Owner subsequently reported the city visible (`виден`). This confirms visibility;
do not turn it into a separate new tail-motion observation. Current native37 /
world15 remains installed. A fresh known-peer read-only QBDI observation during
boot-core work again returned phase5/error0,101commands,24196padded helper bytes,
result0,valid SMBIOS/no variant, BMI05020001/type8, rootstage5/error0,
adapterCLOSED12/cleanup14/DMAusers0. No BLE characteristic write or new native
delivery occurred, no main-image asset exists on Dell, Wi-Fi not connected.

Implemented `boot_image`, `boot_transport`, `boot_native` and a Yukabox-only
`verify_boot_core.py`, with pinned Linux/firmware/crypto references. The planner
admits only the selected 8124-byte Dell board data,24193-byte helper and727125-
byte main image by exact SHA256. It configures host-interest, writes board data,
reads back every byte before the initialized flag, reloads/executes calibration
(parameter0, require result0), streams the exact main image and BMI_DONE. The
native coordinator validates fresh setup/query bindings, rehashes/pins the full
751436-byte receiver asset, checks TLVs, uses bounded DMA transport and waits for
a strict endpoint0 HTC_READY message. Board writes additionally reject overlap
with fresh pipe/service configuration and host-interest spans. Unpin is denied until actual adapter DMA
ownership is fully released, including on errors. No SOC/NVRAM/flash-section or
permanent programming command is admitted.

42 host sanitizer scenarios and COFF builds of all3 modules pass. Main/coordinator
device replies are explicit MOCKS, not UEFI/physical proof. The real pinned
container caught an over-strict assumption about zero alignment padding; only
the NUL-terminated magic is compared and alignment is skipped, while the full
container hash remains fixed. Code is not integrated into a native PE builder or
admitted by a signing gate. Evidence:2026-10-05/boot-core-host.

NEXT: integrate the loader with a new generation-bound receiver, fresh second
hardware setup and independent status observation. Validate actual entrypoints,
complete signed-asset fixtures, both hardware/RAM lifetimes, one-call resident
close, timeout/cancellation and normal/EMPTY-city QEMU before signing. Audit
target clock/UART configuration and BMI-to-HTC ring transition against pinned
Linux. The board-address window0x400a00..0x410000 is deliberately conservative;
unexpected actual pointers must be diagnosed and reviewed BEFORE permitting a
write. Never reuse old generation34 or retired native35 sessions.

Then physical board/calibration/main/HTC trial. WMI/HTT, scan, authentication,
DHCP/IP and actual Dell-to-Yukabox traffic remain separate unimplemented stages.
An asynchronous question asks owner for SSID and WPA2/WPA3; no password requested
in chat, no credentials persisted. Local private credential entry is still to
be implemented. Do not imply SSID alone or main-image startup completes Wi-Fi.

## 2026-10-05 — exact generation38 boot receiver integration; delivery in progress

Owner explicitly requested main firmware integration, physical Dell startup,
SSID scan/protected association, IP and Yukabox exchange. SSID screenshot reads
`SILK_56E35E_Plus`. Password was entered through a native Mac hidden dialog and
saved in `/Users/yukakust/.rabbit-owner/wifi-connection.json`0600, owner directory
0700, outside repository. Do not print/read the secret into tool output or send
it to Yukabox. No encrypted credential channel exists yet; do not send a raw
passphrase over the current unencrypted GATT.

Added boot builder, generation38 exact receiver policy, UUID22/23 read-only
QWBT status, observer/strict decoder, actual two-lifetime fixture, physical asset
route and separate boot signing gates.65 first-lifetime cases,8 two-lifetime
cases,42 core cases, COFF, both QEMU cities and341-source/current-world/two-rebuild
checks pass on Yukabox.96 malformed QWBT bounds/success cases are rejected.
Cancellation exposed the need to unpin after actual hardware release before RAM
close; this path now passes during both calibration and main streaming. All
firmware/DMA/HTC replies in these tests are MOCKS, not physical success.

UART disable is now an explicit finite write before BMI_DONE. Pinned Linux PLL
return is ignored by core_start; this candidate intentionally admits no SOC PLL
commands and tests the reference-clock path. Do not claim PLL configured. Board
pointer policy remains deliberately narrow and rejects any fresh overlap with
pipe/service configuration or host interest before board write.

Candidate PE139264bytes SHA
`8ececc0196f1cbc22430d0327b8c5974898284c3d6aa4827534c8ac678debf86`.
Local gate check also rejected a wrong native generation before any private-key
read; the correct context reached the signing boundary with a test sentinel.
A fresh known-peer read before delivery confirmed native37 board query/teardown
phase5/error0/101commands/24196bytes/SMBIOS2/no variant/type8/05020001,
adapterCLOSED12/cleanup14/DMAusers0. No new user city observation in this turn.

The exact locally signed native38 session is
`runs/text-world/pci-native-nwwhys2x` under connected supervisor. It is currently
STAGING, not yet an applied receipt. Continue `native_route.py deliver` with the
same state/session/packet, never create another generation/nonce. Do not retire
native37 or claim38 installed until exact correlated APPLIED. State world15
and semantic city hash remain unchanged. Owner key stayed on Mac; no USB,
bootstrap, permanent programming or autonomous Dell reboot occurred.

NEXT: finish native38; fresh read-only QPD18 must show complete first setup and
teardown, QWBT boot_round0. Prepare/deliver exact generation38 firmware asset
with `boot_asset_route.py`; preserve one controller lock and immutable packets
across retries. Final accepted chunk starts the second fresh hardware lifetime.
Read QWBT to prove actual calibration/main/HTC_READY and teardown or the precise
bounded failure. Existing native34 RAM and retired native35 packets are invalid.
After physical evidence, implement live HTC/WMI/HTT, scan, protected credentials/
authentication, DHCP/IP, and actual Dell-Yukabox exchange. Wi-Fi is NOT connected
and main firmware is NOT yet running at this checkpoint. Evidence host gates:
`experiments/native-wifi-qca9377-v1/evidence/2026-10-05/boot-native38-host/`.

## Native38 applied; full firmware asset transfer started (2026-10-05)

Exact session `pci-native-nwwhys2x` reached all139552 transport bytes. The first
paced stage hit its normal300s limit; the next read confirmed retained79200bytes
and resumed the same session. COMMIT lost the Bluetooth connection, then the
sender reconnected and obtained the exact SHA/session/counter38 APPLIED receipt.
Controller state now native38 SHA
`8ececc0196f1cbc22430d0327b8c5974898284c3d6aa4827534c8ac678debf86`,
world15/semanticfa5a3250 unchanged. Physical QPD18 freshly confirms stage5/error0,
setup4/error0, BMI05020001/type8, adapter12/cleanup14/DMAusers0. QWBT observer
first saw RAMphase2, then freshly confirmed RAMphase4/error0, empty asset,
boot_round0, no loader pin or main/HTC_READY. This physically verifies the new
receiver/first hardware lifetime, not the main image. Evidence:
`evidence/2026-10-05/boot-receiver-native38/`.

User was asked asynchronously whether city/rooftop tail remain visible/moving.
No answer at this checkpoint; do not turn host gates/receipt into physical pixels.

Exact generation38 asset packets were signed locally after the new profile,
current native receipt and fresh completed QPD18 checks. The saved session is
`runs/text-world/firmware-ram-xn9ncwla`. State `hardware_trial_pending` binds it;
currently data transfer is active, complete0/12 at checkpoint. Continue the SAME
`boot_asset_route.py deliver --state .../state.json --session .../firmware-ram-xn9ncwla`;
query and resume immutable packets/checkpoints after any bounded timeout. Do not
regenerate signatures, increment generation, change world/source inputs or
attempt another native engine while this trial is pending. No firmware startup,
Wi-Fi scan/association, IP or Yukabox traffic has been confirmed. Password remains
only in the owner-only local file; never print or send it on current GATT.


## 2026-10-05 — operating-protocol preparation while exact asset uploads

Native38 `pci-native-nwwhys2x` remains installed. Same signed asset session
`firmware-ram-xn9ncwla` is still active: seven full RAM chunks accepted at this
checkpoint (bitmap127), partial next chunk may progress after this text.
The bounded local resumer retains the exact existing signatures/session and
only continues after correlated known-peer receipts. Do not prepare another
asset, close/replace the native module, or change the frozen native38 inputs
while `hardware_trial_pending` remains. All341 recorded inputs were rehashed
unchanged during protocol preparation. Native38 still has no verified main
firmware startup, association, IP or Yukabox exchange at this checkpoint.

Independent future source under `experiments/native-wifi-qca9377-session-v1`
was prepared/checked on Yukabox and pushed in `7f11c25`, `cc46656`, `99774d6`:

- bounded HTC PCI wire codec with validated trailers and pinned-struct wire
  differential (11331 assertion groups), freestanding COFF;
- READY → WMI/HTT connect → PCI setup handshake with matching service/unique
  endpoint/confirmed-transmit sequence tests (16 groups);
- passive VDEV0 WMI-TLV scan constructor, request-correlated event parser and
  malformed/truncated/duplicate rejection tests (8234 groups);
- read-only initial WMI service ABI/regulatory band/memory request/READY MAC
  information parser and bounded malformed-event checks (47340 groups).

ASAN/UBSAN and COFF proofs are HOST ONLY, archived under the new experiment's
`evidence/2026-10-05/wire-codecs`. No new native was signed or transmitted.
Actual CE2/CE3 handling, operating credit ledger, WMI memory/init/VDEV/regulatory
configuration, physical scanning and beacon/security parsing, confidential
credential delivery, authentication and IP remain to implement. Described band
limits are NOT regulatory approval. This does not alter the previous world,
bootstrap or USB. Do not claim current physical city/tail pixels until the owner
answers the pending observation question after native38.

Yukabox read-only network inventory shows a private router IPv4 address and a
Tailscale overlay address, with no global IPv6 on its Wi-Fi interface in that
snapshot. A normal Dell router lease alone does not prove reachability to
Yukabox in Poland; preserve that distinction when planning a WAN transport.
Credentials remain on Mac only, outside Git/Yukabox. Do not read/print them or
send the raw password/derived equivalent credential over unauthenticated GATT.


## 2026-10-05 — native38 exact asset complete; calibration result3 stop

All12 existing owner-signed packets in `firmware-ram-xn9ncwla` have correlated
known-peer QFS_DONE receipts; final bitmap4095/ready1. Full751436-byte official
container staged and rehashed. The actual second hardware lifetime completed
fresh setup/BMI/helper query, wrote/read back all8124 board bytes at0x401fc0,
loaded the helper again and executed parameter0. Its result was3. Native38's
zero-only planner stopped at178 submitted/completed commands: QWBTphase6,
error0x206,planphase21/planerror6. Main image was NOT uploaded/executed;
HTC_READY, Wi-Fi scan, association, IP and Yukabox traffic remain unverified.

Cleanup physically completed: rootstage6,adapterCLOSED12,cleanup14,DMAusers0,
assetpin0. `read_boot.py` verified the current native binding and cleared
`hardware_trial_pending`. Native remains38/worldtransport15. Full staged asset
is still owned by that module; a replacement closes/frees its RAM, so do not
replay generation38 asset packets as if they were generation39 packets.

Physical receipts/packet hashes/raw QWBT observations are archived in
`experiments/native-wifi-qca9377-v1/evidence/2026-10-05/main-native38-physical`.
Summary explicitly says main/HTC trialfalse, associationfalse, IPfalse. No
secret/binary/credential was copied. Owner city/tail observation after this
trial is requested and pending; do not claim physical visibility from mocks.

Reference audit found a concrete missing compatibility rule in our planner:
exact container features_hex=c0 advertises bit7 IGNORE_OTP_RESULT. Pinned
Linux `core.h` defines it as7 (SHA
`da6f9d89225467310770e9ebf67ccdd66ad381c203a50e38afadc03c85da16b2`);
`core.c` does not fail nonzero helper result when that firmware flag is set.
The new narrower profile should admit only0 and observed3 for this exact
pinned bundle, preserve raw result3, reject other unreviewed values, and still
require actual main/BMI_DONE/HTC_READY/complete physical cleanup. This is NOT a
claim that helper result3 itself proves calibration or Wi-Fi connectivity.
Source may now change because the previous physical owners are proven closed;
all new source/current-world/lifetime/COFF/QEMU/reproduction gates must rerun
before signing any new native counter. Preserve old native38 evidence intact.


## 2026-10-05 — result3 compatibility candidate39 host gates complete

Zero-only result handling fixed for the exact hash-pinned C0-feature bundle:
only0 and observed3 admitted, raw result retained. Unknown1/2/4/ffffffff remain
rejected; no global skip knob or alternate images added. Receiver policy now
binds next native generation39. Planner/native core47 ASAN/UBSAN/COFF scenarios
include full main→HTC/pin release with injected3. Actual two-lifetime8 cases,
first-lifetime65 entrypoint cases, normal/EMPTY actual city/GATT QEMU and98
malformed QWBT rejections pass on Yukabox. These are HOST/MOCK proofs only.

Two identical current-source/current-world rebuilds: PE SHA
`663b6833e7dc216eba2274dfec15dfa848e132da25a6ff678445d7ac89db3c06`;
world package SHA `c347d5541494979eab0467933d0953102d0ad94b07f309b85c13488e21dea0f7`;
341 public inputs bound,9 changed versus native38. Reproduction SHA
`1768dea8324a488e9550b0a99f730c01174ddc1bc384b4bc3fe7829d331f368c`;
report SHA `9d5f35c1e86bd59134963e3e7ed68015f5ee0aea8a24580ff342b44d94788836`.
Mac gates() revalidated checked bytes before any owner signing. Public proofs
archived under `evidence/2026-10-05/boot-native39-host`. Candidate not physically
applied at this checkpoint; main/HTC/Wi-Fi remain unverified. City/tail owner
question after the physical result3 stop is pending. Never replace that pending
observation with QEMU screenshots or advance claimed connectivity from mocks.

## 2026-10-05 — native39 BEGIN rejected; closed-trial write gate corrected

Fresh physical QWBT again confirmed native38's faulted trial had released all
hardware/DMA owners and the firmware pin. Locally signed candidate39 saved as
`pci-native-f_6ar4mr`, but its BEGIN failed with ATT write-not-permitted.
Both surrounding exact peer queries still reported the completed native38
receipt; native39 confirmed prefix is0 and no application was reported. Evidence:
`experiments/native-wifi-qca9377-v1/evidence/2026-10-05/native39-write-block`.
The generic sender labels this recovery-required receiver loss; the actual
observed cause is installed native38's unconditional boot_round write rejection,
which incorrectly also covers legacy resident update handles after cleanup.

Do NOT replay that pending candidate against bootstrap after reboot. Its exact
signed bytes remain preserved. An owner reboot has been requested, not yet
confirmed at this checkpoint; no reboot/USB operation was performed by the agent.
Use separately gated `reboot_recovery` with the pending39 predecessor to reserve
recovery40, restore the exact saved actor city as worldtransport16, then use a
fresh result3-compatible Wi-Fi candidate41. Policy generation is now41.

Generated native write guard now keeps RAM asset handles13..19 sealed and blocks
legacy writes while any actual adapter/PCI/DMA owner or firmware pin remains.
Once cleanup is complete, legacy handles1..12 are delegated to the resident
again. The actual two-lifetime eight host scenarios verify active write blocking,
both write opcodes delegated after successful/faulted/cancelled cleanup, retained
asset sealing and one-call final close. Sanitized host tests pass on Yukabox;
this fix is NOT installed physically. Fresh recovery preflight also passed two
native builds, actor-world C checks and normal/EMPTY QEMU. Full candidate41 gates
and physical recovery/application remain separate next steps.

Recovery40 is now locally signed and saved as
`runs/text-world/native40-city-recovery-plan`, PREPARED-NOT-ACTIVATED.
Its checked directory is `native-wifi-qca9377-v1/runs/native40-recovery-preflight`;
payload SHA `0fb9fa6c1c307e8ca0fe51b4b29e3cd815c3e2881f9c1ceba6d01d80ce52b4ce`.
No recovery radio writes occurred. Require the owner's reboot report and a fresh
exact empty receiver read before `reboot_recovery.py restore --dell-rebooted`.
Preparation does not mutate the live controller; it still retains pending39.
Do not change gated source while this saved recovery is awaiting activation.

Candidate41 full host gates and two-rebuild/current-world reproduction also
finished. Mac gates() independently revalidated341 current public inputs against
the exact planned restored worldtransport16 package SHA
`8254c70465eac5a04612e2e33f74be5afa078c2e71b9f00b5d5e13a8f02f0f5e`.
Candidate PE139264 bytes SHA
`e24248302a81e5def809d2379722e2389ec4c4c47458c9bf3b027cc5fc2d38d1`;
report SHA `562b2f1f78cb61045566d94e22fe2c8bcb7d8256d46d963403874e61ab34d8a4`;
reproduction SHA `dd5ad5d4f08e1075f3444b69b3ec441a626986301974e02b2fa0df8473ac3572`.
Checked folder `native-wifi-qca9377-v1/runs/boot-profile-native41`.
Host evidence is `evidence/2026-10-05/boot-native41-host`; recovery evidence is
`evidence/2026-10-05/native40-recovery-host`. These are not physical Wi-Fi proofs.
Do not sign candidate41 until exact recovery40 and restored-world16 receipts
have promoted controller state. Then fresh QPD18/QWBT must admit a new locally
signed generation41 full-asset session; retired38 packets cannot be reused.
Main/HTC startup, scan, protected association, IP and Dell→Yukabox exchange are
all still physically unverified. Owner reboot and scene observation are pending.

## 2026-10-05 — owner reboot; city40/16 restored; candidate41 radio staging

Owner explicitly reported reboot. `native40-city-recovery-plan` was activated
only after a fresh known-peer exact EMPTY RFS read. Both recovery native40 and
worldtransport16 have correlated SHA/session/counter APPLIED receipts; controller
promotion completed and recovery_pending cleared. Old candidate39 was preserved
and retired, not replayed against bootstrap. Physical receipt evidence:
`evidence/2026-10-05/native40-recovery-physical`. Actual screen/tail observation
was requested and remains pending; do not infer visible pixels from receipts.

Mac gates rechecked the restored world and locally signed native41 once as
`runs/text-world/pci-native-tsp9rho2`. Bluetooth suffered repeated CBErrorDomain6
timeouts/reconnect-limit stops with discovery RSSI as low as-95. Two bounded
deliver invocations retained the same packet. A final independent read-only
query confirmed EXACT same-session staging114500/139552 bytes, error0, state1.
The last applied world receipt counter16 in RFS is not native41 application.
Controller remains native40/world16; native_pending is that exact41 directory.
Report status `STAGING-RETAINED-AWAITING-PHYSICAL-RADIO-POSITION`; no ABORT,
new nonce, re-sign or bootstrap/USB write occurred. New41 firmware asset packets
have NOT been prepared/sent. Evidence: `evidence/2026-10-05/native41-radio-staging`.

Owner was asked to put Mac within one metre of Dell and report it; no response
at this checkpoint. Do not assume the radio position changed. Keep Dell powered,
do not reboot again, and preserve all exact staging/checkpoints. After the owner
reports proximity, run `native_route.py deliver` against the existing pending
session, never prepare another native packet. After exact41 APPLIED receipt,
read fresh QPD18/QWBT, admit locally signed generation41 asset session, deliver
it, then observe actual calibration/main/HTC cleanup. Candidate41 full host gate
and future-world binding remain intact. Wi-Fi association/IP/Yukabox are false.

## 2026-10-05 — native41 applied; firmware partial; bounded radio experiments

Owner says Mac already stands nearby and internet interrupted. Do not keep
assuming distance or claim internet loss caused BLE timeouts. The local Cocoa
sender uses direct GATT; the observed failures were Bluetooth disconnects.
Same `pci-native-tsp9rho2` resumed114500/139552, completed and received exact
APPLIED SHA/session/counter41. Controller is native41/worldtransport16,
native_pending clear. Fresh physical QPD18: stage5/error0/setup4/op10/masks31;
BMI type8/version05020001, adapterCLOSED12, cleanup14/DMAusers0. Initial QWBT:
boot_round0,ram_phase4,bitmap0. Evidence: `evidence/2026-10-05/native41-applied-initial`.
Visual city/tail observation is still pending; receipts are not screenshots.

After these gates, the owner key locally signed twelve immutable generation41
asset packets ONCE as `runs/text-world/firmware-ram-ytrkhw7x`. Standard paced
controller delivered three fully accepted packets (bitmap7), plus a confirmed
partial fourth. Total confirmed firmware-data floor225856/751436; packet4's
last confirmed received29472/65760 includes224-byte envelope. Twenty bounded
iterations ended after two no-progress observations. Do not re-sign, ABORT,
reboot or replay older-generation assets. `hardware_trial_pending` retains that
exact directory; default resume is `boot_asset_route.py deliver --session ...`.
All frozen native/source/world/gate bindings remain unchanged.

Two isolated Mac-only control-helper derivatives were tested using the same
immutable packets and checkpoint, same50ms pacing,512-byte receipt window.
Only DATA limit changed to16 or48. Offline preflight starts no manager; owner
signatures/current native/source/target/world checks ran before physical use.
The standard supervisor was paused while its child completed naturally, then
resumed after experiments; no concurrent radio managers or driver changes.
Frame16 ran240s to its own bounded timeout, confirming18480→28208 without
disconnect in that ONE interval. Frame48 confirmed28704→29232 and disconnected
after~13s. This is not proof of a fragmentation cause or sustainable throughput.
Public actual helper/controller sources and receipts are archived in
`evidence/2026-10-05/native41-ram-staging-radio`. No key, credential or binary.

Final fresh known-peer QWBT confirms boot_round0,phase0,plan0,board0,
asset_bitmap7,ready0,pin0,boot_attempted0; adapter12/cleanup14/DMAusers0.
No calibration/main/HTC attempt was triggered; Wi-Fi/IP/Yukabox remain false.
The partial RAM session is retained, and no sender remains running/stopped.
Mac read-only CoreWLAN still reports channel8/band1 (2.4GHz), security3, with
SSID hidden by privacy: do not identify this as the requested router network.
Owner asked whether "5GHz Wi-Fi" means cellular5G; explained they differ.
Available Mac5GHz network name/band is still unknown. Apple interference
reference: https://support.apple.com/en-us/102319 ; a common interference cause
is possible, not proven. Keep the physical evidence separate from this hypothesis.

Independent `native-wifi-qca9377-session-v1/beacon_info` now parses bounded
ordinary beacons/probe responses, exact SSID/BSSID, DS/HT channel, privacy and
opaque RSN. It cannot authenticate an AP, validate security or associate.
Pinned Linux ieee80211.h hash
`572535ac04d9dda668501b0233746d0e5c143195d85c02ed3be2532a37c0e8d7` supplies an
independent layout/constant oracle.9117 ASAN/UBSAN groups and native COFF pass
on Yukabox; proof is `session-v1/evidence/2026-10-05/beacon-info`. No integration
into the frozen native41 image and no physical scan. Credential stays on Mac.


## 2026-10-05 — no 5GHz network; radio isolation and HCI framing proof

Owner reports no available 5GHz Wi-Fi. It is not a requirement. A bounded45s
Mac Wi-Fi-off trial verified Off, attempted the SAME native41 firmware packet,
then verified On again; an independent restore watchdog was reaped afterward.
The query confirmed packet4 received31024/65760; sending disconnected with no
further confirmed progress. Turning off Mac Wi-Fi did not eliminate the observed
Bluetooth failure. This does not exclude other RF causes or prove a software
cause. Internet availability is not the direct GATT sender's dependency.

The cached16 helper avoids repeatedly fsyncing an unchanged attempted checkpoint,
while retaining save-before-first-write and durable validated receipt floors.
Offline Cocoa mock tests cover actual16-byte writes, receipt persistence and
save-failure blocking. Physical ordinary and Wi-Fi-off attempts still failed;
no reliability or throughput improvement is claimed. Public actual helper/test/
wrapper sources and observations: session-v1/evidence/2026-10-05/mac-radio-followup.
No key, credential or generated binary is archived.

Independent bt_event_stream prototype passes33926 ASAN/UBSAN mock cases and
freestanding COFF on Yukabox, using the actual derived BLE link. It reproduces
old rl_event loss of a21-byte connection event split16+5 and two7-byte credit
events coalesced into14 bytes; the assembler delivers both correctly. Every
payload length0..255, split position and mixed block size1..260 is exercised.
Public proof hashes were checked against local sources:
session-v1/evidence/2026-10-05/bt-events. Reference:
https://raw.githubusercontent.com/torvalds/linux/6b5a2b7d9bc156e505f09e698d85d6a1547c1206/drivers/bluetooth/btusb.c
The prototype accepts only successful USB read bytes. It is NOT integrated into
usb_port poll or shutdown, NOT installed on Dell, and NOT proof of physical
failure causality. Shutdown integration must preserve connection-race capture,
exact disconnection completion and unknown-outcome unload refusal.

Native41/world16 and frozen source closure remain unchanged. Pending exact
firmware-ram-ytrkhw7x is retained: three accepted packets, bitmap7, partial fourth.
Last confirmed body floor227408/751436. No firmware boot, scan, association, IP
or Dell-to-Yukabox exchange occurred. No sender or radio-off watchdog is running.
Next: isolated USB poll/close integration tests, then deliberately gated native
replacement if needed. Do not mutate frozen41 inputs or silently clear its
pending session; replacement would discard partial RAM staging and requires a
fresh generation-bound asset session with originals preserved.


## 2026-10-05 — native42 USB framing applied; fresh signed asset session

Native42 incorporates bt_event_stream into actual USB poll AND close, with one
shared stream across their handover. Successful reads only; complete events are
checked even after the awaited completion, and a trailing partial prevents
unload.618 ASAN/UBSAN poll/close/race/timeout cases plus18 original USB tests and
COFF pass on Yukabox. Historical unknown-disconnect recovery is retained in the
link verifier; framing does NOT reconstruct an orphan tail whose header was
lost. The previous QEMU orphan-injection fixture exposed this limitation. The
native42 fixture instead verifies a genuine connection split16+5 and matched
disconnection through actual UEFI replacement. No arbitrary resynchronization
or physical root-cause claim. Both normal/EMPTY city QEMU gates pass, alongside
65 initial-lifetime fixtures,8 two-lifetime cases,47 boot-core cases and98 boot
telemetry rejections. Host proof includes388 original/new dependencies plus the
checked resume script (389 total); missing isolated crypto/media imports were
restored and included before final reproduction. Two builds and current-world
C sanitizer check match payload
`0460c259f65abb7ffa02cc430b05bae30f89cb36db9a976bb309f83cb6bb2201`.
Report SHA `cc043f79b5a974a591d9b4aaae2e6732032a370079f005fb2ecdf47063c983c5`;
reproduction SHA `ee0cfdc640ee0c6d1b364d52d6dc6ecb56f99e527ed68d6dde921fd0e1d76168`.
Public evidence: native-wifi-qca9377-v1/evidence/2026-10-05/boot-native42-host.

Before changing any frozen41 source, fresh physical QWBT verified boot_round0,
ready0,pin0,boot_attempted0,bitmap7,adapter12/cleanup14/DMA0. The separately
checked next candidate and389 proposed source hashes passed offline route gates.
`retire_partial_boot.py` preflight then deliberately retired only the partial
host-RAM session in the controller; no ABORT/device write/reboot. ALL341 frozen
old source inputs and all original signed packets/checkpoints are preserved in
firmware-ram-ytrkhw7x/frozen-source-before-replacement and retirement.json.
Old packet41 assets MUST NOT resume/replay. Retirement proof is archived in
native41-partial-retired. Device RAM staging was discarded on actual old-driver
close during the subsequently verified replacement.

Mac locally signed one native42 packet `pci-native-weu86l9x`. First paced100-byte
attempt reached its300s deadline; fresh exact matching query confirmed79900.
Same signed packet resumed to140064; commit caused expected disconnect, and
reconnect obtained exact SHA/session/counter42 APPLIED. Controller is42/world16;
native_pending clear. This is an applied receipt, not device attestation or
proof all Bluetooth disconnect causes are fixed. New42 QPD18: stage5/error0,
setup4/error0,BMI type8/version05020001,adapter12/cleanup14/DMA0. New42 QWBT:
boot_round0,ram_phase4,bitmap0,ready0,pin0,boot_attempted0. Physical proof is
native42-applied-initial. Owner was asked whether city/tail remain visible;
visual observation is still pending and must not be inferred from receipts.

After fresh exact gates, Mac locally signed all twelve immutable generation42
firmware packets once: `runs/text-world/firmware-ram-pwg6_pnz`. This is now the
exact hardware_trial_pending; retain it across retries. Standard
boot_asset_route.py deliver was started against that saved session. At this
checkpoint first packet is partially staging; no accepted chunk/main startup,
scan, association, IP or Yukabox exchange has been confirmed. Do not mutate
389 frozen inputs, create a new nonce/counter, replay retired41 packets, reboot
Dell or touch bootstrap/USB. Read actual current report/receipts before resume;
full bitmap4095 only proves RAM staging. After final packet auto-triggers the
bounded boot lifetime, read fresh QWBT and keep hardware pending until actual
all-owner cleanup. Native operating/WMI/security/IP/WAN integration remains
separate, described in session-v1/NATIVE-INTEGRATION.md.


Independent native-wifi-qca9377-memory-v1 now provides a PURE host-memory size
plan, outside frozen42 inputs.4,605,536 ASAN/UBSAN differential/budget/overflow/
duplicate cases plus COFF pass on Yukabox against exact Linux wmi.c
SHA68a4fedc3d0cd815c209dda9c0eb3aa3869bd3d35847c633e0c458ba53c320f4
and wmi.h SHAfff0e5749d68c461ed08e69060321942d68bdb050954c39b2a57c0045457106c.
No actual allocation, mapping, physical-address validation or WMI INIT occurs;
no native integration/physical Wi-Fi proof. Fixed future station resources and
retained-mapping lifetime checks are still required. Reference:
https://kernel.googlesource.com/pub/scm/linux/kernel/git/torvalds/linux/+/6b5a2b7d9bc156e505f09e698d85d6a1547c1206/drivers/net/wireless/ath/ath10k/wmi.c
Generation42 exact session resume is bounded24 attempts, stops after two attempts
without confirmed progress, and has one sole radio owner. Mac idle-sleep guard
follows controller36915 and automatically releases on exit. At this additional
checkpoint two chunks are accepted (bitmap3) and the third is partially staged;
confirmed body floor178368/751436. These figures are historical checkpoints;
read current report before continuing. Owner visual answer still pending.


### 2026-10-05: physical native42 firmware startup complete; operating prerequisites

This supersedes the historical partial asset counts above. After Mac restart,
fresh QWBT retained bitmap255 and unstarted/released ownership, permitting the
same immutable signed42 session to resume. All12 packets completed, bitmap4095.
Actual Dell main transfer progressed through plan17 to plan20. Fresh QWBT:
phase5/error0, submitted=completed3114, calibration_result3 (exact admitted
feature policy), ready_bytes20, credits2,credit_size1792,max_endpoints4.
A following read verified native_stage5/error0,adapter12,cleanup14,DMAusers0,
asset_pinned0,boot_round1 and physical_trial_complete true. hardware_trial_pending
is clear. Public raw/decoded/log/checksum proof is in
native-wifi-qca9377-v1/evidence/2026-10-05/native42-firmware-ready.
This is a CLOSED diagnostic; no active radio connection, scan, DHCP or WAN.
No Dell reboot/bootstrap/USB/OTP/flash change. City/tail visual remains pending.

New pure session-v1 `htc_credit` and `htc_control` prerequisites pass on Yukabox:
100,487,721 pinned-cost/credit ownership checks and1,418 endpoint/early-response
ordering checks under ASAN/UBSAN, plus native COFF. Credit cost includes HTC
header, ticketed reservation is cancellable only before publication, committed
credits return only through bounded firmware reports. Caller must consume each
actual RX completion once; ledger cannot independently detect report replays.
The control coordinator validates/copies one early endpoint-zero response and
publishes it only after that exact TX completion. No actual CE submission,
retained adapter, early WMI service queue, host-memory allocation, WMI INIT,
regulatory/VDEV profile, scan, protected credentials, association, IP or WAN
has been integrated. Public proof: session-v1/evidence/2026-10-05/htc-credit and
htc-control. Next: actual retained native CE0/CE1 handshake and CE2 WMI service
RX/memory-init, with monotonic deadlines and explicit quiesce before replacement.
Mac credentials remain owner-only; no key/password output or remote export.


### 2026-10-05: actual native CE control candidate, not delivered

New native-wifi-qca9377-operating-v1 derives a generation43 candidate from the
unchanged42 boot path. It calls the tested HTC control/credit coordinator from
actual native entrypoints after firmware READY, drives actual CE0 TX/CE1 RX/
CE2 WMI RX with retained registered buffers/pin, and validates SERVICE_READY.
RX is posted first; endpoint0 CE transfer metadata is0, not BMI0x3fff. One early
endpoint-zero response waits for its exact TX completion, one early WMI frame
waits for the assigned endpoint. One mapped data buffer per direction; no repost
while hardware-owned.20-second trial; all outcomes close through existing actual
all-eight-stop/BM-off/flush/unmap/free before unpin. Persistent radio/quiesce,
WMI INIT/host-memory allocation, regulatory/VDEV/scan/security/IP/WAN remain.

17 actual native-entrypoint/CE hardware-model scenarios pass ASAN/UBSAN +COFF on
Yukabox, covering original boot faults/cancellation plus operational TX/RX timeout,
bad endpoint/service/ABI, ambiguous doorbell, cancellation, early RX order and
successful SERVICE_READY. Full UEFI build initially exposed an unavailable
___chkstk_ms dependency; removed the large stack temporary, retained static state.
Generated protocol formatting is deterministically normalized for strict GCC and
Clang; actual native tests use those exact generated bytes.

Full candidate147456bytes SHA72a758d543f4cf53244295fbcf525e52367fd3b97fee037870d69e365229537b;
two identical full builds, normal/EMPTY supervisor QEMU(city/clock/fullscreen/
restore/rejection/read-only GATT) and406 current-source input hashes plus exact
world16 C/sanitizer reproduction pass. Operating telemetry: handles23..25,
service/characteristic UUID24/25,QWOP0001/96bytes, separate from QWBT boot status.
Public logs/reports/reproduction: operating-v1/evidence/2026-10-05/native-candidate.
Mac ignored checked payload: operating-v1/runs/checked-candidate/candidate.efi.

NOT signed/delivered/physically verified. Existing native_route does not admit
this new profile: extend strict admission/evidence and negative checks before
local signing. Controller remains42/world16, no pending asset, no radio lease.
Next: strict candidate admission, fresh physical baseline, exact sign/send,
separately signed generation43 RAM assets (42 packets MUST NOT replay under43),
read QWOP+QWBT and verify physical all-owner cleanup. Asset staging must repeat
because cross-module RAM ownership has not been implemented. All credentials/
owner key stay on Mac, never output/export. No bootstrap/USB/reboot/OTP action.


### 2026-10-05: native43 strict admission complete; exact signed transfer active

Operating admission is now `operating-v1/operating_route.py`: original native42
port/reset/IRQ/allocation/USB/asset/boot checks remain mandatory through unchanged
native_route.gates on the retained baseline, plus exact operating policy, source
closure,17 operational and65 NEW actual derived initial-entrypoint scenarios,
current-world sanitizers and both read-only-GATT/fullscreen/city QEMU gates.
321 corruption/rebinding/log/payload negative cases reject, no secret or radio.
Original native_route.py/boot_build.py and all389 baseline inputs stay unchanged.
The new reproduction binds411 current inputs. Same147456-byte native payload SHA
72a758d543f4cf53244295fbcf525e52367fd3b97fee037870d69e365229537b.
Evidence: operating-v1/evidence/2026-10-05/native43-admission. During gate work,
source-snapshot mismatch and README closure inconsistency correctly blocked the
candidate; corrected and repeated all65+17 tests/builds/QEMU/reproduction.

Fresh native42 QWBT before signing confirms READY, all3114 commands complete,
no errors,stage5/adapter12/cleanup14/DMA0/pin0. Local owner signing occurred only
after all admission/owner/target/next-counter/fresh-release checks. Exact pending
native session `pci-native-39db645t`, counter43; native_pending is set. Actual
Bluetooth staging began (known peer), confirmed4100/147744 at this checkpoint;
NOT APPLIED yet. Read newest logs/state before resuming. Preserve exact packet,
nonce,counter and411 frozen source inputs; do not edit them while pending.
Bounded controller operating-v1/runs/control/resume_native43.py, at most6 calls,
stops after two no-progress calls. It uses the same route query-before-send and
all admission checks every time. Finite idle-sleep guard follows controller12113.
No bootstrap/USB/reboot/OTP action. City observation remains separate/pending.

After exact43 APPLIED, read fresh QPD18 first-lifetime completion before staging
assets. operating_route.py asset-prepare/asset-deliver reuse unchanged finite
boot_asset_route/signing/sender machinery with stricter operating installed
payload/policy/owner/target/counter/APPLIED binding. A new signed43 asset session
is necessary (42 packets MUST NOT replay). Prepare only once, retain checkpoints.
After final asset triggers firmware+control trial, read QWOP+QWBT and verify all
actual owners released before any replacement. Persistent radio/WMI INIT/scan/
protected credentials/association/DHCP/WAN are still unimplemented.


### 2026-10-05: native43 physically applied; new immutable43 assets staging

Exact native session pci-native-39db645t completed147744 bytes. Commit disconnected
as expected; reconnect verified exact SHA/session/counter43 APPLIED. Controller
is43/world16, native_pending clear. Payload72a758d543f4cf53244295fbcf525e52367fd3b97fee037870d69e365229537b.
Native initial lifetime QPD18: stage5/error0,setup4/error0,BMI type8/version05020001,
adapter12/cleanup14/DMA0. QWOP0001/96bytes is physically readable via UUID24/25;
all initial fields0, so no operational/control startup claimed. Visual city/tail
confirmation after43 was requested and is pending, never inferred from receipts.
Proof: operating-v1/evidence/2026-10-05/native43-applied-initial.

First cached Mac PCI helper reported diagnostic service absent: its discovery
filter omitted UUID0D although its callback accepted0D. Read-only inventory found
service0D. An ignored derived Cocoa helper explicitly requests0D/0C and filters
the known peer; it read actual QPD18 successfully. Original frozen read_pci.m and
all411 source inputs remain unchanged. Public derived read-only helper source is
archived with proof. `runs/control/read-operating` similarly reads known-peer
UUID24/25, QWOP0001/96byte envelope, no write. Do not infer missing hardware from
stale/filtered CoreBluetooth service inventory alone.

After fresh exact physical QPD18 and all operating admission/current-installed
APPLIED/policy checks, owner locally signed twelve NEW immutable generation43
packets once: firmware-ram-5yo48w3h. It is now hardware_trial_pending. New asset
RAM began empty (bitmap0), current first packet SHA
e4d1e5dac54440706a810a28c19abf82b0f3156659ceaa504a960a77d0665c16.
At checkpoint4320/65760 receiver-confirmed, no accepted chunk; use latest logs.
Bounded controller operating-v1/runs/control/resume_asset43.py uses
operating_route.py asset-deliver,24 attempts maximum, stop after two no-progress
attempts, exact saved signatures/packet/checkpoints, same source checks every run.
It is sole radio owner; finite idle-sleep guard follows controller20859.
Do not edit411 frozen inputs, re-sign/change nonce/counter, replay42 packets,
change world, touch bootstrap/USB or reboot Dell during this trial.
After all12 accepted, boot/calibration/main/HTC/control-SERVICE_READY trial runs
and closes through actual all-owner cleanup. Read BOTH QWOP and QWBT; only the
latter reports boot readiness/closed ownership, while QWOP distinguishes actual
control/service-ready success/failure. RAM bitmap alone proves only staging.
No persistent radio/WMI INIT/scan/router association/IP/Yukabox exchange yet.


### 2026-10-05: WMI INIT envelope prepared independently of frozen43

Exact43 firmware session firmware-ram-5yo48w3h continues under its existing
bounded controller; historical checkpoint:2 accepted chunks (bitmap3), third
partial17280/65760. Read latest receipts; do not infer main/control startup or
edit411 frozen native inputs. No second radio owner or new asset signature.

New independent native-wifi-qca9377-wmi-init-v1 provides a PURE complete WMI INIT
serializer (command1/TLV74,75,18,76), ABI from pinned Linux wmi-tlv.c/.h.
44-word/176-byte resource vector is opaque except vdev/peer binding: it is NOT a
reviewed station policy. Existing memory plan is recomputed; one unsplit mapping
per request, exact ids/count/sizes, nonzero/aligned32-bit addresses, extent and
mutual-overlap guards. Actual map ownership/control-buffer exclusion/retention
remain caller responsibilities. No allocation, WMI transmit, credentials or
native43 integration. Active-peer mode/64-bit addresses/split requests excluded.

1,691,012 independent pinned-layout/capacity/address/plan/rejection checks under
ASAN/UBSAN plus COFF pass on Yukabox. Source oracle caught/fixed resource size and
memory-plan success-code mismatch before integration. Primary Linux commit
6b5a2b7d9bc156e505f09e698d85d6a1547c1206, wmi-tlv.c SHA
02309cad56513a1ef0975c9d73e568e343c874d35124f39111ddd26d8a75c5bb,
wmi-tlv.h SHA16c6b984177dd8c0f80dbc4df52597a6def435d8892fb55381091bdb88a258c9.
Remote refs /home/yuka/rabbit-world/wmi-init-next/reference; public proof in
wmi-init-v1/evidence/2026-10-05. All411 active native inputs rechecked unchanged.
Next after physical SERVICE_READY: actual memory requests, reviewed station
resource profile and retained DMA memory lifecycle, then WMI INIT+actual READY.
Persistent radio, scan, protected association, DHCP/IP and WAN remain unfinished.


### 2026-10-05: native43 physical HTC READY; first control response rejected

All12 generation43 firmware assets accepted (bitmap4095). Main firmware loaded,
3114 commands confirmed, boot phase5/error0, READY20 bytes, credits2/1792,
endpoints4. QWOP0001: phase3/error4, session2, posted16, TX1/RX1. RX1 proves
CE completion/cookie/length validation passed; HTC control parsing rejected
first response. Original43 did not retain raw bytes; reason not proven.
Actual adapter12/cleanup14/DMA0/pin0, native stage6/error8448. Read BOTH statuses:
boot READY is not a successful control handshake. Asset trial pending cleared
only after actual all-owner release. Known-peer read-only observations archived
in operating-v1/evidence/2026-10-05/native43-control-fault. Scene observation
remains pending; no inferred cat visibility. No Wi-Fi association/IP/WAN.

Owner authorized exact CE1 diagnosis/fix. Isolated native44 diagnostic candidate
in native-wifi-qca9377-operating-diagnostic-v1 retains all original43/42 source
bytes and strict checks. QWOP0002/208 bytes adds receive stage, pre-consumption
ring indices, descriptor8 and bounded prefix64. No credentials or keys present
in this pre-association diagnostic.22 actual-entrypoint CE/fault scenarios and65
initial scenarios passed on Yukabox; full EFI/QEMU/current-world reproduction
and strict admission are in progress. Not yet physically installed. Do not
claim a format fix until actual diagnostic bytes identify the rejected response.


### 2026-10-05: native44 diagnostic admitted and exact transfer started

Yukabox22 CE/native-entrypoint scenarios and65 initial scenarios pass ASAN/UBSAN
and COFF. Full EFI builds identical:147968 bytes SHA256
34126735c8c35f854d4a3cb1410e359e55999fef86298a5467cd9e6515dfab83.
Both actual supervisor QEMU city/fullscreen/restore/rejection/read-only GATT
cases pass, and current world16 C checks/reproduction pass across427 current
inputs, including every unchanged native43 input.350 admission corruption/
physical-release cases reject with zero secret loads/radio writes. Physical43
raw QWBT and QWOP were freshly reread together; exact known43 CE1 failure and
all-owner release required before44 signing. No broad failure bypass added.
Evidence: operating-diagnostic-v1/evidence/2026-10-05/native44-admission.

One locally signed saved native44 session: pci-native-7jesbhyh. Controller
operating-diagnostic-v1/runs/control/resume_native44.py: at most6 delivery
attempts, stops after two no-progress attempts, exact saved signed bytes only.
It is sole radio owner, finite idle-sleep guard follows controller. Transfer
started; NOT yet observed APPLIED. Preserve427 frozen source inputs and exact
world16. Read report/state/latest receipts before any next action. No new
firmware44 assets signed/staged yet. Once APPLIED, read fresh QPD18/QWBT and
QWOP0002 using read_diagnostic.py, then prepare exact generation44 assets through
operating_route.py asset-prepare/deliver. Do not replay43 signed assets. Actual
firmware pin/DMA ownership must close before any further native change.

QWOP0002 expands to208 bytes, retaining original22 status words then ten receive
words(pipe/step/hardware index/read/write/published/cookie/length/ring fault/
hardware error), pre-consumption descriptor8 and bounded DMA prefix64. Steps1
MMIO index,2 CE completion,3 cookie,4 length,5 HTC control reject,6 duplicate
SERVICE_READY,7 HTC service frame reject. Descriptor captured BEFORE consume
clears length. Snapshot survives existing teardown. No guard relaxed or guessed
format fix. Next: actual44 raw response -> narrow evidence-supported correction.
Wi-Fi association/IP/WAN/Unreal on Dell remain unfinished.


Native44 finite trial continuation is running in ignored runs/control/continue44.py
(exec session61366). It waits for the existing native44 controller to exit,
requires exact native44 APPLIED/state/hash, then under the same exclusive state
lock reads known-peer QPD18 using the verified read-pci43 helper. It calls strict
asset-prepare exactly once, only after actual fresh setup/BMI/all-owner-release
and unchanged427-input gates. If any gate/read/receipt fails it stops without
bypass or re-signing. It then runs the24-attempt/two-stall exact asset controller,
followed by at most30 boot observations,120 seconds apart, and final QWOP0002
read only after actual all-owner release. Wait for native controller is capped
at one hour. Finite caffeinate guard follows continuation process. Archived
inspectable controller sources in native44-admission evidence. Current observed
native staging checkpoint24600/148256 is sender progress, NOT APPLIED; exact
report confirmation floor is still0 during the paced-stage invocation. This
chain performs the authorized diagnostic trial only, never a guessed format
change. After final raw response, agent must inspect it before any next candidate.


### 2026-10-05: native44 exact APPLIED; fresh initial gates and44 assets started

Native44 now EXACT-APPLIED-RECEIPT, counter44/payload SHA
34126735c8c35f854d4a3cb1410e359e55999fef86298a5467cd9e6515dfab83.
Initial continue44.py correctly stopped on probe-active PCI read. Fresh read-only
retry after setup completed passed strict QPD18 gate, then owner locally signed
NEW immutable44 firmware session firmware-ram-z9vgatek exactly once. It is now
hardware_trial_pending. No43 assets replayed; all427 frozen inputs unchanged.
Evidence: operating-diagnostic-v1/evidence/2026-10-05/native44-applied-initial.

Sole asset controller runs under ignored runs/control/finish44.py (exec53902),
calling resume_asset44.py with exact session,24-attempt/two-stall limits.
finish44.py's post-asset observation portion lacks import time (caught during
review); do not interrupt the active asset sender or replay preparation. Its
first post-asset boot read is still safe, then it may exit at time.sleep. A
separate corrected observe44.py (exec7499) waits for finish44 process to exit,
requires actual all12 accepted/exact full-RAM report/current44 before any read,
then performs bounded boot reads/final QWOP0002 after all-owner release. It owns
no radio while waiting. Finite idle-sleep guard follows observer. Correct the
old ignored finish44 import only after it exits if it is ever reused. Do not
restart either asset sender while the current controller is live. If asset
controller stops unconfirmed, observer also stops; resume only saved exact
session after checking receipts. Raw CE1 diagnostic still pending; no format
fix, router association/IP/WAN/Unreal display success yet.


### 2026-10-05: native44 complete; actual CE1 response identifies length rejection

All12 exact44 assets accepted. Fresh physical QWBT boot complete3114/3114,
READY20/error0, native stage6/error8448, adapter12/cleanup14/DMA0/pin0.
hardware_trial_pending cleared only after actual all-owner release. QWOP0002
phase3/error4, CE1 step5, RX20 bytes, cookie0x501, no ring/MMIO fault.
Actual frame prefix00000c0000010000030000010001f80600000000: HTC body12,
CONNECT message3/service0x100/status0/endpoint1/max1784/trailing4 zero.
Existing qca_htc_connection in session-v1/htc_wire.c requires EXACT8-byte body
and rejects this actual12-byte body before field parsing. Narrow reason proven;
next candidate must use pinned connect-response struct and validate metadata/
lengths, not blindly widen input. Pinned ath10k htc.c checks control_resp_len
against sizeof(message header)+sizeof(connect response). Preserve original
427 inputs; derive isolated override for next candidate, rerun actual CE fixtures
with observed20-byte response and malformed variants. Evidence archived at
operating-diagnostic-v1/evidence/2026-10-05/native44-control-response.
No new45 candidate signed/sent. Still no router association/IP/WAN/Unreal stream.


### 2026-10-05: bounded actual CONNECT response fix, native45 admitted/sending

Isolated native-wifi-qca9377-connect-response-v1 preserves every native44/43/42
source byte unchanged. Derived driver overrides only htc_wire.c: pinned ath10k
CONNECT core is8 bytes (message header2 + response6); Linux accepts minimum core.
Actual44 has12 bytes with four zero trailing bytes. New parser accepts only8 or
this12-byte zero suffix, preserving message/service/status/endpoint/capacity
checks;9..11/13+ or nonzero extension remain rejected. No claim of standardized
metadata format. Native44 QWOP0002/208 diagnostic and all-owner teardown retained.

Pinned-struct independent oracle + captured Dell20-byte frame + early-RX/control
checks:5186 under ASAN/UBSAN/COFF on Yukabox.27 actual native CE fixture scenarios
include20-byte default reply, early completion, short/malformed/wrong-service/
non-success/unknown extension rejection and valid legacy16-byte frame.65 actual
initial scenarios pass. FullEFI two identical builds147968 bytes SHA256
127c950855f275e839ca4a5f614280b6b0ef9e15fb2754d0cd4e60dd2a928302.
Both real supervisor QEMU city/fullscreen/restore/rejection/readonlyGATT cases
pass. Two exact current-world builds/C ASAN checks and446-source reproduction
pass.357 admission corruption/physical-observation cases reject with zero
secret loads/radio writes. Additional response proof/log/source hashes required
by admission. Evidence: connect-response-v1/evidence/2026-10-05/native45-admission.

Fresh actual native44 QWBT+QWOP reread; exact known CE1 failure/captured20-byte
response and all-owner release mandatory before signing. Saved one NEW native45
signed session pci-native-s9npn8cw; transfer started, NOT yet APPLIED. Controller
runs/control/resume_native45.py (exec40527):6 attempts/two no-progress stop.
Exact continuation runs/control/continue45.py (exec6947) waits for existing
controller exit (one-hour max), requires exact45 applied/hash/state, retries
initial read-only PCI only for documented probe-active result (8 max), then
strictly signs NEW45 assets once after exact initial live gate. It delivers
through24-attempt/two-stall saved-asset controller and performs bounded30 boot
reads/final QWOP0002 only after actual owner release. time import checked; no
second radio owner while waiting. Finite caffeinate guard follows continuation.
No45 assets prepared yet. Preserve446 frozen inputs/world16; do not replay44
assets, re-sign existing packets, reboot Dell, touch USB/bootstrap or print key.
Physical first-control/SERVICE_READY success remains unconfirmed. No persistent
radio/WMI INIT/router association/IP/WAN/Unreal display success claimed.


### 2026-10-05: native45 APPLIED;45 firmware staging; pure WMI INIT coordination

Native45 EXACT-APPLIED-RECEIPT observed, hash
127c950855f275e839ca4a5f614280b6b0ef9e15fb2754d0cd4e60dd2a928302.
continue45.py correctly waited for completion and used bounded read-only retries
until initial QPD18 passed setup/BMI/all-owner cleanup. Signed NEW immutable45
assets once: firmware-ram-to7dn7gd, now hardware_trial_pending. Sole controller
continue45.py/resume_asset45.py is running; first packet confirmed21600/65760,
zero complete chunks at this historical checkpoint. Read latest receipts.
No44 asset replay/re-signing. All446 active input hashes unchanged. Evidence:
connect-response-v1/evidence/2026-10-05/native45-applied-initial. Finite sleep
guard still follows continuation. No physical CONNECT/SERVICE_READY proof yet;
no inferred city observation, association/IP/WAN/Unreal display success.

Independent native-wifi-qca9377-wmi-transaction-v1 now coordinates existing INIT
serializer, exclusive credit ledger and READY decoder.945 ordering/early READY/
credit reports/cancellation/fault/malformed/session mismatch checks pass ASAN/
UBSAN and COFF on Yukabox. Reserve during construction, commit BEFORE descriptor
publication, no DMA-completion refund; unposted cancellation or validated firmware
reports alone refund. Genuine READY plus matching TX completion required, in
either order. Completion IDs reject repeated API consumption, not authenticated
replay. Minor53 matches current encoder. Ambiguous publication faults retain
committed credit/actual external DMA owners; no allocation or MMIO here.
This is NOT native45 integration or station policy/mapping approval. Opaque test
resource vectors are not hardware configuration. Native proof lives separately
in wmi-transaction-v1/evidence/2026-10-05; no new Dell packet sent for this module.

Before real INIT: actual SERVICE_READY requests/capabilities, approved station
resource vector and separately checked live DMA mappings/non-overlap/lifetime.
Existing qca_dma_open requires bus mastering off; cannot simply allocate while
current CE adapter is active. Also current208-byte QWOP reports memory_count but
not every memory request; need exact read-only request telemetry or validated
native-only use of actual service object. Do not guess geometry from host tests.
Next remains finish physical45 control trial, inspect actual status/data, then
checked memory/INIT integration. Credential provisioning, scan/association,
DHCP/IP and WAN/video receiver remain unfinished.


### 2026-10-06: physical native45 CONNECT success; native46 SERVICE_AVAILABLE trial

Actual45: HTC session RUNNING7, TX3/RX3, endpoints WMI1/HTT2, credit2,
no ring/MMIO fault. Zero-extended CONNECT fix confirmed on Dell. First CE2
frame36 is WMI event3/TLV559/value20/advertised extended length128/four words,
not SERVICE_READY1. Current45 rejected it (operating error9). Boot3114/3114,
READY20, actual adapter12/cleanup14/DMA0/pin0. Hardware pending cleared by actual
release observation. Physical evidence: connect-response-v1/evidence/2026-10-06/
native45-control-result. No association/IP/WAN/Unreal display success.

Pinned wmi-tlv.h/.c enum and dispatch identify SERVICE_AVAILABLE separately;
first field is service_map_ext_len, NOT an offset. New pure service-available-v1
validates only known event3/tag559/value20/length128 and preserves opaque4 words.
7198 actual-payload/mutation/truncation checks ASAN/UBSAN/COFF on Yukabox, pinned
enum oracle. Physical packet itself was36 bytes; an initial38-byte hex literal
in new admission was caught/rejected before any key access, corrected to actual36.
Negative test range also corrected to22 status+10 receive words; variable DMA
address was intentionally not an admission authority. Full proof rerun after
all source changes; no guard relaxation or fabricated report rebind.

New isolated service-start-v1 candidate generation46 retains exact45 source/owner/
world. At most one validated SERVICE_AVAILABLE, negotiated WMI endpoint, zero
credit reports; rearm CE2 and await SERVICE_READY under existing deadline.
Malformed/duplicate/foreign/missing events and ambiguous rearm retain all owners
until actual teardown.35 actual native CE scenarios +65 initial scenarios pass;
existing5186 CONNECT oracle checks retained. Two exactEFI builds148480 bytes SHA
 dd261ac34e720259bc5d199b5f9832ddf7cb9ead7d7b607d3974af6593f5fcfc.
Both supervisor QEMU city/fullscreen/restore/rejection/read-only long-GATT cases
pass, current-world C/reproduction pass across469 inputs.365 admission rejection
cases pass with zero key loads/radio writes. New available proof/log/source
bindings mandatory. Evidence: service-start-v1/evidence/2026-10-06/native46-admission.

Read-only QWOP0003 is488 bytes (within512-byte GATT attribute), original22 words/
receive metadata/prefix plus available seen/advertised length/4words. Final256
bytes are16 decoded memory-request slots if service_valid, otherwise bounded
raw service-frame prefix (up to256 bytes, total length in existing field).
CoreBluetooth reader checks exact488-byte/magic envelope. QEMU explicitly tests
first246-byte ATT payload, second242-byte payload, end/invalid offsets and writes
rejected. Future INIT still requires actual request review/station vector/live
DMA ownership; no allocations/INIT/credentials/scan/association introduced.

After fresh actual45 dual QWBT/QWOP and owner release, signed one NEW native46
session pci-native-z_yxuvwo. Sole resume_native46.py controller exec85816,6 attempts/
two no-progress stop. Exact continue46.py exec48385 waits native PID57975 (one-hour
cap), exact46 APPLIED/hash/state, then bounded8 probe-active read-only retries,
strict NEW46 asset preparation/signing once, exact24-attempt/two-stall asset
controller and up to120 boot reads120 seconds apart (four-hour observation cap)
plus final QWOP0003 only after real all-owner release. Finite sleep guard follows
continuation. All469 frozen inputs verified, none edited after signing.

Current native transfer has weak local Bluetooth RSSI-83..-87 and repeated
connection timeouts, partial first staging reached5900/148768; this is NOT
APPLIED or receiver-confirmed floor until next exact query. Saved packet/session
retained; do not re-sign/replay/change base/world. Async asks owner move Mac about
one metre from Dell; response pending. No46 firmware assets yet prepared. Check
latest receipts/controller status before resume; do not start another radio owner.
No Dell reboot, USB/bootstrap changes or private-key output.


### 2026-10-06: physical46 prelude fixed; actual SERVICE_READY128-value format

Fresh QWOP0003 confirms HTC RUNNING7/TX3/RX4/endpoints1,2, no CE/MMIO faults,
available.seen1/length128/word0=0x08000000. CE2 rearm succeeded; actual next320-byte
packet is WMI SERVICE_READY1, first TLV32 value128. Existing decoder requires104
and rejects it (operating error9), so service_valid0 and memory_count0 are NOT
proof of absent memory requests. First256 bytes archived, full320 retained on
Dell. Fresh boot confirms3114/3114/READY20/error0/all owners released (adapter12,
cleanup14/DMA0/pin0). All469 inputs preserved; no new47 code/signature yet.
Evidence: service-start-v1/evidence/2026-10-06/native46-control-result.
Next actual-layout review/strict bounded decoder compatibility and tests, then
new candidate. No association/IP/WAN or Unreal display claimed.


### 2026-10-06: native47 SERVICE_READY common-prefix/memory validation admitted

Pinned wmi-tlv.h/.c svc_rdy struct104 and parser use common prefix; firmware
reports TLV value128 with same prefix and opaque24 extra bytes. Independent
service-layout-v1 derives wmi_boot_info.c without changing any46 inputs: accepts
only104/128, exact ABI major/namespaces, reported minor (actual574), known chain/
request limits and full memory array/declaration consistency. Hardware capability
limits2300..2800 and4900..6500 cover actual2312..2732/4920..6100; metadata parsing
is not regulatory/channel permission, and no RF scan/TX operation introduced.
Actual46 prefix declares num_mem_reqs0 at pinned offset72. Final array must still
be validated physically; zero metadata in failed46 was NOT proof of no requests.
Full320-byte host fixture uses observed256 prefix plus explicit synthetic bitmap
suffix/empty memory array; it is host-only, not a new physical capture.

22244 pinned-struct/common-prefix/extension/ABI/band/memory/truncation ASAN/UBSAN
and COFF checks pass on Yukabox;41 actual native CE scenarios include extended
packet, mismatched declaration/unknown size/band/chain/ABI rejection.65 initial
scenarios and prior5186 CONNECT/7198 available proofs retained. Two identicalEFI
builds148480 bytes SHA76e5db52405f86e60a7d6d95791289f4e73b09213f8e5302d58d131a31b3f910;
both supervisor QEMU city/fullscreen/restore/rejection/long-read-GATT cases pass.
Current-world C/reproduction491 inputs pass;367 admission corruption/owner-release
cases reject with zero key loads/radio writes. Layout proof/log/source mandatory.
Evidence: service-layout-v1/evidence/2026-10-06/native47-admission.

Fresh46 dual QWBT/QWOP and actual all-owner release read. Known immutable46
baseline record is hash pinned in47 route; entire488-byte packet compared except
variable descriptor DMA address. Prepared one NEW signed native47 session
pci-native-_pg_zhuu. resume_native47.py exec7209/native PID92408 started exact
transfer; still NOT observed APPLIED. continue47.py exec40911 takes exact saved
session/PID args, waits bounded native completion, requires47 APPLIED/hash/state,
read-only initial probe retries, strict NEW47 asset signing once, exact bounded
asset sender and120 boot observations/final QWOP0003 after real owner release.
Finite caffeinate guard follows continuation; all491 inputs frozen/unchanged.
Initial Bluetooth RSSI-69..-70, better than prior46 transfer but not a reliability
proof. No47 firmware assets yet prepared. Do not replay46/re-sign/mutate world,
reboot Dell/touch USB/bootstrap or print private key. Physical city observation
not inferred from receipts. No INIT/association/IP/WAN/Unreal display success.

Future INIT review: actual service ABI minor574 is reported; Linux compatibility
checks major/namespaces, not minor equality. Existing pure wmi-transaction-v1
uses a narrow READY minor53 profile and is not yet native-integrated. Review that
profile against real/pinned READY semantics before integration; do not blindly
require advertised574 or assume no host buffers for later HTT data reception.

### 2026-10-06: native47 applied; new firmware trial in progress

Exact correlated APPLIED receipt confirms native47, payload76e5db52405f86e60a7d6d95791289f4e73b09213f8e5302d58d131a31b3f910,
148768 signed transport bytes. State native_pending cleared. Bounded continuation
read initial PCI after five probe-active retries and admitted NEW47 firmware
asset session firmware-ram-xa_97zti. Delivery of first of12 chunks is active;
no final SERVICE_READY/memory result yet. Do not duplicate sender, replay46,
re-sign, reboot, or edit491 frozen native47 inputs. Existing continuation/
resume_asset47 processes and finite caffeinate guard remain the owners.

Independent host-only wmi-transaction-v1 revision removes READY minor==53
equality: pinned Linux READY parser reports the minor as metadata; our strict
major/namespaces/status/MAC/credit/order checks remain. Synthetic minors
0/53/54/574/65535/UINT32_MAX with both DMA/READY orders and independent
major/namespace corruptions pass1029 ASAN/UBSAN and freestanding COFF checks
on Yukabox. Evidence wmi-transaction-v1/evidence/2026-10-06. Not integrated
in native47, and actual WMI READY is still unobserved. Firmware transfer
continues; no scan, association, IP, WAN or Unreal display is claimed.

### 2026-10-06: INIT resource reference prepared; firmware delivery progressing

New independent native-wifi-qca9377-resources-v1 replaces opaque fixture
assumptions with full44-word Linux QCA9377 PCI TLV resource reference: vdev4/
peers33/TIDs66/AST16/WDS32/MSDU1056/WoW22 and all exact remaining fields.
Base bitmap uses FOUR low bits per u32; service65 RX_FULL_REORDER is word16/
bit1. Only32-word base map admitted by this pure builder; no extended174
TX_ACK_RSSI assumptions. Reference host capability512 requires a management
bundle completion handler or an explicitly tested alternate policy before
native admission. Linux chain masks7 preserved as reference, not RF permission.

Independent compiled Linux cfg assignments/struct/macros and pinned hardware
defaults compare randomized base maps; memory-plan/INIT serialization uses
actual reference counts with0..16 synthetic requests.8347 ASAN/UBSAN and COFF
checks pass on Yukabox; source/oracle/reference hashes recorded in evidence/
2026-10-06. Candidate remains HOST ONLY, not station-profile admitted, no DMA
owners/command dispatch/physical READY claimed. All491 native47 inputs checked
unchanged. Physical firmware-ram-xa_97zti first chunk is accepted (bitmap1),
second underway; continue47/resume_asset47 and sleep guard active. Do not
duplicate controller or read final operating result before actual completion.
No router association/IP/WAN/Unreal display yet.

### 2026-10-06: management completion decoding/ID plan checked; firmware3/12

Independent native-wifi-qca9377-mgmt-completion-v1 prepares single/bundle
WMI completion wire handling required by Linux host_capab bit9. Actual pinned
Linux enums/struct and callback array semantics; strict2048-byte/32-report
local envelope, matching count/array lengths, unique IDs, ACK RSSI only when
validated policy enables it. Full batch matched against outstanding IDs before
a mask is returned; unknown/duplicate ID rejects with no partial mutation.
No mask is a DMA release: generation, actual DMA completion, retained owners
and dispatcher integration remain required. No credit refund or radio command.
33502 ASAN/UBSAN and freestanding COFF checks pass on Yukabox; exact source/
reference/oracle hashes in evidence/2026-10-06. HOST ONLY: physical wire
compatibility, native dispatcher and station admission are still unverified.

Firmware trial firmware-ram-xa_97zti now has three exact chunks accepted
(bitmap7); fourth underway. Existing continue47/resume_asset47 and sleep
guard alive,491 frozen native47 inputs unchanged. Do not start duplicate radio
work, replay sessions, reboot or alter the pending candidate. No final47
SERVICE_READY/memory result, WMI INIT, association, IP or WAN success yet.

### 2026-10-06: bounded real CE WMI INIT native48 candidate checked, NOT signed

New independent native-wifi-qca9377-wmi-native-v1 derives from unchanged47.
After actual HTC + parsed SERVICE_READY it reuses retained14-map/pin guard,
requires zero memory requests and exactly32 base bitmap words, builds Linux
reference resource vector/INIT228 bytes, reserves/commits credits BEFORE actual
CE0 publication (WMI endpoint transfer metadata), posts CE1/2 and requires
actual TX completion plus valid READY/MAC. Early READY retained;20s timeout.
Only firmware reports refund committed credit. Unposted cancel refunds;
ambiguous TX/RX, nonzero memory, wrong fields/endpoint/cookie, replayed READY,
clock reversal or poisoned pin fault while all real owners remain held.
Shared operating errors propagate to startup status; resident stop cancels
logical startup before existing ALL-engine stop/flush/unmap/free/unpin.
No new allocation, RF scan/management TX, credential, association or IP.
Management-bundle reference flag is not native station dispatch admission.
This diagnostic closes its radio lifetime even after successful INIT.

22 actual generated-entrypoint/real-CE ASAN/UBSAN scenarios and all65 initial
entrypoint cases pass on Yukabox. Every success/fault/cancel case proves all14
maps released and pin removed; synthetic target is explicit, never physical.
New read-only UUID26/27 handles26..28, QWIN0001/96 telemetry tracks startup,
READY/MAC/minor/credits/last RX. Existing QWOP3/QWBT unchanged. Mac helper
compiled only (zero radio reads/writes); --read requires exact installed48/hash.
Two byte-identical EFI156160 bytes SHA203e606ab41663170a3307dd3dbe18b26ccb8db67d5566b6e03f9fc7b1e893b7;
actual supervisor QEMU city/fullscreen/restore/rejection/read-only new GATT
checks pass in normal and EMPTY boot. Current world package8254c704... validated
under C ASAN120 ticks/16 adversarial cameras. Full reproduction525 exact source
inputs verified unchanged. Evidence: wmi-native-v1/evidence/2026-10-06/native48-candidate;
unsigned EFI/report/reproduction saved locally in runs/operating-profile.
No physical admission/signing route exists for48 yet. Required next: finish47
firmware trial, fresh real QWBT/QWOP success/memory and actual all-owner release,
then bind an exact48 admission gate before signing/delivery; do not bypass it.

Current physical firmware-ram-xa_97zti has6/12 chunks accepted (bitmap63),
seventh transferring. continue47/resume_asset47 and finite sleep guard remain
active; all491 signed native47 inputs unchanged. No47 final SERVICE_READY
result yet, no48 signed/sent and no Wi-Fi router/IP/WAN/Unreal display success.

### 2026-10-06: owner reboot reset native47; plain city restored as48/world17

User reported an actual Dell reboot. Existing firmware sender/continuation had
already stopped after bounded timeouts, old session firmware-ram-xa_97zti
completed6/12 chunks. Fresh known-peer RFS EMPTY/counter0 confirmed reset with
zero query writes. No old staging resumed or erased. New native-reboot-staging-v1
verifies owner/public target, exact historical native47 signature, twelve saved
chunk signatures/hashes, world/native binding and all491 frozen sources.
Explicit owner reboot + fresh EMPTY log required; archives exact old state/report
and signed hashes, marks RAM staging retired, clears only hardware_trial_pending.
11 isolated tests pass; zero retirement private-key loads/radio writes.
Original report archived byte-exactly and audit hash checked.

Existing verify_reboot_recovery on Yukabox repeated plain BLE-recovery city
EFI builds, current restored world17 C/roof-cat timing checks, normal/EMPTY
supervisor QEMU. Payload47616 SHA0fb9fa6c1c307e8ca0fe51b4b29e3cd815c3e2881f9c1ceba6d01d80ce52b4ce.
Baseline BMI reproduction metadata copied without changing frozen sources.
Gates checked again on Mac before authorized local signing. Exact plan
native48-city-recovery-plan consumes native48/world17, freshly EMPTY checked
again before any BEGIN. Native commit disconnected/reconnected; correlated
exact receipt confirmed48, then exact restored-world receipt confirmed17.
State recovery_pending and hardware_trial_pending cleared; semantic world
fa5a3250633f2bbbd288d947be567c2c5db8e3395033da99b765edf0a0f5cc74 preserved.
Physical city/tail observation requested, still not inferred from receipts.
No reboot/USB/bootstrap/storage write or key output by agent.

Evidence native-reboot-staging-v1/evidence/2026-10-06. Old firmware packets
remain immutable. Need fresh Wi-Fi trial after visual confirmation, whole
firmware delivery must restart from0. Unsigned WMI candidate48/203e606a... is
historical now: native48 was consumed by recovery, engine is plain city with
no Wi-Fi probe. Rebuild/rebind future counter/policy and current world17; do
not reuse old48 payload/session or its world16 reproduction as current evidence.
No scan/association/IP/WAN/Unreal display success.

### 2026-10-06: visible city confirmed; new bounded WMI INIT49 signed/delivering

User confirmed restored city visible/moving and authorized continuation.
Native48 remains exact plain city recovery; world17 package47d63aa6... current.
New independent wmi-native-v2 derives unchanged INIT candidate with generation49
and world17 reproduction. Captures original legacy hardware/boot42 evidence
with its ORIGINAL world16 bytes (no rebinding/fabrication), while49 itself has
separate current-world17 C/normal+EMPTY QEMU/two-rebuild proof. The physical
starting-state gate now requires exact completed reboot recovery48 (signed
bootstrap-bound payload/plain no-Wi-Fi profile, preserved world17), fresh known
peer zero-write actual world17 receipt and owner scene observation. This replaces
obsolete post46 live-state assumptions after user reset; all actual49 CE guards
still require physical parsed SERVICE_READY before INIT, and nonzero memory
requests reject without command/new allocation. No scan/station traffic/PSK/IP.

Initial65 and real CE INIT22 ASAN/UBSAN/COFF cases pass. Pinned INIT/memory/
transaction/resource evidence is mandatory in535-source closure. Two identical
EFI156160 SHA145bb27e7f066ac24f471cf9e130329aedbc9bd33d9bf11b2ae78a5a82b535e3;
normal/EMPTY supervisor QEMU and current-world C120 ticks/16 adversarial camera
checks pass.24 admission corruption/legacy-world/missing source/log cases reject
with zero key loads/radio writes. Delegated native transport gate regression
caught recursive baseline gate selection BEFORE any signing; captured original
BASE_GATES fixed and delegated path tested. All535 inputs re-proved afterwards.

Fresh actual recovery48/world17 read verified. Local owner signature produced
once; exact saved session pci-native-cizvcg3f counter49; native_pending active.
No49 APPLIED/firmware/INIT result yet. Sole bounded continue49 PID1524 handles
exact native delivery, fresh initial QPD18, strict fresh49 asset preparation
once, saved firmware delivery, actual all-owner QWBT release then QWOP3/QWIN1
reads. Finite caffeinate follows its PID. Script/metadata archived in native49-
admission evidence; script operational state in runs/control. No duplicate
sender, re-sign, old47 firmware replay, reboot, USB/bootstrap or key output.
535 source inputs frozen while delivery/trial active. Bluetooth initial RSSI
-66..-69; not a reliability guarantee. Owner gate/proof/current world bound.
Physical WMI INIT success, router/IP/WAN/Unreal display still unconfirmed.

### 2026-10-06: native49 progressing; independent station wire prepared

Sole continue49 PID1524 and finite sleep guard remain active. First native
staging call reached77900 then bounded300s timeout; next fresh read confirmed
80500 bytes of SAME nonce/hash saved session pci-native-cizvcg3f and resumed.
Latest staging checkpoint117400/156448, NOT APPLIED. No re-sign/replay/new
asset session.535 signed candidate source inputs checked unchanged. Wait for
exact49 application/initial probe, then full firmware delivery and real
QWBT/QWOP/QWIN READY/MAC results; no router connection claimed.

Independent native-wifi-qca9377-vdev-wire-v1 prepares strict STA CREATE/STOP/
DELETE bodies from pinned Linux enum/struct/CREATE assignments:28/12/12 bytes,
STA2/NONE0, four resource IDs, actual READY MAC input and zero padding.12723
ASAN/UBSAN/COFF wire/MAC/bounds/alias tests pass on Yukabox; report/log/source/
oracle/reference hashes recorded. HOST ONLY, not part of535 native49 inputs,
not physically sent. No scan/channel/keys/association/IP. Firmware acceptance
requires a future confirmation/ordering path; DMA completion is not acceptance
and stop/delete serialization is not all-owner release. Persistent radio and
actual INIT result must come before interface/scan integration.

### 2026-10-06: exact native49 APPLIED; fresh initial accepted; firmware restarted

Sole saved pci-native-cizvcg3f transfer completed156448 transport bytes. Commit
disconnected, sender reconnected and exact correlated SHA/session/counter49
APPLIED receipt confirmed. State engine49/payload145bb27e... and native_pending
cleared. Fresh known-peer QPD18 initial snapshot accepted by unchanged strict
asset preparation guards (actual setup/BMI/target/all initial14 owners released).
NEW exact signed firmware session firmware-ram-s23u1qom, generation49, prepared
once; no old47 chunk replay. First of12 packets started with valid fresh empty
asset status and staging length65760. No full chunk/firmware/INIT result yet.
continue49 PID1524 remains sole controller with finite sleep guard,535 inputs
checked unchanged. Exact native receipt and initial snapshot archived at
wmi-native-v2/evidence/2026-10-06/native49-applied-initial. WMI READY/MAC,
radio persistence, router association/IP/WAN/Unreal display unconfirmed.
Physical scene observation after49 not inferred from receipts.

### 2026-10-06: physical49 all firmware/boot/SERVICE_READY pass; INIT TX timeout

All12 firmware-ram-s23u1qom chunks accepted, bitmap4095. Actual main boot
submitted/completed3114, calibration3, HTC READY20 observed. Actual QWOP3
phase2/error0/session7, tx3/rx4, valid SERVICE_READY320, build21/minor574/
chains1, zero memory requests. This is the first physical full SERVICE_READY
parse success. No fabricated zero-request claim from a truncated capture.

QWIN1 phase3/error12 (20s deadline), transactionFAULT, INIT228 bytes posted
once, zero RX, no TX completion and no READY/MAC. One committed credit remains;
no DMA-completion refund invented. Actual QWBT adapter12/cleanup14/DMA0/pin0
proves all owners released; hardware_trial_pending cleared, controller exited.
No router/IP connection or WMI INIT success. Exact captures/asset report in
wmi-native-v2/evidence/2026-10-06/native49-control-result.

Code review identified concrete routing mismatch: startup49 posts/completes
INIT on CE0/ring0/buffer1. The actual signed/readback initialization service
table init_tables_native.h maps WMI_CONTROL0x100 OUT to CE3 and IN to CE2.
Pinned Linux pci.c has the same map; reserved HTC control service1 uses OUT0/
IN1, explaining why prior handshake worked. CE3/ring3/buffer7 already belongs
to the14-map scope. Next candidate must add actual CE3 ownership/mapping/
register guards, transmit/completion on CE3 and independent route-aware target
fixture (current host fixture incorrectly accepted INIT on0). Do not merely
change a doorbell number or widen timeouts. Physical corrected-route success
is not yet established; native49 sources/captures remain unchanged.

### 2026-10-06: user-authorized parallel Wi-Fi development

Three isolated agent outputs reviewed; no physical writes, credentials or owner
key access. persistent-v1: lifecycle retain/quiesce/actual-stop/release, 1976
ASAN/UBSAN checks and COFF; review fixed invalid/epoch-mismatched observations
to terminal RETAINED, prohibiting further work/release/unload. station-scan-v1:
READY/MAC -> ordered STA-create -> passive scan/event coordinator, 11166 checks
and COFF against pinned Linux create/scan structs. security-plan-v1: concrete
mature-supplicant/HTT/key-confirmation/encrypted-provisioning/lwIP integration
plan and framing-only EAPOL-Key parser, 201477 checks and COFF against actual
hostap2.11 headers. None is integrated into the physical Dell; framing is not
a WPA handshake, and scan coordination is not discovery of an actual network.

Root integrates the prerequisite separately in wmi-native-v3 counter50: CE3
INIT using existing ring3/buffers6,7, actual ownership/register guards, target
fixture route derived from setup table plus independent pinned Linux pci.c
route oracle, explicit regression rejection of the old CE0 publication. Keep
physical trials under one controller and leave all native49 source/evidence
unchanged. Join order: physical INIT/READY -> persistent radio -> scan/beacons
and regulatory policy -> association + real HTT + supplicant/key installation
-> IP -> actual Yukabox exchange -> video/Unreal. Host subparts can proceed in
parallel, but no router/IP/Unreal success is inferred from their tests.

Native50 CE3 candidate host proof completed: 65 initial scenarios,22 actual
startup/CE/ownership scenarios plus rejected old CE0 regression, two identical
EFI rebuilds, full and empty-boot supervisor QEMU, current world17 C/ASAN check
and unchanged535-source reproduction. Payload156672 SHA256
c56f1d738253c4505a5d5485c352fa6d697c5ff5c6218f981b399ee463546d46.
Local checked-candidate passes24 admission/corruption cases, no key/radio.
Candidate is UNSIGNED and NOT delivered. Next physical50 admission needs fresh
known-peer combined native49 boot/operating/startup owner-release observations,
exact current counter/world/gates and one sequential controller. Do not replay
firmware49, assume READY or combine this diagnostic with unintegrated scan.

### 2026-10-06: native50 hardware continuation started

Fresh sequential known-peer zero-write BOOT/operating/startup observations
matched actual native49 timeout and all14 owners/pin released. Strict current
world/counter535-source gates passed. Exact CE3 native50 signed locally once
and saved as pci-native-n4pntq1v; controller17105 + finite caffeinate17106 owns
sequential delivery, initial read, NEW generation50 firmware session and final
boot/INIT capture. Controller/log: wmi-native-v3/runs/control/continue50.py and
continue50.log. First DATA checkpoint4100/156960 observed. NOT yet APPLIED, no
READY/router/IP claim. Preserve and resume this exact session; do not resign or
replay49 assets. Device reboot retires RAM staging only through existing proof
path. Three agents work in NEW separate scopes on persistent native integration,
STOP_SCAN and mature supplicant port; no device owner or secrets delegated.

### 2026-10-06: native50 physical trial completed; new RX parser failure

All12 exact firmware chunks accepted, bitmap4095. Main firmware boot3114/3114
completed, HTC READY20, SERVICE_READY320 build21/minor574/zero host-memory
requests parsed successfully. After CE3 INIT publication228, one RX credit
completion accepted (available2/outstanding0), then actual CE2 completion68
bytes/cookie1538/index3 was rejected by transaction parser: startup phase3
error8, diagnostic step4. No validated WMI READY/MAC or TX completion recorded.
This is different from49's RX0 deadline. Correct routing is not sufficient
proof of full INIT acceptance; rejected raw frame content is not exposed by
current96-byte GATT telemetry. Next diagnostic must expose exact RX prefix
and bounded reject reason; do not guess packet type or relax validators.
All14 actual owners/pin released, hardware_trial_pending cleared; controller
17105 completed, no ongoing transfer. Exact observations/asset evidence at
wmi-native-v3/evidence/2026-10-06/native50-control-result. Router/IP/WAN absent.

### 2026-10-07: native51 precise INIT reject capture implemented and trial started

Isolated wmi-native-v4 preserves native50 sources. Same INIT acceptance and
all-owner teardown, extended read-only QWIN0002/244: old96 fields retained,
then reject stage/frame bytes/prefix bytes/endpoint/payload bytes at96..115,
128-byte exact zero-padded RX prefix at116. Captured before parser: the physical
68-byte rejection will fit completely. Reasons1 coordinator/preconditions,
2 HTC framing,3 endpoint,4 READY/schema/ABI/status/MAC,5 credit accounting.
Does not claim diagnosis of unseen physical bytes or relax validators.
65 initial +22 startup scenarios ASAN/COFF (including exact exported bytes and
reject-stage checks), oldCE0 regression, two EFI rebuilds, both QEMU gates,
currentworld17 C/ASAN,535-source reproduction and24 admission cases passed.
Payload156672 SHA fd073f22156ad9921ca628d02b4384f370869ebf0cb04959b10ad8df70112fa7.
Fresh native50 boot/op/startup tuple and actual all14 owner release admitted
local signing once. Saved pci-native-o59ttl2m. Sole controller32341 and finite
caffeinate32342, wmi-native-v4/runs/control/continue51.py/continue51.log, execute
exact native delivery -> fresh initial -> NEW firmware51 session -> boot/INIT
observation. Preserve this exact session, never replay old50 firmware.
At this record trial just started, not APPLIED or Wi-Fi connected.

### 2026-10-07: physical51 complete exact READY response and proven schema mismatch

All12 assets accepted. Boot3114/3114, HTC READY20, SERVICE_READY320 passed.
QWIN2 captured COMPLETE68-byte RX, endpoint1/payload60, reject_reason4. Exact
WMI event2/tag35 contains52-byte READY value: ABI01000000/minor574/pinned
namespaces, MACc0:b5:d7:78:c3:fb, status0,16-byte suffix. Current codec
requires exactly36 and rejects a valid common-prefix extension. Actual pinned
Linux wmi-tlv.c READY policy uses min_len sizeof(wmi_tlv_rdy_ev)=36 and its
pull consumes prefix ABI/MAC/status without exact-length check. New isolated
wmi-native-v5 will use that bounded minimum, preserve mandatory ABI/status/MAC
checks and expose all old diagnostics. Host captured-frame prefix/extension
ASAN/COFF proof4294 checks passed, complete native/QEMU proof in progress.
No WMI INIT TX completion/physical success claimed. All14 owners/pin released
and controller32341 exited. No hardware_pending. Exact evidence stored under
wmi-native-v4/evidence/2026-10-07/native51-control-result. Wi-Fi/IP absent.

### 2026-10-07: native52 READY prefix fix verified and hardware trial started

Isolated v5 overrides only wmi_boot_info.c READY exact36 -> minimum36 in
existing bounded/aligned TLV parser, following pinned Linux policy and pull.
ABI/namespaces/status/nonzero-unicast MAC requirements preserved. Independent
actual Linux struct oracle verifies size36,MACoffset24,statusoffset32. Exact
physical51 payload and every extension byte mutation passed;4294 ASAN/COFF
codec checks,65 initial,23 startup (new52-byte READY actual-model case),
CE0-rejection regression, two EFI rebuilds, both supervisor QEMU gates,
world17 C/ASAN,540-input reproduction and24 admission cases passed.
Payload156672 SHA0b4dfbf03b12eef58cbaa4eabe965dda606ded3337a60708b22574b02edb52f6.
Fresh sequential native51 diagnostics and actual all14 resource release
admitted local signing once; exact saved session pci-native-cpez9mi7.
Sole controller41277/caffeinate41278: v5/runs/control/continue52.py and
continue52.log, metadata controller52.json. Performs native52 transfer then
NEW firmware52 generation/session and all-owner INIT observation. Preserve
saved bytes, no resign/replay51. Trial just started, not APPLIED/connected.
Heartbeat wi-fi-dell every30min remains active; use actual latest state, not
old automation creation snapshot of51 or its retired controller.

### 2026-10-07: native52 applied; parallel offline integration reviewed

Exact native52 applied; sole controller41277 continues NEW saved firmware
session firmware-ram-r7mvy8zb. At heartbeat2 full chunks confirmed, third
confirmed prefix57600/65760 before resume. Preserve exact session; controller
is live, no second Bluetooth owner. WMI INIT result not yet available.

Reviewed and source/evidence hash-verified offline outputs now preserved:
persistent-native-v1 (27 actual-entrypoint model ASAN/COFF cases): real14-map
retention after validated READY, explicit stop/release and fault revocation;
no RX pump yet. scan-stop-v1 (280685 ASAN/COFF checks): pinned Linux STOP_ONE,
actual terminal event plus published-TX completion, no DMA credit refund.
supplicant-port-v1 (1038 ASAN boundary cases): unedited mature RSN object,47
unresolved dependencies, upstream PTK no-reinstall boundary; NOT linked/native
or full handshake. set_key must wait genuine firmware completion, uncertain
timeout requires teardown before retry. These host results are not physical.
Independent next necessary task delegated to persistent_radio in NEW
persistent-rx-v1: real bounded CE1/CE2 RX completion/credit/dispatch servicing
after READY, with actual guarded owners. No hardware/state/secrets delegated.

### 2026-10-07: bounded persistent native RX reviewed; station dispatch next

Native52 firmware transfer still advancing under controller41277 (8/12
confirmed, ninth prefix21600 at heartbeat). No completed INIT result yet.
Reviewed persistent-rx-v1:41 actual-entrypoint model ASAN/COFF scenarios,
exact source/log hash bindings; derives native52 and reviewed owner bridge.
Adopts real posted CE1/2 descriptors, bounded completion/cookie/address/length
guards, fresh retained owners, trailer-only once-per-completion credits,
two owned raw-event slots/backpressure and all-owner release before clear.
No station/event registry or physical payload admission. Host proof only.
Next independent station-dispatch-v1 delegated to scan_pipeline: RX pump owns
credit accounting; dispatch owned payload without calling old full-HTC receive
which would apply credits twice. Monotonic event IDs may skip credit-only RX.
Must retain unmatched events, real scan/request/vdev identity, no invented
VDEV_CREATE firmware ACK. No hardware or frozen source edits delegated.

### 2026-10-07: native52 loading; owned station dispatch reviewed

All12 firmware52 chunks accepted, chip main image advancing offset159960
at heartbeat; controller41277 live, all14 owners/pin intentionally retained
until trial result. No WMI INIT result or station connection yet.
Reviewed station-dispatch-v1,50478 ASAN/COFF checks on Yukabox, source/log
bindings verified. Owns copied pump payloads, accepts monotonic completion gaps,
updates only validated scan state; ledger never reapplied. Exact pending
scan/request/VDEV0 and ordering, unknown/foreign/unsupported TLV retained with
explicit ownership/backpressure; no invented CREATE firmware ACK. Host only.
Independent next work in new scopes: persistent-profile-v1 prepares bounded
10s actual persistent/RX trial with read-only telemetry, counter53 provisional
and full EFI/QEMU/world17 proof; owned-scan-stop-v1 joins stop to owned events
without raw receive or double credit. Neither has physical admission yet;
native52 must complete/actual INIT/owner-release before any new hardware trial.

### 2026-10-07: physical native52 INIT succeeds; bounded persistent53 admission next

Exact native52 and all12 firmware52 chunks accepted. QWBT phase5/error0,
3114/3114, native_stage5/error0; QWOP SERVICE_READY320 accepted. QWIN0002
phase2/error0, transaction RUNNING4, READY seen1, INIT TX complete1, ABI574,
MAC c0:b5:d7:78:c3:fb, credit2/outstanding0, memory requests0. Complete68-byte
READY frame accepted under pinned Linux common-prefix policy. All14 DMA/PCI/
IRQ/link/wake/pin owners released; hardware_trial_pending cleared and sole
controller41277 exited. Exact receipts/raw bytes/hashes archived in v5
evidence/2026-10-07/native52-control-result. No router/IP/WAN or new physical
scene observation claimed. Preserve world17, no reboot/USB/flash.

Next isolated persistent-profile-v1 candidate53: bounded10s genuine retained
owners plus CE1/CE2 RX pump, read-only QWRX0001 handles29..31, checked stop.
WholeEFI four equal builds, both supervisor QEMU, currentworld17 C/ASAN and24
actual-native model scenarios prepared on Yukabox; admission not yet signed.
Do not edit candidate source bytes. Separate root admission scope will bind
565-source closure, generated inputs and all proofs before physical signing.

### 2026-10-07: exact bounded persistent53 admitted and sole controller started

Root separate persistent-admission-v1 leaves all frozen52/profile source
bytes unchanged.565-input/source + generated-compiler bindings, inherited52
complete gates,24 actual-entrypoint ASAN/COFF fixtures, both actual supervisor
QEMU and world17 C/ASAN verified.20 corruptions rejected with key/radio mocked
unreachable. Fresh sequential known-peer zero-write52 QWBT/QWOP/QWIN confirms
actual READY/MAC/INIT TX and all14 owners released before signing once.
Payload163840 SHA261649e8cd7ab2bd59621f8ee559c421c36cc5e54c5d19238b558e55dc55a522.
Saved exact53 session pci-native-0iwr2hpw. Sole controller46741 and caffeinate
46742: persistent-admission-v1/continue53.py, runs/control/continue53.log,
controller53.json. Finite native resume -> NEW firmware53 -> actual boot
release -> QWIN/QWRX reads. Can resume SAME native/asset sessions; no resign or
replay52 firmware. Counter53 not yet APPLIED at this record.

Final53 success must include actual owner release and READY/TX, QWRX bounded
trial PASS, rx_error0 and valid RX phase. Legacy stage6/8448 is controlled stop
and insufficient alone. Two-event backpressure intentionally limits this
trial; not proof of sustained station traffic. No station/RF/credentials.
Owned-scan-stop-v1 reviewed100568 ASAN/COFF checks; matching terminal + genuine
STOP TX completion, retained unknown/foreign ownership, deadlines/overflow
fault without credit refund. ENDED alone NEVER permits DMA unload. Host only.

### 2026-10-07: native53 applied; firmware53 transfer progressing

Exact53 APPLIED receipt archived in persistent-admission-v1/evidence/2026-10-07/
native53-applied. Sole controller46741 live; native_pending cleared, NEW exact
firmware53 saved session firmware-ram-8sztj97t, hardware_trial_pending remains.
At heartbeat two complete chunks accepted and third confirmed prefix30240.
Use latest report/checkpoints, preserve exact bytes; no second BLE owner.
Bounded physical RX result not yet available, Wi-Fi/router/IP absent.

Reviewed scan-native-plan-v1 reference/source/log/physical52 evidence bindings.
Pinned ath maps regdomain108=0x6c to WORC_WORLD, not Georgia; actual GE country
mapping distinct. Capability bands alone cannot select channel permissions.
Linux integration order: filtered SCAN_CHAN_LIST then PDEV_SET_REGDOMAIN,
actual CE3 TX plus one RX credit owner, owned dispatch/STOP and all14 teardown.
Real SSID proof additionally requires management/HTT beacon/BSS RX, not only
scan events. Plan has empty selected frequencies and no RF admission.
Independent necessary offline work assigned in NEW channel-wire-v1 serializers
and regulatory-policy-v1 provenance/filter. No hardware, candidate, signatures
or credentials delegated; actual53 completion is prerequisite for next trial.

### 2026-10-07: native53 assets advance; offline channel and policy proofs reviewed

Sole controller46741 still live. Exactfirmware53 session firmware-ram-8sztj97t
confirmed7/12 chunks, eighth prefix57600 at heartbeat; native53 already APPLIED.
No concurrent radio operation, no retransmission/resigning of oldsessions.
Physical bounded RX/owner result still pending, router/IP/WAN absent.

Reviewed new channel-wire-v1:77367 differential/negative ASAN/UBSAN+COFF checks
on Yukabox, exact source/log bindings. Pure SCAN_CHAN_LIST/PDEV_SET_REGDOMAIN
serializers, explicit authenticated-policy input boundary, passivelegacy20,
limits/flags/units/overlap/target guards; max63 rows at actualWMIlimit1784.
Pinned mature caller ath10k_regd_update passes combinedregdomain to allthree
domain fields, then separate perbandCTL; forWORC_WORLD108 this is108/108/108,
NO_CTL255/255. This mapping must be independently bound before RF admission.

Reviewed new regulatory-policy-v1:199278 purefilter ASAN/UBSAN+COFF checks on
Yukabox, exact sources/log/proposal bindings. Officialregdb2026.09.03 CMS uses
only pinnedLinuxwens signer; officialdb.txt rebuild byte-identical to signeddb,
altereddata/signature rejected. Trust is pinnedkey/HTTPS, not PKIX/time or
archiveOpenPGP validation; no primaryGElegal instrument independently verified.
ExplicitownerlocationGE intersected with unchangedworld108 and actualcapabilities:
13 candidate passivelegacy20 channels2412..2472,20dBm ceiling;12/13 retainNO_IR.
No countryoverride, probes,5GHz/DFS,RFadmission or nativepublication. Mature
signeddatabase is engineeringreference; caller must validate completeprovenance
and actualcurrenttarget/lifecycle before one native trial.

Independent next necessary preparation delegated to persistent_radio in NEW
persistent-tx-v1: actualserializedCE3 owner/publication using sharedRXHTCledger,
no DMAcreditrefund, ambiguityretaineduntilactualstop. Nohardware/candidate/secrets.

### 2026-10-07: all53 assets accepted; runtime TX and beacon adapters reviewed

Native53 exactfirmware session firmware-ram-8sztj97t all12 accepted bitmap4095,
RAMready1. Solecontroller46741 remainslive; actualchipmainloading offset120032
submitted/completed663/663 at heartbeat, all14 owners+pin appropriately retained.
Do not sign/change engine until actual allownerrelease/result. NoWi-Fi/IP/WAN.

Reviewed persistent-tx-v1 exact source/log+54 compiledfixturebindings:16 actual
nativebridge/RX/CE3 scenarios ASAN/UBSAN+COFF onYukabox. Sole serializedCE3
publisher borrows sharedRXcreditledger, commitsbeforepublication, exactmapping/
cookie/address/index/length guards, runtimeHTCsequence, boundedcreditwait and
ambiguityretaineduntilactualstop. DMAcompletion onlyorderscommands; no credit
refund or inventedfirmwareACK. INITcoordinator is not runtimeTX. Host-only.

Reviewed beacon-rx-v1 source/log+unchangedsessionbeaconhelper bindings:
459252 adapter +9117 baseline ASAN/UBSAN checks+COFF onYukabox. Pinnedactual
WMI MGMT_RX0x7001/header40/TLV44+17, boundedbytearray (unalignedlenperLinux),
rawchannel/rate/SNR/status/RSSI preserved, copiedBSSID/SSID/opaqueRSN. Errors/
unknownextensions/foreignframes unaccepted with callerownership intact.
MGMT_RX lacks vdev/scan/requestIDs: collector MUST bind actualownedCE/radioepoch
and reviewedchannelpolicy, never manufacturecorrelation or SSIDfromSTARTED.
No physicalMGMT_RX/SSID claim; no HTT/FCSguessing.

Next independent NEW scan-coordinator-v1 prepares HOST-ONLY runtimeTX/RX +
policy/channel + station/ownedSTOP + beaconjoin. Oldstationprepare/post/STOP
reservecredits too: newcoordinator MUST use purewire bodies and soleactualTX
owner, reflect publication/DMAordering into pendingstate without doublecredits.
No frozenedits/nativecandidate/RF/hardware/secrets delegated.

### 2026-10-07: Bluetooth observer recovered; scan coordinator model reviewed

Old solecontroller46741 exited on BOOT read disconnected while chipmainloading
at offset218488. Firmware was alreadyfullyaccepted; native53 unchanged.
Sequential zero-write reconnect confirmed loading699608 with noerror. Noasset
replay, noresign, noreboot. NEW observer-v1/observe53.py solecontroller51276 +
caffeinate51277 resumes ONLY BOOT/OP/QWIN/QWRX reads with finite retries.
Metadata/log/results in observer-v1/runs/control. Latest BOOT phase5/error0
3114/3114+HTCready20, all14maps/pin stillheld beforeboundedtrialresult.
Use final result53.json and actualrelease, not time/progresssnapshots.

Reviewed scan-coordinator-v1 source/logbindings:15scenarios1376ASAN/UBSAN+COFF
onYukabox. Real TX/RX/CEbookkeeping/lifecycle/v5READY linked; loweroperating/
MMIO/devicebackend mocked, NOT actualfullnative orphysicalproof. Purewirebody
commands use solepersistentTX creditowner; actualPOSTED/DMA_DONE projects
matchingpendingrequest/bytes. RXtrailers appliedonce, foreign/controlretained,
naturalterminal cancels only unpostedTX, rollback/timeouts guarded. SSID only
acceptedMGMT_RX aftermatchingSTARTED/FOREIGN_CHANNEL withselectedpolicy+epoch.
Exact14modelrelease versus14retainedonwrong_epoch.

Next NEW scan-native-profile-v1 actualentrypointadapter/wholeEFIproof delegated
to persistent_radio; counter54 provisional, no signing/hardware until actual53
allownerPASS. Bounded setup/scan/STOP/overalllimits in newsource only, keepunknown
FIFO owned andquiesce underbackpressure. Separate rootRFadmission must verify
signedregdb/rebuild/target/domain/caps/owner/epoch and passive13rows/CTL255;
proposalartifact stays RFfalse. Useralreadyauthorized scan/connect; this is
deterministicadmission, not a newuserapprovalstep. Credentials untouched.

### 2026-10-07: physical native53 bounded persistent RX succeeds; actual release

FreshQWINREADY/MAC/TX complete1, error0. QWRXtrialDONE3/error0, expired1,stop1,
lifecycleRELEASED4/errors0, polls45, RXcompleted2/posts3, credits2/outstanding0/
reserved0. Actualall14 buffer/DMA/PCI/wake/link/IRQ/pin/bus/accessowners0,
adapter12/cleanup14. Genuine10sboundedreceive-and-stop trial PASS. Router/IP/WAN
and SSIDstillabsent; no newscenevisualobservation claimed.

FrozenlegacyBOOTdecoder expectedassetready1/bitmap4095 afterphase5; actual
qca_stop rightlyreleasedRAM: phase0/assetready0/bitmap0 whilecachedboot5/20
3114/3114 remains, native6/error8448 controlledstop. Do NOT relaxolddecoder.
NEW release-observation-v1 strict exact53 tuple binds priorcorrelated12chunk
acceptance + freshQWIN/QWRX actualreleasedinventory,56negativecases, zero-write.
Result/rawbytes/receipt/sourcehashes archived evidence/2026-10-07.
Hardware_trial_pending cleared ONLY aftercombinedproof understate lock.
Old46741 exited and recoveryobserver51276 stopped afterdecoderissue; no live
radio controller aftermanualsequentialcombinedread. Noassetsreplayed/resigned.

RXphase1/postedRX1/queue2/backpressure1 are retainedcachedbookkeeping after
actualquiesce, not liveDMAowners. Two unknowncopiedeventpayloads are NOT exposed
by53QWRX and NOT exported/consumed/identified. Nextadmission must explicitly
bindthisdocumentedobservationlimit; neverinventrawbytesorSSID. No arbitrary
memoryreadbypass. Native54 preparation adds stable read-only rawexport ofall
retainedslots afteractualquiesce; rootmustsaveexactbytes/hashes beforefuture
unload. Replacingtheauthorizedboundedtrial afterallhardwareownersreleased
needs nonewuserapproval; preserveworld17.

Native54 scanprofilepreparation continuesoffline onYukabox withactualentrypoint
adapter/readonlyexport/model/wholeEFI/QEMU/world/sourceproof. UNSIGNED/not sent.
RootRFadmission remainsseparate fromproposal andrequiresallprovenance/current
policy/target/domain/caps/epoch/owner plusphysical53PASS.

### 2026-10-07: passive native54 admitted, signed once and physical trial started

NEW scan-native-profile-v1 frozen offlinecandidate187392 bytes SHA
3eefea77fbab35bca609216e4a418c2abad695f1a8a83da8aa2ee147bbfefca3.
10 actualnativePCI/CE/DMA entrypointmodel scenariosASAN/COFF (lowerbackend
modeled), four equalEFI builds, normal+EMPTY real supervisorQEMU, world17ASAN
120ticks/16cameras,628input closure verified. IndependentCMS/signedregdb
rebuild/exactGE×unchanged108 passive13-row headerbinding verified; proposal
RFfalse stays unchanged. Generatedcopies whitespace-onlynormalized forstrict
compiler; originalfrozenmodules untouched andexactcompiledfixtures checked.

Rootseparate scan-admission-v1 binds allproofs/policy/currentcity;17corruptions
rejected withsecret/radio mockedunreachable. Freshsequentialzero-write53
BOOT/QWIN/QWRX/QWOP confirmsactual allownersrelease,READY/MAC andcurrent
regdomain108/capabilitybands. Explicitoldunknown2/unexportedlimit archived.
Existinguserscan/connectauthorization permits ONE checked bounded25spassive
trial. Target/owner/nextgeneration validatedbeforekeyaccess; nocredentials.

Signedexactonce savedpci-native-1qq9s17x. Solecontroller52976/caffeinate52977,
scan-admission-v1/continue54.py, runs/control/continue54.log/controller54.json.
Native54 notyetAPPLIED at record. Finite exactnative resume -> NEWfirmware54
session -> BOOTread-only ownerobservation -> QSCN+all40exportpages collected.
Preserveexact savedbytes, neverreplay53 firmware/resign orsecondBLEowner.
BOOT54 collector acceptsactualRAMrelease withoutchanginglegacydecoder; no
successor pendingclear is inferred fromtime orDMAcompletion alone.

New54 retainsALL8potentialrawslots (archive2/observation/orphan/dispatch2/RX2)
as40readonlypages. Rootmustcapturealltwice withstablestatus, preserve exact
bytes+hashes beforeanylaterunload. QSCN STARTED/terminal/SSID/credits/ownerstate
are observational, not deviceattestation. MatchingSTARTED alone isn'tSSID;
realacceptedMGMT_RX/rawexport andpolicy/epochbinding needed. Physicalscan/SSID
notyetconfirmed, noassociation/IP/WAN. Macnativezero-writecollectorpreparation
in NEW scan-observer-v1 delegated; noagenthardware/secretaccess.

### 2026-10-07: native54 applied; association/key reference correction

Exact54 APPLIED receipt archived under scan-admission-v1/evidence/2026-10-07/
native54-applied. Sole52976 stilllive; NEW firmware54 session firmware-ram-
g9g89amj, full2chunks and thirdprefix21600 at heartbeat. Preserve exactpacket/
checkpoint, no newradioowner. Physicalscan/SSIDnotyetavailable, Wi-Fi/IPabsent.

Reviewedstation-association-plan-v1:28422 pinnedPEER_CREATE DEFAULT peer oracle
ASAN/UBSAN+COFF checks onYukabox, exact source/logbindings. Purewire block, no
peer/association/DMAACK claim. PinnedWMI KEY_COMPLETE handler is debug-only;
actualmature install_key_done usesHTT SEC_IND withpeer/session/keyvalidation.
PEER_ASSOC config doesNOTperform actualoverairAPassociation.
CurrentphysicalQWOP alreadyopensHTTservice768 endpoint2; nextindependent
htt-version-v1 mustreuse validatedconnection, negotiateactualVERSION_CONF/
opmapping/CE4TX+dataRX routes, not blindlyCONNECTagain orclaimdataplane-ready.
NoRF/secret/hardwaredelegated.

Scanobserver-v1 reviewedsource/static2722/preflight proof, NOactualradio. Root
foundterminaldecoderfalse-rejection: coordinatorclearslive_frequency onterminal
butretainedacceptedbeacon persists. NEWscan-observer-v2 preparesfix+negative
tests preservingv1proof/source: validateexactpolicyfreqandSTARTED/slot/floor/
epoch, requirelivefreqequalityonlywhen nonzero. Preserve rawcaptureBEFOREdecode.
Existingfrozencontinue54 stillcalls v1 collect.py afteractualrelease; ifthat
rejects retainedterminalbeacon, DONOTreplayassets/resign/clearpending. Onceold
controllerexits, root mustrunv2collector--readsequentially, saveall40pagestwice
andstableQSCN, thencombinedverdict. v2CLI samecollect.py--read innewscope.

### 2026-10-07: reviewed terminal observer2, HTT codec and BSS eligibility

Sole52976 stilllive. Savedfirmware54 g9g89amj advancing7completechunks plus
eighthprefix61920 at heartbeat; use latestreport, no secondcontroller/resign.
Physicalscan/SSID/association/IPnotyetconfirmed.

Reviewedscan-observer-v2:2749staticnegative/terminalcases+MacObjCpreflight,
sourcehashesverified, noactualradio. Preservesv1. Acceptsretainedterminalbeacon
withlive_frequency0 onlyquiesced/released+STARTED/rawslot2/completionfloor/
nonzeroepoch/exact13policy; nonzerolivefreqmustmatch. RawstdoutsavedBEFORE
decode; oldpositivedecodedarchived/invalidatedonnewfailure. FinalassetDONE4/
state2/digest/length/floor boundtoreal lastpacket; publicsignatures+allbodies/
wholeFWdigest verifiedbeforeactualread. flowstate.lockcompatible.
Afterfrozen54controllerfinishes, ifv1collectorrejects terminalobservation run
ONLYnewv2collect.py--read sequentially; retainstableQSCN+all40pagestwice and
combinedBOOT+receiptbeforependingclear/futureunload. Never replayfirmware.

Reviewedhtt-version-v1:131677ASAN/UBSAN+COFF onYukabox, exactsource/logbindings.
ReusesRUNNINGsession withactualHTTendpoint2; VERSION_REQ/CONF strictTLVop3/
major2or3. CurrentoperatingALREADYconnectsHTT768; QWOP lacksmaxbytes sointernal
validatedsessionrequired. HTTflowcontrol disabled, notWMIledger debit/refund.
CE4buffers8/9 TX +singleCE1buffers2/3 control/HTTdemux needed; frozenRXpump
rejectsendpoint2. VERSION_CONF alone isn'tdataplaneready.

Reviewedbss-security-v1:117075ASAN/UBSAN+COFF, independentoriginalhostap2.11
wpa_common.c oracle, exactsource/logbindings andBSDcoreretained. CopiedMGMT
context+epoch/channel/policy + actuallegacy/basicrates + RSNsuites/PMF checked.
Select onlyexplicitPSK/CCMP, rejectenterprise/SAE-only/TKIP/MFPR/truncation/
duplicates/incompatiblerates. PSK/SAEtransition onlyactualPSK+CCMP withoutMFPR.
Candidate meanseligibility, NOTauth/association ornetworkready. Credentials
untouched. NextHOST-ONLYhtt-native-v1 actualPCI/CE/DMA owneradapter/model
delegated: exclusiveCE1completionowner, CE4versionquery, nosecondRXowner,
bounded3s andall14checkedquiesce/export. No hardware/candidate/signing.

### 2026-10-07: all54 assets accepted; HTT actual-owner adapter reviewed

Sole52976 live; exactfirmware54 g9g89amj all12acceptedbitmap4095/RAMready1.
Actualchipmainloading advancingoffset121024/submitted667/completed667 at
heartbeat, noerror, real14owners+pin retained. No otherBLEowner orassetsreplay.
Physicalscan/SSID/association/IPresultstillpending.

Reviewedhtt-native-v1 exactsource/log+112compiledfixturebindings:21 actual
PCI/CE/DMA entrypointmodels ASAN/UBSAN+COFF onYukabox. DerivedprivateRX gives
ONECE1/CE2completionowner withendpoint0/control+negotiatedHTT2 andWMI1, exact
mappings/trailers/credits. HTTCE4request usesbuffers8/9, exclusivehtt_ownertoken,
currentendpoint/session/epoch andpublicationwatermark; noWMIcreditdebit/refund.
RequiresactualDMA plusgenuineVERSION_CONF, notoneorfakedACK. SixrawHTCslots
response/archive2/FIFO2/rejected includecredit-onlytrailers; allcopiesretained.
Clock/owner/fault distinctions: actualadapterrelease separatefromlifecycle
unloadpermission; faultremainsretained. Checkedcurrenttimequiesce before
legacyqca_stop preventsfalseclockrollback. Model-only, nowholeEFI/physical.

NextNEWhtt-native-profile-v1 preparesproductionloop/readonlyframedexports/
authenticatedfirmwareIE6 HTT-op provenance/wholeEFI+QEMU+world+sourceproof on
Yukabox. Counter55provisionalUNSIGNED, hardwareblockeduntil54combinedresult
andALLrawexportssaved. Rehashretainedowner-signedcontainer andbindmain/helper
planpointers beforeparsedTLV3 query; nohardcodedguess orRF/dataplanereadyclaim.

Independentsecure-provision-plan-v1 preparation: matureECDH/AEAD/ownertranscript
andexplicitdeviceauthentication+secureRNG boundary. ExistingBLEUUID/signature/
targetreceipts aren'tdeviceattestation. No realpassword/keyread/export. Ifno
existingpinnedDellidentity, physicalSAScomparison is eventualrequiredstep
beforesecrets; donotbypasswhileusersleeps. No approvalrequestneedednow.

### 2026-10-07: native54 actual release; offline55 and provisioning boundary

At heartbeat54chipmainloading696880 thenfull3114/3114, HTCready20; BOOT5/error0,
native6/8448 controlledstop, actualadapter12/cleanup14/DMA0/pin0, RAMreleased.
Sole52976 nowcapturingQSCN+all40pages; doNOTparallelBLE. Hardware_trial_pending
STILLfirmware-ram-g9g89amj untilcombinedfreshreceipt/BOOT/QSCN/exportproof.
Ifcollector1failsorfinishes, rootdecodeitsrawusingv2offlinewhenpossible; else
runv2collectonlyafteroldPIDexit. No firmware/assetsreplay/resign.

Reviewedhtt-native-profile-v1 frozenOFFLINE55:168448-byte EFI SHA
c4c656e38ed37027c56dffb4f22c35ba5b339a279c6ecf400eebe684452ed72f.
24productionentrypointPCI/CE/DMA ASAN/UBSAN+COFF cases, actualmodel14release;
4equalEFIbuilds+normal/emptyactualsupervisorQEMU+world17ASAN120ticks/16camera.
598inputclosure and116compiledfixtures exactlocalhashesverified. Rehashes
retainedowner-signedfirmwarecontainer andIE6 plusmain/helperplanpointerbinding
beforequery; nohardcodedop. ProductionteardownobservedonlyAFTERgenuineall
map/PCI/DMA/IRQ/link/wake/pinrelease (notintermediatecleanup). ReadonlyQHTT
statusUUID2e/2f handles29..31; QHTX6rawslots as30pagesUUID80..9d handles32..92.
Allrawframing/trailers retained. NoRF/dataplanereadyclaim. Counter55UNSIGNED
andNOTsent; prerequisite54result+ALL54rawexportsstored+rootadmission.

Reviewedsecure-provision-plan-v1 draft:38476syntheticMonocypher4.0.3 ASAN/COFF
primitive+independentHKDForaclechecks, source/logbindingsverified; NOTcomplete
authenticatedkeyexchange/provisioning. NoDellpinnedprivateidentity orintegrated
EFI_RNG pathfoundinproject; nohardwarepresenceconclusion. Physicalfullrecipient
fingerprint/QR/sessioncomparison mandatorybeforesecretloadifnopinnedidentity.
OwnerEd25519signatureauthenticatesMaconthischannel, notsubstitutedDellkey.
No realkey/credentialread/export orsigning. IndependentNEWefi-rng-port-v1
preparesboundedofficialprotocol/provider/length/failure/zeroizetests; diagnostic
exportsNEVERrandomsamples. NEWprovisioning-review-v1 checksmatureAKE reuse
(e.g.Noise-C) versuscustomcomposition, no actualprovisioning/hardware.

### 2026-10-07: physical54 real scan responses; dispatch/STOP fault isolated

Sole52976 finished; no liveBTcontroller. ALL40rawpagestwice+three stableQSCN
savedbyv1; rootdecodedwithv2offline andvalidatedALL12packetpublicsignatures/
body/layout/wholeFWdigest/finalreceipt. Exactraw/status/receipt/BOOT/hashes
archived scan-result-v1/evidence/2026-10-07. Actualall14ownersreleased,life4
noerror,READY/TXseen1; hardware_trial_pending clearedONLYaftercombinedproof.
World17unchanged. NoSSID/association/IP/WAN.

QSCNnativeFAULT5/error6,coorFAULT5/error15,stage5,all5commands actualDMAcomplete
(includingSTART_SCAN/STOP), pendingSCAN_WAIT7/STARTEDnotprocessed,STOPFAULT7/
terminal0/TXcomplete1. Archive2full:completion1debug0x1d011,2event0x1d019;
dispatch2stillownedcomp3event0x16006 andcomp4debug0x1d011. RX2holds genuine
matchingSTARTEDcomp9 andFOREIGNcomp10. Bufferblockage behindretainedunknowns
causedownedSTOPdeadlinefailure; no proofolddecoderreachedtheseSCANevents.

ExactSTARTEDpayload36bytes(tag36/value28) hex
013000001c00240001000000060000000000000008a0000007a000000000000000000000
FOREIGNpayload36bytes hex
013000001c00240008000000060000006c09000008a0000007a000000000000000000000
IDsrequesta008/scana007/VDEV0 andFOREIGN2412matchsubmittedtrial. Preserve
reason6opaqueonSTARTED/FOREIGN; nevercallitcompletionreasonorclaimSSID.
PinnedLinuxpolicyminsizeofwmi_scan_event24/pull6-wordprefix, STARTED/FOREIGN
handlers ignorereason. Existingexact24/reason<=4/STARTEDreason0 code would
rejectthesevalidnonterminalextendedevents independentlyofqueueblockage.

Immediatepriority NEWscan-native-profile-v2 GEN55 + scan-event-v2: pinned
boundedminimum-prefixcodec, nonterminalreasonopaque, terminalnonzeroconservative
failure; generatedprivateoldmodules untouched. Archive16 forobservedbootdebug
burst, no packetdiscard; truefullcapacitySTOP/deadline, ALL22slots110pages
export. Physical54rawregression+actualnative/ASAN/COFF/EFI/QEMU/world/source
proofinprogressonYukabox. HTT55offlinecandidate remainsFROZEN/UNSIGNED/DEFERRED,
notreservationofphysicalcounter; derivefutureHTT56onlyafternewscan55result.
Rootnext55gate requires exact54failure/owner/rawproof + newcompleteproof before
localkey/signature. Newobserver-v3 GEN55/110pages2x budget600s (actual54capture
175.23s) preparesstrictreadonlycollector; no hardware/privatekeysbyagents.

### 2026-10-07: observer55 ready; RNG and mature provisioning review archived

Newscan-observer-v3 GEN55/22slots110pagestwice:2855staticnegative/ownercases
+MacObjCpreflight, exactsource/proofhashesverified. Usesactual55candidate and
engine.last_release_report absolutepath, no guessedfuturepayload/session.
Finite600sreader/620swrapper+90sstalled-progress; raw/partialpersistedBEFORE
decode, staleaccepteddecodedinvalidated. Final55candidateproofstillrequired.
No actual55radio byagent. Frozenv1/v2unchanged.

RootRNGreviewfoundv1outputaliasintosession/review couldcorruptauthstate orplace
random bytesinpublicmetadata. NEWefi-rng-port-v2 rejectsrangeoverflow/overlaps
BEFOREcallback/statechange;1742ASAN/UBSAN+COFF mockedABIcases onYukabox passed,
source/logverified. V1mock557proof retainedasbaselineNOTnative-approved.
Arithmeticguards aren'tarbitraryEFIaddress validity, provideridentityapproval
orentropy-quality proof. No physicalRNGcalls/randomsamples/realkeys exported.

Reviewedprovisioning-review-v1:10743ASAN/UBSAN actualpinnedNoise-C checks and
exactCacophonyNKvectors, source/logbindingsverified. NKfitsphysicallypinned
RAMDellreceiver butdoesn'tauthenticateownerMac. OwnerordinaryEd25519AUTH
boundtofinalhandshakehash/target/epoch/prologue mustbeinsidepostSplittransport
withencryptedDellACK BEFOREcredentialread. No AUTHimplementation/physical
fingerprint/RNG/fullEFI proof orprovisioning. Defaultbackend hosttext116677
+data2648 exceedsnative54headroomproxy74752; NOTapprovedfit.
NEWnoise-monocypher-backend-v1 preparersuseexistingreviewedcrypto+unedited
matureNoisehandshakestatemachine, exactIETFnonce/ChaChaPoly notXChaCha, no
realkeys/RF/device/signing. Fullprotocol/nativefit/trustgates remainrequired.

Scanv2GEN55 newactualnative19caseproofpassed incl physical54blocker replay,
STARTED/FOREIGNvalue28/nonterminalreason6/opaqueextensions, wrongSSID→target
andtargetduplicate→terminal, archive16/fullSTOP. FullrepeatEFI/QEMU/world/source
proofstillinprogress. Donotsignuntilfinalfreeze/rootnegativeadmission/fresh54
release/raw proof. HTT55offline remainsdeferredunchanged.

### 2026-10-07: fixed passive scan55 admitted and signed physical trial started

FrozenNEWscan-native-profile-v2 GEN55 EFI187392 SHA
cc8d7fec39a812273c1af5d52711fe6dc281b48873925aec2136cf3cb8533297.
19actualnativePCI/CE/DMA modelcases incl exact54debugblocker+real28/reason6
SCANreplay, archive16/fullSTOP, wrongSSID→target/duplicate→terminal. Newshared
scan-event-v2 minimum24prefix/nonterminalopaquereason followspinnedLinux;
8967ASAN/COFFcodecchecks. FourequalfullEFI+normal/EMPTYsupervisorQEMU+world17
ASAN120ticks/16camera,642sourceclosure/138compiledfixtures/hashbindingsPASS.
Signedregdb/exact13GE×unchanged108 headerbindingrechecked; unchangedproposal
RFfalse. Allold54/HTT55sources/frozenproofs untouched.

RootNEWscan-admission-v2 gates:17candidatecorruptions+38offlinecopied-fixture
negatives (TOTAL55) reject beforekey/radio. ActualfreshsequentialBOOT54 +
newv2collectorALL40pagestwice confirmsunchangedexactretained54raw/QSCN and
actualall14/lifecycle/READYrelease; copiedfixtures NOTusedforadmission.
Full54assetpublicsignatures/digest/target/layout+failedtrialrawproof bound.
Owner/target/nextgenerationcheckedbeforelocalkeyaccess; no realcredentials.

SignedONCEsaved pci-native-ehv85hvp. Solecontroller61367/caffeinate61368:
scan-admission-v2/continue55.py, runs/control/continue55.log/controller55.json.
Native55 NOTyetAPPLIED atrecord. Finiteexactnative resume -> NEWfirmware55
session -> exactBOOTallownerobservation -> scan-observer-v3/collect.py--read.
Collector3 actualGEN55/22slots/110pagesTWICE,600/620sbound; retainallrawbefore
futureunload. Controller's missingcollectorerrorstillmentions40 (legacytext
only); actualcollectorcontract110. NootherBLEowner/resign/replay54.

ImmediategoalphysicalmatchingSSID andgenuineSTARTED/terminal/raw/ownerproof;
DMAcomplete alone notsuccess. NextstageHTT55offline remainsdeferred; counter55
is NOWassignedthisactualscantrial, derivefutureHTT56fromfrozensourcewithnew
proof/policy onlyafterall55rawsaved. Noassociation/IP/WANclaimed.

### 2026-10-07: native55 applied; compact crypto reference reviewed

Exact55 APPLIED receipt archived scan-admission-v2/evidence/2026-10-07/
native55-applied. Solecontroller61367 live; NEWfirmware55 savedsession
firmware-ram-g4w7ruqs, firstfullchunk andsecondprefix57600 at heartbeat.
Preserve savedbytes/checkpoints; nosecondBTowner/resign/replay54.
Physicalfixedscan/SSID/IPresultnotyetavailable.

Reviewednoise-monocypher-backend-v1 source/logbindings,3,672,371ASAN/UBSAN
adapterdifferentialchecks+10743compactchecks onYukabox, exactpublishedNKvectors.
UnmodifiedmatureNoisehandshake, existingMonocypherX25519+exactChaChaPolyIETF
nonce(4zero||LE64), freshcontext/rekeydiscard+wipe. Hosttext45575/data2640
versusreference116677; NOTCOFF/fullEFI/nativefit/entropy/AUTHapproval.
LegacyNoise permitsnull/low-orderzeroDH; rootreviewcaught mismatch withour
fail-closedprovisioningboundary. NEWbackend-v2 hardensinvalidinput only,
nulls_allowed0+zeroSharedKeywipe/error, requireactualhandshakeFAILED/noSplit.
Keepvalidvectorsunchanged andoldreferenceproof frozen. Genericupstreammix_dh
mixeswipedzerotransientlyevenonerror; doNOTclaimnointernalKDF, prohibitfailed
stateuse. Realcredentials/keys/signatures/device/provisioning untouched.
Upstreamconstructorerror mayleavenonnullalreadyfreedoutput: nativewrapper
MUSTnullerroroutput, neverfree/dereferenceit. No liveprotectedchannel yet.

### 2026-10-07: strict Noise backend2 proof reviewed (no native admission)

Newnoise-monocypher-backend-v2 preservesv1source/proof. Rootverified source/log
bindings for3,672,981ASAN/UBSAN checks onYukabox: validpublishedNKvectors still
byteidentical, allzero/low-orderDH rejected+wiped, nulls_allowed0 preventscore
erroroverride. Actualfailedhandshake output0/FAILED, Splitforbidden. Upstream
transientmix_key-on-wipedzero stilloccursbeforeerror; no claimabsenceofKDF.
NoCOFF/fullEFI/allocator/actualRNG/ownerAUTH/physicalfingerprint/provisioning
claim; no realkeys/credentials/signatures loaded.

NextNEWnoise-native-port-v1 HOST-ONLY actualunchangedlibrary/compactbackend
withboundedownedarena, constructorerrornulling/no doublefree, cleanupwiping/
quarantine andborrowedreviewedrng-port-v2; explicitMS-x64COFF portability.
NoUnixrandomfallback oractualdevice/providerapproval. No counter/candidate/
hardware/state/privatekeys. Solephysical55controller61367 unaffected.

### 2026-10-07: exact55 firmware transfer resumed after Bluetooth timeout

Physical receipts confirmed 5/12 chunks (bitmap31). Sixth saved packet reached
49920/65760 bytes, then connection timed out. Controller61367 exited after
bounded no-progress attempts. No live sender/controller remained before restart.
Root corrected only host controller peer-progress filter typo 310A55 -> actual
310A54; signed native payload and asset packets remain unchanged. Sole resumed
controller63271, metadata controller55.json, same append-only continue55.log,
same pci-native-ehv85hvp and firmware-ram-g4w7ruqs. No signing/key/credential
access, reboot or world change. Radio scan/SSID/IP remain unconfirmed.

### 2026-10-07: transfer6/12 confirmed; offline portability review

Sole55 controller63271 now confirms6/12 chunks bitmap63. No scan/IP evidence yet.
Root verified noise-native-port-v1 source/log/report hashes:277103 ASAN/UBSAN
checks and19 actual COFF objects on Yukabox, borrowed mocked RNG, no credentials.
Unresolved __chkstk and full EFI/actual RNG/AUTH/physical pin remain unapproved.
Root found rng_bind can replace previous retained RNG pool when arena live0;
BASELINE NOT ADMITTED. Agent preparing NEWport-v2 regression/fix plus runtime
integration; old v1 preserved. Parallel NEWoffline HTT56 profile preparation
from frozen HTT55; no physical admission until all55raw/release proof saved.

### 2026-10-07: physical55 full firmware staging; offline next components

Exact55 firmware-ram-g4w7ruqs full12 accepted bitmap4095 ready1, container
RAM report EXACT-FULL-FIRMWARE-CONTAINER-IN-RAM. Public receipts archived
scan-admission-v2/evidence/2026-10-07/firmware55-full-staging. Solecontroller63271
now observation only. Last BOOT native_stage18/board_phase2/14DMA users;
not release, INIT/SSID/IP or firmware execution proof. No other BLE operations.

Root verified new port-v2 source/log bindings and retained RNG rebind fix:
277113 ASAN/mock ABI checks+19COFF. Runtime-v1 bindings verified: genuine pinned
LLVM chkstk probe,65436 guarded stack checks+233521 memory shim checks; isolated
public-vector EFI66048 linked only, NOT executed or combined Rabbit budget.
Actual native RNG/TargetPack/stack/ownerAUTH/physical pin remain unapproved.

HTT profile-v2 GEN56 frozen offline168448 SHA
ede1f957d94dc85280659474982874112c9c39c10f3012f900cc7ae15ca95df5;
root reran read-only admission_gate validating600sources/compiled fixture/proof
bindings. Native24,4equalEFI,2QEMU/world17/50gate checks pass. NEVER admitted/
signed/device-sent. Must capture55 all110pages2x+genuineall14release first.

Owner-auth-frame-v1 reviewed1538actualnegative/KAT+syntheticACK cases; positive
signedAUTH chain explicitly unproved. NEWv2 uses only published RFC8032 dummy
seed for offline test signing+actualNoise handshake/Split positiveproof;
no real key/credential/device/RNG/signing access or provisioning approval.

### 2026-10-07: bounded diagnostic read120s with stage logging

User asked whether timeout should expand. New read_boot55_v2.m copied from
frozen observer with120s overall bound and stage logs: powered-on/cached-peer
connect/service/characteristic/envelope. Exactknownpeer160byte/read-only gates
unchanged; compiled Mac ObjC/preflight, no manager started during preparation.
NEWread_boot55_v2.py130s wrapper/continue55_v2.py preserve full55asset session.
Current63271 read active; NOT interrupted or overlapped. Sole non-radio waiter
77697 resume_observer_v2.py waits bounded900s for previous controller exit,
checks controller identity/no prior read, then records newsolePID in
controller55.json and resumes observation only (12 assets alreadyaccepted).
Waiter metadata/log runs/control/resume-observer-v2.*. No signing/newfirmware,
credentials/reboot/worldchange. Timeoutcause still unknown; last successful
BOOT completed258,phase17; repeated disconnect/60stimeout. Stage2 diagnosis
will distinguish connection wait from slow service/read;120s not connectionproof.

### 2026-10-07:120s proves connection-stage stall; fresh scan prepared

Observer-v2 activated solePID78295 after63271 exited; repeated120s timeouts
stage=connect-cached-peer, BEFOREservice/envelope. Longerread not sufficient.
NEWread_boot55_v3.m/py scans fresh advertisements(no cachedconnect), knownpeer
only allowedconnection, logs genericadvertisement arrival+knownRSSI,120sbound,
160byteexact/read-onlyvalidation. Compiled/preflight only sofar; MUSTwait78295
andallchildren exit beforev3read. No signing/firmwarereplay/hardwarechange.

Root reviewed owner-auth-frame-v2 hashes/log2650ASAN/COFF actualpublishedNK/
Split/context+realEd25519 PUBLICdummyAUTH→encryptedACK. Frozenadapteridentical
v1. Realphysicalpin/RNG/keys/nativecredentials remain unapproved.

Runtime-efi-proof-v1 rootsource/logbindingschecked: genuineNK/wipe/mockRNG/
stackshim QEMUpositiveexit33 andMACtampernegativeexit35. WholeRabbitoffline
composition220160file fits BUT mapped4206592>immutable4194304 by12288;
REJECTED/noadmission. Requires reviewed callerownedarena placement, notlimit
bypass. Oldnative54 reproduced byteexact; no countersigning/devicechanges.

### 2026-10-07: physical55 fresh scan failed; user screen observation needed

Previous observer-v2 controller78295 completed bounded retries andexited.
Root sequential freshv3read afterexit/childcheck: Macpoweredon, scanreceiving
advertisements, knownDell neverdiscovered before120sdeadline. No cachedconnect,
no write/signing/replay. Exactlogs/meta/lastsuccessfulBOOT archived
scan-admission-v2/evidence/2026-10-07/fresh-scan55-timeout. NOTproofDellcrash,
rangeproblem ordrivercause. No activeBLEcontroller/read now; full55assets and
hardware_trial_pending retained unchanged. LastsuccessfulBOOT completed258/
phase17/all14DMAowned, no releaseproof, neverunload/sign56.
Requireduseraction requested: observewhethercityvisible/cattailmoving, noreboot.
Parallelsoftwarememoryowner preparation continues independently; hardware
continuation requires restoreddiscovery/physicalobservation, nottimeoutincrease.

### 2026-10-07: user confirms live city; no Rabbit advertisement at any UUID

Human explicitly confirmscityvisible andcattailmoving. Rootsequential repeated
freshv3knownpeer120s timedout, otheradvertisementsseen. Then passiveexisting
probe20s(allUUID,Rabbitservicefilter locally) reports149advertisements,
Macpoweredon5/authorization3, connectedRabbit0/cacheddisconnected0,
RabbitcandidatesEMPTY. No connection/write frompassiveprobe, no activeBLEjob.
Exactlogs+userobservation archivedlive-city-no-rabbit-advertisement.
RulesoutonlyknownUUIDcache explanation forthis20sscan; NOTproofchipcrash,
driverfault/range/coexistencecause. Full55asset/pending unchanged; cannotadmit56.
UseraskedtoverifyMac0.5–1m fromDell (notjustsamehouse/7m), no reboot/USBchange.
Nextafterproximityanswer: solepassive/freshread; ifstillabsent need preserve
blockedhardwarediagnostics andexplicit recoverydecision, no forcedrestart.

### 2026-10-07: close-range Rabbit absent; recovery preparation only

User movedMacnearrequested0.5–1m. Solepassive20sprobe133advertisements,
Rabbitcandidates0/connected0, no connections/writes. Archivedclose-range-no-rabbit.
City/tail liveuserconfirmation stands; no proofWiFiprogress sinceBOOT258.
No activecontroller, preservefull55signedassets/native/state/pending/raws.
Cannot repair receiver overunavailableBLE. Root assigned NEWreboot-retirement55-v1
OFFLINE preparation ONLY: exactpublicsignatures/642closure/world17+explicit
ownerreboot AND freshactualEMPTY0 beforeany retirement; no modelsasphysical,
no state/privatekeys/radio/reboot. Prepareconcretereviewablecityrecoveryplan,
nextcounter56conditional; offlineHTT56 isdeferred, neverautoconsume/replay.
UserhasNOTauthorizedrebootexception. Mustreviewrecoveryroute beforeasking.
Productionmemoryowner softwarework independentlycontinues.

### 2026-10-07: root archived55 bindings; recovery execution preparation

Root exactstate_lock snapshot root-before-recovery/before-state.json copied;
public_bundle +archived_state actual55 verificationPASS: real55signature/
12assets/container/642sources/world17/pathbinding. root-preflight recordsSHA.
LatestBOOT/discovery included; nolive statewrite/retirement/rebootauthority.
Recovery55offline sources/evidence hashes rootverified; plaincity2equalEFI/
ASAN/world17+normalEMPTYQEMU pass. Copiedexactofflineproof committedseparately.
Actual executable lockedretirement/recoveryadmission adapter NEWroot-v1 still
inpreparation; don'trequestrebootuntilreview. Needsactualhumanexception+fresh
EMPTY0; cannotinventownerrelease, raw55lostmarkedunknown.

Productionmemory-plan-v1 bindingsreviewed: genuineOVMF pool33407rawbytes aligned16,
checkedderivative detach beforewipe/free;534736ASANpoolowner+8failureprocesses,
3QEMU outcomes. File222208/mapped4177920 fitimmutablecaps, but testrootuncalled,
strongrealRNG/physicalpin/nativecoordinator approval absent. NoDellwrite/signing.

### 2026-10-07:0742 heartbeat state unchanged; executable route review

State SHA89711c57e22e8771a10d5adee7b323f501fba9b4406c89737babcac5e8c6916e
still exactarchived55/full12pending. Solepassive20s read105otheradverts,
Rabbitcandidates0/no connections/writes; no livecontroller. No newphysicalproof.
Rootreview NEWreboot-recovery55-root-v1 writer/guardedoriginalprepare:
requires exactstate/authorization/freshEMPTY; rootrequested nestedarchive dirs
fsync bottom-up +failuretest BEFOREatomicstatecommit, notjustfile/topdirfsync.
Agentcopied-state/mocktests stillinprogress; nosigning/retirement/rebootallowed.
Guardedprepare mustrecheck state/journal/counter55/source/freshness insideoriginal
lock immediately beforeload_private. Don'taskrebootuntilfinalrootreviewPASS.

### 2026-10-07: executable recovery ROOTreviewPASS; owner exception pending

FinalNEWreboot-recovery55-root-v1 routeSHA65e50887ef9f7b8ff36700cdc9bd413607fde631c8b1d1080e3e1201ed26d0b8.
Root verifiedallsource/evidence/hostlog hashes andactualstate stillSHA89711c57...
12copied-state testsPASS Yukabox; realoriginalprepare reaches mockedraising key
boundary only, rejects counter/freshness/source/journal changes beforekey under
originallock. Nestedarchive dirs+parent fsync BEFOREatomicstatecommit tested;
failurespreserveoldpending. ROOTreview/source/durability proof committed.
No actualreboot/retirement/signing/keys/BLE. Ownerpermissionmustexception prior
no-rebootconstraint. Concreteplan: authorizecontrolledreboot, humanconfirmactual
reboot, genuinefreshEMPTY0, archiveandretireexact55lostRAM(noall14/rawproof),
guardedplaincity56/world18signonce/restore receipts+physicalcitytail. FullRAM
firmware mustredeliver later; Bluetoothrecoverynotguaranteedbyhostproof.
OfflineHTT56unconsumed; ifcity56used futureHTTneedsnewcounter. Waitowneranswer.

### 2026-10-07: owner authorized controlled manual reboot; awaiting confirmation

Human explicitly said“разрешаю, но разве это не я должен делать??”after root
reviewPASS/permissionquestion. Rootrecordedauthorization boundexactbefore-state
SHA89711c57e22e8771a10d5adee7b323f501fba9b4406c89737babcac5e8c6916e,
actioncontrolled-dell-reboot-for-native55-recovery. Savedruns/owner-recovery/
authorization.json andevidencecopy; timestamp/hash authenticuserreference.
Exception permits ONLYthiscontrolledrecovery, notfutureautomaticreboots.
Rootexplainedphysicalreset mustbedonebyuser(no remote power capability), then
human“перезагрузил”confirmation needed BEFOREactualreboot observation/EMPTY.
0812heartbeat exactstateunchanged/noactiveBLE/noobservationyet. Permission
isNOTrebootproof; no pendingretirement/signature/transmission alloweduntil
confirmation+genuinefreshknownpeerEMPTY0. DoNOTrepeatpermissionquestion.
Nextuserrebootconfirmation: recordactualtime, freshquery/log, strictrootroute
retire/admit/guardedprepare56 thenoriginalrestore exactsavedpackets.

### 2026-10-07: owner reboot actual; Bluetooth restored; city56/world18 applied

Humanconfirmed“перезагрузил”. Rootactualknownpeerzero-write freshEMPTYcounter0
receipt/log boundauthorization/reboottimestamp. Reviewedrootroute actualretire
archives55native/full12signedassets/world17/BOOT/discovery beforeatomicpending
retirement. Raw55unexportedlost, NOall14release/scan-successclaimed. Original
signed55reports/payload/packets unchanged; no oldfirmwarereplay.

Rootread-onlyadmissionPASS then guardedprepare56localowner SIGNONCE exact
native56-city-recovery-plan, usingYukaboxplaincity199closure/gates. Original
restore freshEMPTYgate +pacedstage47904/commit reconnect => genuineexactAPPLIED56;
restoredworld2128/commit=>exactAPPLIED18. reportAPPLIED engine_done/world_done true.
Semanticfa5a3250633f2bbbd288d947be567c2c5db8e3395033da99b765edf0a0f5cc74
unchanged, worldpackagef306120fdd548b6d4cc1d3915a13ae8cbe7848b162caa78528add353b9cb3f32.
State native56/world18 allpendingnull. Allrealreceipts/savedplans archived
root-v1/evidence/2026-10-07/actual-city56-world18. No activeBLEcontroller now.
Humanphysicalcity/tailconfirmation requested; notinferredfromreceipts.

Currentengineplaincity56 hasNO WiFiprobe; prior55firmwareRAMlost. HTT56offline
nowobsoletecounter iffuturedeployment; derive newGEN57 ONLYnewproof/source.
Beforeblindfulltrial rootparallel link-loss55-review-v1 investigates specific
BLElossduringphase17mainFWloading withlivecity; causeunproved. Noadditional
rebootauthority, USB/bootstrap untouched, credentials/privatekeyneverexported.

### 2026-10-07: restored city visible; next bounded boot-prefix diagnosis

Human“видны, делай давай дальше пожалуйста!”confirmsrestoredcity/catvisible;
motionnotseparatelystated. Rootsingleknownpeerzero-write freshquery confirms
exactworld18APPLIED/f306... samecurrentsession RSSI-65; baselinearchive saved
actual-city56-world18/stable-baseline-read. Current56/world18 allpendingnull.

Source triage(last55BOOT17/completed258/offset19592): phase17 is BMI_LZ_DATA
MAINFWstream command14, beforeHTC/INIT/scan. SampleSTALE, no finalstopinferred.
Boot/transport/native code55identical54; scan/archive16 notexecuteduntilACTIVE.
Potential110GATTchars vs54 40 hostdiscovery pressure remains hypothesis, notcause.
NEWboot-prefix57-native-v1 preparing bounded MAINprefix/noRF/INIT/scan +minimal
GATT +visibleBLE/USB/CE/frame/offset telemetry andcheckedall14stop; fullsigned
firmwarecontainer remainsrequired, no unsignedprefixshortcut. No57sign/counter/
actualdeviceoperations yet. Need actualmodels/source/fullEFI/QEMU/world18gates
beforeadmission; safechipnextinit afterpartialstop mustbeprovenorreportedgap.

### 2026-10-07: priority prefix57 review prevents premature or unsafe test

Rootverified link-loss55review exactphysicalevidence hashes; causeunproved.
Nextprefix57 offlinepreparation uses600sboundedbootdeadline ratherthan45s,
becauseactual55 reachedMAIN onlyafterminutes. RoutineHCI nowlast12ring+
explicitoverwrites andprotected4criticalrecords; no earlyordinary-eventstop.
Rootcaught intermediate overlay240/status244 stackoverflow; preparercorrected
allgeneratedstatus/GATT/overlay contract240/58words, needsactualframe/status
ASANcanary tests beforefreeze. Rootalso requestedactualproductionmodel proves
no134thMAINpublish/BMI_DONE/HTC (completion+nextpublishsamepoll couldbypassouter
pending0 guard). Prefixlimit32984bytes/133MAINchunks; hostall14release isNOT
chipROM/LZready. Nextreuse requiresfreshcheckedchipreset/ROM, no Dellreboot
permission implied. New57 notsigned/sent/reserved. Current56/world18 stable.

### 2026-10-07: prefix57 preflight/reader preparation in parallel

Userexplicitlyauthorizes finishstop/overlaychecks/build/send. Newscope still
unsigned/unfrozen, actualnative/driver/overlaymodels inprogress. Rootreview
uint32 prefix_clock_ms()*1000 overflow71.58min before uint64assignment; requested
cast-before-multiply andactualdriver boundary+rollback tests. Rootverified
BluetoothSIG Core5.4 ATT3.2.9 maxattribute512:
https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Core-54/out/en/host/attribute-protocol--att-.html
Single4672rawchar unacceptable; requested10boundedread-onlypages9×512+64,
one240status, no110charwholearchive. Newprefix57-observer-v1 preparer waits
frozencontract, zeroactualBLE. Newprefix57-admission-v1 purepreflight validates
candidate/source/fullEFI/models andprioractual56/world18/55retirement public
proofs; newworld18freshquery≤300 requiredbeforelocalkey, oldEMPTY onlyhistorical
atretirement chronology. Rootusesuntouchednative_route.prepare/deliver with
scopedgates andexplicit57owner/target/gen checks. Do notsignuntilfreeze/model/
QEMU/currentworld18/admission rootreviewPASS. Current56/world18 unchanged.

### 2026-10-07: prefix57 ordinary native8 modelPASS; fullproof underway

persistent_radio agentturnstopped byautomaticpossiblecyberriskflag; no retry/
rephrasingblockedagent. Rootcontinued ordinaryauthorizedoffline driver
compilation onYukabox. Missingpci_identity.c testlinkinput fixedunfrozen
verify_native.py; overlaystrictindentationwarningfixedbraces, native8 actual
PCI/CE/USB/overlay ASAN/COFF rerunPASS. Rootverified hostlog+allcompiledfixture
source hashes; archivedBASELINE only, notfinalcandidate/fullsource admission.

prove_prefix.py producer sourcechanged afterinitialsnapshot; strictproducer
correctlyrejectedstalenative sourcehash. Scan_pipeline nowreruns verifier to
bindfinalproducer then4EFI/fullQEMU/currentworld18/sourcecaps proof, onlyits
file/outputdir ownership. Sourceworld18.json copiedpublic: canonicalfa5,
decodedpacketdropsnames(hashdifferent). Signaturecreator03a107...531b8,
NOTnativeowner622b. Frozenobserver-v1 worldauthoritywrong; NEWv2 beforeactual
read, no silentfrozenedits. Native56RRT stillowner622b. No57sign/BLE/reservation.

### 2026-10-07: frozenprefix57 admitted/signONCE; sequential physical launch

Finalprefix57 reportc362eb73bdfa96cef85962db9d625d6aa9664476f8b47b44fb60756f6f5099d1,
EFI150528 SHA9c63e6622c10190a8a17de2ff01ee03f72de95e93fd7326ca4da6e2c429be161,
mapped4083712;3equalEFI+actualnormal/EMPTYsupervisorQEMU EXACTworld18+ASAN.
417sources/162generated/native8 actualdriverPCI/CE/USB/frame/status/clock/ATT
models, no134thMAIN/BMI_DONE/HTC; rootcandidate gateactual269casesPASS.
Rootnewknownpeeractualworld18zero-writequeryconfirmedf306/current56, genuine
freshobservation +unchangedstate/owner/target/source/gates underlock beforekey.
LocalSIGNONCE saved pci-native-bq9nq_ik; native57notyetAPPLIED atrecord.
Firstpacedstage300stimeout after77900; genuinequery80300/150816 retained,
secondresumesSAMEsignedsession to88500+; no resign or discard.

SoleforegroundnativePID4153 execsession73398; continuationPID4424/caffeinate
waitsfor4153exit beforeANYBLE, root-route-v1/continue57.py andruns/control/
controller57.json/continue57.log. Itresumesexactnativebounded6, thenfreshQPD18
initialall14setup/ROM/teardown gate andnewgen57fullfirmware EXACT12packets
signedONCE byassetprepare. No actualfirmwaresession yet atrecord; statepriority.
Controllerassetresume30bound+samepacketfloor(nopeer typo), stop2no-progress,
no otherBLEowner. Afterall12 accepted wait660squiet(30ssteps) toavoidnormal
connect/disconnect fillingprotectedHCI4 duringboot, thenobserver-v2all10pages2x/
3status underoperationlock. ContextschemaPREFIX57-PUBLIC-CONTEXT-2 corrected
beforewaitingcontroller launch; oldwaitingno-radio4327replaced, nochildoverlap.

Native modelprintf OWNERS=get(240) is aPCIconfigword, NOTactualowner count;
rootreviewreliesactual14allocation/free/unmap assertions+240statusall14release,
notthatmislabel. Frozen reportradio_backend MOCKUSBONLY describesmodel backend;
productioncompile has noRABBIT_PREFIX_DRIVER_MODEL flag, realUEFIUSB remains.
Newobserver-v2 propercreator03a1+sourceJSON, frozenv1 retainedNOTforactualread.
Raw55lost acknowledged, no old55firmwarereplay; partialchipstate after57stop
NOTROM-ready proof, nextreuse requiresfreshcheckedchipreset. No additional
Dellrebootauthority. World18 preserved, credentials/privatekeyneverexported.

### 2026-10-07: physicalnative57 applied; soleasset controller active

Foregroundnative4153 finished exactAPPLIED57 receipt; stateworld18unchanged,
native_pendingnull. Continuation4424 nowSOLEactiveBTowner (caffeinate4425;
actualmetadata authoritative). FreshinitialQPD18 realsetup/ROM/all14closed gate
passed. NEWfirmware57session firmware-ram-efn8f6wx SIGNEDONCE/all12saved packets,
firstdeliveryactive. Preserveexactsession, no old55 replay, no secondcontroller.
Native57APPLIED/initialQPD18/publiclogs/preparedasset report archivedroot-route-v1/
evidence/2026-10-07/applied57. Fullfirmwareaccept/bootprefix/USBHCIdiag NOTyet
confirmed. Tinyoverlayexpectedonphysicalcity; notclaimedvisuallyconfirmed.
Controller quiet660safterall12beforeobserver2read underlock; notrouter/IPproof.

### 2026-10-07 13:16 UTC: native57 asset transfer stopped; inspect physical screen

Saved native57/world18 remain unchanged, pendingfirmware-ram-efn8f6wx preserved.
Ten of12 full chunks accepted (bitmap1023). Chunk10 (eleventh) reached4320 bytes
before connection timeout; queries44..48 returned invalidhandle. Controllers
4424 and9222 exited. Passive knownpeer advertisement remains visible onMac.
DO NOT restart continue57 or sign/replay/retire pending packets automatically.
Current controller57.json status STOPPED-PHYSICAL-OBSERVATION-REQUIRED and
restart_allowed=false. Old native51 automation snapshot is not current state.

New host-only gatt-read-diagnostic-v1 under existing state.lock, no writes/key,
proved error specifically on asset status READ callback: CBATTErrorDomain/code1,
ATT Invalid Handle; service/characteristic discovery callbacks succeeded. Ordinary
file status exact60 bytes RFS1+allzero (IDLE/session/length/counter/digest), and
targeted prefix57 service40 discovery returned absent. Cached all-service list
is NOT physical proof of an active driver. Receiver reset/lost native services
is possible, exact cause not proved; no same-boot RAM resume currently admitted.
Do not claim reboot, firmware boot start, prefix teardown or Wi-Fi/IP success.

Exact phase1/phase2 source, callback logs, last accepted chunk, failed attempts,
passive advertisement capture, controller logs, public asset report and unchanged
state hash manifest saved at experiments/native-wifi-qca9377-gatt-read-diagnostic-v1/
evidence/2026-10-07/physical57-handle-failure/bindings.json. Needed user action:
photo of current Dell screen, including top-left diagnostic area; preserve power,
USB and boot. No additional reboot permission exists. Then establish fresh
runtime/boot context before deciding resume or separately reviewed recovery.

### 2026-10-07: owner startup-screen photo; city restored as58/world19

Owner supplied photo419b002f: smallblue rectangle+BLEconsole, no city/cat or
prefix57overlay. Fresh knownpeer locked read again exactEMPTY RFS1. Reset/context
loss observed; manual owner reboot NOT confirmed, cause NOT established. No
reboot command or USB/bootstrap write performed. New observed-reset57-recovery-v1
route/restore derivative reviewed and frozen,8copiedstate testsPASS. Original
reboot_recovery.prepare unchanged; no fake dell-rebooted/human authorization.

Before retiring obsoletehardwarepending57, route verified actualAPPLIED57 and
all12 saved firmware signatures plus lastaccepted10/bitmap1023/ready0/world18,
durably archived all sessions/packets/logs/photo/state/journal under ignored
runs/actual-recovery58/retirement, then cleared ONLYhardwarepending andappended
audit;57/18 counters unchanged untilactualnewreceipts. Originalsigned57files
unchanged; do notresumecontinue57 or resenditsRAMpacketsinto bootstrap.

Yukabox plain-city58-ble-reset-recovery preflight:2equalEFI, sameprevious56payload
0fb9fa6c1c307e8ca0fe51b4b29e3cd815c3e2881f9c1ceba6d01d80ce52b4ce,
ASAN/UBSAN120ticks/16camera/roofcat timing,normal+EMPTYactualsupervisorQEMU,
199source inputs. Initialdefault(noBLErecovery)preflight was NOTapproved;
actualsigned58 uses --ble-recovery and identicalproven56payload.
World19package89ffda340552cf33a4c732597388f4fea358d47b0850f7720bdce51a2b3968b7;
semanticfa5a3250633f2bbbd288d947be567c2c5db8e3395033da99b765edf0a0f5cc74 unchanged.
Fresh actualEMPTY+photo/archive/state/source guards underexistinglock beforekey.
SIGNED ONCE native58 plan runs/text-world/native58-observed-bootstrap-city-plan.
Soleforegroundcontroller completed EXACTAPPLIED58 thenEXACTAPPLIEDworld19;
allpending/null, noactiveBTcontroller. Publicexactlogs/reports/manifest at
observed-reset57-recovery-v1/evidence/2026-10-07/physical58-world19/bindings.json.
Visualcity/tail motion still requiresowner confirmation; Wi-Fi/IP notconfirmed.

Read-only sourceaudit identified reachable resident HCIdeadline same-opcode
generation bug: coalesced COMPLETE200a/connect/disconnect mayissueNEW200a before
resident sees pending0, retainingprevious10sdeadline. Physical57 cause unproved.
CriticalHCIoverflow before assetready is ruledout (capture/request ignoresphase0).
Separate scan_pipeline preparation of minimaldriver-onlydefer/model was stopped
byautomaticpossiblecybersecurityriskflag; no rephrasedretry, no producedcandidate
admitted/signed/deployed. Partialhci-command-generation-v1 files remainuntracked,
NOT approved. Next: confirm restoredcity/tail, then diagnose actualreset/transport
cause beforeanotherfirmwaretrial; do not claim the flagged fix is implemented.

Owner now confirms "виден кот и город" after58/world19 recovery. Saved exact
message at physical58-world19/owner-city-visible.json; city/cat visual restoration
confirmed, tail motion not yet separately confirmed. Motion question pending.
No new radio packet signed/sent, no reset command, counters remain58/19. Next
hardware trial needs transport/reset diagnosis and reviewed new candidate;
the rejected HCI timer preparation is not retried or assumed completed.

### 2026-10-07: authorized read-only reset investigation; city19 still matches

After owner "делай", ROOT fresh locked knownpeer read confirmed exactRFS state2,
counter19/2128bytes/package89ffda..., savedstate unchanged58/19/allpendingnull.
No new signatures/firmwaretrial or frozen source changes. Tail-motion question
still pending; receipt does not prove animation.

Mac's actual bluetoothd history for failed sender7694/1367: connection completed
12:47:59.379814UTC, timeout12:49:03.413076UTC (~64.033s), newconnection succeeded
12:49:06.428398UTC. Host recorded LSTO72/720ms andinterval24, final handle0x4c
radio history Good thenNo-Sync, RSSI-63..-71. These are host observations, not
Dell terminal USBfault or watchdog-stage evidence; reset cause remainsunproved.
Do not declare10s same-opcode bug actual57cause solelyfromthis64s connection.
Public selectedlogs +currentworld19 exactreadback at gatt-read-diagnostic-v1/
evidence/2026-10-07/host-reset57-timeline-city19-readback/bindings.json. Fullselected
Mac logs remainlocalignoredruns; no credentials/privatekey accessed/exported.
Rejectedtimer preparation was NOT retried/renamed/deployed. GitHubpush53fdfcc
attempts returnedremoteInternalServerError; localcommits preserved, retrypushlater.

### 2026-10-07: new59 observation-only candidate prepared, not timer fix

Owner requires bare-metal Dell only; no Linux installation on Dell. Yukabox remains
the native build/test host and Mac the command/signing station. Rejected HCI timer
preparation remains untracked, not retried or included. Current actual state58/world19,
all pending null; actual owner city/cat visible. No Wi-Fi association/IP evidence.

Frozen transport-observation59-native-v1 payload eb38baaf0b8e2ee120290744a116d02c33ff7bf2f011a73e945a10e239d51e55,150528file/4083712mapped bytes.
Report030bafe91d289a71264e5c7af86753517ad33dfc890ff2cf4c32508e877acf3a.
Independent exactdiff127 production C/H shows only3 generation57→59 constants;
5 absolute include-root relocations, no USB/HCI/watchdog/timer logic change.
Yukabox8nativePCI/CE/USB/overlay models, ASAN currentworld19/120ticks/16camera,
3equalEFI,normal+EMPTYactualsupervisorQEMU PASS; host/model notphysicalproof.
Scope remains bounded prefix32984MAINbytes/133descriptors/noBMI_DONE/noHTC_INITscan,
600s,all14checkedstop. Visible PREFIX57 is familylabel; rawgeneration59.

Frozen host asset-observer-v1:41callback/sequence+260decoder/preflight checksPASS.
Same knownpeer/oneCBCentralManager; after each true64byteRFCS saves checkpoint,
reads raw240QPFX in same connection, fsyncs diagnostic before next transport action.
Exact failed-connect/disconnect/timeout NSError saved. Invalid/missing prefix stops
without NEXT/replay. Extra ATTread/fsync changes host timing, not timer fix.
Host-proof18548e99bff3447b5df490bde84c882a2b51c809b095ece3950c3406b62651db.

New observation59-root-route-v1 checks419source/162generated inputs/public58signature,
world19receipt, productiondiff and policy before fresh<=300s knownpeerRFS query/key.
7offline mutation guardtests PASS; assets derivative preserves original immutable
packets/signatures/floors and adds serialized host diagnostics. Original prepare and
signed sources unchanged. continue59.py one native send, initialQPD18, sign12once,
assetdeliver once; any failure stops (no reconnectloop); full12 thenquiet660s/read.
At this entry no59 signature/reservation/radio trial yet. Resume only actual saved
state/session; never replay retired57. Rootproof includes pinned helper/executable
hashes. Next step fresh liveworld19 query → exact local59 signing → solecontroller.

Native59 now signed ONCE after fresh actualworld19RFSread, reserved exactsession
runs/text-world/pci-native-o_atkvtj; solecontrollerPID8339 launched from
observation59-root-route-v1/continue59.py, metadata/log in runs/control.
Snapshot at evidence/sign-and-launch: pacednative delivery inprogress, no APPLIED
claim yet, hardware_trial_pendingnull/no59firmware signed at snapshot. Actualstate
and newest receipts override this entry. No secondcontroller; if stopped preserve
exactsession and do notsignagain. Last code/evidence push758bd7d succeeded.

### 2026-10-07: physical59 APPLIED; correct initial service; assets59 started

Actual exact APPLIED59 receipt package5462ada06c7a1e2fb801c31f9f3ab35c3eecc286dc7fbba8b3c296c7d9ce62ad, native_pendingnull,world19 retained.
PID8339 exited after initial read-pci43 “diagnostic service absent”; NOfirmware
signed by thatcontroller. New knownpeer locked readonlyRFS counter59 and240QPFX
generation59 bothsuccess: noreset/contextloss evidence. Hostread_pci service list
excluded0D; adding0D to multi-service list stillfailed. New read_initial59.m requests
ONLY exact0D service + knownpeerfilter; got actual hashjoinedQPD18/924 bytes with
alloriginal setup/ROM/14teardown gates; no native/HCI/timer/source/key changes.
Evidence at observation59-root-route-v1/evidence/applied59-and-initial.

Then originalassetprepare through strict59guards signed12newRAMchunks ONCE,
exactsession runs/text-world/firmware-ram-e66kaqfm. SoleassetcontrollerPID10417
assets.py deliver, metadata runs/control/asset-controller59.json, logassets59.log.
Do not restart continue59.py or signagain. Check livepid/newreceipts beforeanything
Bluetooth. On failure retain exactpackets/checkpoints/diagnostics; no automatic
reconnectloop. After all12accepted/ready1 allow660s quiet before prefixread.
Wi-Fi association/IP stillunconfirmed; city/catvisual59 notyetnewownerobservation.

Assets59 firstsend reachedconfirmed43200/65760bytes ofchunk0, nochunkcomplete.
Stopped onlyhost240s boundedtimeout;13durableobserverrows includeexacttimeout
RabbitAssetObserver/code1, precedingprefixreadsvalid; no disconnectcallback.
PID10417exited. Reviewed same-session continuationPID11665 now assets.py deliver,
query-only before write, noresign; metadataasset-controller59-resume1.json,
logassets59-resume1.log. Actualnewstate/receipts priority. After ordinarytimeout
with progress mayqueryandresumeexactsession; anydisconnect/invalidservice/loss
needsdiagnosis first. Full12/boot/Wi-Fi/IP notconfirmed.

Assets59 chunk0 fullyaccepted(bitmap1/ready0); chunk1 confirmed43200/65760 then
ordinaryhost240s timeout. PID11665exited. New host-only resume_assets59.py starts
soleboundedcontroller (actualpid runs/control/bounded-asset-controller59.json,
logbounded-assets59.log). Up to24 same-session resumes ONLYafter validgeneration59
240QPFXchain, ordinaryhosttimeout, forwardprogress; query-before-write everytry.
Disconnected/servicefault/invaliddiagnostic/no-progress stops, noresign/reboot.
ActualtimeoutguardPASS pluscopied disconnected/no-progress/badgeneration reject.
Afterfull12/ready1 quiet660s thenrawprefix; no earlyWi-Fi/IPclaim. Signed59 source
and timerintervals unchanged. Check thislivecontroller before anyBLEoperation.

### 2026-10-08: physical59 all12 received; bounded MAIN prefix checkedstop

PID12867 completed/exited. Sameexactassetse66kaqfm all12 accepted bitmap4095/ready1;
full751436bytefirmwarecontainer retainedRAM. Afterquiet660s actualknownpeer240QPFX
generation59: phase3/reason0/released1, offset32984, submitted312/completed312
(these count alltransport, not133 MAINcap), stage6/failed8448 (deliberatestop path),
adapterclosed12/cleanup_slot14; held/DMA/claimed/access/bus/pins/IRQ/link/wake/reset0;
usb_fault0/raw_overflow0. NoBluetoothreset observed duringthisfullcontainer delivery.
Physicalprefixlimit reached andreportedreal14ownerrelease; rawchecked source
prefix_released requiresall14buffersclosed. Evidence/classification under
observation59-root-route-v1/evidence/full-assets-and-checked-prefix.

This59 profile deliberately STOPSafter32984MAINbytes, BEFOREfullMAIN/BMI_DONE/HTC
INIT/scan; notWi-Fi firmwareboot or association/IPsuccess. Do notresumecompleted
assetroute/replayfirmware intochipstate orclaimearlierresetcausefixed. Session
hardware_trial_pending stillpreserved forROOTclassification/retirement, notactive
controller. Next reviewedisolatedgeneration needsfullMAIN/bootcontinuation with
samehostobservability/currentworld19 andfreshchipROM/reset-lifetimechecks; no
Dellreboot/USB/bootstrap/OTP/flash permitted. Rejectedtimerfix remainsuntouched.

### 2026-10-08: authorized nextfullboot60 preparation inprogress

Owner explicitly “делай” fullfirmwareboot andnetworksearch. observation59 agent
prepares NEW unsignedfullboot60/currentworld19 derivative using originalvalidated
wmi-native-v5 fullMAIN/BMI_DONE/HTC/INIT/READY andpassiveQPFXobservability, no
rejectedtimerfix. independent secure_connection agent read-onlyauditofgenuine
scan integration; don't claim scanincluded60beforeproof. Root publicverifyactual59
RRTsignature+all12firmwaresignatures+bitmap4095 PASS. New transition59.py public
archive/retirement gates and5copiedproof faulttestsPASS; retirementNOTexecuted.
State still59/world19/exactcompletedhardwarependinge66kaqfm,noactivecontroller.
No60signatures/reservation/radiooperationsyet. Rootgate/controllerpreparation
infullboot60-root-route-v1, candidatefullboot60-native-v1. Wait frozenactual60
source/native/fullEFI/currentworld/QEMU proof beforekey/retirement/devicewrites.
Actual59prefixclock elapsed255.354s/all312transport to32984MAINbytes;600s prefix
watcher may notcover full727128MAIN. Newfullbootwatcher deadline must beexplicit
bounded andjustifiedfrommeasuredtransport; HCI/resident/USBtimersunchanged.

60 developmentupdate:103 actual productionnative Cmodels PASS onYukabox
(38fullboot/startup/transport+65initial), includingactiveGATTreadpurity, actual
fullMAIN727128/BMI_DONE1/WMIINIT1/READY andreal14closure inmodel. WholeEFI
repeat/currentworld19ASAN/normal+EMPTYQEMU proof stillinprogress, notadmitted.
Fullboot watchdog5400s: actual59 312transactions/255.354s vsmodel full3114,
projected~2548.6s;~2.12allowance, deterministicdeadline/rollbackchecked. HCI/USB/
resident andper-commandtimeoutsunchanged. Roottransitiontests6PASS incldurable
copyarchivefailleavescopiedstateunchanged; actualstate59stillpendingcompleted.

Frozen fullboot60-collector-v1:44hostcallback/preflightPASS, proof
0615819bee8531eb9a92d4eac8fb1a6a28812f0444ae14bd84bd250ddd240859.
One knownpeer/connection, sequentialsingle-servicediscovery, QPFX240 every30s
untilactualphase3/released1,thenQWBT160/QWOP488/QWIN244 samelink. Max5460s,
outstandingATT60s; errorsdurablysavedbeforestop; noreconnect/writes/readyclaim.
Rootcollector_gate independentlychecksallsource/compilerinputs/executable;
continue60.py willstageexactpackets thenmonitor. No60signature/radioyet.
Read-only scan61-integration-audit-v1 README documentsreuseofscan-native-profile-v2,
adoptpersistentownersBEFORE60diagnosticstop, lifecycle/RX/credits/regulatory and
GATThandle29..51vs32..255 conflict; notscanimplementation/admission.

### 2026-10-08: frozen60 source/model/fullEFI/root gates allPASS, awaitingfreshhardware

Fullboot60 report5e5b1be82bf69048d22cd02380e9dd850820e39befd24a7991ce653bd637e772,
payload3984d3f5d1c9a3c3540bf2ef00972bea52406a6f78edc56bd215507110668fd6
163840file/4096000mapped; reproduction88a1a7adc9cdc03fe0cc0f10b1c4fceadfff10e9b6945bbf1fa224f84a8c3fb1,
native103report00fc467844ddda4111b3e639f74acb22beb6510ac4f22efe446aa563bffb3d6a.
ThreeequalEFI+postQEMUbuild/currentworld19ASAN/normalEMPTY PASS. Rootindependently
verified420source/162generated/64compiledfixture hashes/alllogs/actualmappedcap,
all127productionfiles only4declaredfullbootchanges+5absoluteinclude-root relocations,
protecteddriver/USB/HCI/event/recovery byteequal59. Full103model scope and5400s
bound; expectedmodeltotal3114transportdesc+fullMAIN727128. No scan in60.

Root11faultguardsPASS (6transition inclcopieddurablearchivefailure +5fullcandidate),
collector44proof/executable/initial-reader/sourcecheckedbeforekey. No60signature
statechange/retirement/radioyet atthisentry. Next: freshknownpeerRFS59+QPFX59all14
released → archiveactual59session → once-sign60 → solecontinue60.py. New RAMassets
willbeonce-signedafteractualAPPLIED60+freshQPD18setup; observer/boundedresumes then
one-connectionfullbootmonitor untilcheckedrelease, fixedQWBT/QWOP/QWIN capture.

### 2026-10-08: actualprior59 released archived;60 signedONCE/solecontroller launched

Fresh locked knownpeerRFS59 exactpackage5462ada... +240QPFX59 phase3/reason0/all14
released/32984confirmed, publicall12/native59sigverified. Rootdurablyarchived
everyactual59native/assetpacket/log/hash underfullboot60-root-route-v1/runs/retired59
(fsyncallfiles+alldirectories+parent BEFOREpendingclear). ClearedONLYcompleted
hardware_trial_pending, preserved59/19 counters/payload/world andretirementrecord.
NoDellreboot/USB/bootstrap/flash/OTP/credentials.

Then signed60 ONCE exactsession runs/text-world/pci-native-84rxxr3h. Solelive
controllerPID26509: fullboot60-root-route-v1/continue60.py; logruns/control/continue60.log,
metadatacontroller60.json. Nativepacedstage started,notAPPLIEDyet; assets60NOTsigned
at snapshot. Actualstate/currentreceipts priority. No secondcontroller, noresign.
Controller handlesnative→QPD18exact0Dread→sign12assets once→boundedprogressing
same-sessiontimeoutresumes→ONEconnectionQPFXmonitor30s up to5460s→QWBT/QWOP/QWIN.
Anytransport/diagnostic/no-progress faultstops+preservesevidence. Wi-Fi/IPnotproven.
Publicretirement/sign/launch snapshots evidence/signed60-launched. Source/rootproof
commits9c36c53 and3ac0b1a; collector/audit095466f.

Independent observation59 agent nowprepares UNSIGNEDscan61/currentworld19 using
frozen60+existingmature55scan components, persistentadoptBEFOREdiagnosticstop,
explicitGATTlayoutresolution. OnlyYukaboxmodels/sourceproof, notphysicaladmission
andno61sign/state/BLE. Mustfirstcapture/classifyactual60rawresultbefore61hardware.

Native60 controller26509 exited ordinary300s hoststagingtimeout atconfirmed
156200/164128bytes; noDISCONNECTED inlaststage. Actualstate still59/world19,
exactnative_pendingpci-native-84rxxr3h, no60assetsyet. Same-source rootgatePASS.
SolecontinuationPID34914 nowcontinue60.py sameexactnativepacket, query-before-resume;
metadata controller60-resume1.json/logcontinue60-resume1.log. Noresign. Snapshot
at evidence/native60-staging-timeout-resume. Inspectlivepid/newstate beforeBLE.

Unsignedscan61 technicalcandidate/hostobserver nowfrozen byindependentagents: no
actual61signature/BLE/state. Candidate report0188ad2b1663804fbc6cf663beef4fb3cba2daa05c06eee2fe48fabece5dc388;
payload305d0171c3c2e296fdf00f82a01cc838d67c0a1f3ffa836a847f4f12770ce074,
191488file/4177920mapped.19scan/native models+293policy+199278regdbchecks/repeatedEFI
world19ASANnormalEMPTYQEMU/ATTgap29..31 passed. Samepassive13channels/exactSSID,
QSCN+110rawpagesonly,noassociation/credentials. RFadmission/GElegalprimaryfalse
remainexplicitgate, notimplicitlyadmitted bytechnicalproof. Rawactual60READY/
resourcesnotcapturedyet. 61collector495fakecallbacks+794purechecks, proof
3ee5a595e0c3d2206ab02310c03cc42095bb1aed6ce8670086c8287b444434f9; actual61
positivebindingstillRootrequired. Frozen60andUSB/HCI/residentunchanged.

Native60 same-signature resume succeeded actualEXACT-APPLIED-RECEIPT60; native_pending
null,enginecounter60/payload3984d3...,world19retained. NoWMIREADY/association/IPclaim.
SolePID34914 continue60.py nowinitialexact0D/QPD18checks thenoriginalassets60prepare
/sign12once andstaging+monitor. Inspectlatestactualstate/log; do notstartanother
controller orsign60again. PublicactualAPPLIED report evidence/applied60.

Actual60initialQPD18 passed; originalprepare signed12assets ONCE session
runs/text-world/firmware-ram-6fuyx2jq. continue60 PID34914 thenstopped BEFOREany
assetwrite duehostcontroller AttributeError assets60.current (missingalias);
no sendersteps/no60firmwarebytes transmitted atfailure. Frozen/signedsources
untouched. NEW hostonly resume_assets60_v2.py one-lineinterfacefix route.current
(actual60guard), copied-public actualentrypoint test/mocknonordinaryfailstopPASS;
reproducibleregression test_resume60_v2.py PASS, no hardware/keys/statewriteintest.
SoleactualassetcontrollerPID35102 nowresume_assets60_v2.py SAMEsaved12packets,
noresign; metadataasset-controller60-v2.json/logassets60-v2.log. Originalfailed
controller/source preservedforaudit. Lateststate/receipts/livepidoverrideearlier
PID34914entry; doNOTrestartcontinue60.py orsign60assetsagain.

60assets firstchunkaccepted(bitmap1), secondlastconfirmed17280 thenactual
CBErrorDomain/code6 disconnected; PID35102 stopped asrequired(non-timeout).
ROOTfreshserializedknownpeerreadonlyRFS60 exactnativepkg b12c2ee8ae3eac069adfc5b907b65f1b8edf442884e72510d3c9badd382b087e,
QPFX60phase0/usb_fault0/overflow0, actualRFCS64 state1/error0/len65760/received18480
/exactchunk1packetSHA478cb587.../bitmap1/ready0. Engine/partialassetretained; no
resetobserved; disconnectcauseunproved. Originalstate/signedpacketsunchanged.
Newhostonly continue_assets60_after_checked_disconnect.py ROOTfreshretentionguard
validatedallrawcallbacks/statehash+<=300s underlock, thenone exactsavedquery-before
resume (noresign). SolePID57474 nowthisscript, checked-disconnect60-controller.json/
logchecked-disconnect60-resume.log. Thereafterv2allowsONLYprogressingordinary
timeout; anotherdisconnectstops/investigate, no blindreconnectloop. Evidence
disconnect60-retained-and-resume. Actualstate/newreceipts/livepidpriority.

ReviewedresumePID57474 alsoSTOPPED: secondactualCBErrorDomain/code6 ~1.53s
aftervalidQPFX60read beforeanynewcheckpoint (lastconfirmed18480); secondchunk
notcomplete/fullbootnotstarted. Noordinarytimeout/resumeallowed; noactiveBT
controller. Exact native60/asset6fuyx2jq packets/checkpoints preserved; noresign.
Evidence repeated-disconnect60-no-new-receipt. Actualpost-secondlosscontext
notyetnewread, don'tinferresetorzeroadditionalbytesfrommissingACK. Repeated
realdisconnectcauseunproved; do not blindlyretry. Askedowner Mac<=1m +current
city/movingcat confirmation throughasyncquestion, pendingreply. Independent
Macradio-log analysis maycontinue withoutBLEwrites; no reboot/USB/bootstrap.

Owner “да и да”: Mac<=1m, city+movingcat visible aftersecondloss. NoDellreboot
needed/authorized. Macbluetoothd exactpeerF45…: 10:33:32.693+0400 handle0x54
connected, 10:33:35.54 disconnected; LSTO72, RSSI-78..-85/SNR10..31, NACK/
No-Sync history; hostradio synchronizationlost, rootcausenotproven. Onlyselected
exactpeer recordspublic, fullotherdevicelogs localignored. NoactiveBTcontroller.
Independent secure_connection prepares NEW host-only small-data100B derivative
fromfrozenassetobserver, exactone-token DATAcap240→100, same50mspacing/240stimeout
andbyte-exactsavedpacket/status/diagnostics. No native/HCI/resident/timerfix.
Awaitmodel+source/executable proofandfresh60/retainedassetbeforeonesinglehardware
trial; noresign/blindreconnect. Nothingnewtransmittedduringthisanalysis.

DATA100 frozenhost65casesPASS: exactone-tokensender change240→100, maxATT104,
same50ms/240stimeouts/status/signedpackets/serialQPFX. Proof
8ee677d70d128280fbae23cedfc5bb70449a8afb9e8e1596925153bd9e7eed8c, sender
f86f50806b4959de5441c21eb26840891c934a487786a6da527febf3ee66cca9. Rootindependent
alloriginal/newsource+compiledexe+hostlog+exactdiff gatePASS. New small_data60_trial.py
ONLYdeliverexisting12assets, no sign. FreshknownpeerRFS60/QPFX60phase0/noUSBfault
/RFCSexactchunk1retained +unchangedstate validatedunderlock beforetrial.
SolePID60888 small_data60_trial.py; small-data60-controller.json/logsmall-data60-trial.log.
Existing6fuyx2jq packets/checkpoints reused; no native/HCI/timer modification,
newsignatures0. One controlledtrial; anyfailureSTOP(noauto-reconnect); outcome
unconfirmedatsnapshot, notclaimedRFcausefix. Evidence/small-data60-trial-launch.

DATA100 actualtrialPID60888 STOPPED sameCBErrorDomain6/connectiontimeout before
newRFCScheckpoint; lastconfirmed18480. Reducingcap100 didNOTresolveobservedloss;
don'tclaimPHY/long-PDUcauseproved. NoactiveBLEcontroller. Preserve6fuyx2jq
exactpackets/floors, noresign/abort/replay/reboot. Outcomeofunacknowledgedwrite
unknown; freshreadsrequiredbeforenextauthorizeddelivery. Publicfailureevidence
evidence/small-data60-trial-failed. Ownercity+movingcat previouslyconfirmed.
Rootassignedobservation59 read-only audit of actual frozen60 ATT→DATA→RAM ownership
andHCIACL path at18480; no deniedtimerfix ornewhardwarecandidate, no privatekey.
Do not blindlyretry. IndependentMaclogs/sourceauditcontinue; fullMAIN/Wi-Fi/IP
stillnotstarted/confirmed.

Preparedwifi_quiet60_trial.py (NOTRUN): single60sMacen0Wi-Fi-off/Bluetooth
experiment, explicit --human-authorized-wifi-off required; initialOncheck,
finallyrestore+verifyOn, independent75srestorewatchdog; no new signature.
3fake restoration normal/timeout/error casesPASS, no actualnetwork/BLEactions.
RootaskeduserapprovalbecauseMacinternet/chattemporarilyinterrupted; pending
reply, doNOTinfer fromtimeelapsed orpreviousMac-nearby answer. Noairportpower
change yet (readonlyinitialpowerOn). Afterapprovalfreshnative60/QPFXphase0/
exactRFCSretention/allsourcegates beforeone trial. FullWi-Fi/Dellstillnotready.
Read-onlyaudit: nineproductiondata/BTfiles59↔60byteequal, chunk1payload/18480..18719
bytesidenticaltoalreadyaccepted59; DATAcopyonly, crypto/firmware/MMIO later.
No currentproofwhether inboundACL/outboundACK/creditstall orradio itselfcausesloss.

### 2026-10-08: humanauthorized60sMacWi-Fi quiet test, progress/restored/normalresume

Owner “делай” explicitlyauthorizedpreparedsingle60sMacWi-Fi-offtest. Fresh
knownpeer60/RFCSpartialretention+source/packetowner checksPASS; noresign.
Actualwifi_quiet60_trial.py originalDATA240 helper: firstRFCS18580 then22900
then27220, validQPFX60 reads, noCBError beforecontrolled60sparentlimit. Sender
killedatlimit/outcomeunknownpastlastACK; preservedcheckpoint. finallyen0On
restored+verified, independent75swatchdogterminatedafterconfirmedrestore.
Actualsecond -getairportpower alsoOn. Notproofpermanentfix/soleRFcause.

Freshknownpeer60/RFCSafterrestore retains exactpacket; one reviewednormalWi-FiON
continuationPID64363 nowcontinue_assets60_after_checked_disconnect.py,
wifi-on60-posttrial-controller.json/logwifi-on60-posttrial-resume.log. New
RFCSconfirmed33460 then37780(secondchunk); normaltransfercurrentlyprogresses.
Same6fuyx2jq/same12signatures, no extraWi-Fi-offinterval/permissions assumed.
Anynewrealdisconnect stops; ordinaryprogressing240shosttimeouts handledv2.
Noactiveothercontroller/fullMAIN/Wi-FiDell/IPclaim yet. Evidence
wifi-quiet60-result-and-on-continuation. Actualnewreceipts/livepidpriority.

Owner “Давай, делай, всё подтверждаю” authorizescontinued existingWi-Fi plan;
prior noDellreboot/USB/bootstrap/OTP/flash/privatekeyorplaintextcredentials
boundaries remain. ActualsolePID64363 stillnormalMacWi-FiON delivery; chunks3/12
fullyaccepted(bitmap7), chunk3confirmed12960 atcheck, forwardprogress. No new
controller/signature. All12→fullboot+oneconnectionrawREADY monitoringautomatic.

Rootindependent readonlyscan61technicalcheck PASS:480source/194generated/149native
compiledfixture hashes+logs/reproduction/normalEMPTYQEMU/wholeEFIcaps+world19
match. Report0188ad2b...,payload305d017...,191488file/4177920mapped. RF/GEprimary
flags stillfalse, actual60READYpending, no61physical/signingadmission. Preserved
code/evidence fornextstep; this technicalcheck doesNOTsubstituteactualREADY
orprimarypolicy/RFproof. scan61-independent-technical-check/report.json.

### 2026-10-08: physical60 all12 accepted; fullMAIN active

Actual6fuyx2jq all12accepted bitmap4095/ready1; exactfullcontainerinRAM. Sole
PID64363 nowoneconnectioncollector --monitor; DO NOTopenanotherBLEconnection
whileprotectedfullbootactive. Latestrawsnapshot gen60 phase3, MAINoffset0/727128,
submitted3114/completed3114, boot/planerror0, failed0, USBfault0/overflow0,
held/DMA14 ownersretained asrequired whiletransferactive. NotREADY/association/IP
proof. Sourcefullbootbounded5400s, collector5460s, actualelapsedfromsnapshot
~2501.300s (samehighword); progressstillvalid.
Evidence full-assets-and-MAIN-progress. ReadonlysavedmonitorJSONL mayinspect
withoutnewconnection; afterphase3/released1 collectorwillcaptureQWBT/QWOP/QWIN
andexit, thenRootclassifyactualINIT/READY/MAC/ownerrelease beforeenginechange.

### 2026-10-08: physical60 FULL MAIN / HTC / INIT / WMI READY CONFIRMED

SolePID64363 finishedcollector/exited. Actualraw240QPFX60phase3/reason0/released1,
stage5/failed0/adapterCLOSED12/cleanup14; ALLheld/DMA/claim/access/bus/pins/IRQ/
link/wake/reset0, USBfault/overflow0. QWBT160 bootphase5/plan20/error0, all3114
transportsubmitted==completed, HTCready20bytes. QWOP488 operatingphase2/error0,
SERVICE_READYvalid1/memoryreq0/domain108/bands2312..2732,4920..6100. QWIN244
startupphase2/error0/transactionphase4/INITtx_count1/ready_seen1/tx_complete1,
ABIminor574, MACc0:b5:d7:78:c3:fb. ExactownedHTC/WMIrawREADYframe68bytes,
endpoint1/payload60/event2/tag35/value52/ABImajor01000000/namespacesvalid/status0;
Rootindependentlyparsedframe andMACmatch, notmerelystatusboolean. Checked14
ownersactuallyreleased AFTERconfirmedREADY; runtime60didnotretainactivestation.
Publiccompletecallbacklog/rawQPFX/QWBT/QWOP/QWIN/classification at
evidence/physical60-fullboot-READY. Native60/asset6fuyx2jq stillpreserved in
statehardwarepending forRootretirement; don'treplayorresigncompletedfirmware.

FULLradiofirmwarebootstrap/INIT/READY nowphysicallyproven. SCAN/association/
credentials/DHCP/IP/Yukaboxexchange NOTperformed/notproven. Nextscan61 needs
independentpolicy/RFadmission plusfreshphysical60releasedcontext+archivebefore
newsign; frozenunsignedtechnical61proof alone notauthorization. Preservecitycat,
noDellreboot/USB/bootstrap/OTP/flash/privatekeyexport/plainBLEcredentials.

### 2026-10-08: Root bounded passive scan61 signed and sequential controller launched

New scope native-wifi-qca9377-scan61-root-route-v1. Exact unsigned61 technical
proof rechecked480sources/194generated/149fixtures, native19models, policy/header
logs, normal/EMPTYQEMU/world19. Independent review17rejections+11retirement/fresh
testsPASS; fixed newroute diffreport binding, four-envelope fresh provenance and
Pythonnamecollision by root_route.py (frozen59/60 unchanged). Current2026GE
primaryreference reviewed; SEPARATE bounded strict-passive13channels2412..2472
20MHz/25s admission. FrozenRF/primary/probe/antenna flags remainfalse; no physical
zeroTX or antenna measurement claimed. Firmware assumed honors passive request.

Actualfresh knownpeerRFS60 + fixedcollector4envelopesQPFX/QWBT/QWOP/QWIN passed,
all14released/rawREADY retained. Exact60 native+all12assets+allrawproofs durably
archived at newscope/runs/retired60 BEFORE clearing completedhardwarepending.
Signednative61 ONCE: pci-native-6gw77kuj, package
ecd2703c73c1bc92e266542cf08241ef03c613ad4cfba75dcf6942ad0812d71c, payload
305d0171c3c2e296fdf00f82a01cc838d67c0a1f3ffa836a847f4f12770ce074.
Solecontroller PID73430 continue61.py, runs/control/controller61.json and
continue61.log. Liveactualstate/logs takepriority; doNOTstartsecondcontroller,
resignnative61 orreusecompleted60assets.

Hostnewstaging41callback+216offline, progressmonitor75callback, fullscanreader
495callback+794pure checksPASS; allsource/exe/log pins checkedbeforekey. Staging
uses QWBT160 ratherthan removedPREFIX29..51; QWBT has NOgeneration. Root exact61
current/APPLIED binding mandatory. Unchanged QFS/signedpackets/checkpoints/240DATA
/50mspacing/240s-send/60s-query andquery-before-write reused. Only ordinary
progressing hosttimeout resumesbounded24; realdisconnect/error STOPpreserves
exactsignedsession. After actual61APPLIED+freshQPD18 setup, controller signs12
firmware61 once, stagessequentially, waitsoneconnectionQWBT→QSCN/all14released,
then captures110pages2x withfrozenread-scan61. Root mustparseactualownedMGMT/raw
beforeSSIDclaim. Atlaunch61APPLIED/SSID/association/WPA/DHCP/IP/Yukaboxnotclaimed.
NoDellreboot/USB/bootstrap/OTP/flash, noWi-Ficredentialsread/plainBLEprovisioning.
Currentcity19 preserved. Anyrealcontrollerfault requiresreadlogs/exactsession;
do not blindlyretry. This supersedes staleautomationnative51 snapshot.

Native61 physicalpaced transfer confirmed41000 thenmorebytes; native sender has
existing300s hostinterval andflowonlytwo resumableattempts percall. This isnot
Dell/firmwaredeadline. Atordinaryprogressingnative hosttimeout flowfirstqueries
sameexactsession,thenresumeswithoutsigning. IfPID73430 eventuallyexits with
DELIVERY-NOT-CONFIRMED andnative_pending still6gw77kuj, NEWresume_native61.py
maycontinueONLYafterALLcontroller61*.json PIDs gone, exactpacket/loghashes, last
FAILonly300sboundedtimeout, noBLE/receiverfault, andpositivefloorabovepriorquery.
Itreusescontinue61.py; no newnativecounter/signature. Never runwhilePIDalive.
Actualcurrentstate/receiverquery priority; pending/rejection/recovery/fault are
NOTordinarytimeouts andmustbeinvestigated.
Nextstage read-only matrix evidence/association-next-stage.json binds36existing
files: realHTTpacket/PEERMAP/SECIND,airassociation,keyinstall/coordinator and
ARP/DHCP/IP arestillgaps. Existinghostapsupplicant models/compiledobjectsareNOT
fullphysicalWPA. Scan61 cleansall14, nextstationneedsnewlive acquisition and
actualHTTVERSIONCONF; no duplicateHTTCONNECT. EFI61headroom16KB requiresreviewed
nextversionmemorylayout. Credential provisioning stillrequiresphysicalentropy
andpinnedrecipient/channelproof; no credentialread/plainBLE shortcut.

Native61 twohost300s intervals completed atconfirmed156400; PID73430 exited
DELIVERY-NOT-CONFIRMED (ordinaryboundedtimeout, noBLEfault/receiverloss).
Rootguard checkedimmutablepacket/query/loghashes+positiveprogress, allpriorPIDs
gone; ONLYnewcontrollerPID74229 nowcontinue61.py viaresume_native61.py, log
runs/control/continue61-resume1.log andcontroller61-resume-74229.json. Actual
newknownpeerread-onlyquery counter60/sessionmatchesyes retains156900/191776
(500previouslyunACKbytesreconciled). Samepci-native-6gw77kuj/signature/packet,
noresign/newcounter/reboot. DoNOTstartsecondcontrollerwhile74229alive.
AfterAPPLIED61 itcontinuesfreshinitial→12once-signedassets→progress/rawmonitor
automatically. Atthissnapshot61notAPPLIED, noSSID/WPA/IPproof. Evidence
native61-resumed-query.json/log. Rawarchive hostreader has600s internalbound;
currentcontrollerouter240s canstopwithpartialcapture, preservepartial and
Rootcanrerunread-onlyaftercheckedquiescencewith>=660shostboundifneeded; never
usepartial110pages/status asSSIDsuccess. No frozenreader/runtimeedit needed.

### 2026-10-08: native61 physically APPLIED, firmware61 stagingstarted

Exact APPLIED RFS/session/SHA/counter61 received; stateengine61payload305d017...
andnative_pendingnull. Commit-timeCBError7 wasreconciled byunchangednative
sender exactsame-sessionquery andactualAPPLIEDreceipt, noassumption/replay.
New61initialQPD18 realsetup/BMI/all14close passedafter5boundedactive-probe
read-onlyretries. ControllerPID74229 nowhasEXACT12 signedfirmware61session
firmware-ram-ko8zoixg, all12 publicsignatures independentlyverifiedRoot.
NOresign/old60assetreuse/newnativecounter. Continue61controller ownsoneBLE
path; atthissnapshot completedchunks0, receiverprogress actuallogspriority.
Afterfull4095ready1 itautomatically monitorsQWBT→QSCNrelease thenfullraw110x2.
DoNOTcreateanothercontroller/connection; doNOTuse60PREFIXcollector on61:
PREFIX29..51 removed, QWBT160 hasnogeneration. Actual61APPLIED sourcebinding
isRoot prerequisite. Evidence native61-APPLIED.json/initial61-setup.json/
firmware61-staging-start.json. SSID/association/WPA/DHCP/IPnotyetconfirmed.

### 2026-10-08: active61 staging; corrected postboot host ABI; parallel network preparation

SolePID74229 stillcontinue61.py firmware61ko8zoixg; actualchunks4/12accepted
atthissnapshot, currentreport/logspriority. Normalprogressing240shosttimeouts
query/resumeexactpackets, noresign/nosecondBLE/enginechange. Bootnotyettriggered
untilall12 bitmap4095/ready1. Preservecurrentcity19/noDellreboot/USB/flash.

RootfoundHOST-only v1progressmonitor bug: QSCN serviceUUID2a VALUEUUID2b at
ATT34;2c isRAWEXPORTSERVICE, notstatusvalue. V1collector requested2c andwill
stopmissing-characteristic AFTERQWBTphase5; this doesNOTerase retainedscanraw.
Frozenv1/native61 untouched. NEWprogress-monitor-v2 onlyhostconstant2b,75fake
callbacksPASS plusindependent actualgeneratednativeGATT/reader UUIDjoin.
Native-bindingproof6d61b383..., hostproof41adef14...; incorrectv1 explicitly
rejected. NEWfinish_scan61_v2.py MUSTNOTRUNwhile74229(oranycontroller61PID)
alive. AfteroldcontrollerexitANDactualall12complete, itreusescurrent61/APPLIED/
all12signature+contiguous/fullbodydigest underone statelock, correctedone
connectionQWBT→QSCN, thenfrozenrawreader with660shostbound(600sinternal).
Noextra signature/firmwareupload/nativecounter. CLI:
python3 experiments/native-wifi-qca9377-scan61-root-route-v1/finish_scan61_v2.py --state experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json --output /ABS/NEW_OUTPUT_DIRECTORY
Useonlyfreshnewdirectory. classify_scan61.py independentlyjoins227callbacks
(4discoveries+223reads),3stablestatuses/110pages2x, actualcurrentnative61+exact12
firmware signatures/container, policy/epoch/ownedrawMGMT beforeSSIDclaim.
Purefixtures/partial/cached/error/UUID/order mismatchesreject. Native/security/
association/IP remainseparate. Independentreviewcorrectedhelper15negativecases
PASS; rootpurecapture10rejectionsPASS. Noexistinghardwarefailureyet.

ParallelUNSIGNEDsoftwareprepared: htt62-native-v1 actual24productionASAN/COFF,
3equalEFI/currentworld19normalEMPTYQEMU;433sources/176generatedcheckedRoot.
Report9345001639d4eda7d224a8b5d2a7571324ee481f7f3e4c14b33df7f4e8ae46ce;
payload22cde47acd97eec959522b720ebfb6b28fefd2581a32f790fe1f85f2a29d2b81,
173568file/4132864mapped. VERSION_REQ/CONF only, noRFdata/duplicateCONNECT;
future62UNRESERVED/notadmitted/not signed. Requireactual61raw/releasearchive
andseparatehost62 layout/sourcebinding beforephysical62. Frozen60/61unchanged.

network-nosys-v1 pinnedlwIP2.2.0 source181files, hardened339realstack synthetic
ASAN/UBSAN checks+18freestandingCOFFunits onYukabox. Root187source/loghashes
verified; report6407225292e43566293798097194b863e8b6616fefcf7d41e113bc1377213fd5.
NEWadapter rejectsACKwrongserverinREQUESTING/RENEWING, allowsREBINDINGserver
onlyafteractuallwIPacceptance. Vendorunchanged; originalupstreamgap preserved.
ACKserverIDpresence isstricterRabbitprofile, notuniversalRFCrequirement.
25,520text+32,361BSS+2,813rdata: notblindlyfitinto61remaining16KB; futurecomplete
EFI/allpool/lifetime proof required. No real IP/DHCP/HTT/portauthority created.
Supplicant-linked-v1 realhostap2.11supplicant+authenticator/realOpenSSL M1-M4
syntheticpassed, moreproofongoing; hostABI/native and2026PMKSAsecuritybaseline
fix remainunresolved. APauthorized isNOTlocalIPauthority: M4 canprecedefailed
localkeyinstall; requirelocalconfirmedPTK+GTK/currentassociation/noquarantine.
Alllibraries independentsoftwareonly; no privatekey/credentials/device ops.
No retryofdeniedHCI timer/preparation scope. Hashpinnedcopied/vendor whitespace
preserved (19files); allnewauthored-file whitespacechecksPASS.

Parallel supplicant-linked-v1 nowFROZEN (realhostonly): report
ab6d3fc62a2ff757c40f20088f28b160a929ae63b1c66aa12467eecbfdbd6bb2; freeze
6403204028e0b2f53f4cf63371b424891a67c454b4a4f417e1ce9720aa8a9290.
10actualmature supplicant/authenticator interopscenarios ASAN/UBSAN PASS,
18upstreamunits/realOpenSSL3.5.5/publicsyntheticfixtureRNG. Rootall22local
source/log hashes+331remote dependency/object/exe hashesread-onlyverified.
PTK/GTK replay/rekey, MIC/counter/length/wrongPMK andambiguousinstalledtimeout
quarantine/localcontrolledport exercised. NativeCOFFactualattempt FAILED
missingstdlib.h; noclaimnativeport/physicalWPA. Official2026-2 PMKSAcontext/AKMP
fix STILLNOTAPPLIED tohistorical2.11; notapprovedforactualcredentials.
APauthorized!=localIPauthority proven: M4canprecedelocalset_keyfailure;
localport0mustblockIPevenAPauthorized1. Ethernet/DHCPadapterbridge+actual
confirmedPTK/GTK/association/entropy/secureprovisioning stillneeded.
Actualfirmware61transfercurrently7/12acceptedandcontinuing sole74229; noSSID/
association/IPproof, nohardwareengine62/signing/credentialsread.

### 2026-10-08: physical61 all12 accepted; MAIN706552 progressing; next-stage host/core prepared

Actualall12 firmware61ko8zoixg accepted4095/ready1, solePID74229 remainsv1
QWBTmonitor. Atthissnapshot MAIN706552/727128 phase1/plan17, boot/planerrors0.
DoNOTopenanotherBLEchannel orrestart/resign. AtQWBTphase5 oldv1 statusUUID2c
willfail asdocumented; wait74229exit, thenfinish_scan61_v2.py undersolelock
reusingcurrent61/all12 exactsignedassets, freshnewoutput. CorrectedV2UUID2b
proofs alreadycommitted; no replay/download necessary. Scanrunsin61 itself;
hosttool onlyreadsretainedresults. CapturedMGMT/SSID/raw110x2 notyetconfirmed.

Parallel newhost62 scopes FROZEN/unadmitted: staging41callbacks+216pure checks,
observer175callbacks+441pure checks/nativegeneratedGATTABI join. QHTT2e/2f at
ATT31/status320, QHTXservice30/80..9d/raw30pagesx2+3statuses,67callbacks incl
4discoveries; actualfirmwareIE6 and ownedrawVERSIONCONF major2/3 joined.
Staging61→62 ONLYpacketgeneration guard changes; allQFS/checkpoint/timers
unchanged. Rootallsource/compiler/exe/pinnedbindingschecked; noactual62/keys.
Stagingproof2399bb303f37225ca7cc5eea13d5ec39913ce7fd3d0372f97c212e94d8f4e2db,
observerproofa1f3f1d48551f4c6f5e34c38806390743edae74fa355bb88942e7a6813ca6852.

NewhistoricalBSSbridge7194ASAN/UBSAN+5COFF onYukabox and6Python testsPASS.
Frozenmaturegrammarcopiedexactly; publiclive_frequency0 stays0, observed
frequencyseparate, selected_rates0/nativecapabilitiesUNKNOWN. Privategrammar
comparison operands useactualIE-derivedrate/frequency only, NOTauthority.
Optionalnativecapabilitymask structuralcheck can'tapproveassociation; fresh
liveBSS mandatory. Report3fba0b3e689a2382af7666411537043939255bac4a42965e48bc2c9ba79f6309.
Allpositivecases synthetic/notphysical61. RootsourcehashcheckPASS.

New supplicant-native-v2 softwarelane ongoing: separateexactzero-fuzzofficial
2026-2 PMKSAcontext/AKMPfix, realportablehostapAES/SHA/HMAC noOpenSSL;13genuine
hostASANinteroptests+24COFFcompiledunitsPASS. Actualunpatchedwrongctx/wrongAKMP
regression FAIL vs patchedPASS andmatchingpositive. NativeLINK stillfails31
OS/eloop/string services; caller-ownedcallbackABI proofseparate/notconnected.
Noactualnativeimage/credentials/entropy/confirmedfirmwarekeys/physicalWPA.
Don'tmistakecompiledobjects fordeployment; futurecompleteGC/EFI/cap and
allpool/lifetime proof remainsneeded. Frozenpreviousscopes/driver unchanged.

### 2026-10-08: physical61 boot complete; scan status recovered through inconsistent Mac GATT inventory

All12 firmware61 assets remain accepted; controller74229 exited. QWBT reports
phase5/plan20/errors0/submitted=completed3114. Both frozenv1 and correctedv2
monitor stopped on missing status characteristic. No firmware replay/signature.
Full public CoreBluetooth discovery returned historicalPREFIXservice40 absent
from native61, a CBService inside its characteristics, empty statusservice2a,
and missing rawservice2c. V1 inventory crashed on unexpected object; newV2
records runtime class safely. NewV3 read-only diagnostic selected existing
UUID2b under historicalservice40, actual callback416bytes/QSCN0001, error0.
Decoder accepts generation61/policy13, startupREADY1, all4TXcompleted, scan
terminal_seen1/reason0, ownersreleased1/adapter12/cleanup14/zeroDMA, SSIDseen0.
This inconsistent parent is NOT accepted by full scan classifier: no complete
110pagesx2 export, no SSID/association/IP claim. Exact logs/source/executable
hashes in evidence/physical61-gatt-inventory. State unchanged, zero writes.
No active Bluetooth controller. Need supported Mac-side cache refresh then
fresh full inventory and raw capture; do not change frozen61/replay assets.
SystemSettings shows Dell is not a paired MyDevice; no scoped Forget action.
Asked owner for 20s Mac Bluetooth off/on (accessories temporarily disconnect);
not yet performed. Do not reset Dell/USB/bootstrap or edit system cache DB.

Owner selected alternate hotspot iPhone (9) and reports it enabled. No password
collected. Current frozen61 still targets SILK_56E35E_Plus and its bounded scan
is terminal; enabling hotspot does not start another scan. Next target recorded
in evidence/requested-next-network.json, not a deployment/configuration claim.
New isolated candidate/gates needed for changed target; no frozen edits/replay.
Mac Bluetooth off/on consent remains unanswered; do not infer it from hotspot
enabled. First preserve/read full61 raw before retiring completed generation.

Owner explicitly authorized20s MacBluetoothoff/on; completed viaSystemSettings,
UIconfirmedON restored. Freshknownpeer inventory nowhas NO oldPREFIX40, correct
2a/2b and raw2c with110 actualread characteristics, error0. Dellnotrebooted,
stateunchanged/zerowrites. evidence/physical61-gatt-refresh preserveslogs/hash.
Sole finish_scan61_v2.py nowreading full retained61 export understate_lock;
output runs/finished61-after-bluetooth-toggle. DoNOTstartanotherBLEconnection.
Waitfull227callbacks/classification beforeSSID/release/raw conclusions.

### 2026-10-08: physical61 full scan capture COMPLETE, no accepted target

Sole finish61 reader completed; no livecontroller/reader. Full227 actual
callbacks/noNSError,3stableQSCNstatuses,110pages twicebyteequal. Rootclassifier
PHYSICAL61-COMPLETE-SCAN-CAPTURE-NO-ACCEPTED-TARGET. ActualREADY/startupTX1,
scanterminalreason0, nativeerror0/all14released confirmed, SSIDseen0. Five
retainedarchiveevents1d011/1d019/16006/1d011/1d011; no retainedMGMT7001,
observation slot16empty. This is no acceptedtarget, NOTproofAPabsent or cause
identified. NoSSID/auth/keys/IP. Evidencephysical61-complete-scan storesfull
logs/capture/classification/hashes. State retains completed61firmwaretrial;
doNOTreplay or clear without reviewedretirement. Next isolate radio RX/HTT
path before assuming SSIDrename alone fixes receiving beacon. Owner requests
iPhone(9) for nextscan; retain exactspacedSSID, passwordnotcollected. Prepared
unsignedHTT62 VERSIONREQ/CONF candidate mayhelp establishtransportbaseline;
requiresRootphysical61archive/publicclosure and separateadmission before
signing/deployment. No new62counter reserved or signingperformed here.

### 2026-10-08: exact HTT62 signed once; sole sequential controller started

Freshphysical61 RFS APPLIED/counter61/ecd270... plus currentGATT2a/2bQSCN
actualrelease14/READY/status byteequal completed227raw capture PASS. Public
all12firmware and native61 signature checked; durable untouchedcopies assets/
native/freshobservation/fullphysicalscan saved runs/retired61 beforeclearing
completedhardwarepending. Exact new62report934500... payload22cde47...433source/
176generated/130fixture/native24/threeEFI/normalEMPTYQEMU/world19 gatesPASS.
USB/HCI/resident unchanged. No retry deniedHCI generationtimer scope.
Hostobserver-v2 fixes productionHTT pipe1 event0 vsWMIeventword/creditonly0;
175fakecallbacks/451purePASS, hostgate55negatives, monitor75fakecases+actual
f56/nativeGATT2e/2f ABI; transition10offline tests, independentreview26checks.
Model resultsNOTphysicalHTTsuccess. Versionquery only/nonRF/noSSID/password.

Native62 locallysignedONCE saved pci-native-7meuoneq; exactpackageSHA
874b02081c58525bc2fb2efaec0dd3f3b53d84b8a64f8955ab93dcd17fb27ca5.
SolecontrollerPID90808 htt62-root-route-v1/continue62.py,
metadata runs/control/controller62.json/logcontinue62.log. FIRST inspectPID/
state/receipts beforeanyaction; nosecondBLEcontroller/noresign. Atthissnapshot
queried priorphysical61 receipt, native62notyetconfirmedAPPLIED. Controller
thenexactdeliver→freshQPD18→sign12gen62firmwareonce→query/resumeonlyordinary
progressingtimeout→QWBTphase5→QHTTgen62actualall14release→30rawpages twice/
3statuses/67callbacks→Rootclassifier. Realdisconnect/no progressstops/saves.
Rawouter660s; bootstrap5580s hostbound unchanged. QHTTfailure stillrawexport
diagnostics, VERSIONpass requires actualowned raw/IE6/op3; noHTTdataplane/
SSID/association/keys/IPclaim. Maccachemayneed supportedrefresh ifnewGATT
missing; noblindreplay. Evidence root62-prepared storespublicmanifest/
retirement/freshread/hashes. Ownerhotspot iPhone (9) enabled; remainsNEXTscan
target only, HTT62 doesnot scan. Passwordnotcollected. Dellnotrebooted.

Native62 controller90808 exited ordinary progressing300s native-stage timeout;
lastconfirmed156400/173856 aftertwooriginalpaced attempts (logs1/3), noactual
disconnect/CBError/regression. Exactsessionpci-native-7meuoneq/statesaved,
engine61 remainsuntilAPPLIED. NEWisolated htt62-native-resume-v1/resume62.py
validatesstoppedlog hash/exactpacket/currentgate andrequiresoldPIDsgone, then
execsame frozencontinue62.py queryingbeforewrites. Sole newPID92963, metadata
htt62-root-route-v1/runs/control/controller62-resume-92963.json; log
htt62-native-resume-v1/runs/resume62.log. Zero newnative signatures.
No secondBLE/nofirmware62signedyet/noDellreboot. CheckactualPID/state/logs
beforeanotheroperation. Wrongstatus/counter/nonprogress rejected in3checks.

Physicalnative62 EXACTAPPLIED confirmed: package874b0208... sessionpci-native-
7meuoneq/counter62. CommitCBError7 recoveredbyoriginalsame-sessionquery; exact
receiptSHA/session/counter matched, notassumed. stateengine62/nativependingnull.
SolePID92963 continuesfrozencontinue62.py viaresumev1; initial62QPDsetupPASS,
exact12gen62firmware locallysignedONCE sessionfirmware-ram-8wiq3vc5. Firstchunk
notyetaccepted; ordinary240s progress43200 resumedexactpacket; latestconfirmed
floor51360/65760 atthissnapshot. Actualreports/logspriority. DoNOTrestart
controller/re-sign/replayprior61firmware. NoactualHTTversion/IP/SSIDyet.
Evidencephysical62-APPLIED retains exactreceipt/commit/signaturemanifest hashes.

### 2026-10-08: physical62 HTT VERSION_CONF3.56 confirmed, all14 released

All12 exactsignedfirmware62 chunksaccepted bitmap4095/ready1/fullcontainer.
QWBTbootstrapphase5 succeeded; QHTTphase3/error0/versionmajor3/minor56/
submittedDMA1/actualrelease1/CLOSED. SolePID92963 subsequentlyexited after
originalrawreader secondpage UUID81 CBATTError1 invalidhandle. No replay or
resign. Repeatedowner-authorized20s MacBluetoothoff/on viaSystemSettings,
restoredON; separatezero-write freshreader understate_lock/current62 and
all12publicsignature/fullcontainer check completed.

Newfreshcapture67actualcallbacks/error0,3byteequalstatuses/30pagesx2equal;
Rootclassifier PUBLIC62signaturebase61/world19+firmwareIE6/op3+ownedslot0
HTC VERSION_CONF abovecompletionfloor+DMAverified =>
PHYSICAL62-OWNED-HTT-VERSION-CONF-RELEASE14, HTT3.56. All14actualresources
released. Evidencephysical62-HTT-VERSION-CONF retains originalfailedraw/
monitor and freshcompletecapture/classification/fullfirmwaremanifest/hashes.
No livecontroller/reader now. Currentstateengine62/hardwarependingcompleted
firmware-ram-8wiq3vc5; doNOTclear orreplay withoutdurable reviewedretirement.

This provesboundedHTTquery/response, NOTdataplane/RX-ring/MSDU/PEER_MAP/
SEC_IND/scanSSID/association/keys/IP. Causeofscan61 missingbeacons stillnot
proved. Nextimplement/review actualHTT RX-ring/frame path (respect realop3/
firmwareTLV/layout/ownership/DMA/credit/lifetime), thencombine appropriate
station scan/managementreceive with fresh target iPhone (9), ownerhotspot
enabled. Mac remainscommand/signing; allC/ASAN/COFF/QEMU onlyYukabox; noLinux
Dell/noHCI deniedscope/USB/bootstrap/flash/reboot/secretread. Priorworld19
modelpreservationverified; no newhumanphysicalrenderobservationclaimed.
WiFi/IP/router/Yukaboxdataexchange STILLNOTconfirmed; automation staysACTIVE.

### 2026-10-08: next RX/scan software preparation; minimal filter63 trial planned

Currentphysical62 completeHTT3.56/release14 unchanged; noactivecontroller, no
newnativecounter/signature/devicewrite. Primaryath10kcore QCA9377PCI hw1.0/1.1
sets hw_filter_reset_required: supportedTLVdummySTAcreate0→delete0→actualECHO
reply barrier precedes HTTstartup. TLVops lacksgen_pdev_set_base_macaddr, core
toleratesEOPNOTSUPP; doNOTinventbaseMACcmdfromconstants. Source reviewfrozen
htt-rx-startup-review-v1/evidence/review.json e001f9cb...; hardwarecauseof61
missingMGMT STILLNOTPROVEN.

Chosenfirstboundedpartial experiment63: actualREADY.mac dummycreate/delete/
ECHO(ownedraw+arg+epoch/newRXfloor+actualDMA)→actualHTTversion→reviewed13channel
passive0x21/emptyprobe lists realSTA scan matching exact b'iPhone (9)'10bytes.
NOTfullath10kstartup/dataplane; RX_RING_CFG+AGGR stillfuturematurebaseline.
All14existingDMAowners remain. Nocredentials/WPA/IP. iPhonecompatibility2.4GHz
question pending; optional, keepsoftwareworkindependent.

Frozenfilter-barrier-v1 report18890d3f...140125ASAN/UBSAN+pinnedoracle/5COFF
ONLYYukabox. BODYONLY; qcaPersistentTx SOLEHTC/credit/CE3owner; immediatePOSTED
observation BEFOREnextRXpump mandatory. ActualECHO beforeDMA cannotpassuntil
DMAcompletion; DMAalone NOTbarrier. RXcreditsalreadyappliedonce, noseconddebit.
FrozenRXdecoder-v1 report049bcdf7...705ASAN/COFF/oracle; ring-v1 report79c43f57...
27764ASAN/COFF/oracle. These AREPURESOFTWARE/noDMAallocated/nophysicaladmission.
Defaultfuture2048ring/fill1023 proposes33realextra maps/47total/~2.1MB runtime;
notfit/native/lifetimeadmitted. Fullreorder requiresactualTLVservice65 low4bits
perword, NOTversion3.56. RX_IND FIFO/reorder/fragment/datareassembly remainmissing.

Native63 producerbeingbuilt in filter63-native-v1, provisional/unfrozen. New
localraw/payloadbyteunion savesduplicate2040bytes perrecord tofit4MiB; fixed
unbundledHTC payloadraw+8 only. Mustrebuildactualproducer/ASAN/COFF/wholeEFI/
world19 andindependentreview; pure4081unionmodelnotABI/nativeadmission.
Retainactualrawtrailer; normalizedexportvirtualpaddingmustnotzerooriginalraw.
Handlevalidcreditonly/HTTunrelated frames beforeoldscandispatch, preserveowned
raw, avoidfalsefault11/doublecredits. Host63awaitsactualproducer/GATTschema;
Rootprefersfullraw56header+2048/5pages with22slots110pages cap. No physical63
untilall exactgates/admission/fresh62release/durablearchive prepared.

Rootfilter63-root-route-v1 transition62.py/observe62.py publicpreparation:
actualold62signednative/all12/full67rawversion/release proofPASS;9readonlytests
and31independentadditionaltestsPASS. Explicitfrozenbindings callback_join
added; genericmodules/sys.path preserved. No keys, state writes or BLE invoked
bythispreparation. New63gate/retirement/controller notready. Preservecompleted
firmware62pending; neverclear/replay/re-sign withoutrevieweddurabletransition.
DoNOTretrydeniedHCI generation/timerscope; Maccommand/sign only, nativeC
ASAN/COFF/QEMU ONLYYukabox, noLinuxDell/USB/bootstrap/OTP/flash/reboot.

### 2026-10-08: isolated filter63 actual software pipeline/whole EFI verified

Physical62/world19 unchanged; no live BLE controller, new63 signature/counter,
retirement or firmware operation. New filter63-native-v1 final unsigned producer
passed sixteen actual driver/native synthetic ASAN/UBSAN scenarios,92 actual C
query-handover checks and15 COFF modules ONLYYukabox. Includes earlyREADY52-byte
retention across latest16-byte credit-only input before INIT DMA, wrong/missing
ECHO,unsupportedHTT,wrongSSID,scan faults,mixedHTT and archive16 overflow.
Whole EFI202240/mapped4194304 exactly immutable4MiB; three builds identical;
normal/EMPTY QEMU distinct images, exact world19 timing/semantics PASS.
Candidate report ba46f2c04021b71744a45a0fc31769d93629062422b8a6fbf878e66d8767fe37;
payload a636b40f10103a90879bad00a55de173fa36ab2b7a4fd4f38262825191bf4442;
native report ca983db6fb2e9723a0f4371442307c2f3684cf5244fc6a22e1008167c9e543cc;
reproduction931d3174122b73cc60a4856c5a165273e951528a684fd3ddf9e1dd7a4f08f4f0.
Root exact public technical gate verifies473repo/207generated/161compiled
fixture inputs,15COFF/twoactualsanitizer executables,fullPE/QEMU/world19.
This remainsPARTIALstartup: noRX_RING_CFG/AGGR/association/keys/IP. Frozen
oldproduction untouched; noHCI generation/timer forbidden scope retry.

Root63 draftgate/route/assets/controller/classifier prepared; final independent
review/host63 freeze/admission stillpending. Retirement12syntheticFS testsPASS
includingfsyncbeforestate-save/corruption/symlink/race; NOTactualretirement.
Gatealone cannotauthorize signing; admission UNFROZEN stillrejects. Final
hostbindings mustjoin exactproducer448QF63/416QSCN/22x2104QFEX before fresh62
observation, durablearchive, one localsignature and sequentialphysical trial.
Fresh62read NOTyetinvoked; preservecompleted firmware62hardwarepending.

### 2026-10-08: actual62 fresh read; native63 host semantic correction

Realzero-write pre63-observation-1 confirmed exactAPPLIED62/currentstateSHA
bc39c023... and unchanged ownedHTT3.56/release14; archivedpublicevidence. Its
300s freshness expires normally; MUSTreread beforefinalprepare ifexpired.
Noactualretirement/newcounter/signature/BLEwrite; actual62world19 unchanged.

Rootfound frozenobserver-v1 treated filter.tx_completed (last-commandBOOL1)
as cumulative3 and frozenmonitor-v1 finalJSON mislabeledgeneration62. V1
scopes retained unchanged/notused. Newobserver-v2 proof fdbb11cd...511fake+
1189pure; monitor-v2 proofce28833b...100fake+4 actualfinalJSON63cases; hostgate
55tampercasesPASS. Rootusesv2 only. New independent native63-host-oracle-v1
report535a1dc3898d2f6f2d615f3aec1804b62ff5ca641ebbba49c76196f9a626e4d3,
ONLYYukaboxASAN/UBSAN3actualproducer cases+COFF, exact160frozenmodelcompiler
inputs+8candidate supplements. C emits tx_count3/tx_completed1; ordinary+
earlyREADY→purev2completed/target/ownedtrue, missingECHO→allfalse. ALLcaptures
explicitlysynthetic-actual-C-producer; physicalcallbackgate rejects them.
Rootoracle/hostgates recheck exactinput/capture/executable/hash joins.

Final independent63 source/model/orchestration review currentlyrunning.
Rootadmission literal UNFROZEN; no63physicaloperation untiladopted. Exact
producerreport/payload/softwareclosure remain ba46f2c0.../a636b40f.../473/207;
no newCnativebuild/firmware replay justbecause hostdecoder changed. NoSSID/IP
physicalclaim; fullRXring/aggregationstill absent inthisboundedpartialtrial.
