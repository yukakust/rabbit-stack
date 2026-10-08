# QCA9377 startup: source facts and partial diagnostic choice

Pinned ath10k uses READY → supported baseMAC attempt → dummy STA create/delete → real WMI ECHO barrier → RX refill → HTT version → conditional fragment bank → RX_RING_CFG → aggregation before real STA scan. QCA9377 PCI's filter-reset workaround is enabled; its continuous-fragment flag is false. TLV baseMAC has constants but no generator, so the mature wrapper returns unsupported and core tolerates it. A new sender must not be invented from the tag alone.

Essential management frames have a documented WMI path; HTT duplicates serve monitor reception. This does **not** prove that our firmware needs—or does not need—RX-ring setup before WMI beacons. Native61's missing MGMT remains unexplained. The normal driver's order is an implementation baseline, not a demonstrated cause.

Root chose a smaller partial native63 diagnostic: dummy create/delete + exact ECHO, HTT version, then real STA and the same reviewed13-channel passive scan for iPhone(9), with existing14 maps. A positive requires actual owned WMI beacon bytes and exact SSID; a negative establishes only no accepted target in that trial. It cannot be called complete RX startup, a repaired physical filter or Wi-Fi connection.

BranchB remains the complete ring/aggregation/frame path and needs explicit added DMA-owner accounting. SERVICE_READY bit65 selects full reorder using four low bits per32-bit bitmap word; HTT3.56 alone cannot select RX_IN_ORD. The two MGMT_TX service bits are TX capabilities, not an RX enable gate.

[evidence/review.json](evidence/review.json) contains exact primary source links/hashes, line anchors, scan/filter/configuration gaps and bounded admission conditions. No hardware, key, state, signing or frozen native changes occur in this review.
