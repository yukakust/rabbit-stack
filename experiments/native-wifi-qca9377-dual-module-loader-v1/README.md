# Shared TLS/RSN module ownership

New derivative of frozen role2 loader/artifact, preserving original strict
role1 and role2 gates. Selects signed RABMOD01/role1 or RABRSN01/role2 explicitly;
never silently reinterprets a role. Only the two exact reviewed child file
digests are accepted. Owner/target/ABI/epoch/counter and asserted parent file
hash remain bound; Root must prove the actual installed signed parent before
signing any child. Relocated-image hashing is not substituted for that proof.

One actual ModBudget covers the parent and BOTH child images: mapped size and
strictly increasing counter are reserved before firmware LoadImage/entry.
Failed ambiguous entry/unload retains reservations, artifact/code and
quarantine. No independent budgets can each falsely claim4MiB. Different
active handles/images must own disjoint code. Byte arenas remain separately
owned and held until exact child close/unload; this is not a total-RAM4MiB cap.
Incomplete cross-role stages are serialized. New images are blocked after
both are loaded and the reviewed code-set identifier is sealed. This seal is
not entropy approval. Close first revokes the actual bound entropy provider;
borrowed/failed revocation cannot unload code. Failed child close/unload holds
all remaining owners. Successful repeated close does not repeat callbacks.

There is deliberately no generic untyped child dispatch here. The production
parent must still provide exact TLS/RSN nested-span/provider/lifetime adapters,
real seed-source revocation, actual code-load/digest policies and private ABI.
This is a reusable loader ownership slice, not yet a whole native candidate.

Software tests use genuine owner Ed25519 and real copied loader lifecycle with
explicitly injected firmware: both roles/shared cap, counter reservation before
entry, all288 header corruptions, wrong reviewed digest, aliases/epoch/reentry,
ambiguous LoadImage, failed StartImage, child close, unload and entropy
revocation. Native C/ASAN/UBSAN/COFF only Yukabox. Actual two-child OVMF/whole
image/repeatability/world19/candidate admission and physical proof still needed.
