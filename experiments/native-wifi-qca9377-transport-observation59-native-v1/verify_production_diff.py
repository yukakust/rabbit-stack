"""Read-only generated production comparison: exactly three generation constants."""
import argparse,difflib,hashlib,json
from pathlib import Path
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--baseline',type=Path,required=True);ap.add_argument('--candidate',type=Path,required=True);a=ap.parse_args();a.baseline=a.baseline.resolve();a.candidate=a.candidate.resolve()
 baseline=json.loads((a.baseline/'report.json').read_text());candidate=json.loads((a.candidate/'report.json').read_text())
 repo=a.candidate.parents[3]
 for name,h in baseline['source_sha256'].items():assert sha(repo/name)==h, 'frozen inherited source changed '+name
 expected={'init_probe.c':[(b'.generation=57ull',b'.generation=59ull'),(b'uint32_t f[58]={57,',b'uint32_t f[58]={59,')], 'prefix.c':[(b'const uint32_t v[14]={57,',b'const uint32_t v[14]={59,')]}
 changes={};relocated=[];patch=''
 old_root=str(a.baseline.parents[3]).encode();new_root=str(repo).encode()
 assert set(baseline['generated_compiler_sources_sha256'])==set(candidate['generated_compiler_sources_sha256'])
 for name,h in baseline['generated_compiler_sources_sha256'].items():
  p=a.baseline/name;q=a.candidate/name;assert sha(p)==h;assert sha(q)==candidate['generated_compiler_sources_sha256'][name]
  if '/' in name:continue # Nested outputs are current-world/QEMU model fixtures, not production inputs.
  old=p.read_bytes();new=q.read_bytes();normalized=new.replace(new_root,old_root)
  if normalized!=new:relocated.append(name)
  want=old
  for x,y in expected.get(name,[]):assert want.count(x)==1;want=want.replace(x,y,1)
  assert normalized==want, 'unapproved generated source diff '+name
  if normalized!=old:
   changes[name]={'baseline_sha256':sha(p),'candidate_sha256':sha(q)}
   patch+=''.join(difflib.unified_diff(old.decode().splitlines(True),normalized.decode().splitlines(True),fromfile='prefix57/'+name,tofile='observation59/'+name))
 assert set(changes)==set(expected)
 (a.candidate/'production.diff').write_text(patch)
 report={'status':'EXACT-THREE-GENERATION-CONSTANTS-PASS','baseline_payload_sha256':baseline['payload_sha256'],'candidate_payload_sha256':candidate['payload_sha256'],'generated_source_count':len(candidate['generated_compiler_sources_sha256']),'production_source_count':sum('/' not in n for n in candidate['generated_compiler_sources_sha256']),'production_changes':changes,'diff_sha256':sha(a.candidate/'production.diff'),'source_changes':3,'absolute_include_root_relocations':relocated,'relocation_only_referenced_sources_verified':True,'USB_HCI_watchdog_unchanged':True,'baseline_report_sha256':sha(a.baseline/'report.json'),'candidate_report_sha256':sha(a.candidate/'report.json'),'signing_admitted':False,'device_operations':0}
 (a.candidate/'production-diff-report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
if __name__=='__main__':main()
