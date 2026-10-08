Pure HTT RX decode component — no deployment or ring integration

Pinned Linux commit 6b5a2b7d9bc156e505f09e698d85d6a1547c1206. Source hashes are
in references.json. Existing htt-version-v1 reference bytes remain unchanged.
The firmware IE6 op3 chooses the TLV message table. The observed HTT3.56 is
explicitly required by this narrow component; major/minor do not select hardware
descriptor format or prove service capabilities. QCA9377 PCI core.c selects
qca988x descriptor v1 and target_64bit=false. Full reorder additionally requires
actual SERVICE_READY RX_FULL_REORDER bit65 under the TLV id/4 representation;
this component does not invent a physical capability proof.

Compiler oracle uses exact pinned rx_desc.h and balanced extracted htt.h types:
1byte response header, RX_IND hdr7/PPDU36/prefix4; dynamic ranges at48 plus
roundup(fw_rx_desc_bytes,4). RX_IN_ORD header7 after response1; paddr32 record8.
Descriptor/payload300, attention4, frag8/ring2_more10, MPDUstart12,
MSDUstart24/info1 32, MSDUend40/info0 56, raw header status236.

qrx_indication copies complete bounded raw2048 before classifying known/unknown.
Unknown returns2 and remains raw owned diagnostics. Malformed returns0 and does
not change output; caller must retain original raw on failure/capacity overflow.
Known-but-unsupported flush/release, PPDU extension, fragment, offload and MPDU
error status remain parsed/raw with usablefalse. No fields are removed.
Maximum255 parsed records/ranges is a local bounded capacity; not a new hardware
ring size. RX_IND MPDU counts are not guessed to equal MSDU buffers: its FIFO
consumption/reorder/reassembly is deliberately not implemented.

qrx_claim accepts only decoded usable INORD after caller-proven full-reorder.
Caller owns posted ledger up to2048 entries; default1023 can fit without changed
DMA owner counts. Require epoch, last completion/floor, paddr32/alignment8,
2048-byte nonoverlapping actual posted map addresses, nonzero map identities.
Addresses are never dereferenced. Validate all matches before any POSTED→OWNED;
unknown/duplicate/overlap/replayed/already-owned/freed references change nothing.
qrx_retire requires matching epoch+paddr+completion and creates a RETIRED
tombstone. It does not replenish, remap, unmap, free or permit address reuse.
Caller must bind map identities to actual resource coordinator and provide real
DMA acquire/coherence proof before descriptor bytes. Epoch/floor are supplied
by trusted caller, not forged into wire fields. These are software contracts,
not proof that the DMA engine has stopped or physical firmware posted a frame.

qrx_frame handles only completed raw-decap, single first+last MSDU, descriptor300
with payload24..1748 within2048. Reject done0, length/FCS/decrypt/MIC/overflow
errors, hardware/framing fragments, buffer chains, nonraw decap, AMSDU/reassembly
and contradictory expected length. Preserve caller's original descriptor/raw
on rejection. Frame bytes remain exact, including FCS if present; no Ethernet
conversion, authentication, key processing, association, DHCP or IP. Encrypted
metadata is diagnostic only. Peer/TID reorder, fragment assembly, deaggregation,
replenishment, active Rx-ring integration and physical capture remain future.

WMI MGMT_RX and HTT are separate transports. Pinned htt_rx.c documents essential
management frames already arrive through WMI; HTT duplicate management handling
is for monitor use. scan61 had no retained MGMT; that is not proof that missing
HTT ring caused it. Native63 currently selected filter/ECHO→HTT VERSION→passive
scan with prior14maps; this decoder neither edits nor expands that candidate.

verify.py runs only isolated Linux/Yukabox C ASAN/UBSAN, independent primary-type
oracle and freestanding COFF object compilation. Objects are not a linked EFI.
No private keys, credentials, state, BLE, HCI changes, signing or hardware.
