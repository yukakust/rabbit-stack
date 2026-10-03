# Connected owner supervisor v1 — emulator-tested candidate

This connected file service delivers ordinary worlds and owner-signed combined
Scene/radio native drivers without USB shuttling. Physical Dell evidence now
includes driver1->2 (walking cat/blue line), driver2->1 (blue line removed), and an
exact rejected nativecounter3 receipt for the reviewed unhealthy module. A new
connection confirms the rejection receipt is retained. Owner confirms the cat still walks and the blue line is absent after rejection;
nativecounter3 is consumed, so any
fresh native release must use at least4 with a refreshed review.

Radio reliability remains under investigation: long unpaced staging lost root
state even with stronger RSSI. Two100-byte/50ms-paced long prefixes succeeded,
including world2 restoration by exact receipt and native3 staging35000/36640;
small unpaced tails then completed. This supports a candidate mitigation, not a
proven cause or general reliability. See `evidence/dell-radio-pacing-comparison.json`
and `evidence/dell-connected-native-trial-3-rejected.json`. Discovery/status are
not authenticated device attestation. Earlier candidate sections are historical.

## LE packet-boundary repair and diagnostics (2026-10-02)

Actual C replies used first-fragment PB=10, forbidden for LE Host -> Controller.
They now use PB=00, with PB=01 for continuations and BC=00. Controller -> Host
receive parsing still accepts its direction's PB=10. The defect is independently
reproduced, but its responsibility for the physical disconnect is not yet proven.
See [Bluetooth Core, HCI ACL packet boundary flags, section 5.4.2](https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Core-60/out/en/host-controller-interface/host-controller-interface-functional-specification.html).
Host tests assert EVERY outgoing reply header, including fragmented reads. The
real UEFI QEMU mock now rejects invalid LE outgoing flags instead of silently
accepting the defect.

Driver ConOut prints advertising ready, connection and disconnect transitions.
Poll errors print hexadecimal code, link state and pending HCI opcode. Root fatal
paths print the failed stage before existing watchdog recovery; unknown outcome
still forbids unloading or claiming radio off. Poll codes: 1 arguments, 2 event
size, 3 interrupt transfer, 4 bulk size, 5 bulk IN transfer, 6 command transfer,
7 ACL OUT transfer, 8 packet kind, 9 controller/parser link fault. These are small
diagnostic codes, not raw USB status or a complete trace.

`run_qemu.py --fault-test` injects mock USB bulk-IN failure into the actual root
loop, records the real driver/root ConOut calls (forwarded to firmware), checks
code 5/state 2 and root stage, captures the visible screen, then observes watchdog
reboot. This fixture-only fault/proxy cannot enter production images. New physical
installation is NOT authorized by the request to fix and test this candidate.

The baseline contains generic RUP2/RUP3 RGBA/RLE assets/VM, not baked-in cat art.
It boots into an empty safe world. RAM worlds and downloaded drivers are volatile;
power-off/reboot restores that baseline, not the last downloaded cat.

## Raw HCI diagnostic candidate (2026-10-02)

The owner installed the PB-fixed candidate, but Mac still disconnected during
service discovery at phase0/offset0. Dell photo remained at advertising-ready,
without connection/error messages. Esc returned to UEFI's missing-disk notice;
owner then powered off. No successful radio cleanup or physical cause is proven.

This diagnostic build observes the **existing sole interrupt read** before its
bytes reach the parser. `USB EVENT LEN=... STATUS=... RESULT=...` and `HCI RAW:`
show reported length, full 64-bit EFI status, USB result and up to 24 valid bytes.
Numbers are hexadecimal. Standard LE Connection Complete is 21 bytes and fits.
Up to 48 observations per driver attach are printed; larger events are explicitly
prefix-only. Normal unchanged-length timeouts are counted, not printed as data.
Failed/oversized reads show metadata only, never uninitialized buffer bytes.
Four bounded heartbeat samples show successful event reads and timeout counts,
at poll counts 1024/4096/16384/65536 (not a claimed number of seconds).

Mismatched HCI lengths and unhandled LE subevents get explicit labels, but the
parser/protocol is NOT changed to accept them. No extra USB reader, HCI command,
radio authority, async callback or persistent write is introduced. Console output
can affect timing; this is diagnosis, not a throughput benchmark.

