# Prepared recovery after Bluetooth loss

The Mac preserves world12 (city and animated roof cat), confirmed native14 and the
exact still-pending native15 packet. Loss of Bluetooth does not establish a reboot.
The owner observed the city and tail still moving, including after bringing Mac
nearby. The cause of lost Bluetooth is not established.

`verify_reboot_recovery.py` runs on Yukabox. It builds the plain actor city driver
twice, runs actual UEFI normal/empty-bootstrap load, restore and rejection gates
with mocked radio, and checks the exact saved world at counter13 in portable C
under ASan/UBSan (120 frames, tail/smile timing, adversarial cameras). Recovery
does not run a Wi-Fi-chip probe. These are preparation checks, not physical proof.

`reboot_recovery.py prepare` runs on Mac after those gates. It validates current
world, idle journal, installed owner gate and old pending packet; signs native16
against installed bootstrap1 and EMPTY world, and saves world13 plus both exact
sessions. Current controller state and native15 files remain unchanged. The owner
private key remains local and is never copied or printed.

Only after the owner actually reboots Dell may the agent invoke `restore` with
`--dell-rebooted`. Before retiring any old operation or writing DATA/COMMIT, the
route requires a fresh read-only receiver response containing the exact all-zero
idle RFS state. Missing/nonempty/foreign response leaves native15 pending. It does
not reset radio, erase receiver staging, modify USB/bootstrap or infer a reboot.

After that proof, one atomic controller-state write records native15 as retired
and activates the new recovery. Every original native15 file and hash is retained.
Native16 and world13 use the established paced sender, exact signed packets and
correlated receipts. Disconnects keep the same sessions and confirmed byte prefix;
resume uses the same directory without generating counters/nonces. A rejection or
receiver regression stops recovery for inspection. Only exact receipts promote
engine/world state. User must separately confirm the physical city and moving cat.

Use the dedicated `reboot_recovery.py restore` route for this recovery, including
resumes; the GUI's older `city_recovery` route does not support this pending-native
transition. After completion normal text/voice world edits use the same controller.
No promise is made that reboot will fix the hardware radio; if bootstrap also
cannot advertise, recovery remains pending and physical diagnosis is required.
