"""Source-only/pure bytes model. No C compilation/device/state/key operations."""
from pathlib import Path
import importlib.util,hashlib,json,struct
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[1];NEW=REPO/'experiments/native-wifi-qca9377-filter63-native-v1/components';FROZEN=REPO/'experiments/native-wifi-qca9377-htt62-native-v1/runs/checked-candidate'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
codec=load('union_review_htc',REPO/'experiments/native-wifi-qca9377-htt62-observer-v2/decode_htt.py')
def main():
 wire=(FROZEN/'htc_wire.c').read_text();rx=(NEW/'rx.c').read_text();header=(NEW/'rx.h').read_text();export=(NEW/'scan_native.c').read_text();checks=0
 assert 'v.payload=p+8;' in wire and 'if(p[1]&~3u)return 0;' in wire
 assert 'union {uint8_t raw[2048];struct {uint8_t htc_header[8],payload[2040];};};' in header
 assert 'if(f.payload!=p+8)return fail(s,14);' in rx
 assert 'e->payload[j]=' not in rx
 cases=[]
 for trailer in (False,True):
  maxn=2040-(8 if trailer else 0)
  for n in range(maxn+1):
   body=bytes((i*7+11)%251 for i in range(n));tail=bytes([1,4,0,0,1,1,0,0]) if trailer else b'';raw=bytes([1,2 if trailer else 0])+struct.pack('<H',len(body)+len(tail))+bytes([8 if trailer else 0,0,0,0])+body+tail
   ep,payload=codec.htc(raw);assert ep==1 and payload==body
   owned=bytearray(raw+bytes(2048-len(raw)));view=memoryview(owned)[8:];snapshot=bytes(owned);normalized=bytes(view[:n])+bytes(2040-n)
   assert normalized==body+bytes(2040-n) and bytes(owned)==snapshot and owned[:len(raw)]==raw
   if trailer:
    assert bytes(view[n:n+8])==tail
    assert any(bytes(view)[n:]) # unbounded old export would leak trailer into normalized padding
   # Value-owned copy survives original DMA zero/repost and source-object deletion.
   copy=bytearray(owned);owned[:]=bytes(2048);assert copy[:len(raw)]==raw
   checks+=1
  cases.append({'trailer':trailer,'payload_lengths':maxn+1})
 # Actual codec rejects bundled/unsupported HTC flags; there is no all-dialect guarantee.
 for flags in (4,8,16,32,64,128,255):
  raw=bytes([1,flags,0,0,0,0,0,0])
  try:codec.htc(raw)
  except ValueError:checks+=1
  else:raise AssertionError('unsupported dialect accepted')
 unbounded='else out[j]=e?e->payload[k-44]:0;' in export
 has_bound=('k-44<e->bytes' in ''.join(export.split()))
 report={'status':'SOURCE-AND-PURE-MODEL-UNION-CONDITIONAL-REVIEW','source_sha256':{str(p.relative_to(REPO)):h(p) for p in [Path(__file__),NEW/'rx.h',NEW/'rx.c',NEW/'scan_native.c',NEW/'dispatch.c',NEW/'coordinator.c',FROZEN/'htc_wire.c']},'pure_model_checks':checks,'cases':cases,'actual_C_producer_or_ABI_tested_by_child':False,'safe_proposal_under_conditions':True,'all_HTC_dialects_supported':False,'payload_pointer_is_embedded_bytes':True,'dangling_pointer_in_embedded_event_copy':False,'raw_trailer_preserved_in_model':True,'current_unbounded_normalized_export':unbounded,'bound_present_in_current_source':has_bound,'requirements':['Exact offsetof payload==offsetof raw+8 and 2048/2040 sizes static_assert on actual native ABI.','Raw-only actual producer copy, no writes or normalized memset beyond payload length.','Serialized QEXP must virtual-zero padding beyond bytes without changing owned raw trailer.','Rebuild all event consumers/oracle/fixtures together; no old-object ABI mixing.','Actual full RX/CE producer and owned copy tested, never incompatible fabricated raw/payload stores.','Mixed credit-only/HTT records need explicit owned routing, strict scan validation preserved.','New host decoder must accept/review present credit-only zero-payload records; frozen old decoder rejects them.','Proof raw full HTC records separate from normalized QEXP when trailer evidence is claimed.'],'native_admission':False,'device_operations':0,'key_accesses':0,'state_operations':0};(ROOT/'evidence/report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],checks,'unbounded',unbounded,'bound',has_bound);print('REPORT',h(ROOT/'evidence/report.json'))
if __name__=='__main__':main()
