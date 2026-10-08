# QCA9377 owned RX PN metadata

New isolated software component. Run `verify.py` only on Yukabox with its dedicated TMPDIR. It compiles actual C ASAN/UBSAN models, exact primary PN oracles and four freestanding COFF objects. `check.py` only verifies public local closure and frozen input pins; it never compiles native C or accesses BLE/state/keys.

See INTEGRATION-CONTRACT.md for the mandatory protected-frame quarantine and missing authenticated commit/backend. QPN_COUNTER_ACCEPTED is counter metadata evidence only.
