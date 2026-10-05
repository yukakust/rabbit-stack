# Physical native44: CE1 control response captured

Boot complete:3114/3114 commands, HTC READY20, boot error0. Actual all-owner
cleanup: adapter12, cleanup14, DMA0, asset pin0. Operating phase3/error4,
CE1 receive step5, descriptor completion20 bytes, no ring/MMIO fault.

Actual prefix:00000c0000010000030000010001f80600000000.
HTC header declares12 payload bytes; CONNECT response message3, service0x100,
status0, endpoint1, maximum message1784. Remaining4 bytes are zero. Existing
htc_wire.c qca_htc_connection requires EXACT8 payload bytes and rejects this
actual12-byte response before field parsing. This establishes that rejection;
next fix must verify pinned protocol layout/metadata bounds and keep malformed
frames rejected. No guard was relaxed, no new native sent, no Wi-Fi connection.
