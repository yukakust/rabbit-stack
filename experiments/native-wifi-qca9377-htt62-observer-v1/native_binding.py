"""Public immutable native/host ABI join, no physical APIs."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent.parent;C=REPO/'experiments/native-wifi-qca9377-htt62-native-v1/runs/checked-candidate'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
REPORT='9345001639d4eda7d224a8b5d2a7571324ee481f7f3e4c14b33df7f4e8ae46ce'
PAYLOAD='22cde47acd97eec959522b720ebfb6b28fefd2581a32f790fe1f85f2a29d2b81'
compact=lambda s:''.join(s.split())
def check(reader=None):
 if sha(C/'report.json')!=REPORT:raise ValueError('frozen62 report')
 r=json.loads((C/'report.json').read_text())
 if r['native_counter']!=62 or r['payload_sha256']!=PAYLOAD or sha(C/'payload.efi')!=PAYLOAD:raise ValueError('candidate identity')
 for n in ('profile_gatt.c','init_probe.c','firmware_op.c','version.c','htt_native.c'):
  if sha(C/n)!=r['generated_compiler_sources_sha256'][n]:raise ValueError('actual native source '+n)
 g=compact((C/'profile_gatt.c').read_text());s=compact(reader or (ROOT/'read_htt.m').read_text());i=compact((C/'init_probe.c').read_text())
 for token in ('uuid(out+6,start==29?0x2e:0x30);','uuid(out+7,decl==30?0x2f:0x80+(decl-33)/2);','elseif(h==31){qca_htt_status(value);bytes=320;'):
  if token not in g:raise ValueError('actual native UUID/layout')
 for token in ('uid(0x2e)','uid(0x2f)','uid(0x30)','i<30','d.length!=320','word(b+8+54*4)!=62','word(b+8+44*4)!=12','word(b+8+45*4)!=14','word(b+8+46*4)!=4','for(unsignedi=35;i<=43;i++)'):
  if token not in s:raise ValueError('host native field/layout join '+token)
 if '62,persistent.stop_latched' not in i or 'persistent.life.phase==QCA_RADIO_CLOSED&&prefix_released()' not in i:raise ValueError('actual closed ownership semantics')
 return {'status':'HOST-HTT62-NATIVE-UUID-FIELD-JOIN-PASS','candidate_report_sha256':REPORT,'payload_sha256':PAYLOAD,'status_service':'2e','status_value':'2f','status_ATT_handle':31,'raw_service':'30','raw_values':'80..9d','raw_pages':30,'status_bytes':320,'physical_admission':False,'source_sha256':{str((C/n).relative_to(REPO)):sha(C/n) for n in ('profile_gatt.c','init_probe.c','firmware_op.c','version.c','htt_native.c')}}
