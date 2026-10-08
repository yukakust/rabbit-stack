"""Exact primary packed types/enums only; no kernel success implementations."""
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def types():
 w=(ROOT/'references/wmi.h').read_text();h=(ROOT/'references/wmi-tlv.h').read_text()
 pre='''/* Primary Linux 6b5a2b7d9bc156e505f09e698d85d6a1547c1206 packed WMI excerpts.
 * Upstream notices remain in references; this is wire geometry, not RF admission. */
#ifndef RABBIT_STATION_PRIMARY_TYPES_H
#define RABBIT_STATION_PRIMARY_TYPES_H
#include <stdint.h>
#include <stdbool.h>
#define u8 uint8_t
#define u32 uint32_t
#define __le16 uint16_t
#define __le32 uint32_t
#define __packed __attribute__((packed))
#define WMI_TLV_CMD(g) (((g)<<12)|1)
'''
 for n in ['wmi_tlv_grp_id','wmi_tlv_cmd_id','wmi_tlv_tag']:
  pre+=re.search(r'enum '+n+r'\s*\{.*?\};',h,re.S)[0]+'\n'
 for n in ['wmi_phy_mode','wmi_cipher_suites','wmi_tlv_cipher_suites','wmi_peer_flags']:
  pre+=re.search(r'enum '+n+r'\s*\{.*?\};',w,re.S)[0]+'\n'
 for n in ['wmi_mac_addr','wmi_ssid','wmi_channel','wmi_key_seq_counter','wmi_vdev_up_cmd','wmi_vdev_install_key_cmd','wmi_vht_rate_set']:
  pre+=re.search(r'struct '+n+r'\s*\{.*?\n\} __packed;',w,re.S)[0]+'\n'
 for n in ['wmi_tlv_vdev_start_cmd','wmi_tlv_peer_assoc_cmd']:
  pre+=re.search(r'struct '+n+r'\s*\{.*?\n\} __packed;',h,re.S)[0]+'\n'
 for n in ['WMI_CHAN_FLAG_PASSIVE','WMI_KEY_PAIRWISE','WMI_KEY_GROUP']:
  pre+=re.search(r'^#define '+n+r'\s+[^\n]+',w,re.M)[0]+'\n'
 return pre+'#endif\n'
if __name__=='__main__':(ROOT/'generated/primary_types.h').write_text(types())
