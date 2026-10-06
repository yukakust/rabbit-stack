# Persistent QCA9377 lifecycle policy

This is a pure lifecycle coordinator, not a Wi-Fi driver deployment. Its baseline
is the current bounded startup test, which releases all owners after either
success or fault. The hypothesis is that retaining the same owner set after a
validated INIT/READY can allow later station commands, while an explicit stop
must still precede release. The checks falsify unsafe admission/release orders.

`lifecycle.c` has no MMIO, firmware writes, credentials, signing or physical I/O.
It does not establish a station, find a network, associate, or obtain an IP.
The physical native49 timeout is **not** a persistent READY baseline.

## Contract

- Begin requires actual successful INIT TX and parsed WMI READY plus the exact
  current fourteen-map/DMA-user owner set, firmware pin, active bus, PCI,
  wake, link, and interrupt owners. Caller must enforce that READY condition.
- Active mode retains these owners. It has no automatic lifetime expiry.
  Work admission requires a fresh validated ownership observation on each
  operation; the helper does not poll hardware itself.
- An explicitly authorized local quiesce immediately blocks new work. Existing
  RX and TX descriptors, credits and firmware pin remain owned. Timeout does not
  grant permission to release or refund anything.
- Stop proof is separate from release proof. Stop means **every owned engine**
  halted, device interrupt source quiesced, actual PCI bus-master bit off, and
  DMA completion/stop fences observed. Only then can the caller try release.
- Nested buffers, mapping handles and active bus owner must be released before
  pin/IRQ/link/wake/PCI owners. Owner counts cannot grow during release. Actual
  unload is permitted only after every owner is zero and stop proof remains.
- Time rollback, ownership loss and deadlines produce terminal `RETAINED`.
  This v1 deliberately has no recovery override. The existing adapter may still
  carry out its checked cleanup/recovery independently; its own fresh all-owner
  proof, not this faulted coordinator, would establish a subsequent safe unload.

Observations are trusted local adapter outputs. `epoch` binds one acquisition;
it is not cryptographic attestation or an RX replay defense. Untrusted packets
and the LLM must never supply these ownership flags or a quiesce authorization.

## Integration points (not implemented here)

1. In the derived driver's full probe, when `qca_wmi_startup_poll` returns1,
   require startup.phase2, transaction.RUNNING, actual TX completion and parsed
   READY. Build the owner snapshot from fresh PCI and mapping/pin guards. Switch
   to an active runtime phase instead of beginning diagnostic teardown.
2. Validate all fourteen exact mappings and routes. The corrected WMI pipe is
   CE3: `channels.rings[3]`, descriptor `buffers[6]`, payload `buffers[7]`.
   CE0/1/2/3 and every other owned engine are part of stop proof. No new mapping
   allocation is introduced by this policy. CE3 must not be omitted from a
   persistent owner guard merely because the old operating guard checked0..2.
3. Keep polling both HTC/WMI RX queues and consume each completion once. Validate
   credit reports in the shared ledger; TX DMA completion is **not** a refund.
   WMI READY does not create a station VDEV. A later station/create/start command
   must use validated capability/resource policy and its own completion check.
4. Connect the supervisor's authorized stop/unload path to quiesce. Call existing
   adapter close/cancel/poll routines, respecting their real deadlines and order.
   Observe CE/bus stop before release, then buffer unmaps/frees, pin release,
   IRQ/link/wake/PCI close. Do not reset the lifecycle while it retains owners.
5. Expose distinct telemetry: active radio, station ready, scanning, associated,
   IP ready, quiescing, releasing, retained fault, and fully released. Never map
   `accepts_work` to “Wi-Fi connected.” World-only updates may continue while
   owners remain; native replacement must require actual all-owner release.

## Verification

Run `verify.py --clang <pinned-clang> --output <ignored-run-dir>` **on Yukabox**.
It compiles and runs ASAN/UBSAN checks, then compiles freestanding x86-64 COFF.
The tests cover missing/malformed owners, unchanged active lifetime, stale epoch,
explicit quiesce, all mapping releases, timeout boundaries in both stop/release,
premature pin/PCI release, reacquisition, lost stop proof and clock rollback.

Evidence contains only host checks. No physical readiness claim is made.
