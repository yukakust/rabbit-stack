"""Private derived RX demux: sole CE1/2 owner, native52 bridge unchanged."""
import importlib.util,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
RX=ROOT.parent/'native-wifi-qca9377-persistent-rx-v1'
VERSION=ROOT.parent/'native-wifi-qca9377-htt-version-v1'
sys.path.insert(0,str(RX));import rx_build as prior
one=prior.one
CHECKED=prior.CHECKED;BRIDGE=prior.BRIDGE;BASE=prior.checked.BASE
def sources(directory):
 prior.sources(directory)
 for n in ('version.c','version.h'):(directory/n).write_bytes((VERSION/n).read_bytes())
 for n in ('htt_native.c','htt_native.h'):(directory/n).write_bytes((ROOT/n).read_bytes())
 p=directory/'persistent.h';s=p.read_text();s=one(s,'QcaPersistentRx rx;','QcaPersistentRx rx;void *htt_owner;');p.write_text(s)
 p=directory/'rx.h';s=p.read_text();s=one(s,'#include "lifecycle.h"','#include "lifecycle.h"\n#include "version.h"')
 s=one(s,'uint8_t payload[2040];','uint8_t payload[2040];uint16_t raw_bytes;uint8_t raw[2048];')
 s=one(s,'QcaRxEvent events[2];','QcaRxEvent events[2],rejected;')
 s=one(s,'uint8_t posted[2],head,count,backpressure;', 'QcaHttBinding htt;uint8_t posted[2],head,count,backpressure;');p.write_text(s)
 p=directory/'rx.c';s=p.read_text()
 s=one(s,'s->phase=QCA_RX_ACTIVE;return 1;', 'if(!qca_htt_version_bind(&w->operating->control.session,3,&s->htt)){s->phase=QCA_RX_FAULT;s->error=19;return 0;}\n s->phase=QCA_RX_ACTIVE;return 1;')
 s=one(s,'if(f.endpoint&&f.endpoint!=credit.endpoint)return fail(s,9);', 'if((k==0&&f.endpoint&&f.endpoint!=s->htt.endpoint)||(k==1&&f.endpoint&&f.endpoint!=credit.endpoint))return fail(s,9);')
 s=one(s,'if((k==0&&f.endpoint)||(k==1&&f.endpoint!=credit.endpoint)||f.payload_bytes>2040)return fail(s,10);', 'if((k==1&&f.endpoint!=credit.endpoint)||f.payload_bytes>2040)return fail(s,10);')
 s=one(s,'QcaWmiStartup*w=s->startup;', 'QcaWmiStartup*w=s->startup;QcaHttBinding binding={0};\n if(!qca_htt_version_bind(&w->operating->control.session,3,&binding)||binding.endpoint!=s->htt.endpoint||binding.max_bytes!=s->htt.max_bytes)return fail(s,19);')
 s=one(s,'if(!qca_htc_decode(p,n,&f))return fail(s,8);',
  """s->rejected.completion=s->completed+1;s->rejected.pipe=(uint8_t)(k+1);s->rejected.endpoint=p[0];s->rejected.raw_bytes=(uint16_t)n;
 for(unsigned j=0;j<2048;j++)s->rejected.raw[j]=j<n?p[j]:0;
 if(!qca_htc_decode(p,n,&f))return fail(s,8);""")
 s=one(s,'uint32_t id=s->completed+1;\n if(f.payload_bytes){','uint32_t id=s->completed+1;\n { /* Own even credit-only raw frames; no trailer discard. */')
 s=one(s,'s->count++;',"""e->raw_bytes=(uint16_t)n;for(unsigned j=0;j<2048;j++)e->raw[j]=j<n?p[j]:0;
  s->count++;""")
 s=one(s,'s->startup->operating->control.credit=credit;s->completed=id;return 0;',
  's->startup->operating->control.credit=credit;s->completed=id;s->rejected.completion=0;s->rejected.raw_bytes=0;return 0;')
 p.write_text(s)
