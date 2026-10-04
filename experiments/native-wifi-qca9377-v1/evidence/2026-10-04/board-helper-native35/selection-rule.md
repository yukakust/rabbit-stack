# Exact board selection rule

Primary reference: [pinned Linux ath10k core.c](https://raw.githubusercontent.com/torvalds/linux/6b5a2b7d9bc156e505f09e698d85d6a1547c1206/drivers/net/wireless/ath/ath10k/core.c).

A complete physical QBDI helper query plus released DMA ownership is required.
SMBIOS state1 (absent) or state2 (valid without BDF_) supplies no variant;
state3 supplies the bounded BDF_ suffix. Fault/unfinished state forbids selection.

If the returned helper low8 bits are zero and board ID is nonzero, build
`bus=pci,bmi-chip-id=X,bmi-board-id=Y[,variant=SUFFIX]`. If IDs are unusable,
use physically proven PCI/subsystem IDs, not guessed IDs. Search group0 of
pinned board-2.bin for the exact name, then the same identity without variant.
A valid BMI identity MUST NOT silently fall back to a different PCI identity.
Require a unique record and hash/size validation. The existing PCI record is
only a catalog candidate until the physical query completes.

Main startup is a separate profile: fresh reset/config/identity check, exact
board data, calibration helper, exact main LZ stream, BMI_DONE, then a valid
HTC_READY response. Upload completion alone is not code execution proof;
HTC_READY alone is not Wi-Fi association. Interrupt/DMA ownership must stay
valid while firmware can access host descriptors. Never free active DMA.
