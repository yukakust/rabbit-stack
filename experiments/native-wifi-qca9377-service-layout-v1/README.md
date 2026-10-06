# Bounded SERVICE_READY common-prefix compatibility, native47 candidate

Pinned ath10k service struct104 bytes; target advertises128. Accept ONLY104/128,
parse the same checked104-byte core and retain/ignore opaque24 extension without
approving features. ABI major/namespaces remain exact; minor is reported as in
Linux. Hardware capability limits2300..2800/4900..6500 cover actual advertised
2312..2732/4920..6100. These are metadata, never legal channel/power permission.
The observed header declares zero memory requests; full array consistency must
still be validated on physical Dell. Keep all previous source snapshots intact.
No memory allocation/WMI INIT/scan/association/IP. Full admission required.
