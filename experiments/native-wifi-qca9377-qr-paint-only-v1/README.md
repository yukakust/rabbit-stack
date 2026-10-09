# Public QR paint-only adapter

Frozen identity child generates the public full-SPKI QR. Parent consumes only
that typed current-epoch export; this renderer has no encoder or crypto native
dependency. Verifies epoch,600s lifetime, exact canonical public hash text,
version1..6 symbol size, framebuffer boundaries and alias/alignment. Reads the
pinned Nayuki packed public bit format. Injected host tests compare every pixel
of six genuine generated frames against the original public renderer.

Caller must verify actual child provenance and clear panel on identity retirement.
Does not decode QR, verify human pairing, approve entropy or accept host keys.
Copied pinned MIT generator is test-only; native COFF includes only paint.c.
