"""Pin-check and exact primary structs; no rewritten layout definitions."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parent

def block(text,name):
 start=text.index(name+' {');brace=text.index('{',start);level=1;i=brace+1
 while level:
  if text[i]=='{':level+=1
  if text[i]=='}':level-=1
  i+=1
 return text[start:text.index(';',i)+1]
def header():
 pin=json.loads((ROOT/'references/pin.json').read_text())
 for n,v in pin['files'].items():assert hashlib.sha256((ROOT/'references'/n).read_bytes()).hexdigest()==v['sha256'],n
 htt=(ROOT/'references/htt.h').read_text();htc=(ROOT/'references/htc.h').read_text();wmi=(ROOT/'references/wmi-tlv.h').read_text()
 prefix='''#include <stdint.h>\n#include <stddef.h>\n#include <assert.h>\n#include <string.h>\ntypedef uint8_t u8;typedef uint16_t __le16;typedef uint32_t __le32;\n#define __packed __attribute__((packed))\n#define __aligned(n) __attribute__((aligned(n)))\n'''
 blocks=[block(htc,'struct ath10k_htc_hdr'),block(htt,'struct htt_cmd_hdr'),block(htt,'struct htt_data_tx_desc_frag'),block(htt,'struct htt_data_tx_desc'),block(htt,'struct ath10k_htt_txbuf_32'),block(htt,'enum htt_data_tx_desc_flags0'),block(wmi,'enum wmi_tlv_service')]
 return prefix+'\n'.join(blocks)+r'''
_Static_assert(sizeof(struct ath10k_htc_hdr)==8,"primary HTC8");
_Static_assert(sizeof(struct htt_data_tx_desc)==15,"primary packed descriptor15");
_Static_assert(sizeof(struct htt_data_tx_desc_frag)==8,"primary fragment8");
_Static_assert(sizeof(struct ath10k_htt_txbuf_32)==40,"primary aggregate40");
_Static_assert(offsetof(struct ath10k_htt_txbuf_32,htc_hdr)==16,"two fragment entries");
_Static_assert(offsetof(struct ath10k_htt_txbuf_32,cmd_tx)==25,"packed HTT descriptor offset");
_Static_assert(WMI_TLV_SERVICE_RX_FULL_REORDER==65,"actual service65");
static void primary_tx_assert(const uint8_t*bytes,uint32_t base,const uint8_t*packet,unsigned n,unsigned id,unsigned mode,unsigned tid){
 struct ath10k_htt_txbuf_32 primary={0};
 primary.frags[0].dword_addr.paddr=base+1024;primary.frags[0].dword_addr.len=n;
 primary.htc_hdr.eid=2;primary.htc_hdr.len=(uint16_t)(16+((n<50?n:50)+3u)/4u*4u);primary.cmd_hdr.msg_type=1;
 primary.cmd_tx.flags0=HTT_DATA_TX_DESC_FLAGS0_MAC_HDR_PRESENT|HTT_DATA_TX_DESC_FLAGS0_NO_ENCRYPT|HTT_DATA_TX_DESC_FLAGS0_NO_AGGR|(mode<<5);
 primary.cmd_tx.flags1=(uint16_t)((tid<<6)|0x800);primary.cmd_tx.len=(uint16_t)n;primary.cmd_tx.id=(uint16_t)id;primary.cmd_tx.frags_paddr=base+(mode==3?1024:0);primary.cmd_tx.peerid=65535;
 assert(!memcmp(bytes,&primary,sizeof(primary)));assert(!memcmp(bytes+40,packet,n<50?n:50));assert(!memcmp(bytes+1024,packet,n));
}
'''
