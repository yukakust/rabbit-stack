# Trusted native execution RDSEED → mature DRBG — software preparation

Actual inventory65 reports Intel CPUID0x906ea (family6/model9e/steppingA),
RDSEED present, no hypervisor bit, no SRBDS_CTRL. Its raw inventory is public
context; neither feature advertisement nor synthetic samples are approval.
No hardware CPUID/RDSEED/GetRNG/MSR sample is executed in this scope's tests.

Primary reviewed guidance:
- https://www.intel.com/content/www/us/en/developer/articles/technical/software-security-guidance/technical-documentation/special-register-buffer-data-sampling.html
- https://www.intel.com/content/www/us/en/developer/articles/guide/intel-digital-random-number-generator-drng-software-implementation-guide.html
- https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-90Ar1.pdf

Intel distinguishes the cross-core SRBDS confidentiality exposure from the
DRNG entropy source. Its mitigation guidance permits trusted execution without
untrusted software/guests. Missing SRBDS_CTRL is not an absolute entropy wall;
it also does not establish mitigated microcode. This narrow Rabbit approval
therefore explicitly assumes trusted bare-metal firmware and every executable
on every core, owner-admitted reviewed native/child code, no untrusted guests,
and a fixed reviewed executable code set. Data-only foreign worlds may pass
existing deterministic validators; arbitrary foreign executable modules cannot
inherit this authority. No unsupported MSR read or mitigation change is used.
CPUID no-hypervisor is inventory, not cryptographic device attestation.

RngApproval is a PARENT-PRIVATE reviewed authority, not an accepted network
message. Root must construct it only after actual signed-parent/current epoch,
actual65 inventory hash, owner/target and complete executable-code-set checks.
Those hashes are bindings/domain separation, never entropy. Root must revoke
all shared sources/DRBG clients BEFORE code-set or trust assumptions change;
passing a retained old hash cannot detect an unannounced external code change.
The code cannot authenticate firmware or count every core by itself.

seed_source.h/c +native.c form a TLS-independent native parent component.
It rechecks exact Intel/signature/flags before use, then collects 8..64 bytes in
8-byte units using RDSEED with Carry Flag checked each time. Zero is valid when
CF indicates success. Maximum256 attempts and2500us per collection are explicit
local fail-closed budgets, not Intel fairness guarantees. PAUSE is issued.
Rollback, clock/error, invalid CF, exhausted attempts, overflow and partial
collection wipe all output/scratch and permanently revoke that source lifetime.
No RDRAND, jitter, timer, MAC, prior seed, cache or deterministic fallback exists.
The callback is ONLY for an authenticated/admitted leased native child, never
GATT/diagnostics/host random-byte export. Parent composition must enforce that
lease and lifetime; this standalone component does not invent such admission.

entropy.c contains genuine pinned Mbed TLS3.6.7 AES256 CTR_DRBG. It accepts the
same parent-owned source or its explicit software model, uses48 fresh source
bytes per seed/reseed and prediction resistance on every request; nonce
requirements follow the mature construction. Personalization is only the
reviewed code-set digest. Each request is bounded1024 bytes, at most4096 requests
per epoch; stale epoch/hash, source or DRBG failure wipes complete output and
revokes. Metadata/output/provider alias or pointer-overflow requests are rejected
before calls. Close cannot occur during borrowed callbacks; private DRBG state
is freed/wiped, and a consumed same-context lifetime cannot silently reopen.
Shared parent source outlives leased DRBG clients and is closed by its owner.

Host tests link --wrap injections for both native instruction wrappers, including
zero-valid, partial failure, stalled/rollback clock, deadline, repeated reseed,
wrong CPU/approval/code/epoch, alias, reentry and split-source ownership. Crypto
is mature real code, not a success stub. No output/seed/key bytes are logged.
Intel hardware health mechanisms are not replaced by statistical sample tests;
no NIST certification or physical entropy validation is claimed.

All C/ASAN/COFF compilation/tests only Yukabox, own TMPDIR. The native instruction
wrapper is compiled but NEVER called by host proof. Physical sampling, native
signing/admission, internal Dell identity creation and physical full-SPKI pairing
remain subsequent separately reviewed steps. No credentials/private keys/BLE/
state/firmware source changes are present here.
