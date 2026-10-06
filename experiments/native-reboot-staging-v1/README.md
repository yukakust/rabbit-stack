# Retiring RAM firmware staging after an owner-confirmed reboot

Controller-only retirement, not a device abort. An explicit human reboot report
and a fresh known-peer, zero-write EMPTY bootstrap receipt/log are mandatory.
Verifies current installed public owner/target gate, signed completed native
release, old partial firmware signatures/hashes/context and frozen source proof.
Rejects competing operations, wrong/stale/nonempty observations, altered packets
and already retired sessions. No private key loader or radio sender is called.
Archives exact pre-retirement state/report, all signed packet hashes and reboot
observation before clearing only hardware_trial_pending. Signed packets survive.

`test_retire.py` uses real historical signed fixtures in isolated temporary
copies. Eleven checks cover invalid evidence/bindings, corruption, dry run and
atomic retirement; private-key loading and radio calls are explicitly forbidden.
After retirement it uses the archived pre-reboot state/report, so it remains
reproducible. Observations in tests are synthetic copies, never fresh device proof.

The native47 trial had6/12 firmware chunks accepted before the user's reboot.
Actual fresh EMPTY receipt proved the receiver reset. Old RAM progress cannot
be resumed. Existing gated reboot_recovery restored plain city engine counter48
and the unchanged semantic world at packet counter17. Exact native/world receipts
are recorded separately from physical screen observation. Wi-Fi testing must
restart with fresh counter/policy/current-world gates. The previously unsigned
WMI INIT candidate called48 is now historical: counter48 was consumed by city
recovery; its payload/current-world proof cannot be reused for a new release.
