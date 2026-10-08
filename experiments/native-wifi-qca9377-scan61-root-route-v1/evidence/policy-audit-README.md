# Scan61 passive-policy audit

Read-only audit; no device, state, key, credential, native-source or frozen-flag
operation. Root accepts a separate bounded strict-passive trial intent and makes
no physical zero-TX promise. This evidence itself grants no physical admission.

Current primary source: [ComCom №4,30 July2026; official publication18 August2026](https://comcom.ge/ge/legal-acts/resolutions/2026-4-.page),
[official gazette record](https://www.matsne.gov.ge/ka/document/view/6960074),
[Annex1](https://www.matsne.gov.ge/ka/document/download/6960074/0/2).
The annex was fetched to memory only:93887bytes, SHA256
`375521dbc40214d1435bce35203e97179b33e1dff35d28de2ce4a3d84a110116`.
Table3 specifies WAS/RLAN2400–2483.5MHz,100mW EIRP, non-FHSS density10mW/MHz,
EN300328 and a sharing requirement. Candidate13 legacy20MHz centres2412..2472
fit within that band. This is a current spectrum reference, not proof that the
modified device satisfies every transmitter requirement.

Wire intent uses PASSIVE0x01 in flags0x21; TLV-filter inversion0x20 is unrelated
to active transmission. Broadcast-probe0x02 is absent and SSID/BSSID/probe-IE
lists are empty. See [pinned ath10k header](https://github.com/torvalds/linux/blob/6b5a2b7d9bc156e505f09e698d85d6a1547c1206/drivers/net/wireless/ath/ath10k/wmi.h)
and [TLV implementation](https://github.com/torvalds/linux/blob/6b5a2b7d9bc156e505f09e698d85d6a1547c1206/drivers/net/wireless/ath/ath10k/wmi-tlv.c).
Closed firmware honoring passive command intent remains an explicit assumption.
Host tests cannot prove physical probe absence. Rule antenna_gain_db0 is not a
measured zero-gain antenna. Existing false flags remain false in frozen artifacts.

The JSON records exact proposal/candidate/source hashes, parent-supplied actual60
context, Root decision and still-required source/session/owner/raw-capture gates.
No source-policy flag was flipped and no legal/antenna/physical measurement was
fabricated. SSID discovery still requires actual accepted owned MGMT bytes.
