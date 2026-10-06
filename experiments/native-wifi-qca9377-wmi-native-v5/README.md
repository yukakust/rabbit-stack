# Native52 extensible READY common prefix

Physical51 exported complete68-byte HTC/WMI frame: endpoint1, payload60,
READY event2 / tag35 with52-byte value. ABI major/namespaces/minor574, MAC
c0:b5:d7:78:c3:fb and status0 fit the36-byte common prefix. Native previously
required value length exactly36 and rejected the16-byte suffix.
Pinned Linux wmi-tlv.c READY policy uses min_len=sizeof(wmi_tlv_rdy_ev), not
exact length; its pull_rdy_ev consumes ABI/MAC/status prefix and ignores suffix.
Isolated codec now follows that minimum36 within unchanged bounded/aligned TLV
parser. ABI/namespaces/status/nonzero-unicast MAC validation remains strict.
No hardware success is inferred from parsing recorded bytes. Same CE3 transport,
QWIN2 exact capture, bounded all-owner release; no station/RF/credentials.
