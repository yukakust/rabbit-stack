# RDSEED prerequisite assessment — no hardware instructions

The handoff identifies Dell i5-8500T, but actual CPUID/microcode/control evidence
is absent. Therefore there is no approved native entropy backend yet.
`inventory.py` decodes explicitly supplied public fixture fields only: 2 unittest
methods plus malformed strict-integer vectors, zero hardware/RNG calls. It never grants entropy approval.

Primary sources reviewed 2026-10-09:

* [Intel DRNG implementation guide](https://www.intel.com/content/www/us/en/developer/articles/guide/intel-digital-random-number-generator-drng-software-implementation-guide.html):
  RDSEED capability is leaf7/subleaf0 EBX18; CF indicates success. Seeds can be
  concatenated. Unlike RDRAND, there is no guaranteed retry count: bounded async
  retries and PAUSE are appropriate. Rabbit would fail after a finite budget;
  the guide's optional RDRAND fallback is deliberately excluded here.
* [Intel DRNG updated guide, official PDF](https://cdrdv2-public.intel.com/864722/drng-software-implementation-guide.pdf).
* [Intel SRBDS technical guidance](https://www.intel.com/content/www/us/en/developer/articles/technical/software-security-guidance/technical-documentation/special-register-buffer-data-sampling.html):
  SRBDS can disclose RDSEED results cross-core. Mitigated microcode defaults to
  protection; CPUID7 EDX9 enumerates IA32_MCU_OPT_CTRL(0x123), whose bit0 disables
  mitigation. No unenumerated MSR access or mitigation change is proposed.
* [Intel affected processors](https://www.intel.com/content/www/us/en/developer/articles/technical/software-security-guidance/resources/processors-affected-srbds.html):
  family6/model0x9e Coffee/Kaby Lake steps<=B and C/D are affected. Actual family,
  model and stepping must be captured; CPU marketing name is insufficient.
* [Intel i5-8500T product reference](https://www.intel.com/content/www/us/en/products/sku/129941/intel-core-i58500t-processor-9m-cache-up-to-3-50-ghz/ordering.html).
* [NIST SP800-90A Rev1 final](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-90Ar1.pdf)
  and [SP800-90C final](https://csrc.nist.gov/pubs/sp/800/90/c/final): a mature DRBG
  requires an appropriate entropy-source construction; identifier/time bytes
  and statistical-looking samples do not establish entropy strength.

Prospective Root-owned physical inventory (not executed):

1. Capture public CPUID0 vendor/basic max, CPUID1 signature/hypervisor bit,
   CPUID7.0 EBX/EDX, hardware identity and exact diagnostic-source hash/epoch.
   No random bytes are requested, exported, hashed, or logged.
2. Correlate actual stepping and current loaded microcode with authoritative
   Intel mitigation guidance. Read-only MSR0x123 only when EDX9 enumerates it and
   the driver has a reviewed safe fault path; otherwise record unavailable.
   No BIOS/microcode/MSR writes, no reboot instruction, no guessed revision.
3. Explicitly review native/hypervisor/provider provenance and SRBDS protection
   for the actual execution environment. CF/nonzero values do not replace this.
4. Then a separately reviewed backend may collect fresh seeds with a bounded
   CF-checked RDSEED loop and PAUSE, all-or-nothing scratch, secret wipe on every
   failure, no RDRAND/jitter/timer/MAC fallback, no seed logging. Failure to meet
   time/retry budget means no TLS key generation or credential admission.
5. Seed/reseed a mature Mbed TLS CTR/HMAC DRBG with sufficient reviewed entropy,
   epoch/domain personalization, explicit reseed/usage limits and lifetime. This
   profile currently has external PSA RNG; DRBG adaptation is still absent.
   Firmware's internal DRNG health checks cannot be replaced by a few host
   output tests; no NIST validation/certification is claimed.

Root can proceed with software composition independently. Actual strong RNG
approval and full physical SPKI confirmation remain concrete physical gates.
