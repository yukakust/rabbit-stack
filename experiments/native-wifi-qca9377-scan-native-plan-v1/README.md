# Reviewed next native passive-scan integration plan

Reference-only plan. No new candidate, command publication, channel permission,
signing, credentials or physical access. The executable check verifies the pinned
reference facts and physical52 evidence bindings; it never authorizes RF.

## Baseline and exact policy blocker

Physical52 proved INIT/READY/MAC/actual TX completion, SERVICE_READY valid, zero
memory requests and all14 owners released. It reported regdomain108 (0x6c),
capability bands2312..2732 /4920..6100. The radio is not thereby persistently active.
Use the fresh physical53 ownership/result before the next integration step.

Pinned Linux ath/regd_common.h identifies0x6c as WORC_WORLD (NO_CTL/NO_CTL), not
Georgia. CTRY_GEORGIA=268 maps to ETSI4_WORLD and alpha2 GE. ath/regd.c selects
ath_world_regdom_67_68_6A_6C for0x6c. These identifiers and capability intervals
are inputs, not a blanket channel allowlist or country-specific permission.

The missing policy artifact must explicitly record country/location provenance,
the pinned and authenticated regulatory ruleset (or separately reviewed world
fallback), actual board/regdomain binding and the resulting allowed channels with
disabled/NO_IR/radar/width/power limits. Its source hashes alone are not authority.
Do not simply replace108 with a country code or enumerate every capability MHz.
No approved policy/channel artifact currently exists in this plan: its selected
frequencies remain empty. User SSID/password do not establish that policy.

## Ordered implementation after physical53 result

1. Adopt the actual persistent INIT/READY/radio lifecycle, with the current epoch,
   CE1/CE2 pump and retained14-buffer ownership. Require actual retained ring/PCI/
   IRQ guards before every command; unload still requires actual stop/all release.
2. Produce/review the policy artifact above and port the relevant channel filter.
   In Linux ath10k_regd_update first sends SCAN_CHAN_LIST, then PDEV_SET_REGDOMAIN.
   ath10k_update_channel_list excludes DISABLED, carries NO_IR and RADAR into
   passive mode (including a firmware DFS-active-probe caveat), and converts power
   fields to their required units. Implement independently pinned serializers;
   do not guess channel fields, DFS support, CTL values or legal limits. The
   checked passive scan profile must not use probes to bypass NO_IR.
3. Add one serialized CE3 TX publisher using the actual startup WMI buffer/ledger.
   Borrow the common credit owner used by RX pump. Build/reserve, commit before
   descriptor publication, then publish one retained descriptor/cookie. Actual
   matching CE3 DMA completion permits command ordering only. Unknown publication
   retains descriptor/mapping/credits until actual stop. Never refund on DMA.
   No fabricated regulatory or VDEV_CREATE ACK; record exactly which commands
   were submitted/completed and which actual firmware events were observed.
4. Bind station-scan/dispatcher/owned STOP to the same pending request and epoch.
   Station constructor must use the physical52/v5 READY decoder (actual52 value
   length52), not old SESSION strict36. CREATE completion yields CREATE_ORDERED.
   Only after that ordering and the reviewed policy setup may one bounded passive
   START_SCAN be published for an explicitly selected subset of allowed channels.
5. RX pump applies HTC credits once. Transfer owned payload events with completion
   IDs (gaps permitted) to station dispatcher and owned STOP. Preserve unknown/
   foreign/control payloads or bounded backpressure. Only matching SCAN_STARTED
   establishes scan acceptance. Terminal event plus STOP TX, when posted, proves
   scan ended; starvation, deadline, rollback or malformed event retain fault.
6. Close/quiesce the trial and prove actual all14 releases. Report real STARTED/
   terminal IDs, CE3 completions, policy hash, submitted passive-command flags,
   credits and owner state. Do not claim absence of over-the-air probes without
   independent RF observation.
   Finding SILK_56E35E_Plus additionally needs actual management/HTT beacon RX and
   BSS collection feeding the existing beacon parser. Scan events alone do not
   prove SSID discovery. Association/EAPOL/keys/HTT data/DHCP remain later stages.

## Concrete tests before admission

Model actual CE3 buffer/address/cookie/ring ownership; frozen RX pump/owned dispatcher
join; real credit return with once-only application; no CREATE-ACK assumption;
policy tamper/missing provenance/disabled/NO_IR/radar rejection; selected-frequency
intersection and unit conversion; early events and completion gaps; unknown FIFO
backpressure; post ambiguity, credit starvation, deadlines and rollback; real
quiesce/all14 release. Then repeated EFI builds/QEMU/current-world/source/admission
checks under a newly assigned candidate. This plan does not assign its counter.

Pinned source commit:6b5a2b7d9bc156e505f09e698d85d6a1547c1206. references.json contains
exact source URLs/hashes; evidence/2026-10-07 records reference/physical52 checks,
not successful RF, policy approval or native integration.
