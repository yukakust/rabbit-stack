# Deferred ciphertext pump

Stages only bounded240-byte ciphertext fragments on the ATT path. Actual typed
TLS feed/poll/drain/revoke callbacks run only in the sole privileged loop.
Incoming exact duplicates do not reach TLS twice; altered duplicates/sequence
or epoch changes revoke. Outgoing reads are nondestructive until an exact ACK.
One pending outgoing fragment enforces backpressure; partial reads do not alter
TLS stream ownership. Borrowed callbacks cannot close/unload the provider.
Fresh monotonic time is checked after each provider call before successful
progress escapes. Disconnect/deadline/error clears ciphertext and defers actual
key/source revocation until outside ATT; failed revocation retains the lease.

This component has no plaintext API, RNG, identity creation, signature, peer
approval, SPKI pairing or credential permission. Bind only from the private
admitted TLS lifetime after actual first-pair policy. No GATT/parent integration
or real TLS provider proof is asserted by the injected adversarial tests.
All native C/ASAN/UBSAN/COFF only Yukabox; no physical operations.
