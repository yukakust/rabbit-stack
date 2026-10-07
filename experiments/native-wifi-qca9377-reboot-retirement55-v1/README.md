# Full native55 lost-link recovery — offline proposal

No reboot has been authorized or performed by this module. No state writer,
Bluetooth operation, signature creation or private key loader exists here.
`gate.py` verifies public signed native55 + all12 signed firmware parts and the
642-source closure. It accepts only a separately archived exact pre-recovery
state, explicit owner reboot authorization bound to its hash, actual owner reboot
confirmation, and a fresh real known-peer 60-byte EMPTY/counter0 read plus log.
Its conditional PASS does **not** mutate state, clear pending, reserve56, or prove
all14 owners released. Models cannot replace actual evidence. Root must recheck
freshness and unchanged state under its sole operational lock immediately before
any separately reviewed retirement action.

## Reviewable sequence

1. Root archives exact current state, native55/session/report/payload and signatures,
   all12 firmware packets/report/actual acceptance checkpoints, checked642 closure,
   latest BOOT17/completed258 and discovery failure evidence, world17/package.
   Validate public_bundle and state binding before asking for a reboot exception.
2. Explain that city is alive but Bluetooth is inaccessible. A reboot loses the RAM
   city, firmware and unexported55 scan records; it resets the Wi-Fi chip. It is an
   exceptional recovery, never a normal success or inferred checked-owner release.
3. **Only if explicitly authorized by the owner**, record authorization and actual
   reboot observation. Root performs known-peer read-only bootstrap query. Require
   genuine EMPTY/counter0, timestamp after reboot, <=300s fresh, exact saved query
   log. If peer still absent or receipt differs, stop with original pending intact.
4. Archive all exact inputs before retirement. Root's separate reviewed, locked
   retirement writer may retire only hardware_trial_pending for this exact55;
   preserve native counter55 and signed55 bytes, record reboot-lost raw55 as unknown,
   never manufacture 22-slot/raw110 exports or all-owner proof.
5. Prepare **plain city** next native counter56 from authenticated public-owner
   preflight and exact world17 semantics. It uses bootstrap runtime + empty-world
   base after reboot, not native55 runtime. Existing offline HTT56 is NOT signed or
   consumed. Future HTT must be derived with a new counter if city56 is reserved.
6. After the complete recovery proof and separate root admission, sign56 once,
   send exact saved session, confirm genuine APPLIED and restored world receipts,
   then request screen/tail observation. USB/bootstrap remains untouched.

## Remaining gates

Actual owner reboot authorization, reboot confirmation and fresh EMPTY are absent.
Root must supply archived pre-recovery state and actual BOOT/discovery evidence;
this module never reads production state itself. Plain-city preflight is host-only;
receiver after reboot must be verified before signing/transmission admission.
`test_gate.py` uses explicitly synthetic HOST fixtures, never physical receipts.
