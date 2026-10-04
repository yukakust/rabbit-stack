# Full-channel CE7 fixed-read trial

Native30 physically proved warm reset and fourteen-map channel initialization.
This candidate tests the next falsifiable claim: after the same warm sequence,
one fixed four-byte CE7 read at target 0x004008f8 returns 0x00401ee0.
Baseline: native30 closes channels without any active CE7 exchange.

## Loading and observability

Build on Yukabox only; run host sanitizers, native entrypoint fault/cancel cases,
COFF ABI checks, pinned target pack checks, repeated exact builds, current-world
C checks, and normal/empty-boot UEFI city/ATT tests before local owner signing.
Bind the exact source snapshot, payload, world14 and monotonic native counter.
Send the saved signed session over Bluetooth; a correlated APPLIED receipt proves
installation only. Read QPD16 (924 bytes) via prefix716 plus SHA-bound extension244
on fresh diagnostic service UUID0B. File service UUID1 is unchanged.

Telemetry records warm/reset results separately from CE7 phase/error, value,
bytes, TX/RX completion flags, completion mask, polls and last elapsed time.
Terminal stage5 requires both warm success and exact fixed-read success; stage6
can mean CE7 failed despite successful warm reset. Owner city/tail observation
is separate from the machine receipt and physical Wi-Fi telemetry.

## Physical scope and teardown

Reuse all fourteen validated UEFI common-buffer mappings and existing CE7 rings;
no target RAM writes, pointer-following, BMI commands or firmware upload.
Quiesce device IRQ before enabling bounded DMA. Check fresh PCI identity,
MEM/BME, D0/wake, ASPM, MSI/MSI-X, chip identity, BAR/core-control and IRQ state
before submission and on every poll. Keep the older BME-off guard unchanged.
Check completions before the three-second timeout, validate lengths/cookies and
require the expected word; no further operation follows an unexpected answer.

On success, error or cancellation, close through the existing adapter: stop all
eight CEs, disable BME and prove ownership released before Flush/Unmap/Free and
restore IRQ/link/PCI/wake state. An ambiguous stop/flush retains mappings; never
force free or unload. The twenty-second warm bound and each three-second ROM
bound from native30 stay unchanged. Preserve city14 and all older history.

## Recovery and limits

If teardown proves all resources released, the next gated runtime can replace
this runtime without reboot. If ownership remains, prepare a separately gated
recovery and ask the owner to reboot; never reboot Dell autonomously. Do not
modify USB/bootstrap, export the owner key or call synthetic/QEMU success a
physical Wi-Fi result. This trial does not establish association, DHCP or video.
