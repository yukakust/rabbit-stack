# Native63 integration review

Read-only review of the new producer draft. `review.json` binds the reviewed
component bytes; `checks.json` records 98 pure storage/source scenarios.
Run `python3 check.py` to recheck the currently shared producer source.

The shared-memory handover is correct for the current mapping: response at slot
13, incidental frames at 14/15, response copied first. All 84 combinations of
destination count 0..13, archive count 0..2 and response presence preserve bytes.
Reversing that copy order at count 13 demonstrably destroys the response. Both
query pointers are revoked before scan can reuse the slots; status uses the
retained completion number and the common archive.

One startup witness lifetime risk was sent to Root and the producer: last RX
`startup.prefix` can be valid credit-only after earlier READY but before INIT DMA
completion. The pipeline then rejects an otherwise valid READY startup. This
needs an actual producer model and a bounded fix/proof before final freeze.

These are Python byte-storage and source checks, not native ABI/ASAN, firmware,
RF or physical admission evidence. Whole pipeline ASAN/COFF, exact 4 MiB cap,
normal/EMPTY QEMU and Root admission remain required. No hardware, state, key,
credential or native C operation was performed by this review.
