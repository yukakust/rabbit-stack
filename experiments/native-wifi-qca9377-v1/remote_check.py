#!/usr/bin/env python3
"""Yukabox reproduction/current-world check; never receives owner secrets."""
import argparse,hashlib,json,sys
from pathlib import Path
import diagnostic_build as build
from actors_check import check_city
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--inputs',type=Path,required=True);p.add_argument('--world',type=Path,required=True)
 p.add_argument('--profile',choices=('diagnostic','bringup'),default='diagnostic')
 a=p.parse_args()
 if a.profile=='bringup':
  import bringup_build
  builder=bringup_build
 else:builder=build
 inputs=json.loads(a.inputs.read_text());out=ROOT/'runs'/a.profile
 def check_inputs():
  for name,expected in inputs.items():
   path=Path(name)
   if path.is_absolute() or '..' in path.parts or sha((REPO/path).read_bytes())!=expected:
    raise ValueError('source snapshot differs: '+name)
 check_inputs()
 crypto=[out/'monocypher.c',out/'monocypher-ed25519.c']
 provenance=json.loads((build.actors.engine.old.V1/'crypto-provenance.json').read_text())
 for name,expected in provenance['files'].items():
  assert sha((out/Path(name).name).read_bytes())==expected,'crypto source changed'
 payload=(out/'payload.efi').read_bytes()
 assert builder.compile_driver(out,crypto)==payload
 assert builder.compile_driver(out,crypto)==payload
 checks=check_city(a.world,out/'current-world-check',sanitizers=True)
 check_inputs()
 report={'status':'CURRENT-SOURCES-TWO-REBUILDS-WORLD-C-CHECK-PASS',
  'payload_sha256':sha(payload),'inputs':inputs,'world_package_sha256':sha(a.world.read_bytes()),
  'crypto_provenance':provenance,'host_checks':checks,'build_host':'yukabox','physical_verified':False}
 (out/'reproduction.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
