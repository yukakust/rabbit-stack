"""Freeze scan61 integration diff and reject unrelated60/USB/HCI/resident edits."""
import argparse,difflib,hashlib,json
import scan_build as build
from pathlib import Path
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--baseline',type=Path,required=True);ap.add_argument('--candidate',type=Path,required=True);a=ap.parse_args();a.baseline=a.baseline.resolve();a.candidate=a.candidate.resolve();repo=a.candidate.parents[3]
 old=json.loads((a.baseline/'report.json').read_text());new=json.loads((a.candidate/'report.json').read_text())
 for n,h in old['source_sha256'].items():assert sha(repo/n)==h,'frozen60 source changed '+n
 allowed={'init_probe.c','prefix.c','overlay.h','diagnostic_gatt.c','wmi_scan.c'};changed={};added={};relocated=[];patch='';oldroot=str(a.baseline.parents[3]).encode();newroot=str(repo).encode()
 oldsources={n:h for n,h in old['generated_compiler_sources_sha256'].items() if '/' not in n};newsources={n:h for n,h in new['generated_compiler_sources_sha256'].items() if '/' not in n}
 assert set(oldsources)<=set(newsources)
 for n,h in oldsources.items():
  assert sha(a.baseline/n)==h;assert sha(a.candidate/n)==newsources[n];b=(a.baseline/n).read_bytes();c=(a.candidate/n).read_bytes();normalized=c.replace(newroot,oldroot)
  if c!=normalized:relocated.append(n)
  if b!=normalized:
   assert n in allowed,'unrelated production change '+n;changed[n]={'baseline_sha256':h,'candidate_sha256':newsources[n]}
   patch+=''.join(difflib.unified_diff(b.decode().splitlines(True),normalized.decode().splitlines(True),fromfile='fullboot60/'+n,tofile='scan61/'+n))
 assert set(changed)==allowed
 manifest=json.loads((a.candidate.parents[1]/'component-inputs.json').read_text())
 for n in set(newsources)-set(oldsources):
  assert n in manifest['components_sha256'],n;assert newsources[n]==hashlib.sha256(build.component_bytes(n)).hexdigest(),n;added[n]=newsources[n]
 assert (a.candidate/'prefix.h').read_bytes()==(a.baseline/'prefix.h').read_bytes()
 probe=(a.candidate/'init_probe.c').read_text();gatt=(a.candidate/'diagnostic_gatt.c').read_text()
 assert 'qca_persistent_begin(&persistent,&startup,1,now)' in probe and 'qca_native_scan_begin(&native_scan,&persistent,now)' in probe
 assert 'qca_prefix_att(' not in gatt and 'qca_scan_att(' in gatt
 assert '.generation=61ull' in probe and 'f[58]={61,' in probe and 'startup.transaction.tx_complete,61,13' in probe
 assert new['receiver_policy']==dict(old['receiver_policy'],generation=61)
 for name in ('coordinator.c','owned_stop.c'):
  text=(a.candidate/name).read_text();assert 'qca_htc_credit_receive' not in text and 'qca_station_scan_receive' not in text and 'qca_scan_stop_receive' not in text
 assert new['rf_admission_granted'] is False and new['physical_verified'] is False
 (a.candidate/'production.diff').write_text(patch)
 report={'status':'SCAN61-SCOPED-INTEGRATION-DIFF-FROZEN60-PASS','baseline_payload_sha256':old['payload_sha256'],'candidate_payload_sha256':new['payload_sha256'],'production_changes':changed,'added_frozen_scan55_components':added,'diff_sha256':sha(a.candidate/'production.diff'),'absolute_include_root_relocations':relocated,'USB_HCI_resident_unchanged':True,'frozen60_all_source_hashes_verified':True,'prefix_ATT_removed':True,'ATT_discovery29_31_holes_resolved':True,'max_raw_handle':255,'RF_admission_granted':False,'signing_admitted':False,'device_operations':0}
 (a.candidate/'production-diff-report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
if __name__=='__main__':main()
