# Bounded HTTPS probe message framing

Pure application framing, not TLS, RNG or physical network proof. Generates the
fixed POST/probe request for the isolated Funnel10000 endpoint and recognizes
only its canonical nonce/proof JSON. Nonce bytes must come from an independently
approved healthy production DRBG; public synthetic test inputs prove no entropy.

One transaction/epoch; request Host limited to DNS characters<=127; headers/body
bounded2304; strict200 status, unique Content-Length/Content-Type, no Transfer-
Encoding/folding/control bytes, exact body length/nonce/proof and no trailing
bytes. Success is consumed once. Explicit finish must be called only by a mature
TLS client after authenticating its full response and applying its bounded
end-of-message/closure policy; this parser cannot prove certificate, hostname,
time, freshness or that any peer sent the input. Parser callbacks are not an
admission capability or permission to transmit IP.

`verify.py` executes ASAN/UBSAN and real freestanding COFF only on Yukabox.
817 synthetic framing checks:240 fragment sizes, all truncations, every body-byte
mutation, wrong epoch, duplicate result/headers, chunking, folding, oversized
input, trailing bytes and request injection. No actual HTTP/Funnel exposure,
network, credentials, keys, Bluetooth or frozen source operation.

Remaining integration: genuine nonce generation and non-reuse owner, real TLS
certificate/name/trusted-time verification, owned TCP BIO, monotonic deadline,
actual Dell→Yukabox→Dell same public nonce/serverlog proof. Dedicated protocol
object does not establish the full EFI/file fit or native/current-world gates.
