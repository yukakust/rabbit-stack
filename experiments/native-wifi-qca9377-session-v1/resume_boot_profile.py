#!/usr/bin/env python3
"""Resume only missing QEMU/final gates after unchanged full host checks."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'native-wifi-qca9377-v1'))
import verify_init_profile as prior
import verify_boot_profile as boot

def resume(**kw):
 build=kw['builder'];out=prior.ROOT/'runs'/kw['profile']
 probe=json.loads((out/'probe-report.json').read_text())
 assert probe['scenarios']==65 and probe['native_entrypoints_integrated']
 for name,h in probe['source_sha256'].items():assert prior.sha((prior.ROOT/name).read_bytes())==h,name
 log=(out/'host.log').read_text()
 assert 'QPD18 exact65 snapshots + 2595 corrupt bounds/split/success rejections PASS' in log
 for component in ('port','reset','init','probe'):
  report=json.loads((out/(component+'-report.json')).read_text())
  assert prior.sha((out/(component+'-host.log')).read_bytes())==report['host_log_sha256']
 paths=sorted(p for p in prior.ROOT.iterdir() if p.suffix in ('.c','.h','.py','.json'))
 paths += [build.CITY/n for n in ('actors_build.py','city_core.c','city_core.h','city_display.c','actor_clock.c','actors_gate.py')]
 inputs={str(p.relative_to(prior.ROOT.parent.parent)):prior.sha(p.read_bytes()) for p in paths}
 payload=(out/'payload.efi').read_bytes()
 if (out/'report.json').exists():
  report=json.loads((out/'report.json').read_text())
  assert report['source_sha256']==inputs and report['payload_sha256']==prior.sha(payload)
  assert report['host_log_sha256']==prior.sha((out/'host.log').read_bytes())
  assert len(report['gates'])==2 and {g['empty_boot'] for g in report['gates']}=={False,True}
  for gate in report['gates']:
   q=out/('actors-empty-boot-qemu' if gate['empty_boot'] else 'actors-qemu')
   assert json.loads((q/'report.json').read_text())==gate
   assert gate['payload_sha256']==prior.sha(payload) and gate['observed_log_sha256']==prior.sha((q/'observed.log').read_bytes())
   assert b'FRAGMENTED16+5 CONNECTION AND MATCHED DISCONNECTION VERIFIED' in (q/'observed.log').read_bytes()
  print('UNCHANGED COMPLETE HOST/QEMU PROOFS REUSED; finishing remaining boot gates')
  return
 source=Path(prior.__file__).read_text()
 start=source.index(' gates=[prior.actors_gate.qemu_gate(')
 end=source.index("\nif __name__=='__main__':")
 # Execute the original QEMU/report tail, with the same validated host inputs.
 tail='\n'.join(line[1:] for line in source[start:end].splitlines())
 env={**vars(prior),**kw,'ROOT':prior.ROOT,'build':build,'out':out,'payload':payload,'paths':paths,'inputs':inputs,'log':log}
 exec(compile(tail,str(Path(prior.__file__))+'#resume-qemu-tail','exec'),env)

if __name__=='__main__':
 prior.main=resume
 boot.main()
