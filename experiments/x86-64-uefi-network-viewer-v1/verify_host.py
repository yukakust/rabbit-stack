#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parent
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=True)
    sources=[ROOT/x for x in ('frame_core.c','frame_test.c','monocypher.c','monocypher-ed25519.c')]
    command=['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror',
             '-fsanitize=address,undefined',*map(str,sources),'-o',str(a.output/'frame-test')]
    subprocess.run(command,check=True)
    result=subprocess.run([str(a.output/'frame-test')],capture_output=True,text=True,timeout=90)
    (a.output/'host.log').write_text(result.stdout+result.stderr)
    report={'passed':result.returncode==0,'exit_code':result.returncode,
            'physical_dell':False,'sanitizers':['address','undefined'],
            'source_sha256':{x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in sources},
            'compiler':subprocess.check_output(['gcc','--version'],text=True).splitlines()[0]}
    (a.output/'host.json').write_text(json.dumps(report,indent=2)+'\n')
    print(result.stdout);print(json.dumps(report))
    return int(not report['passed'])
if __name__=='__main__':raise SystemExit(main())