Mock-USB tests cover rejected input visibility, prefix bounds, oversized lengths
and timeout/partial-read metadata. QEMU fault fixture supplies malformed and
unsupported events followed by a valid connection and injected USB failure;
actual driver ConOut output must contain the raw bytes and classification before
watchdog recovery. This is not a capture from the physical Dell. The installed
image remains unchanged until separately approved installation of the diagnostic
candidate after a fresh owner-public Mac gate and device-identity check.

## Boundary

- Immutable supervisor: owner root, loader/verification, root-owned file staging
  and receipts, framebuffer, synchronous timers, watchdog, cooperative dispatch.
- One resident privileged driver: Scene/Anima renderer/VM **and** HCI/ACL/L2CAP,
  ATT/GATT and UEFI USB adapter. No old interrupt reader is running alongside it.
- ABI3 extends RSS2 Scene state with attach/poll/close/command/world callbacks;
  every returned callback address must lie in the loaded PE's executable section.
- RRT3 has a new Ed25519 domain, ABI3/state2, exact target/base/payload/world hashes
  and in-boot native counter. RRT1/RRT2 cannot silently become this new profile.
- World authority remains distinct: the public development Creator can authorize
  data-only bounded worlds, **never owner-native drivers**.
- Native updates are privileged reviewed code, not a sandbox. Neither signature
  nor watchdog guarantees recovery from corrupt memory or disabled interrupts.

Driver entry/init/health do not attach the radio. A trial imports the exact live
RSS2 state on a separate surface, exports it identically, and runs one health tick.
Failed trials retain the prior world/driver. Successful trials require old-driver
radio cleanup before unload; attaching the replacement happens in the root loop,
never during an ATT callback still on the old driver's stack. Attach failure
reattaches the old driver. Uncertain cleanup/unload remains under watchdog instead
of claiming success. No asynchronous driver-owned callbacks are registered.

