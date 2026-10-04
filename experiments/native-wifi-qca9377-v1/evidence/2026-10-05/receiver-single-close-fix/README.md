# Receiver close ABI regression

Resident update calls active.close once. Native34 receiver called cooperative
qca_fwp_close once, releasing workspace but retaining container memory; it
returned failure. runtime_update sets fault before candidate.attach; root fatal
then invokes watchdog recovery. The physical fatal trace was not captured,
but the mismatch is reproduced with actual receiver entrypoints and the full
751436byte signed-container fixture. No chip helper execution is inferred.

The fixed wrapper takes a second bounded release step only when first returns1.
Pinned/uncertain/failing release retains ownership and refuses unload. New
regression requires one successful qca_stop after unpin; the former fixture
used a while loop.65 scenarios+normal/EMPTY city/ATT QEMU pass. Host gates
are distinct from physical deployment. Current native36 has no RAM receiver.
Do not send the historical generation34 fixture artifact; future receivers
require a fresh bound policy generation and complete source/world gates.
