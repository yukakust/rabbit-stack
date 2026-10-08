# Distinct WAN TLS verification profile

New derivative of frozen Mbed TLS 3.6.7 BLE prototype; frozen sources unchanged.
The BLE SPKI policy is not reused for internet certificate trust. WAN requires
VERIFY_REQUIRED, official self-signed ISRG Root X2, exact hostname, certificate
validity and an independently authenticated UTC binding for the current epoch.
No verifier callback clears failure flags. No TLS1.2, PSK, early data or session
resumption. Certificate parsing supports P384/SHA384 and the actual fourth
RSA/SHA256 cross-signed certificate served by Yukabox; its issuer is not added
as a trust anchor. TLS records accept bounded 16KiB inbound/2KiB outbound.

`run.py` on Yukabox builds every mature library unit with ASAN/UBSAN and COFF.
The 2,153 assertions cover actual certificate signatures, CA/name/date/epoch
failures, mutations, expiry of the bounded UTC binding and Gregorian conversion.
Synthetic deterministic entropy is confined to the fixture.
`host_handshake.py` genuinely establishes Mbed TLS1.3 to the existing private
Yukabox HTTPS service, using Yukabox host getrandom and UTC only. It performs a
read-only GET after CertificateVerify/Finished and required verification.
Neither host provider supplies Dell authority. No Funnel configuration changes.

`check.py` checks exact local source/proof and public certificate fixture pins;
it performs no C compilation, network access, hardware operation or signing.
Public PEM fixtures are converted to DER only by the Yukabox test runner.

This scope is not a complete native image or signing admission. Native strong
entropy, authenticated UTC, full integration/arena sizing, physical IP and an
actual protected Dell→Yukabox→Dell nonce exchange remain unproved.
