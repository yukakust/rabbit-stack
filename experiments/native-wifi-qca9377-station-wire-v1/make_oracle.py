"""Compile the actual primary generator bodies in an explicitly hosted fixture."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parent
def body(source,name):
 s=source[source.index(name+'('):];at=s.index('{');depth=0
 for j in range(at,len(s)):
  depth+=s[j]=='{';depth-=s[j]=='}'
  if not depth:return s[:j+1]
 raise AssertionError(name)
def oracle():
 w=(ROOT/'references/wmi.h').read_text();c=(ROOT/'references/wmi-tlv.c').read_text();common=(ROOT/'references/wmi.c').read_text()
 structs=''
 for n in ['wmi_channel_arg','wmi_vdev_start_request_arg','wmi_vdev_install_key_arg','wmi_rate_set_arg','wmi_vht_rate_set_arg','wmi_peer_assoc_complete_arg']:
  structs+=re.search(r'struct '+n+r'\s*\{.*?\n\};',w,re.S)[0]+'\n'
 defines='\n'.join(re.findall(r'^#define (?:WMI_CHAN_FLAG_\w+|WMI_VDEV_START_\w+|MAX_SUPPORTED_RATES)\s+[^\n]+',w,re.M))
 pre='''/* Synthetic hosted fixture: exact original Linux generator function bodies.
 * calloc supplies genuine CPU storage only; no kernel/radio/device operation. */
#include "wire.h"
#include "generated/primary_types.h"
#include <stdlib.h>
#include <string.h>
#define ETH_ALEN 6
#define u16 uint16_t
#define EINVAL 22
#define ENOMEM 12
#define WARN_ON(x) (x)
#define ERR_PTR(x) ((void*)0)
#define __cpu_to_le16(x) (x)
#define __cpu_to_le32(x) (x)
#define roundup(x,n) (((x)+(n)-1)&~((n)-1))
#define ether_addr_copy(a,b) memcpy(a,b,6)
#define ath10k_dbg(...) ((void)0)
#define ATH10K_DBG_WMI 0
#define IEEE80211_CHAN_RADAR 1
struct ieee80211_channel {unsigned flags;};
struct ath10k {uint8_t wmi_key_cipher[16];struct {void*wiphy;} hw_data;struct {void*wiphy;}*hw;};
struct sk_buff {uint8_t*data;unsigned len;};
struct wmi_tlv {uint16_t len,tag;uint8_t value[];} __packed;
static struct sk_buff*ath10k_wmi_alloc_skb(struct ath10k*ar,size_t n){(void)ar;struct sk_buff*s=calloc(1,sizeof(*s));if(!s)return 0;s->data=calloc(1,n);if(!s->data){free(s);return 0;}s->len=(unsigned)n;return s;}
/* Extended channel lookup is never part of admitted legacy fixture inputs. */
static struct ieee80211_channel*ieee80211_get_channel(void*p,unsigned n){(void)p;(void)n;return 0;}
'''+defines+'\n'+structs+'\nvoid '+body(common,'ath10k_wmi_put_wmi_channel')+'\n'
 for name in ['ath10k_wmi_tlv_op_gen_vdev_start','ath10k_wmi_tlv_op_gen_vdev_up','ath10k_wmi_tlv_op_gen_peer_assoc','ath10k_wmi_tlv_op_gen_vdev_install_key']:
  pre+='static struct sk_buff*'+body(c,name)+'\n'
 return pre+'''
static unsigned finish(uint8_t*out,uint32_t command,struct sk_buff*s){if(!s)return 0;memcpy(out,&command,4);memcpy(out+4,s->data,s->len);unsigned n=s->len+4;memset(s->data,0,s->len);free(s->data);free(s);return n;}
unsigned oracle_start(uint8_t*out,const StaWireBss*b){struct ath10k ar={0};struct wmi_vdev_start_request_arg a={0};a.vdev_id=b->vdev;a.bcn_intval=b->interval;a.dtim_period=b->dtim;uint8_t ssid[32];memcpy(ssid,b->ssid,32);a.ssid=ssid;a.ssid_len=b->ssid_bytes;a.channel.freq=a.channel.band_center_freq1=b->frequency;a.channel.mode=b->mode;a.channel.min_power=b->min_power;a.channel.max_power=b->max_power;a.channel.max_reg_power=b->reg_power;a.channel.max_antenna_gain=b->antenna;return finish(out,WMI_TLV_VDEV_START_REQUEST_CMDID,ath10k_wmi_tlv_op_gen_vdev_start(&ar,&a,false));}
unsigned oracle_up(uint8_t*out,const StaWireBss*b,unsigned aid){struct ath10k ar={0};return finish(out,WMI_TLV_VDEV_UP_CMDID,ath10k_wmi_tlv_op_gen_vdev_up(&ar,b->vdev,aid,b->peer));}
unsigned oracle_assoc(uint8_t*out,const StaWireBss*b,unsigned aid,unsigned mask,unsigned caps,unsigned listen){struct ath10k ar={0};struct wmi_peer_assoc_complete_arg a={0};static const uint8_t rates[]={2,4,11,22,12,18,24,36,48,72,96,108};memcpy(a.addr,b->peer,6);a.vdev_id=b->vdev;a.peer_aid=aid;a.peer_flags=WMI_PEER_AUTH|WMI_PEER_NEED_PTK_4_WAY;a.peer_caps=caps;a.peer_listen_intval=listen;a.peer_num_spatial_streams=1;a.peer_phymode=b->mode;for(unsigned j=0;j<12;j++)if(mask&(1u<<j))a.peer_legacy_rates.rates[a.peer_legacy_rates.num_rates++]=(uint8_t)(rates[j]|(j<4?128:0));return finish(out,WMI_TLV_PEER_ASSOC_CMDID,ath10k_wmi_tlv_op_gen_peer_assoc(&ar,&a));}
unsigned oracle_key(uint8_t*out,const StaWireBss*b,unsigned index,const uint8_t*key){struct ath10k ar={0};ar.wmi_key_cipher[WMI_CIPHER_AES_CCM]=WMI_TLV_CIPHER_AES_CCM;struct wmi_vdev_install_key_arg a={0};a.vdev_id=b->vdev;a.macaddr=b->peer;a.key_idx=index;a.key_flags=index?WMI_KEY_GROUP:WMI_KEY_PAIRWISE;a.key_cipher=ar.wmi_key_cipher[WMI_CIPHER_AES_CCM];a.key_len=16;a.key_data=key;return finish(out,WMI_TLV_VDEV_INSTALL_KEY_CMDID,ath10k_wmi_tlv_op_gen_vdev_install_key(&ar,&a));}
'''
if __name__=='__main__':(ROOT/'runs/host/oracle.c').write_text(oracle())
