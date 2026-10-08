# Scan61 — unsigned technical candidate

Frozen fullboot60 is preserved.61 repeats the exact authenticated full firmware
boot under generation61, then adopts the checked persistent14-map lifetime
immediately after actual INIT TX completion + parsed WMI READY, before60's success
teardown. The corrected frozen55 scan components are copied with exact generated
source hashes in component-inputs.json;55.sources is never applied over60/61.
No rejected HCI timer preparation is read, copied, applied or retried.

The existing ordered CE3 coordinator submits SCAN_CHAN_LIST, PDEV_SET_REGDOMAIN108,
VDEV_CREATE0 using the actual READY MAC, then passive START_SCAN. DMA completion
orders commands; it does not invent a firmware ACK or network association. RX alone
applies HTC incremental credits. Coordinator/owned-stop never apply them again.
Models assert exact13 frequencies2412..2472, passive flags, legacy20MHz channels,
START_SCAN flags0x21 and empty SSID/BSSID/probe-IE lists (no active probe payload).
Target matching is local parsing of exact16-byte SILK_56E35E_Plus after valid
STARTED, epoch/startfloor, metadata policy/live frequency and owned raw MGMT_RX.
Unsupported envelopes remain owned/exported; STARTED alone is not discovery.

The13-channel header is the exact existing signed-regdb GE/world108 proposal,
independently rebuilt with the pinned Linux trust anchor and physical52 capability
proof. Actual SERVICE_READY must match regdomain108,2GHz2312..2732 and5GHz4920..6100
before commands. Those capability bands are not an inferred authorization. No5GHz
channel, country/board override, association, credentials, WPA, DHCP or IP exists.
The inherited proposal explicitly has RFadmission=false, GEprimaryinstrument=false,
physicalprobeabsence=false and measuredantennagain=false. This technical proof
must not be used to bypass those gates or invent legal/RF approval. Root must decide
whether additional primary policy proof is required before any physical61 scan.

Bootstrap remains bounded5400s. Scan owns its separate25s overall deadline plus
finite command/credit/STOP deadlines. Terminal/STOP then quiesce precedes the actual
adapter/BME/IRQ stop and14-map/pin/PCI/pool release. The lifecycle must observe
verified stop before mappings decrease. Invalid ownership remains retained; no
terminal, timeout or model counter is substituted for release evidence.

Archive16 preserves the physical54 regression corrections: known scan prefix24
with28-byte suffix and nonterminal reason6; at most2 owned heads drained per poll;
wrongSSID/duplicate accepted management frames archived, first matching target
retained.22slots(archives0..15,observation16,orphan17,dispatch18/19,RX20/21) export
QEXP0001/2084bytes over110 bounded pages, each<=512. All110pages2x stable is required
at quiescence before later unload. Terminal livefreq0 is decoded from retained
RX/policy/epoch rather than an invented current channel.

Explicit ATT layout: existing boot20..22/operating23..25/WMI26..28; holes29..31;
QSCN status32..34(416bytes,gen61) and raw35..255(values37+2page,UUID80..ed).
Discovery starting in29..31 explicitly advances to service/info32 or declaration33,
while1..28 still delegate; native and QEMU range tests cover the gap.
PREFIX29..51 ATT is removed to avoid collision; internal240QPFX, transport capture
and overlay remain. Host61 must use its own QSCN/QWBT/QWOP/QWIN collector and Root's
actual61 receipt/payload/source binding;60 collector is not reused. Scan status
before activation is not firmware readiness or ownership release.

Only isolated Yukabox source/TMPDIR builds C/ASAN/UBSAN/COFF, repeated EFI and current
signed world19 normal/EMPTY supervisor QEMU. Fixed public fixture keys are only
model material. Provisional61 is not reserved/admitted/signed/sent here.

```
python3 verify_policy_binding.py
python3 verify_native.py
python3 prove_scan.py --world runs/world19.rup --world-json runs/world19.json --tmpdir /home/yuka/rabbit-world/parallel-scan61-native-v1/tmp
python3 verify_production_diff.py --baseline /home/yuka/rabbit-world/parallel-fullboot60-native-v1/source/experiments/native-wifi-qca9377-fullboot60-native-v1/runs/checked-candidate --candidate runs/checked-candidate
```
