# Fixed fullboot60 collector (Mac host only)

One CBCentralManager, one cached exact peer
F45BFCB2-ABC2-AB4E-BB0F-310A54D424AF, one connection, sequential service discovery.
There is no scan, alternate peer, reconnect, retry or characteristic write.

Order: service40/value41 QPFX0001/240bytes/generation60 → service22/value23
QWBT0001/160 → service24/value25 QWOP0003/488 → service26/value27 QWIN0002/244.
Each next service is requested only after the previous exact characteristic
callback's full public bytes/NSError/timestamp have been appended and fsynced.
Wrong/error/missing/duplicate service/characteristic/size/magic/generation stops;
raw callback data and NSError domain/code are saved before rejection. Log failure
stops before NEXT. This avoids the old multi-service preferred-selection helper.

Compile and run fake host callbacks + offline preflight:

```
python3 compile_host.py
```

Default is compile/preflight only and creates no Bluetooth manager.44 fake callback
checks passed, including full sequential collection, wrong UUID/error/size/magic/
generation/log failure, missing characteristic/service, foreign service instance,
disconnection, bounded expiry, and monitor ownership states. No key, native C,
state or physical device was accessed. Public proof and logs: `evidence/`.
The compiled executable SHA and exact compiler inputs are pinned in host-proof.

Root's separate sole-controller routing may choose one actual mode:

```
runs/control/collector --collect /ABS/NEW_LOG.jsonl --root-authorized-read
runs/control/collector --monitor /ABS/NEW_LOG.jsonl --root-authorized-read
```

The flag is an explicit invocation guard, not hardware authorization or recipient
attestation. Root must enforce admission/one-controller/current generation/log path
and pin executable before actual use. `--collect` is bounded60seconds total.
`--monitor` stays on the SAME connection: read QPFX first, then every30seconds while
phase/release are incomplete; max5460seconds total. A requested connection/discovery/
read operation has a60second bound, checked each second. No repeated connections.
Only prefix_phase3 AND prefix_released1 advance to the other three services. Even
nonzero fault reason awaits actual release. Phase3/released0 never means finished.
All monitor responses are durably logged; the final stdout bundle contains the
last prefix and three other exact envelopes for Root's independent verification.
No repeated monitor read is attempted after NSError or disconnect.

Collector format validation makes NO readiness/owners verdict. QPFX/QWBT/QWOP/QWIN
must be interpreted together with actual generation/source/APPLIED proof and
validated READY/INIT TX/all14 owner state. No byte count, phase or idle timeout
alone establishes firmware boot, successful Wi-Fi, entropy or ownership release.
No optional QPD extension was added; the four exact envelopes remain the scope.
No native timer/HCI/USB/watchdog/firmware change exists here.
