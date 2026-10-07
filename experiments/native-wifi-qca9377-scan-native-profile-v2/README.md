# Unsigned GEN55 passive scan: physical54 regression correction

This new derivative preserves frozen54 and deferred HTT55. No signing,
admission, Bluetooth/hardware/credential/state access. Native C/ASAN/COFF and
wholeEFI/QEMU only on Yukabox. Provisional counter55 remains root controlled.

The exact physical54 capture hash and six retained payloads are bound in
physical54-regression.json: four boot/debug/notification packets occupied
archive+dispatch, while genuine STARTED/FOREIGN remained in RX. Both have tag36
length28, known six-word prefix24 plus opaque suffix4 and reason6. Pinned Linux
ath10k accepts minimum24 and ignores nonterminal reason. Old exact24/reason
restrictions were compatibility errors; archive2 also exhausted capacity and
blocked semantic progress until STOP timeout. This evidence does not prove an
SSID beacon or connection; actual54 stopped and released all14 owners.

One new scan-event-v2 prefix codec feeds generated WMI match and dispatcher.
Bounded aligned suffix remains opaque; it cannot alter prefix interpretation.
Additional unknown TLVs are archived, never applied. Nonterminal reason is
retained uint32 without success/failure meaning; any nonzero terminal reason
conservatively marks scan unsuccessful. Duplicate STARTED, unknown type bits,
wrong ids/epoch/frequency and malformed/truncated records still fail closed.
Recognized scan events are semantically consumed into checked state; retained
raw exports cover actual still-owned packets, not an invented complete history.

The native wrapper now retains16 unknown archives and drains at most two owned
heads per poll; RX/dispatch each keep their exclusive bounded2 owners. Temporary
RX backpressure while archive space exists pauses receives, rather than
prematurely requesting STOP. Actual archive16 saturation requests owned STOP;
all command/scan/STOP/overall deadlines remain finite. No orphan is discarded.
Accepted non-target SSID management frames and later management frames after
the target observation are explicitly archived; the coordinator leaves them
owned until that transfer. The sole observation is reserved for the first
matching target at checked epoch/live channel. WrongSSID/duplicate frames cannot
block the next target or genuine terminal event.

Existing actual shared-credit CE3 TX ordering, credit trailer validation and
all14-owner stop remain unchanged; no old double-credit APIs are invoked.

Read-only QSCN0001 status416 fields/digests remain unchanged except GEN55.
Archive slots0..15, observation16, orphan17, dispatch18/19, RX20/21 give22slots.
QEXP0001 record2084 =magic8+9u32+owned2040payload; five pages per slot, first4
pages512 and last36,110 pages total. Status service32..34 UUID2a/2b; raw service
35..255 UUID2c, character UUID80..ed/values37+2*page. All READ_BLOB bounds and
write rejection preserved. Exact byte/hash export2x is mandatory before later
unload; status count alone does not prove archival. Static copies stay after
actual quiesce/release. No arbitrary memory reader or mutable ACK is added.

Proof sequence: pinned prefix oracle with exact physical54 packets; actual
native production entrypoint model including replay of all four blocker bytes
then STARTED/FOREIGN28/reason6 and true saturation16; ASAN/UBSAN/COFF; repeated
wholeEFI, real supervisor normal/empty QEMU, exact world17 ASAN120ticks/16camera,
and complete source/generated proof. Host/regression replay is not new physical
RF or SSID evidence. Root may sign only after archived54 raw/result and exact
candidate/source/regulatory/owner/target/epoch admission checks.
