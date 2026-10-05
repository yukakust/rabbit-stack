# QCA9377 bounded CONNECT response compatibility, native45 candidate

Preserves every native44 input unchanged, overriding only derived htc_wire.c.
Pinned Linux ath10k decodes a minimum8-byte CONNECT response core. Physical
native44 receives12 payload bytes: valid8-byte core plus four zero bytes.
Accept ONLY8 bytes or this12-byte zero extension; unknown lengths/nonzero suffix,
wrong message/service/status/endpoint/capacity and malformed HTC remain rejected.
No claim that the suffix is standardized metadata. No scan/association/IP.

Retains native44 read-only208-byte diagnostic and all-owner bounded teardown.
Must pass actual CE response/fault fixtures, ASAN/UBSAN/COFF, two exact EFI builds,
QEMU city/restore/rejection, current-world reproduction, strict admission and
fresh actual native44 owner-release observations before signing/delivery.
Not physically applied until exact receipt. New45 assets only, never44 replay.
