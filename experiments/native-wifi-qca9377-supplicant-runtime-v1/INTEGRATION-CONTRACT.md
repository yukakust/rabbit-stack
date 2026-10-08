# Native caller contract and remaining gates

* Bind one exclusive caller-owned runtime/arena before mature init. Arena must
  not overlap metadata/providers, DMA buffers, firmware assets or other module
  objects. Allocator is128 tracked CPU leases, not a generic platform heap.
* Supply actual independently approved DRBG/monotonic clock provider and source
  closure. Revocation callback is mandatory: close controlled port, stop future
  EAPOL/key requests, retain hardware owners for checked cleanup. Current public
  fixture RNG is deliberately insecure and cannot become a production fallback.
* Native owner uses `rsn_runtime_poll` cooperatively with existing CE/USB owner
  work. Epoch belongs to that acquisition/association. Do not call busy
  `eloop_run` in the resident loop or modify its HCI timers. Callback contexts
  must remain alive until actual cancel/remove-before-call completes.
* Build mature `wpa_sm_ctx` with `os_zalloc`; mature deinit owns/frees it. Keep
  `RsnNativeIo` and approved providers alive until mature objects and owned timers
  are gone. Constructor requires explicit auth timeout≤30seconds, real copied
  AP RSN IE, network context, peer, and concrete key/EAPOL/port handlers.
* `send_owned` must copy/retain EAPOL bytes before return, route actual negotiated
  HTT TX mode and report enqueue/publication ambiguity as failure. Returning0
  does not prove AP receipt or physical radio support. Real descriptor/drain/
  protected data-plane/rate implementation is still missing.
* `install_confirmed` is synchronous, serial and non-reentrant: actual WMI key
  publication followed by fresh owned HTT SEC_IND peer/cipher/cast/floor join.
  Defer EAPOL while polling; never reenter mature core. See frozen station
  integration contract: SEC_IND has no key index/nonce; timeout/ambiguity revokes
  and forbids reinstall. No production handler is supplied here.
* The adapter passes original key/sequence arguments only to that explicit
  provider; it stores or logs no key material. Provider must perform correct
  hostap CCMP3→WMI AES_CCM4→HTT AES_CCMP6 translation and preserve packet numbers.
* Actual mature COMPLETED and RX_TX protection callbacks join frozen station
  PTK/GTK/epoch/owner gates. Runtime health is a prerequisite, not physical port
  authorization. Provider close/revoke must gate every actual protected TX/RX.
* Deinitialize mature objects even after revoke: OS free/wipe stays available.
  Do not erase arena while active mature stack frames still borrow it. Unbind
  requires all CPU leases/timers gone, invokes revocation and final zeroization.
* Measured PE file/SizeOfImage is a standalone module result. Account separately
  for caller arena, runtime/IO structs, stacks, DRBG, radio/HTT mappings and World.
  Do not infer combined262144-file/4194304-mapped fit or native deployment from
  successful component linkage. Module architecture/admission is Root-owned.

Current production providers/admission, native radio legacy-rate capability,
actual association/key/EAPOL/port integration and secure credential delivery are
UNKNOWN/unimplemented. No signature, deployment counter or physical success is
reserved or asserted by these software proofs.