Cleanup confirms advertising-off, known-handle Disconnection Complete, then a
controller-wide HCI Reset completion barrier for delayed events. Setup uses a
fresh Reset too. These reset volatile controller state, not controller flash.
See [Bluetooth HCI Reset semantics](https://www.bluetooth.com/wp-content/uploads/Files/Specification/HTML/Core-54/out/en/host-controller-interface/host-controller-interface-functional-specification.html).
QCA RAM-patch survival through the existing post-load reset was previously
observed; this new repeated-close/reattach sequence remains Dell-test pending.

## File transfer

The connected experiment's UUID/MTU/offset protocol is retained. Kind1 accepts up
to 65,535 signed world bytes; kind2 up to 262,144 owner-native release bytes.
The root, not the unloadable driver, owns staging and the final 60-byte receipt.
State4 is pending: SHA256 transport is complete but application is NOT confirmed.
Only the root's deferred result changes it to applied/rejected. Pending state
rejects abort/substitution/writes; retries cannot queue execution twice.

Successful native replacement intentionally closes the connection. The Mac sender
reconnects (three attempts, overall 300s), queries the SAME saved nonce/session,
and requires exact SHA256/counter/application status. A normal ATT Write Response
is never a final receipt. Lost final response can be queried without a second swap.
Receipts are correlated, not authenticated Dell attestation. No pairing/encryption
is implemented; untrusted peers can still cause denial of service.

Native receipts use uint32 counters; C and Python reject larger values instead
of truncating. Native/world counters are separate, in-boot only. Authorized failed
health trials consume their native counter. Reboot loses anti-replay state.

## Tests and remaining physical gate

```sh
python3 verify.py
python3 ../ble-connected-file-transfer-v1/verify_link.py
python3 ../ble-connected-file-transfer-v1/verify_usb.py
python3 run_qemu.py
python3 run_qemu.py --loop-test
python3 run_qemu.py --fault-test
```

Host checks cover C/Python signatures, profiles, owner/world-key separation,
counter/PE gates, pending/deferred/idempotent root receipts and transport limits.
Existing actual C renderer/GATT/link tests carry the detailed cat and reject bad
worlds, including targeted 128-bit service discovery at default MTU. Mock UEFI
USB tests cover identity, close acceptance/completion distinction,
connection-during-close and unknown final Reset.

The QEMU integration uses real UEFI LoadImage/StartImage/unload, real compiled
drivers and a MOCK USB controller. File bytes traverse its bulk ACL/L2CAP/ATT path
into the supervisor-owned receiver, not a radio shortcut. It observes two combined
driver swaps in one boot, receipt-only retry, failed health/tamper retaining the
exact previous live state, then a signed interrupts-enabled hung init triggering
firmware watchdog return to the immutable baseline. A separate QEMU run exercises
the **actual root loop**, timers and confirmed Esc cleanup. These are not QCA
emulation, real Bluetooth measurements, or proof of Dell watchdog behavior.

`preflight.py` runs these checks, compiles the real Mac sender **without starting
Bluetooth**, repeatedly builds an owner-public provisioned image, then opens that
exact image in Mac QEMU. Missing 0CF3:E009 must show:

```text
RABBIT CONNECTED SUPERVISOR v1.0
TARGET NOT FOUND; NO DEVICE WRITE SENT
NO RESET; NO HCI; NO SCAN; NO RADIO; POWER-OFF ROLLBACK
```

On Mac, in this directory:

```sh
python3 preflight.py --owner-public "$HOME/.rabbit-owner/runtime.pub"
```

After visually checking the lines, close QEMU and type `YES` when asked. Artifacts
are create-only in ignored `runs/owner-gate-*`; the image/report paths and hashes
are printed. The private key is not accessed. The command performs read-only
`diskutil list external physical` and **never unmounts/erases/writes a medium**.
Fresh `diskutil info` identity and review remain separate before installation;
historical disk4/disk10 are stale. Do not reboot the working Dell for these checks.
If a check fails, preserve its log and stop before media replacement.

`--test-key-only --headless` is a non-installable Linux capture path. It produces
a screenshot requiring visual review; it cannot claim an owner Mac observation.
Fixture public keys are explicitly forbidden for production images.

## After separately approved installation (not now)

Compile/sign data-only worlds with the unchanged V3 compiler/save-world tools,
then prepare a stable connected session:

```sh
python3 prepare_file.py /tmp/active-world.rup --kind world --counter 1 --output /tmp/cat-file-session.json
python3 send_file.py /tmp/cat-file-session.json --send
```

Native releases require explicit owner-local `sign_runtime.py` with a reviewed
payload SHA256, new target/base hashes, exact active signed world and native
counter. Old RRT2 artifacts will not work. Wrap the result with `prepare_file.py
--kind runtime`, then the same `send_file.py --send`. Private key never enters
the packet. Do not send fixture keys/modules to physical devices. Unknown delivery
means rerun the SAME saved session while Dell remains powered, not create a new
nonce or reset it. Faster writes have no artificial 450ms UUID dwell, but actual
Mac/Dell speed and interoperability must still be measured.

Future ordinary graphics, VM and radio-driver changes fit this owner-updateable
boundary. Owner-root/immutable loader/ABI or incompatible hardware changes may
still require a bootstrap migration; this is not a last-USB-ever guarantee.

## Missing connection event: controlled 20ms candidate

The owner-installed 1ms baseline received seven setup command completions, then
only `05 04 00 01 00 13` (disconnect, remote termination). The Mac disconnected
during service discovery at offset0. Neither a successful file nor a physical
cause is established. Host tests verify the general/LE mask bit positions and
acceptance of a complete21-byte connection event with the observed handle/buffers.

This candidate changes only synchronous **interrupt-IN** waiting from1ms to20ms
(including bounded close searches). Bulk-IN waiting, masks, GATT protocol, file
signatures and world contents are unchanged. It records descriptor max-packet and
raw bInterval at attach, and prints the exact two masks after successful USB control
submission. Raw bInterval is NOT labelled milliseconds: its units depend on speed.
All reads remain synchronous, exclusively owned, finite; no unloadable callback.
Each close search retains its128-attempt bound (at most2.56s requested USB waits
per search, excluding firmware/command overhead); watchdog/unknown-outcome gates
remain required. Idle polls may be slower; no throughput/animation benchmark claim.

Synthetic mockUSB/QEMU timing fixture requires at least2ms for a connection event.
It tests the policy, **not** Dell's actual timing or a recovered physical packet.
An unchanged-length timeout still cannot safely be treated as received bytes.

After fresh owner preflight and separately approved exact-image installation:

1. Photograph `USB EVENT MAX_PACKET`, `BINTERVAL RAW`, `TIMEOUT MS=00000014`
   (hex14 is decimal20), submitted masks and `READY TO CONNECT`.
2. Send the SAME saved `/tmp/connected-cat-session-1.json` once. Do not rebuild it
   or increase its counter merely because transport failed.
3. A new `HCI RAW: 3E 13 01 ...` plus `BLE CONNECTED` supports progress at the
   event boundary; it does not yet prove file application. Require exact final
   receipt AND a visibly walking cat for that milestone; record elapsed time.
4. If only disconnect arrives again, reject timeout increase as a sufficient
   fix. Preserve Mac log/Dell photo; inspect controller suppression/USB behavior
   next, rather than repeat blind sends or change GATT/graphics.

At the time of that candidate, physical connected delivery remained PENDING. No media-write authorization is
inferred from building/testing this candidate; never reuse an old gate or disk id.

### Owner-observed connected delivery and Mac-only resume check

The owner installed the exact gated image, received the exact file receipt and
confirmed the ginger cat walking. See `evidence/dell-connected-cat-owner-observed.json`.
The first link timed out at sender offset17040; the second reported offset0 and
completed. This proves reported delivery, NOT retained nonzero resume. The cause
of staging reset is unknown; elapsed time was not recorded.

The Mac-only sender now queries receiver staging every approximately4096 bytes,
reports regression of confirmed offsets, and measures elapsed time including
reconnects. The receiver's status remains authoritative, never a guessed client
offset. A strict shared C validator requires exact session/length and final
SHA256/counter; a staging checkpoint is NOT application. Pending receipt timers
cannot query a disconnected peer's old characteristic. No Dell image change.

For a controlled experiment, keep Dell powered and use a NEW saved counter2 cat
session (counter1 is already applied). First run `python3 send_file.py` on Mac:
this only compiles, without starting Bluetooth. Then prepare without sending:

```sh
python3 ../x86-64-uefi-wireless-supervisor-v1/save_world.py ../x86-64-uefi-god-runtime-v3/worlds/ginger-cat-walk-v1.json --counter 2 --output /tmp/connected-cat-world-2.rup
python3 prepare_file.py /tmp/connected-cat-world-2.rup --kind world --counter 2 --output /tmp/connected-cat-session-2.json
```

Both commands refuse to overwrite existing outputs. If they exist, preserve and
reuse the existing matching session rather than regenerate its nonce. Prediction:
ordinary disconnect retains the receiver-confirmed prefix in the same boot.

```sh
python3 send_file.py /tmp/connected-cat-session-2.json --send --stage-only-bytes 8192
python3 send_file.py /tmp/connected-cat-session-2.json --send
```

Run the second command only after `STAGED-NOT-APPLIED`; keep Dell powered between
them. The stop threshold may round up to the next write boundary. First command
does NOT COMMIT and keeps the previous cat active. Second must show a nonzero
`RESUME OFFSET` matching the confirmed prefix, then an exact final receipt. If
it returns zero, preserve Mac/Dell diagnostics: this falsifies retained resume
for that run. Do not silently label a full restart as resume. Power loss still
loses all RAM. Mac compilation and this physical interruption test remain pending.

That pending status is now superseded: owner Mac compiled successfully, stopped
at8400, then a new process resumed at8400 and received the exact counter2 receipt.
The remaining transfer took15.525s, NOT a measured full-file transfer time. See
`evidence/dell-connected-resume-owner-observed.json`. Unexpected link failures and
watchdog recovery remain separate checks.

### First owner-native trial through the connected channel (no USB)

Use the existing owner-gated `driver-revision-2.efi`, not a freshly rebuilt image.
This reviewed engine revision adds a blue bottom line while preserving the exact
cat package, live positions, frames, tick and world counter through RSS2 import.
The full ginger-cat counter2 QEMU/mock-USB scenario is now available:

```sh
python3 run_qemu.py --graphics-world
python3 prepare_native_trial.py --installed-report runs/owner-gate-s0bxi9d8/report.json --world-package /tmp/connected-cat-world-2.rup --world-sha256 cc545d03b210bd3ebdef2141368bd6daa90cc3ec966b7cfb357afc53d30d7645 --owner-public "$HOME/.rabbit-owner/runtime.pub" --output /tmp/connected-native-trial-1.json
```

Preparation reads only the public key. It checks the existing saved image, gated
production sources, exact gated module2 and currently applied world bytes. It
requires a production owner-observed gate and refuses overwrite. It does not build
or install a bootstrap, sign, start Bluetooth, or touch a private key.
Assumptions: same Dell boot, baseline driver1 still active, no native trial yet.
Native counter1 is separate from current world counter2.

Review the resulting plan and its printed SHA256 before explicit signing:

```sh
python3 prepare_native_trial.py --sign-plan /tmp/connected-native-trial-1.json --private "$HOME/.rabbit-owner/runtime.key" --reviewed-plan-sha256 REPLACE_WITH_REVIEWED_PLAN_SHA256
```

This rechecks all bindings, verifies the private key matches the provisioned public
key, signs and independently verifies RRT3, then saves create-only `.rrt` and
`.session.json` files. Private bytes are never printed/sent. The placeholder is
NOT a literal shell command. Only after review/signing, send the saved session:

```sh
python3 send_file.py /tmp/connected-native-trial-1.session.json --send
```

Expected: an intentional disconnect, re-advertising/reconnection, exact applied
receipt, Dell `OWNER DRIVER COMMITTED; RECEIPT RETAINED FOR RECONNECT`, the same
walking cat and a blue bottom line. A disconnect alone is NOT application. Retry
only the SAME saved session to query a lost receipt, never create another nonce
or re-sign to hide an unknown result. Collect both Mac and Dell output.

On failed health, previous live world/driver must be retained. This is QEMU-tested,
NOT physically proven yet. Uncertain radio cleanup invokes watchdog and may lose
RAM world/state on reboot. Privileged native code is not isolated; no guaranteed
recovery from arbitrary memory corruption/disabled interrupts. Do NOT send the
deliberately unhealthy/hung test modules to Dell in the initial trial. Keep the
working bootstrap USB in place; no new media write is required.


### Inspect or cancel a saved staging session on Mac

`send_file.py SAVED_SESSION --query-only` connects and reads the current60-byte
RFS status without BEGIN/DATA/COMMIT/ABORT. It prints the raw status and saved
session match. Query-only also reads connected RSSI (local radio measurement,
not device attestation); its existing timeout bounds RSSI/status callbacks.
Receipt counter is the file service's last counter, not a dedicated
query of native base/world hashes or authenticated boot identity.

`send_file.py SAVED_SESSION --abort-only` first reads status, requires that exact
nonce and stream length are STAGING, sends only ABORT for that nonce, then requires
same-session IDLE/zero length/zero received. It refuses PENDING/applied/rejected or
foreign sessions. This is an explicit cancellation of an uncommitted transfer,
not a delivery retry. Preserve logs and saved session. Both modes are mutually
exclusive with `--send` and staging-stop; compile-only remains the default.

A receiver prefix regression now stops the sender. Inspect physical scene and
status before resuming. A zero offset plus disappeared world does not establish
watchdog cause. No automatic counter increase, re-signing or world restoration.


For a known macOS peripheral, `--query-only --peripheral UUID` retrieves only that
cached peripheral and attempts a direct connection without a filtered scan.
This option is forbidden with sending/abort modes. It remains read-only and is
bounded to60seconds; a UUID is not device authentication. Scan queries now use
the same60second bound. A timeout is not evidence of its physical cause.


### Controlled smaller-DATA write comparison

`send_file.py SAVED_SESSION --send --chunk-bytes 100` preserves exact signed bytes,
nonce, counters and commit checks while reducing DATA payload per acknowledged
write. Default remains240; explicit override bounded1..240, forbidden in query
and abort modes. This changes sender write partitioning only, not receiver code.
One owner-reboot recovery comparison: default240 regressed21600->0 before COMMIT;
SAME world2 session with100-byte writes from0 obtained exact receipt in58.173s,
no disconnect. This does NOT prove fragmentation cause or general reliability.
See `evidence/dell-connected-cat-world-2-recovery.json`. Lost live positions/frame/
tick are not recovered by re-applying the signed original package.


### Staging-only pacing diagnostic

`--send --stage-only-bytes 3000 --chunk-bytes 100 --data-delay-ms 50` compares
small-write delivery with a bounded pause. Delay is1..100ms and forbidden without
a staging-only limit; this diagnostic cannot intentionally commit a release.
Timers are guarded by connection generation, peer, characteristic and offset, so
a callback from a disconnected session cannot resume a new connection. Normal
sends retain the existing immediate-next-write behavior. A successful paced trial
is not a fix unless an equivalent unpaced baseline fails under comparable signal.


### Current V3 scene from text (Mac orchestration)

`ask_connected_world.py` reuses the local subscription-backed Codex proposal runner,
with a small objects/programs edit schema. It retains the exact existing sprites,
palette, frame bytes and world identity. Velocity, placement, VM behavior, animation
period and additional objects using existing sprites are supported. Background
changes and missing artwork return unsupported; the installed runtime fixes the
background to121826. Current art is not degraded to the older16x16 schema.

Initialize once with an operator-confirmed current world JSON, exact signed package
and installed owner-gate report; these must reconstruct byte-identically. Default
state is ignored `runs/text-world/state.json`. Actual Mac state now records
worldcounter3/ginger cat with red hat, after exact receipt. Nativecounter3 is
independent and already consumed by the rejected native trial.

```sh
python3 ask_connected_world.py --initialize --world ../x86-64-uefi-god-runtime-v3/worlds/ginger-cat-walk-v1.json --package /tmp/connected-cat-world-2.rup --installed-report runs/owner-gate-s0bxi9d8/report.json
python3 ask_connected_world.py 'Кот идёт вдвое быстрее' --send
```

The agent runs these commands; the owner need not paste them. Plain intent without
`--send` prepares only. Saved `--candidate proposal.json` is also checked against
the current-world hash. Strict JSON/schema, unchanged assets, exact package/session
bindings, Python signature/bounds and actual installed V3 C signature/activation/
240-tick render checks run before radio. Framebuffer sentinel checks guard rendering.
Crypto source hashes are pinned and rechecked; runtime source is bound to the gate.
This is host verification, not physical scene observation or a permanent health guarantee.

Delivery uses100-byte/50ms-paced staging through the entire stream without COMMIT,
then SAME session for the explicit COMMIT and exact receipt. Current JSON/counter
advances only after exact applied receipt. Unknown delivery retains pending bytes,
nonce and counter, blocks a new intent and resumes via `--resume --send`. A draft
that has never started sending may be discarded with `--discard`; delivery whose
outcome is uncertain cannot be discarded this way. Local state changes are atomic
and one process owns the state lock. Scene observation remains an owner check.

World authority is the installed PUBLIC development Creator, never the private
owner-native key. This helper cannot create/sign/install native drivers or modify
the immutable bootstrap. Host evidence includes a real Codex speed proposal and
resident-C checks: `evidence/connected-text-world-host-ready.json`. The later hat
request below exercised physical asset delivery; host mocked sender tests are not
physical evidence. Automatic artwork/inventory integration and voice remain work.


### Generated artwork through the same checked path

`--world-candidate PATH` accepts a complete generated V3 data world for an explicit
asset request, mutually exclusive with the small objects/programs `--candidate`.
It shares the compiler, pinned resident-C checks, signing, saved session, unknown-
delivery handling and exact receipt gate; no native fields are accepted. Assets
are generated/edited through built-in image_gen and converted with the existing
RGBA importer, preserving genuine alpha. The small-edit LLM schema remains bounded.

First actual end-to-end asset request: owner «давай коту наденем шапку». Four-pose
red-beanie cat imported at128x85/display64x43 with original objects/programs. World3
package35017 bytes, hash8761fa34..., paced entire35049-byte stream, same-session
COMMIT, exact applied receipt in1.694s for COMMIT connection, no disconnects. Current
managed state updated fromworld2 toworld3, pending cleared. Nativecounter3 unchanged
(consumed by prior rejected native trial); no module/media/network/reboot/key action.
Owner confirms cat wearing hat on physical Dell. Movement after the hat update was not explicitly reconfirmed. Evidence: `evidence/dell-connected-cat-red-hat.json`.
No full-stage elapsed time claim; previews/240-tick checks remain host evidence.

### State-aware recovery and common status

`ask_connected_world.py --status` returns local JSON; adding `--query` archives a
read-only Dell query and includes its correlated receipt without promoting state.
Every delivery/resume now starts with a read-only query. Exact already-applied
receipts finish the local operation without DATA/COMMIT; full saved STAGING goes
straight to COMMIT. Partial STAGING resumes the same saved session, with at most
two attempts per invocation. Rejection, application pending, foreign active state
and lost receiver prefix remain distinct unresolved outcomes.

Confirmed-prefix watermarks survive process restarts through report and streamed
logs, including timeouts. The sender receives `--minimum-received` and checks it
before DATA/COMMIT, closing the read/BEGIN reset race. Receiver loss blocks replay,
new nonce/counter and draft discard; it requires receiver diagnosis. The state
lock is inherited by both Python sender and native Mac process, so an orphan
sender retains custody until bounded completion; competing controllers fail busy.

16 orchestration tests and16 native/transport host tests pass. The actual Mac
compiled the changed sender and read the retained world3 hat receipt. A separate
local fixture simulated a lost response/currentworld2+pendingworld3; real Dell
query promoted only that isolated state toworld3, with no BEGIN/DATA/COMMIT/ABORT
and byte-identical managed state. This is physical read-only receipt recovery,
not an induced physical radio failure or a radio stability fix. Evidence:
`evidence/connected-world-control-recovery.json` and referenced archives.

Global remaining milestones: [world control plan](../../docs/CONNECTED-WORLD-CONTROL-PLAN.md).
