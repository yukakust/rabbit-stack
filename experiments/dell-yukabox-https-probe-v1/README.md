# Temporary Dell–Yukabox HTTPS proof endpoint

This is an isolated loopback Python handler for a future **physical Dell** HTTPS
request. It is not running or published by the source/tests, and does not prove
Dell Wi-Fi, IP, TLS, or WAN readiness.

Bind only `127.0.0.1:9784`. A separate Root-controlled operation may publish only
this handler with Tailscale Funnel on port10000, preserving existing443/8443.
Never publish repositories, management handlers, credentials or a whole directory.
Close the endpoint after the correlated physical nonce roundtrip.

The only successful request is `POST /probe` with one JSON field `nonce`, exactly
64 lowercase hex characters (32 fresh random bytes). Body length is at most128,
no transfer encoding or duplicate lengths/JSON keys. A bounded1024-entry
process-lifetime replay set fails closed on exhaustion. Socket reads time out
at5s. There is no file or command interface. The JSON response repeats the nonce
and fixed proof marker. Public logs contain nonce, request/response hashes and
server timestamp, never Wi-Fi secrets. HTTPS certificates/time/name validation
and nonce generation remain responsibilities of the real Dell client.

Tests use temporary loopback ports and synthetic requests. They are software
checks, not physical Dell evidence. Run `python3 -m unittest discover -p 'test_*.py'`
from this scope. Native C builds/tests remain exclusively on Yukabox.
