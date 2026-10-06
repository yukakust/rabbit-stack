# Physical native45: CONNECT fix confirmed, earlier WMI event observed

Actual HTC session RUNNING7, TX3/RX3, WMI endpoint1/HTT endpoint2, credit2,
no CE ring/MMIO fault. Thus exact zero-extended CONNECT response fix succeeded
on physical Dell. SERVICE_READY not validated: operating error9, first CE2
frame36 bytes is event3, TLV559/value20, advertised extension length128 and
four bitmap words (first0x08000000). Pinned wmi-tlv.h names event3
WMI_TLV_SERVICE_AVAILABLE_EVENTID and tag559 STRUCT_SERVICE_AVAILABLE_EVENT;
wmi-tlv.c dispatches it separately and reads service_map_ext_len from first
word. It is not a failed CONNECT or proof of READY. Native currently assumes
first CE2 packet is SERVICE_READY and rejects it. Need bounded validated
SERVICE_AVAILABLE handling and repost CE2, then await SERVICE_READY.

Boot3114/3114/READY20/error0. Actual teardown adapter12/cleanup14/DMA0/pin0.
No association/IP/WAN/Unreal display success. Old446 inputs preserved.
