# Bounded Mac TLS1.3 client preparation

MemoryBIO-only ciphertext endpoint,240-byte fragments,8192-byte bounds,60s
monotonic epoch deadline, full DER-SPKI SHA256 match before application output,
TLS1.3 only/no tickets/session injection/early-data. Client context supplied
with its own transient certificate; no owner/Dell keys or passwords read here.

Before physical use the caller must independently bind the displayed complete
Dell fingerprint and owner-authorized client public identity to actual signed
parent/code-set/epoch. This library alone is not credential admission or peer
authority. No physical BLE or provisioning operations are exposed. Python
runtime memory release is not advertised as explicit secret zeroization.
