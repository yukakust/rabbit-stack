# Guarded native55 recovery — executable ROOT route

**No user reboot authorization exists yet. No live retirement, signing, reboot or
Bluetooth operation was performed during development.** Tests use copied state,
explicit synthetic authorization/EMPTY, and a mocked private-key boundary.

`route.py retire --apply` uses the same nonblocking `state.lock` as the existing
controller. It requires byte-identical current state and archived before-state,
exact signed55/full12/642 closure, an inactive journal, explicit owner reboot
permission bound to the before-state hash, actual reboot confirmation and fresh
known-peer EMPTY/counter0/log. It archives exact signed packets, original reports,
logs/checkpoints, current world17, checked55 and all decision inputs FIRST. Every
archive file and all nested directories are fsynced bottom-up, including the
archive entry's parent. Only then does it atomically replace state, changing
hardware_trial_pending to null and appending the exact55 retirement audit.
Counter55, world17, signed original reports and packets stay intact. The audit
records unexported55 raw as lost after reboot; it does not claim all14 checked
owners released, a successful scan or any Wi-Fi connection.

`route.py admit` is read-only. It verifies the exact retirement transition and
all archives/sources, unchanged state, genuine still-fresh EMPTY, original
completed_reservation, installed owner gate/image, current-world and previously
Yukabox-checked plain-city recovery gate. Target is native56/world18 with the
same world17 semantics. Existing offline HTT56 is untouched and unconsumed.

`guarded_prepare56()` is an executable adapter around the **unchanged** original
`reboot_recovery.prepare`. An isolated module instance overrides only its
reservation/gate/engine references; the original prepare retains the actual
state.lock. Full admission/state/journal/source/freshness and exact55→56 identity
are rechecked at reservation, gate and immediately before load_private. Overrides
are restored on success or rejection. No real invocation or key loading was done.
If preparation is rejected after creating a candidate directory, that unsigned
partial directory is retained for review and must not be reused or sent.

## Reviewed ROOT actions, only after actual owner authorization

1. Archive explicit authorization with `action=controlled-dell-reboot-for-native55-recovery`,
   native_counter55, exact before-state SHA, authorized_at and trusted user-message
   reference. Perform only the authorized reboot; obtain its actual confirmation.
2. Run the existing known-peer read-only bootstrap query. Save exact log and
   original observation. Extend the observation with actual reboot_confirmed_at
   and authorization_sha256, retaining the original raw receipt/timestamp.
   Require EMPTY/counter0; otherwise preserve pending55 and stop.
3. Set ROOT's validated paths. `S` is the existing operational state, `B` the exact
   root-before-recovery/before-state.json, `A/O/L` genuine authorization/observation/log,
   `D` a NEW archive directory in an existing parent, `C` frozen plain-city proof:

   ```sh
   python3 /Users/yukakust/rabbit-stack/experiments/native-wifi-qca9377-reboot-recovery55-root-v1/route.py retire --apply --state "$S" --before-state "$B" --authorization "$A" --observation "$O" --query-log "$L" --archive-output "$D"
   python3 /Users/yukakust/rabbit-stack/experiments/native-wifi-qca9377-reboot-recovery55-root-v1/route.py admit --state "$S" --retirement "$D/retirement.json" --checked "$C"
   ```

4. ROOT invokes `route.guarded_prepare56(S,D/'retirement.json',C,new_candidate,owner_private_locator)`
   only after reviewing admission. The private locator is not printed. This
   wrapper is the only reviewed prepare adapter; do not call generic prepare
   directly between a separate admission and signing.
5. Original `reboot_recovery.restore` must again query genuine EMPTY and validate
   the saved plan before transfer. It archives superseded native55 references
   under the original protocol. Exact native56/world18 receipts are required;
   ROOT then requests physical city/tail confirmation. No USB/bootstrap edits.

## Crash/failure contract

Archive failure, nested directory-fsync failure, stale/wrong receipt, lock
contention or changed state/journal rejects before pending retirement. An archive
left by a crash before state replacement is preserved, never auto-deleted or
reused. Admission after a crash requires exact after-state and matching audit;
otherwise ROOT reviews the intact old pending and archived bytes. Nothing can
turn synthetic tests into physical recovery evidence.
