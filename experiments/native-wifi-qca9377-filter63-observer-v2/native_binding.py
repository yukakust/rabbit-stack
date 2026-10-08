"""Actual producer ABI join. Final report/payload pins come from Root, never guessed."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent.parent;PRODUCER=REPO/'experiments/native-wifi-qca9377-filter63-native-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();compact=lambda p:''.join(p.read_text().split())
def need(v,m):
 if not v:raise ValueError(m)
def check(pins=None,reader=None):
 c=PRODUCER/'components';pipeline=compact(c/'pipeline_status.inc');pg=compact(c/'pipeline_gatt.c');sg=compact(c/'scan_gatt.c');native=compact(c/'scan_native.c');fields=re.search(r'uint32_tf\[64\]=\{(.*?)\};',pipeline).group(1).split(',');need(len(fields)==64,'64actualfields')
 need(fields[44]=='actual_released()' and fields[45:55]==['held','port.dma_users','adapter.access.count','port.claimed','adapter.bus.owned','wake.owned','link.owned','irq.owned','boot.owns_pin','ram.asset.pinned'] and fields[55:60]==['adapter.phase','adapter.channels.cleanup_slot','persistent.life.phase','persistent.life.error','63'],'owner/generation actualfieldjoin')
 need(fields[26:38]==['htt_query.phase','htt_query.error','htt_query.attempted','htt_query.dma_completed','htt_query.version_seen','htt_query.version.major','htt_query.version.minor','htt_query.watermark','htt_query.response_completion','htt_query.binding.endpoint','htt_query.binding.max_bytes','htt_query.binding.op_version'],'actual VERSION fields')
 need('uuid(out+6,0x2e);' in pg and 'uuid(out+7,0x2f);' in pg and 'h!=31' in pg and 'uint8_tvalue[448]' in pg,'pipelineGATT31/2e/2f/448')
 need('uuid(out+6,start==32?0x2a:0x2c);' in sg and 'uuid(out+7,decl==33?0x2b:0x80+(decl-36)/2);' in sg,'scanrawGATT2a/2b2c/110')
 need("constuint8_tmagic[8]={'Q','F','E','X','0','0','0','1'};" in native and '2104-offset' in native and 'k<56' in native and 'e->raw[k-56]' in native,'actualraw2104ABI')
 host=''.join((reader or (ROOT/'read_filter.m').read_text()).split())
 for token in ('uid(0x2e)','self.part?0x2b:0x2f','self.discoveries==1?0x2a:0x2c','self.discoveries?0x2b:0x2f','d.length!=448','word(b+8+44*4)!=1','word(b+8+55*4)!=12','word(b+8+56*4)!=14','word(b+8+57*4)!=4','word(b+8+59*4)!=63','for(unsignedi=45;i<=54;i++)','word(b+8+60*4)!=63','self.page%5==4?56:512'):
  need(token in host,'host actualfield/UUID join '+token)
 paths=[c/n for n in ('pipeline_status.inc','pipeline_gatt.c','scan_status.inc','scan_gatt.c','scan_native.c','rx.c')]+[PRODUCER/'filter63_build.py'];result={'status':'ACTUAL-PRODUCER63-GATT-FIELDS-QFEX-ABI-JOIN-DRAFT','source_sha256':{str(p.relative_to(REPO)):sha(p) for p in paths},'pipeline_service':'2e','pipeline_value':'2f','pipeline_bytes':448,'scan_service':'2a','scan_value':'2b','scan_bytes':416,'raw_service':'2c','raw_values':'80..ed','raw_pages':110,'last_page_bytes':56,'native_binding_frozen':False,'physical_admission':False}
 if pins is not None:
  out=PRODUCER/'runs/checked-candidate';need(type(pins) is dict and pins.get('generation')==63 and pins.get('report_sha256') and pins.get('payload_sha256'),'Rootfrozen63 pins required');need(sha(out/'report.json')==pins['report_sha256'] and sha(out/'payload.efi')==pins['payload_sha256'],'Rootfrozen63 identity');r=json.loads((out/'report.json').read_text());need(r['native_counter']==63 and r['payload_sha256']==pins['payload_sha256'],'actualreportidentity')
  for name,h in r['source_sha256'].items():need(sha(REPO/name)==h,'frozenproducerchanged')
  for name,h in r['generated_compiler_sources_sha256'].items():need(sha(out/name)==h,'generatedABI changed')
  result.update(status='ROOT-PINNED-FROZEN63-HOST-NATIVE-ABI-JOIN-PASS',native_binding_frozen=True,report_sha256=pins['report_sha256'],payload_sha256=pins['payload_sha256'])
 return result
