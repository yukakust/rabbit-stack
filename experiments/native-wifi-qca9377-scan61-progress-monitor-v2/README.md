# Read-only scan61 progress monitor v2

Corrects the v1 status characteristic UUID from2c (the raw export SERVICE UUID)
to2b (the actual native61 QSCN VALUE UUID). Native ATT handle34 is not the UUID.
Only this host constant changes; no frozen/native/runtime/signature input is edited.
The existing controller may finish its v1 read and stop at missing-characteristic;
that outcome does not erase retained scan exports. Once that controller has exited,
Root can reuse exact complete firmware61/currentAPPLIED binding and collect through
v2 followed by the unchanged110page2x reader, without firmware replay/signing.

`native_binding.py` independently compares actual frozen61 generated GATT declaration,
read-info UUID and value handler with both host monitor and frozen raw reader;
callback models alone are insufficient evidence of that ABI join.
