# Rabbit Stack technical debts

## Authenticate wireless Rabbit programs

Current BLE program frames use FNV-1a only as an accidental-corruption check. FNV has
no secret, so it cannot prove that a frame came from the owner's Mac. A nearby sender
that knows the public frame format can construct another checksum-valid program.

Before treating the wireless loader as an authority boundary:

- provision an explicit owner key or reviewed public key;
- authenticate the complete canonical program and its protocol version;
- bind a monotonic counter or nonce to each accepted program;
- reject replayed, stale, substituted, truncated, and reordered transfers;
- define key provisioning, rotation, loss, and recovery without hidden persistence;
- keep authentication distinct from encryption and document whether program contents
  remain visible over the air;
- add deterministic positive/negative vectors and physical evidence;
- never describe FNV, transport UUIDs, Bluetooth proximity, or device ownership as
  authentication.

This debt is intentionally separate from the first Dell-to-Mac acknowledgement. An ACK
lets the current Mac process correlate a receipt with the program it sent, but without
authentication it does not prove that the receipt came from this Dell or from the
authorized owner.
