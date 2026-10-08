# Prospective public CPU inventory only

New source, no existing native integration. `InvRecord` exactly256 bytes holds
QRNG0001/version/size/epoch/compiled-source hash, seven bounded raw CPUID leaves,
vendor/brand/flags. Entropy approval is permanently0; MSR status permanently
NOT_READ. No entropy/private key/seed sample/hash in diagnostics.

`inv_cpuid_native` is a genuine msABI x86 CPUID wrapper for a future explicit
parent probe; this proof NEVER invokes it. All tests inject known public CPUID
register fixtures, verify max-leaf bounds and callback failure leaves destination
unchanged, zero hashes/epoch/aliases reject. ASAN+UBSAN/COFF on Yukabox only.
No RDSEED/RDRAND/RDMSR/WRMSR implementation or instruction calls. No IRQ/HCI/timer
changes. Arbitrary firmware pointers are not discovered with this component.

Physical execution is exclusively Root-owned after exact native source/owner
admission, generation/epoch/source provenance and public diagnostic acquisition.
Record fields/source hash are correlation, not independent hardware attestation.
Root must apply primary Intel assessment in rdseed-prerequisite-v1: actual CPU
signature and virtualization context, current microcode/SRBDS mitigation evidence,
reviewed safe conditional MSR read if supported, then mature DRBG entropy adapter.
This inventory cannot create that approval. Unknown/absent mitigation provenance
continues to block a strong RNG backend even when RDSEED capability is enumerated.
