# Pure station virtual-interface wire preparation

Serializes only three WMI command bodies, not HTC envelopes or physical sends:
station CREATE20481/tag86 with28 bytes; STOP20486/tag93 and DELETE20482/tag87
with12 bytes. CREATE takes six bytes of MAC from the future actual validated
READY, typeSTA2, subtypeNONE0, zero MAC padding. IDs0..3 follow the checked
four-vdev resource reference. Rejects invalid/multicast/zero MAC, IDs outside
that profile, short output, alias and address wrap before changing output.

Independent oracle compiles actual pinned Linux enums/packed structs and CREATE
field assignments from wmi-tlv.c/.h and wmi.h. Compare all bytes including zero
padding and untouched output tail over1024 random MACs/four IDs/three operations;
check short buffers, invalid IDs, all multicast first bytes, zero/null/alias MAC.
12723 ASAN/UBSAN and freestanding x86-64 COFF checks pass on Yukabox. Reference
commit6b5a2b7d9bc156e505f09e698d85d6a1547c1206 and source/log/oracle hashes are
recorded. No new native49 input was changed.

Not integrated or sent on Dell. Serialization does not prove firmware created
an interface; TX DMA completion alone must not be treated as firmware acceptance.
The future dispatcher needs retained owners/current credit ledger, persistent
operating radio, command ordering/deadlines and a documented confirmation path.
Stop/delete command bodies do not prove physical all-owner release. No VDEV
START/UP, channel/regulatory approval, scan, keys, management/data transmission,
association or IP is implemented here. This prepares a required step toward
passive scan after actual WMI INIT/READY is physically confirmed.
