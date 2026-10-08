# Public EFI RNG implementation provenance, no sampling

Physical65 identified EFI CTR256/raw algorithm labels, but no source approval.
This NEW read-only component correlates the current EFI RNG provider with its
handle and actual LoadedImage containing BOTH GetInfo and GetRNG code addresses.
It records the firmware-volume file GUID and hashes only executable/readable,
NON-writable PE code sections containing those methods. Mutable data, DRBG state,
samples, private keys and arbitrary image contents are never hashed or exported.

The trusted UEFI protocol/memory mapping boundary is explicit. Bounded parsers
do not establish mapping validity for malicious firmware pointers. More than
one provider/overlapping image, missing code owner, writable method section or
unknown firmware path fail. GetRNG is never called; no MSR/RDSEED/flash/reset.
Real known pool owners are freed once; failed/ambiguous frees block unload.

An identified module/GUID/code hash does NOT approve underlying entropy. Exact
implementation and its source/mitigation still need separate review. Firmware
shim ownership alone does not prove a called crypto library's entropy source.

Primary layout reference: [UEFI2.11 LoadedImage](https://uefi.org/specs/UEFI/2.11/09_Protocols_EFI_Loaded_Image.html).
Software/native integration and physical delivery are not yet proven/admitted.

This is an optional provenance branch. A source-reviewed RDSEED provider for
explicitly trusted bare-metal firmware, admitted code/cores and no untrusted
guests may remove the need for physical EFI provenance. Missing SRBDS_CTRL is
not an entropy-quality failure or an absolute blocker. It prevents claiming
the mitigation and accessing its unenumerated MSR. Intel explicitly describes
the trusted-only execution case in its [SRBDS guidance](https://www.intel.com/content/www/us/en/developer/articles/technical/software-security-guidance/technical-documentation/special-register-buffer-data-sampling.html).
Future untrusted executable world modules cannot inherit that assumption.
