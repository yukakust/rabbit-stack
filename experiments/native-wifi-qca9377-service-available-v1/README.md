# SERVICE_AVAILABLE prelude: confirmed physical native45

Actual CE2 frame36 bytes contains WMI event3/TLV559, value20 bytes, first word128
and16-byte extended service map. Pinned ath10k dispatches this event separately
from event1 SERVICE_READY. This module validates only the observed bounded form,
preserving the opaque words. It does not approve features or imply startup ready.
Unknown sizes/advertised-length forms rejected, no output changes on rejection.

Next native candidate must validate negotiated WMI endpoint/trailer, accept at
most one such prelude, repost CE2 and await actual SERVICE_READY under existing
deadline/all-owner cleanup. Duplicate/foreign/malformed events remain faults.
This pure module is not included in signed native45 and its446 frozen inputs.
No allocation, transmission, credentials, scan, association or IP.
