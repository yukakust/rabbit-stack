# QCA9377 dummy STA / ECHO barrier — body-only, offline

This standalone component prepares the supported pinned TLV sequence: dummy STA VDEV0 CREATE using actual validated READY MAC → DELETE0 → ECHO with exact public argument. DMA completion orders the commands; only the matching actual ECHO reply plus its actual TX completion permits a barrier pass. This is neither physical RX-filter verification nor complete Wi-Fi startup. No candidate, signing, RF scan, device operation or secret access occurs here.

The pinned Linux TLV command table contains a base-MAC ID/tag, but its ops table has no base-MAC generator. The mature wrapper returns `-EOPNOTSUPP`, which core tolerates. This component therefore explicitly skips unsupported base-MAC and never invents a sender. Primary source and startup rationale are in the separate htt-rx-startup-review-v1 review, pinned Linux commit6b5a2b7d9bc156e505f09e698d85d6a1547c1206.

## Integration contract

The coordinator borrows a shared WMI credit ledger **read-only**. QcaPersistentTx alone wraps HTC, reserves/commits credits and publishes CE3; the sole persistent RX owner has already applied trailer credits before its raw event is offered here. Coordinator functions never apply, refund or reserve credits. Current epoch, raw validated READY, actual live owner inventory, firmware and device binding remain the native caller's responsibilities.

1. `begin` with zero state, exact decoded READY envelope, shared ledger, epoch, current consumed RX-completion floor, nonzero public echo argument and monotonic time. Whole sequence has a3-second deadline.
2. `prepare` yields raw WMI body in `s.frame/s.frame_bytes`: CREATE28, DELETE12, ECHO12 bytes. Pass it to the existing `qca_tx_submit`; bind its returned ID with `submitted`.
3. Observe `qca_tx_poll` first entering actual POSTED, then immediately call `post` with the actual immutable HTC TX frame and current RX completed watermark, **before another RX pump**. The TX poll's guard drained earlier events before publication. Coordinator verifies body/endpoint and the changed credit serial/committed cost. Observing after a fast refund can fault12; a guessed transmit frame cannot advance the sequence.
4. Call `tx_complete` only on the same request's actual DMA completion and exact HTC bytes (36/20/20), then retire that request through the persistent TX owner. CREATE and DELETE completions permit ordering, never imply firmware acceptance.
5. Offer exact already-owned RX raw bytes with epoch/completion/pipe. Return0 means unrelated event remains the caller's responsibility: archive/preserve it. Exact ECHO requires pipe2, actual WMI endpoint, exact argument, fresh completion greater than publication floor and supported event/TLV. Its raw bytes are retained before argument/floor rejection. Reply may arrive before ECHO DMA completion; pass requires both. Duplicate/stale/wrong replies, rollback, malformed bytes and deadline failures never permit pass.

Unposted prepared bodies may be discarded; this API never cancels an already submitted/committed TX. Failure retains ledger state/raw witness; hardware quiesce/release is external. It allocates no DMA and accesses no PCI/registers. A successful combined native63 handoff must keep its radio ACTIVE after HTT VERSION success, with a distinct query-DONE state rather than falsely calling it RELEASED. The final owner-release/export happens after the bounded scan in the separately reviewed new producer.

## Evidence

140125 meaningful checks passed on Yukabox under ASAN/UBSAN, including independent actual pinned Linux enum/packed-struct wire equality, all16-bit Echo tag/length values, bounds/canaries/alias guards, ordering and exact request IDs, epoch/clock/floor/argument rejection, early ECHO versus late DMA, DMA alone not passing, shared-ledger byte equality, duplicate reply, timeout, cancellation and fast-refund integration violation. All5 actual production/dependency units compiled to x64 freestanding COFF. This does not attest or admit hardware.

`evidence/2026-10-08/report.json` SHA256 `18890d3f64dc5ad342114b30787e8cd6c28da4f4fadd1bad00aeff144a41cb6a` pins source, copied dependencies, reference hashes, independent oracle and logs. Reproduce `verify.py` only on Yukabox with its pinned reference, SDK clang, and isolated output below `/home/yuka/rabbit-world/parallel-filter-barrier-v1/`. Source and generated oracle are saved; binaries remain remote.

Upstream excerpts use SPDX ISC; UPSTREAM-ISC.txt retains the exact upstream license. Original notices: Copyright(c)2005–2011 Atheros Communications Inc.; Copyright(c)2011–2017 Qualcomm Atheros, Inc.; Copyright(c)2018–2019 The Linux Foundation; Copyright(c)2022,2024 Qualcomm Innovation Center, Inc.; Copyright(c)Qualcomm Technologies, Inc. and/or its subsidiaries. All rights reserved where stated upstream. Full references remain unchanged in the pinned read-only snapshot.
