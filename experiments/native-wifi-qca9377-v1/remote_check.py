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
 p.add_argument('--profile',choices=('diagnostic','bringup','power','reset','bmi','init','full-read','config-read','setup','receiver','board','boot'),default='diagnostic')
 a=p.parse_args()
 if a.profile=='boot':
  import boot_build
  builder=boot_build
 elif a.profile=='board':
  import board_build
  builder=board_build
 elif a.profile=='receiver':
  import receiver_build
  builder=receiver_build
 elif a.profile=='setup':
  import setup_build
  builder=setup_build
 elif a.profile=='config-read':
  import config_read_build
  builder=config_read_build
 elif a.profile=='full-read':
  import full_read_build
  builder=full_read_build
 elif a.profile=='bringup':
  import bringup_build
  builder=bringup_build
 elif a.profile=='power':
  import power_build
  builder=power_build
 elif a.profile=='init':
  import init_build
  builder=init_build
 elif a.profile=='bmi':
  import bmi_build
  builder=bmi_build
 elif a.profile=='reset':
  import reset_build
  builder=reset_build
 else:builder=build
 inputs=json.loads(a.inputs.read_text());out=ROOT/'runs'/('boot-profile' if a.profile=='boot' else 'board-profile' if a.profile=='board' else 'receiver-profile' if a.profile=='receiver' else 'bmi-profile' if a.profile=='bmi' else 'setup-profile' if a.profile=='setup' else 'config-read-profile' if a.profile=='config-read' else 'full-read-profile' if a.profile=='full-read' else 'init-profile' if a.profile=='init' else a.profile)
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
