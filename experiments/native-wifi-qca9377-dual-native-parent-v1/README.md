# Direct native shared module adapter

Uses actual parent h/SystemTable/LoadedImage from the validated native entry.
Base mapped charge is the genuine LoadedImage.Size, not a fixture constant.
No additional installed public protocol is required: the deferred bounded BLE
chunk handler calls this private dual-role loader directly, and each child
registers through its genuine LoadedImage.LoadOptions during StartImage.

Two separately owned EFI LoaderData arenas each262144 bytes preserve artifacts
until actual child close/unload. Allocation errors with a pointer, success with
no pointer, overlapping ownership and uncertain FreePool outcomes retain
ownership and refuse ambiguous reuse/free. Known no-owner allocation failure
can close the actual admitted remainder. Every free follows artifact retirement
and full arena wipe. A repeated successful close cannot free twice.

Caller compiles exact reviewed child hashes/owner/target and current candidate
lifetime. Root must separately prove actual installed signed parent file bytes
before signing owner assertions for children; a relocated-memory digest is not
substituted. The wrapper does not approve entropy or expose a generic child
argument dispatcher. Typed TLS/RSN/source leases and whole native admission are
subsequent integration requirements.

Actual software proof uses genuine Ed25519 and copied dual loader with injected
UEFI LoadImage/StartImage/UnloadImage/AllocatePool/FreePool. Positive both-child
lifecycle and six allocation/arena/failure boundaries,3,934,829 assertions,
8COFF units on Yukabox. Whole two-child OVMF/physical loading not claimed.
