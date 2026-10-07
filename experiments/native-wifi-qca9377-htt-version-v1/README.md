# HTT version query: reuse the existing connection

Pure host-only codec. No candidate, radio access, RF, credentials or signing.
Native C/ASAN/COFF runs only on Yukabox. No frozen implementation changed.

Correction to the earlier association sketch: native operating already sends
HTC CONNECT_SERVICE for WMI 0x0100 and HTT 0x0300 before INIT. Archived actual
native52 QWOP session phase7 records WMI endpoint1 and HTT endpoint2. Do not
repeat HTT CONNECT on that retained session. QWOP does not export max_bytes;
read the actual retained internal session connection metadata, not a guessed
256-byte limit or the test fixture below.

The exact vendor firmware container inspected read-only on Yukabox is
WLAN.TF.2.1-00021-QCARMSWP-1, container SHA
8f8b002fccfe81d42238f27dd1f56d189604f180bd4772c7c8e75ae1fef16f01;
its declared HTT op-version is3 (TLV), WMI op-version4, main image SHA
57cbd474bda6a5e34e5e9e75ec5aba79f426f4a0b35719421c75f941ec693915.
This metadata inspection is not proof of what any live trial has negotiated.
Admission must bind the exact accepted firmware asset/target and retained epoch.

## Implemented boundary

qca_htt_version_bind requires actual QcaHtcSession RUNNING, no pending prepared
control packet, distinct nonzero negotiated WMI/HTT endpoints within READY's
endpoint budget, exact service ids and HTT max_bytes4..4096. Only pinned TLV
op-version3 is supported. It copies endpoint/max-message/op metadata only;
this cannot attest that hardware owners remain active.

VERSION_REQ payload is four bytes: type0 plus deterministic zero padding.
VERSION_CONF is the narrow four-byte TLV format: type0, minor, major, reserved.
Decoder accepts target major2 or3, any minor, reserved0, exact size; extensions
are rejected pending a separately checked parser. Endpoint/HTC frame/trailer,
receive watermark and current epoch are intentionally caller responsibilities.
No result means data-plane-ready: version acceptance precedes fragment-bank,
RX-ring and aggregation configuration in pinned ath10k htt.c.

Native bindings can be endpoint2 today, but the codec uses actual negotiated
endpoint rather than hardcoding it. Other HTT op-version mappings are refused,
even though VERSION_CONF number0 exists in other dialects; target major2/3 is
independent of firmware op-version3 and must come from a genuine response.

The oracle extracts pinned upstream request/response packed structs and enum
values, plus hw.h's TLV op-version. Tests cover all65536 major/minor pairs,
unsupported types/reserved values, exact bounds, invalid binding/resource
metadata, aliases/NULL/overflow, request canaries and upstream layout. Zero
request padding and reserved-zero response are this narrow native policy;
upstream receive code does not validate reserved0. Tests use a synthetic
session with max_bytes256; no physical limit is inferred from that fixture.

## Next actual native route adapter

Frozen channels_core gives these existing retained allocations:

| Path | Existing owner | Required integration |
|---|---|---|
| HTT TX CE4 | channels.rings[4], descriptor buffer8, payload buffer9, route4; configured payload capacity256 | A serialized CE4 publisher, actual endpoint metadata and cookie/address/length/index guard. Four-byte request fits; do not use WMI CE3 owner |
| HTT/control RX CE1 | channels.rings[1], descriptor buffer2, payload buffer3, route1; posted buffer2048 | Demultiplex decoded HTC endpoint0 control versus actual negotiated HTT endpoint; one consumer owns completion/repost |
| WMI RX CE2 | rings[2], buffers4/5 | Keep WMI endpoint routing and owned event FIFO intact |

Current persistent-rx-v1 explicitly allows only endpoint0 or WMI credit endpoint
and requires CE1 payload endpoint0, so a real endpoint2 response would fault.
A new derived adapter must replace that endpoint policy; attaching a second CE1
reader would race ownership and consume the same completion twice.

1. Bind actual INIT-ready retained lifecycle/address/epoch, operating RUNNING
   session and exact accepted firmware op-version. Verify all14 DMA maps and
   CE4/CE1 descriptor bases/configuration. Existing owner inventory is reused;
   no additional allocation is necessary for this four-byte query.
2. Serialize CE4 request with retained buffer9 and current session HTT endpoint,
   not existing WMI-only shared-credit helper. Pinned htc.c CONNECT_SERVICE configures HTT
   endpoint flow control disabled for PCI; verify exact HTC service contract
   before applying credit rules. Do not debit/refund WMI credits for HTT.
3. Integrate a single CE1 completion owner and bounded endpoint2 response FIFO.
   Validate HTC trailer before any ledger update, route real endpoint-specific
   credit reports correctly, and preserve endpoint0 control packets. No unknown
   frame drop. Retain raw data on backpressure; stop on finite deadline.
4. Accept VERSION_CONF only newer than request publication, exact endpoint,
   route, session/epoch and payload. CE4 DMA completion proves buffer transfer,
   never VERSION_CONF. Wrong/duplicate/stale responses cannot advance readiness.
5. Bound query to3seconds (matching pinned ath10k version timeout), cooperative
   RX/TX servicing, clock rollback/fault retains ownership, then explicit checked
   quiesce/all14-owner release before unload. Archive version+raw response+route
   evidence. No RF, peer creation or station traffic in the version-only trial.

integration-inputs.json pins the frozen local sources/archived physical52
observation used for these routing facts. references.json pins Linux commit
6b5a2b7d9bc156e505f09e698d85d6a1547c1206 (htt.c, htt.h, htt_rx.c,
htt_tx.c, hw.h, htc.c). The native route adapter above remains unimplemented here.

Reproduce: verify.py --clang <pinned-clang> --reference <hash-matched-ref>
--session <frozen-session-headers> --output <owned-proof-directory>.
