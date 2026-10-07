"""Copy immutable public55 evidence to a NEW own output; no operational state."""
from pathlib import Path
import json,shutil
import gate
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent.parent
S=REPO/'experiments/x86-64-uefi-connected-supervisor-v1/runs/text-world'
def main():
 out=ROOT/'runs/public55';out.mkdir(exist_ok=False)
 manifest={}
 for folder in ('pci-native-ehv85hvp','firmware-ram-g4w7ruqs'):
  dst=out/folder;dst.mkdir()
  for p in sorted((S/folder).iterdir()):
   if p.is_file():shutil.copyfile(p,dst/p.name);manifest[str((dst/p.name).relative_to(out))]=gate.sha(p.read_bytes())
 for name in ('world.rup','world.json'):
  p=S/'native48-city-recovery-plan'/name;shutil.copyfile(p,out/name);manifest[name]=gate.sha(p.read_bytes())
 checked=REPO/'experiments/native-wifi-qca9377-scan-native-profile-v2/runs/checked-candidate'
 shutil.copyfile(checked/'report.json',out/'checked55-report.json');manifest['checked55-report.json']=gate.sha((checked/'report.json').read_bytes())
 result=gate.public_bundle(REPO,S/'pci-native-ehv85hvp',S/'firmware-ram-g4w7ruqs',checked,out/'world.rup')
 result['archived_public_files']=manifest;result['production_state_read']=False
 (out/'manifest.json').write_text(json.dumps(result,indent=2)+'\n')
 print('PUBLIC55-EXACT-SIGNED-BUNDLE-642-SOURCE-ARCHIVED-PASS',len(manifest))
if __name__=='__main__':main()
