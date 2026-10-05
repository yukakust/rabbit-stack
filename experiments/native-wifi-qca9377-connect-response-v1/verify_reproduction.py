#!/usr/bin/env python3
"""Exact current-world reproduction only, never physical signing authorization."""
import hashlib,json
from pathlib import Path
import operating_build as build
from actors_check import check_city
ROOT=build.ROOT;REPO=ROOT.parent.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 out=ROOT/'runs/operating-profile';report=json.loads((out/'report.json').read_text())
 payload=(out/'candidate.efi').read_bytes();assert sha(payload)==report['payload_sha256']
 old_proof=ROOT.parent/'native-wifi-qca9377-operating-diagnostic-v1/runs/operating-profile/reproduction.json'
 baseline=json.loads(old_proof.read_text())['inputs']
 for n,h in baseline.items():assert sha((REPO/n).read_bytes())==h,'baseline input changed:'+n
 inputs={**baseline,**report['source_sha256']}
 for p in ROOT.iterdir():
  if p.is_file():inputs[str(p.relative_to(REPO))]=sha(p.read_bytes())
 def check():
  for n,h in inputs.items():assert sha((REPO/n).read_bytes())==h,n
 check()
 crypto=[out/n for n in ('monocypher.c','monocypher-ed25519.c')]
 provenance=json.loads((build.prior.actors.engine.old.V1/'crypto-provenance.json').read_text())
 for n,h in provenance['files'].items():assert sha((out/Path(n).name).read_bytes())==h,n
 assert build.compile_driver(out,crypto)==payload
 assert build.compile_driver(out,crypto)==payload
 world=Path('/home/yuka/rabbit-world/wifi-bt42-v1/world.rup')
 assert sha(world.read_bytes())=='8254c70465eac5a04612e2e33f74be5afa078c2e71b9f00b5d5e13a8f02f0f5e'
 checks=check_city(world,out/'current-world-check',sanitizers=True)
 check()
 proof={'status':'OPERATING-CURRENT-SOURCES-TWO-REBUILDS-WORLD-C-CHECK-PASS','payload_sha256':sha(payload),'inputs':inputs,'native44_reproduction_sha256':sha(old_proof.read_bytes()),'world_package_sha256':sha(world.read_bytes()),'crypto_provenance':provenance,'host_checks':checks,'build_host':'yukabox','physical_signing_admitted':False,'physical_verified':False,'wifi_connected':False}
 (out/'reproduction.json').write_text(json.dumps(proof,indent=2)+'\n');print(proof['status'],'inputs',len(inputs))
if __name__=='__main__':main()
