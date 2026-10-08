from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent;repo=R.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 m=json.loads((R/'evidence/2026-10-09/source-closure.json').read_text());c=json.loads((R/'evidence/2026-10-09/coff-report.json').read_text());i=json.loads((R/'evidence/2026-10-09/interop-report.json').read_text())
 assert sha(R/'evidence/2026-10-09/coff-report.json')==m['coff_report_sha256'];assert sha(R/'evidence/2026-10-09/interop-report.json')==m['interop_report_sha256']
 for n,h in m['source_sha256'].items():assert sha(R/n)==h,n
 for n,h in m['mature_tree_sha256'].items():assert sha(R/'runs/tree'/n)==h,n
 for n,h in json.loads((R/'frozen-inputs.json').read_text()).items():assert sha(repo/n)==h,n
 assert sha(R/'runs/coff/supplicant.efi')==m['image_sha256']==c['image_sha256']
 assert sha(R/'child.c')==i['child_source_sha256']==c['compiled_sources_sha256']['child.c'];assert sha(R/'child.h')==i['child_header_sha256']
 for row in i['modes']:assert sha(R/'evidence/2026-10-09'/('mode-'+str(row['mode'])+'.log'))==row['log_sha256']
 assert c['units']==28 and len(i['modes'])==17 and not c['OS_imports'] and not m['physical']
 print('ROLE2-CHILD-PUBLIC-CLOSURE-PASS source='+str(len(m['source_sha256']))+' tree='+str(len(m['mature_tree_sha256'])))
if __name__=='__main__':main()
