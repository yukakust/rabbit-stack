# Native51 exact INIT receive diagnostics

Isolated native50 CE3 derivation. No acceptance rules relaxed. QWIN0002/244
retains the original96-byte fields, then five LEu32 at96: rejection stage,
actual frame size, copied prefix size, HTC endpoint, payload size. At116 a
128-byte zero-padded exact RX prefix is captured BEFORE parsing. Thus the
physical50 rejected68-byte frame can be exported completely in a next trial.
Reasons:1 coordinator/credit-only precondition;2 HTC framing;3 endpoint;
4 READY event/ABI/status/MAC/schema;5 credit accounting. These observations
do not grant acceptance; unchanged transaction parser remains authoritative.
No credentials, station traffic or persistent radio. All-owner teardown stays
mandatory. Candidate unsigned/not delivered until full gates/fresh50 baseline.
