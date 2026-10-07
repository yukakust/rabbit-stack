# Native55 Bluetooth loss — source/byte review

The last actual QWBT observation has boot phase1/plan17, submitted259/completed258,
MAIN offset19592: 79 completed 248-byte BMI_LZ_DATA chunks and one request pending.
Plan17 is not HTC READY, INIT or scan. The last sample does not prove where the
hardware later stopped. All12 full signed container parts had been accepted;
14 DMA owners and the firmware pin were still held. No later release/raw55 proof
was captured before the authorized reboot. Close-range Mac scan saw133 adverts,
Rabbit0; it does not reveal Dell controller/link state.

Checked native54/55 driver, USB, HCI stream, boot-image/transport/native and loader
are byte-identical. init_probe changes before READY only the signed generation.
The larger archive and scan parser do not execute until valid persistent ACTIVE.
Native54 did complete3114 requests, READY20 and genuine all14 release. Thus neither
"archive overflow at19KB" nor "Wi-Fi scan jammed Bluetooth at that sample" is
proved. Generated USB already has one split/coalesced event stream owner.

The resident supervisor stops subsequent animation ticks after a fatal poll/HCI
command deadline. User-observed continuing tail movement therefore supports
checking silent link/controller mismatch first, without treating it as a measured
USB state. A local RL_CONNECTED with pending0 and endless EFI_NOT_READY/TIMEOUT
is accepted by rl_usb_poll and has no link-liveness timer. If a true disconnect or
connection completion was not observed, advertising can stay disabled while
animation continues. This is a concrete possible path, not an observed cause.

Both channels share the cooperative scene loop: qca_poll runs before the sole
USB event read (20ms finite timeout); Bluetooth TX is bounded16 packets, each with
200ms finite transfer timeout. Worst-case batch latency is seconds, while typical
latency was not recorded. MAIN request completion only proves CE TX DMA completion,
not target firmware success. QCA PCIe and USB sharing/coexistence/power interactions
need real observations, not an inferred fix. Existing mature Linux BMI ordering
supports the same LZ stream commands; it does not prove Dell UEFI USB scheduling.

Native55 adds110 export characteristics versus54's40. That changes CoreBluetooth
service discovery traffic; read_scan.m requests111 total. No captured GATT/USB
last-activity bytes establish that discovery triggered loss. Future diagnosis
should keep GATT small and record local HCI link state, pendingopcode, credits,
streamused/goal, successful-event counters, last complete event, USB status/result,
CE indexes/cookies/offset and time spent in each poll, alongside frame heartbeat.
Visible overlay must remain readable if BLE disappears; bounded owned raw bytes
must survive genuine hardware quiesce. Never infer advertising from a timeout.

ROOT selected the next OFFLINE candidate: full authenticated container admission,
MAIN prefix around32768 bytes then finite checked all14 stop; no BMI_DONE, INIT,
scan or RF. A stopped partial stream does not establish chipset reusable readiness:
any later native requires fresh checked reset/ROM/init. Proof plan comes before
candidate freeze. No55 files were changed and this review did no hardware actions.
