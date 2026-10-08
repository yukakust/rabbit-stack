# Role2 supplicant artifact and parent extension — software only

This NEW scope preserves every original frozen role1, module-parent, inventory65
and supplicant-child-v1 file. Copied sources are pinned in inputs.json and
parent-inputs.json; selected child files are pinned in child-inputs.json.

RABRSN01 is a separate owner-Ed25519-authenticated artifact for exactly role2,
private ABI1. The 224-byte signed manifest and 288-byte chunk header bind owner,
target, actual parent file hash assertion, child SHA256, chunk SHA256, parent
epoch, strictly increasing child counter, total bytes, offset, role/ABI and
mapped size. It cannot reuse RABMOD01 role1 admission. Maximum file262144,
chunk65536 and parent-plus-child mapped4194304 remain unchanged. Mature copied
Monocypher/Ed25519 and SHA256 are real; public RFC8032 test seed is used only by
models. No actual key or credential is read or signed here.

The loader uses genuine EFI LoadImage/LoadedImage.options/StartImage/UnloadImage.
It requires a boot-service driver (PE subsystem11), exact registered dispatch
and unload pointers inside executable sections, and consumes the child counter
before firmware entry. Every unload/exit-data/close failure preserves owned
code/pool and quarantine. Primary operation status and unload status are
separate; stage metadata explains a rejection without overriding its cause.

parent.c owns a typed lease around the child's OPEN/EAPOL/POLL/STATUS calls.
Arguments must be outside loader/artifact/budget metadata and carry the exact
epoch. Reentrant close cannot invalidate providers/code while callbacks are
borrowed. The parent can unload only after child close, actual UnloadImage,
artifact wipe and cleared owner state. Parent-projection derives the frozen
city/module parent, keeps the same world19 renderer, and installs a NEW private
80-byte role2 protocol with GUID d8cbf3df-d7ae-4a64-97e1-779a6ec88dad. It has
exclusive epoch leases plus dispatch; no public untrusted-plugin interface or
bootstrap modification is introduced.

The signed parent hash is an owner assertion. Relocated memory is not hashed as
if it were the signed EFI file. Root must bind the actual installed signed
parent before any physical child signing. Model epoch1 is unreserved; all
physical/signing/entropy/provider/credential admissions remain false.

The OVMF lifecycle fixture genuinely loads the selected child, enters mature
supplicant OPEN with public synthetic PMK/RSN/SSID, rejects stale/alias spans,
refuses image unload while opened, rejects parent close during an actual clock
callback, then deinitializes/wipes arena before code unload/wipe. Synthetic NIC,
key-install and port callbacks FAIL CLOSED and are never counted as success.
It proves loader/lifetime interoperability, not physical RNG, radio, security
handshake, IP or network access. The independent mature authenticator interop
proof belongs to the selected child's frozen scope.

The first selected child-v1 was correctly rejected BEFORE LoadImage because
its PE subsystem10 EFI_APPLICATION disagrees with the reviewed module-driver
policy. Its failure log is retained in evidence/rejected-application-child.
The policy was not relaxed; the corrected child must be a separately frozen
producer derivative with subsystem11.

Image aggregate bounds and external RAM bounds are distinct. The parent report
also includes city pool1958415, artifact262144 and supplicant arena131072 maxima.
The conservative mapped-plus-external sum exceeds4194304; no global4MiB pool
broker is claimed. The immutable4MiB mapped-image cap remains enforced. Real
integration still needs reviewed provider lifetimes, approved entropy and
protected PMK delivery, NIC confirmed key/port operations, and actual admission.

Reproduce C/ASAN/COFF, OVMF and city QEMU ONLY on Yukabox via verify.py,
qemu_probe.py, parent-projection/{verify_parent,native_build,verify_qemu}.py.
No Mac native compilation, BLE, state, signing, random sampling or hardware
operations are part of this scope.
