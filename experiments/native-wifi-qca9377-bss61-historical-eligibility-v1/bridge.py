"""Pure owned/quiescent61 export translation; never creates physical authority."""
from pathlib import Path
import importlib.util,hashlib
ROOT=Path(__file__).resolve().parent
DECODER=ROOT.parent/'native-wifi-qca9377-scan61-observer-v1/decode_scan.py'
DECODER_SHA='abd638a1d3ea0a5d62d45cd9f66d93d6a1a21595dbf3bbae156e4ac7fc065775'
def module():
 if hashlib.sha256(DECODER.read_bytes()).hexdigest()!=DECODER_SHA:raise ValueError('pinned61 export decoder changed')
 spec=importlib.util.spec_from_file_location('historical61_decoder',DECODER);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def translate(capture,root_context):
 m=module();d=m.decode_capture(capture)
 # Root context is structural comparison data. Its authorizing provenance must
 # be independently established from actual receipts/owned immutable capture.
 if (root_context.get('generation'),root_context.get('status_sha256'),root_context.get('epoch'))!=(61,d['status_sha256'],d['epoch']):raise ValueError('Root61 epoch/status binding')
 if d['live_frequency']!=0 or not(d['quiesce_requested'] and d['actual_owners_released'] and d['terminal_seen'] and d['raw_beacon_matches_status'] and d['pending_started']):raise ValueError('quiescent historical61 observation required')
 slot=d['exports']['slots'][16]
 if not (d['start_floor']<slot['completion']<d['terminal_completion']):raise ValueError('observation start/terminal completion bounds')
 beacon=d['beacon'];payload=bytes.fromhex(slot['payload_hex'])
 return {'kind':'COPIED-HISTORICAL61-ADVERTISEMENT-ONLY','generation':61,'quiescent':1,'owners_released':1,'live_frequency':0,'observed_frequency':beacon['frequency_mhz'],'expected_epoch':root_context['epoch'],'observed_epoch':d['epoch'],'completion':slot['completion'],'start_floor':d['start_floor'],'terminal_completion':d['terminal_completion'],'expected_policy_hex':''.join(m.POLICY),'observed_policy_hex':''.join(m.POLICY),'ssid_hex':d['ssid_hex'],'copied_payload_hex':payload.hex(),'copied_payload_sha256':hashlib.sha256(payload).hexdigest(),'status_sha256':d['status_sha256'],'native_capabilities':'UNKNOWN','native_basic_rate_compatibility':'UNRESOLVED','fresh_live_BSS_revalidation_required':True,'association_authority':False,'controlled_port_authority':False,'physical_verified':False}
