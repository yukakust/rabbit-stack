# Full-channel initialization-state read

Baseline native31 physically completed warm reset, fourteen-map host channel
initialization and fixed CE7 host-interest read4008f8 ->401ee0, then restored all
resources. This candidate preserves that sequence and reads exactly three fixed
locations through the same live CE7 rings:401ee0/36bytes,400900/4,4008cc/4.
It never follows the returned table pointers and never writes target RAM.

After every successful operation, retain parsed data before reusing the response
page. Validate ACTIVE PCI/MEM/BME/D0/wake/ASPM/MSI/core BAR/IRQ scope before each
poll/submission. Each exchange observes completion before its3second timeout.
Fault/cancel takes the same all-eight-stop, BME-off, Flush/Unmap/Free lifecycle;
retain on ambiguous ownership rather than force free. Do not reboot Dell or
change USB/bootstrap. Keep world14 and older history.

Build/gate on Yukabox with actual native entrypoint ASan/UBSan cases, per-location
no-reply faults, malformed length and lost BME; repeat payload builds, current
sources/world, UEFI normal/empty boot city and Bluetooth/ATT/decoder gates.
Local owner signature only after all exact gates; deliver saved monotonic
session; exact APPLIED receipt is separate from physical telemetry/owner screen.
QPD17 keeps924byte total / prefix716 plus SHA-bound extension244, diagnostic
serviceUUID0C and original file serviceUUID1. Reuse previously zeroed config
telemetry716..799; retain full-channel HI proof888..923. Decoder must reject
configuration observations without the completed full-channel HI proof.

After physical read, validate table spans and flags with init_preflight's finite
window and overlap rejection tests. Bind raw known-peer/writes0 telemetry to the
current exact receipt/world and require successful warm sequence/full cleanup.
Historical QPD12/13 configuration values cannot authorize this trial or writes.
Next: separately gate configuration writes/readback, done marker LAST, CPU wake,
fresh BMI target identity, exact firmware/board variant and signed asset chunks.
No association, DHCP or video result is implied by a successful read.
