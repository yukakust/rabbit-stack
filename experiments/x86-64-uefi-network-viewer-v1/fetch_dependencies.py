#!/usr/bin/env python3
"""Fetch pinned public source only. Never accepts or accesses an owner key."""
import hashlib
import json
from pathlib import Path
import subprocess
import urllib.request
ROOT=Path(__file__).resolve().parent
IPXE='6262f1081fe185564e8ec8365a1d23597ec6e6f5'
def main():
    vendor=ROOT/'vendor/ipxe';vendor.parent.mkdir(exist_ok=True)
    if not vendor.exists():
        subprocess.run(['git','init',str(vendor)],check=True,stdout=subprocess.DEVNULL)
        subprocess.run(['git','-C',str(vendor),'remote','add','origin','https://github.com/ipxe/ipxe.git'],check=True)
        subprocess.run(['git','-C',str(vendor),'fetch','--depth','1','origin',IPXE],check=True)
        subprocess.run(['git','-C',str(vendor),'checkout','--detach','FETCH_HEAD'],check=True)
    if subprocess.check_output(['git','-C',str(vendor),'rev-parse','HEAD'],text=True).strip()!=IPXE:
        raise SystemExit('existing iPXE checkout differs; not modified')
    provenance=json.loads((ROOT/'crypto-provenance.json').read_text())
    for source,expected in provenance['files'].items():
        path=ROOT/Path(source).name if source!='LICENCE.md' else ROOT/'vendor/monocypher-LICENCE.md'
        if path.exists():data=path.read_bytes()
        else:
            url=f"https://raw.githubusercontent.com/LoupVaillant/Monocypher/{provenance['git_commit']}/{source}"
            with urllib.request.urlopen(url,timeout=30) as response:data=response.read()
        if hashlib.sha256(data).hexdigest()!=expected:raise SystemExit('crypto source hash mismatch: '+source)
        path.write_bytes(data)
    print('Pinned iPXE and Monocypher sources verified')
if __name__=='__main__':main()
