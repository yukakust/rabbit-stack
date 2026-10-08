"""Copy exact pinned type text into a native-only layout oracle."""
from pathlib import Path
import re,json,hashlib
R=Path(__file__).resolve().parent
m=json.loads((R/'references.json').read_text())
for n,h in m['files'].items():assert hashlib.sha256((R/'references'/n).read_bytes()).hexdigest()==h
h=(R/'references/htt.h').read_text();rx=(R/'references/rx_desc.h').read_text();rx=re.sub(r'#include[^\n]*','',rx)
def struct(name):
 start=re.search(r'struct '+name+r'\s*\{',h).start();depth=0
 for at in range(h.index('{',start),len(h)):
  if h[at]=='{':depth+=1
  elif h[at]=='}':
   depth-=1
   if depth==0:return h[start:h.index(';',at)+1]
preamble='''#include <stdio.h>
#include <stdint.h>
#include <stddef.h>
typedef uint8_t u8;typedef uint16_t u16;typedef uint32_t u32;typedef uint64_t u64;typedef uint16_t __le16;typedef uint32_t __le32;typedef uint64_t __le64;
#define BIT(n) (1u<<(n))
#define __packed __attribute__((packed))
#define DECLARE_FLEX_ARRAY(TYPE,NAME) struct { struct {} __empty_##NAME; TYPE NAME[]; }
'''
preamble+=re.search(r'#define RX_HTT_HDR_STATUS_LEN[^\n]*',h)[0]+'\n'
types='\n'.join(struct(x) for x in ['htt_rx_indication_hdr','htt_rx_indication_ppdu','htt_rx_indication_prefix','htt_rx_indication_mpdu_range','htt_rx_in_ord_msdu_desc','htt_rx_in_ord_msdu_desc_ext','htt_rx_in_ord_ind','htt_rx_desc','htt_rx_desc_v1'])
items={'desc_size':'sizeof(struct htt_rx_desc_v1)','attention':'offsetof(struct htt_rx_desc_v1,attention)','frag':'offsetof(struct htt_rx_desc_v1,frag_info)','mpdu_start':'offsetof(struct htt_rx_desc_v1,mpdu_start)','msdu_start':'offsetof(struct htt_rx_desc_v1,msdu_start)','msdu_end':'offsetof(struct htt_rx_desc_v1,msdu_end)','payload':'offsetof(struct htt_rx_desc_v1,msdu_payload)','hdr_status':'offsetof(struct htt_rx_desc_v1,rx_hdr_status)','ind_hdr':'sizeof(struct htt_rx_indication_hdr)','ind_ppdu':'sizeof(struct htt_rx_indication_ppdu)','ind_prefix':'sizeof(struct htt_rx_indication_prefix)','range':'sizeof(struct htt_rx_indication_mpdu_range)','inord_hdr':'sizeof(struct htt_rx_in_ord_ind)','paddr32':'sizeof(struct htt_rx_in_ord_msdu_desc)','paddr64':'sizeof(struct htt_rx_in_ord_msdu_desc_ext)','MSDU_DONE':'RX_ATTENTION_FLAGS_MSDU_DONE','LENGTH_MASK':'RX_MSDU_START_INFO0_MSDU_LENGTH_MASK','DECAP_MASK':'RX_MSDU_START_INFO1_DECAP_FORMAT_MASK','FIRST':'RX_MSDU_END_INFO0_FIRST_MSDU','LAST':'RX_MSDU_END_INFO0_LAST_MSDU','ERROR_MASK':'RX_ATTENTION_FLAGS_MSDU_LENGTH_ERR|RX_ATTENTION_FLAGS_MPDU_LENGTH_ERR|RX_ATTENTION_FLAGS_FCS_ERR|RX_ATTENTION_FLAGS_DECRYPT_ERR|RX_ATTENTION_FLAGS_TKIP_MIC_ERR'}
body='int main(void){\n'+''.join('printf("'+n+'=%zu\\n",(size_t)('+v+'));\n' for n,v in items.items())+'return 0;}\n';out=R/'runs';out.mkdir(exist_ok=True);(out/'oracle.c').write_text(preamble+rx+types+body)
(out/'oracle_types.h').write_text(preamble+rx+types)
