# Physical native46: SERVICE_AVAILABLE handled, real SERVICE_READY received

All12 assets accepted, boot3114/3114/HTC READY20/error0. Actual HTC session7,
TX3/RX4, WMI1/HTT2. Valid SERVICE_AVAILABLE observed/retained, CE2 rearmed,
next actual frame320 bytes is WMI SERVICE_READY1. Thus46 prelude handling works
on physical Dell. No CE ring/MMIO error. Parser rejects SERVICE_READY (error9):
actual first TLV32 value128 bytes, old parser requires104 bytes. Full packet320
retained on Dell; current diagnostics expose first256, so memory requests are
NOT yet parsed/confirmed (zero metadata is not proof of zero requests).
Actual release adapter12/cleanup14/DMA0/pin0. No connection/IP/WAN/Unreal stream.
Next: pinned-layout review plus actual128-byte form/field bounds, deterministic
malformed tests and next exact candidate. Do not guess request geometry.
