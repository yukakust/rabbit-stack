"""Generate exact upstream packed-layout oracle; execution only on Yukabox."""
from pathlib import Path
import re,json,hashlib
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def struct(text,name):
 start=text.index('struct '+name+' {');end=text.index('\n}',start);end=text.index(';',end)+1;return text[start:end]
def generate(out):
 refs=json.loads((R/'references.json').read_text());ref=R/'runs/reference'
 for n,h in refs['files'].items():assert sha(ref/n)==h
 out.mkdir(parents=True,exist_ok=True)
 (out/'linux').mkdir(exist_ok=True);(out/'linux/bitops.h').write_text('#define BIT(n) (1ULL<<(n))\n#define GENMASK(h,l) (((~0ULL)<<(l))&(~0ULL>>(63-(h))))\n')
 (out/'rx_desc.h').write_bytes((ref/'rx_desc.h').read_bytes())
 header=(ref/'htt.h').read_text();parts=[struct(header,n) for n in ('htt_cmd_hdr','htt_rx_ring_rx_desc_offsets','htt_rx_ring_setup_ring32','htt_rx_ring_setup_hdr','htt_rx_desc','htt_rx_desc_v1')]
 text='''#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
typedef uint8_t u8;typedef uint16_t u16;typedef uint32_t u32;typedef uint64_t u64;
typedef uint16_t __le16;typedef uint32_t __le32;typedef uint64_t __le64;
#define __packed __attribute__((packed))
#define RX_HTT_HDR_STATUS_LEN 64
#include "rx_desc.h"
'''+ '\n'.join(parts)+'''
int main(void){printf("{\\\"descriptor_bytes\\\":%zu,\\\"payload_bytes\\\":%zu,\\\"ring32_bytes\\\":%zu,\\\"offsets_words\\\":[",sizeof(struct htt_rx_desc_v1),sizeof(struct htt_cmd_hdr)+sizeof(struct htt_rx_ring_setup_hdr)+sizeof(struct htt_rx_ring_setup_ring32),sizeof(struct htt_rx_ring_setup_ring32));
'''
 names=['rx_hdr_status','msdu_payload','ppdu_start','ppdu_end','mpdu_start','mpdu_end','msdu_start','msdu_end','attention','frag_info']
 for i,n in enumerate(names):text+=f'printf("{"," if i else ""}%zu",offsetof(struct htt_rx_desc_v1,{n})/4);\n'
 text+='printf("]}\\n");return 0;}\n';(out/'oracle.c').write_text(text)
 return refs
if __name__=='__main__':generate(R/'runs/oracle')
