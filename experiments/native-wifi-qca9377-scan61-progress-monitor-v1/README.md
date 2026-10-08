# Read-only native61 bootstrap and scan quiescence monitor

This is a new host-only fork of the frozen fullboot60 collector. It creates one
CoreBluetooth connection to the pinned peer, makes no writes and never reconnects.
Every callback saves exact raw bytes and NSError, fsyncs the log and its parent
before proceeding. Any transport/discovery/size/magic/identity error stops.

Only services 0x22/value0x23 (QWBT0001,160 bytes) and
0x2a/value0x2c (QSCN0001,416 bytes) are requested. Removed PREFIX handles are
never used. Boot progress is read every30 seconds until bootphase5 with no boot
or plan error. The total host window is5520 seconds. Then QSCN is read every2
seconds for at most90 seconds (25-second scan plus finite transport/cleanup
margin). Success requires generation61, policy-count13, actual-released1,
adapter CLOSED12, cleanup-slots14 and all nine held DMA/PCI/pin/IRQ/bus ownership
fields zero.

**QWBT has no generation.** It is progress only. Root must bind the currently
APPLIED exact61 signed native package, immutable source gates, preserved world,
all12 exact61 signed assets, peer and sole-controller lock before invocation.
The CLI acknowledgment does not provide that binding and no readiness is inferred
from old native60 bytes. The final summary proves only a collected61 quiescent
snapshot; no SSID, association, WPA, DHCP or IP claim is made. Root independently
validates the status and subsequently runs the existing scan61 observer to fetch
all110 pages twice, only after checked release.

Compile and offline fake-callback/preflight only:

    python3 compile_host.py

After explicit Root admission, under the existing sole state lock:

    runs/control/collector --monitor /absolute/new/log.jsonl --root-authorized-read

No compiler invocation in this scope runs native driver C/ASAN/COFF/QEMU. The
Objective-C fake callbacks do not create a real Bluetooth manager. There are no
key/credential/state file APIs or signing operations.
