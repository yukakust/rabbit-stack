"""Freeze exact fullboot60 diff; reject every unrelated production source edit."""
import argparse,difflib,hashlib,json
from pathlib import Path
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--baseline',type=Path,required=True);ap.add_argument('--candidate',type=Path,required=True);a=ap.parse_args();a.baseline=a.baseline.resolve();a.candidate=a.candidate.resolve()
 baseline=json.loads((a.baseline/'report.json').read_text());candidate=json.loads((a.candidate/'report.json').read_text());repo=a.candidate.parents[3]
 for name,h in baseline['source_sha256'].items():assert sha(repo/name)==h, 'frozen inherited59 source changed '+name
 allowed={'init_probe.c','prefix.c','prefix.h','overlay.h'};changes={};relocated=[];patch='';old_root=str(a.baseline.parents[3]).encode();new_root=str(repo).encode()
 assert set(baseline['generated_compiler_sources_sha256'])==set(candidate['generated_compiler_sources_sha256'])
 for name,h in baseline['generated_compiler_sources_sha256'].items():
  p=a.baseline/name;q=a.candidate/name;assert sha(p)==h;assert sha(q)==candidate['generated_compiler_sources_sha256'][name]
  if '/' in name:continue # Nested outputs are exact-bound world/QEMU model fixtures.
  old=p.read_bytes();new=q.read_bytes();normalized=new.replace(new_root,old_root)
  if normalized!=new:relocated.append(name)
  if normalized!=old:
   assert name in allowed, 'unrelated production source edit '+name
   changes[name]={'baseline_sha256':sha(p),'candidate_sha256':sha(q)}
   patch+=''.join(difflib.unified_diff(old.decode().splitlines(True),normalized.decode().splitlines(True),fromfile='observation59/'+name,tofile='fullboot60/'+name))
 assert set(changes)==allowed
 p=(a.candidate/'prefix.c').read_text();h=(a.candidate/'prefix.h').read_text();probe=(a.candidate/'init_probe.c').read_text()
 assert 'QCA_PREFIX_LIMIT' not in p+h and 'QCA_PREFIX_DEADLINE_US 5400000000ull' in h
 assert 'v[14]={60,' in p and 'f[58]={60,' in probe and '.generation=60ull' in probe
 assert 'qca_wmi_startup_begin(&startup,&operating,now)' in probe and 'qca_wmi_startup_poll(&startup,now)' in probe
 assert 'qca_prefix_request(&prefix,rc<0?3:0' in probe
 assert 'prefix.reason||(qca_init_adapter_released(&adapter)&&!port.claimed)' in probe
 assert candidate['receiver_policy']==dict(baseline['receiver_policy'],generation=60)
 (a.candidate/'production.diff').write_text(patch)
 report={'status':'FULLBOOT60-SCOPED-PRODUCTION-DIFF-PASS','baseline_payload_sha256':baseline['payload_sha256'],'candidate_payload_sha256':candidate['payload_sha256'],'generated_source_count':len(candidate['generated_compiler_sources_sha256']),'production_source_count':sum('/' not in n for n in candidate['generated_compiler_sources_sha256']),'production_changes':changes,'diff_sha256':sha(a.candidate/'production.diff'),'absolute_include_root_relocations':relocated,'relocation_only_referenced_sources_verified':True,'USB_HCI_resident_unchanged':True,'baseline_report_sha256':sha(a.baseline/'report.json'),'candidate_report_sha256':sha(a.candidate/'report.json'),'signing_admitted':False,'device_operations':0}
 (a.candidate/'production-diff-report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
if __name__=='__main__':main()
