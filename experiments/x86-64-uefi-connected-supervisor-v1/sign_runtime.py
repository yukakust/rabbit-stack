#!/usr/bin/env python3
"""Owner-local reviewed RRT3 signing. No Bluetooth, execution or media writes."""
import argparse
from pathlib import Path
from release import pack,digest,UpdateError,MAX_BYTES
from owner_key import load_private
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('private','payload','world-package','output'):p.add_argument('--'+name,type=Path,required=True)
    for name in ('target-sha256','base-runtime-sha256','reviewed-payload-sha256'):p.add_argument('--'+name,required=True)
    p.add_argument('--counter',type=int,required=True);a=p.parse_args()
    if a.payload.stat().st_size>MAX_BYTES-256 or a.world_package.stat().st_size>65535:raise UpdateError('payload/world exceeds budget')
    payload=a.payload.read_bytes()
    if digest(payload).hex()!=a.reviewed_payload_sha256.lower():raise UpdateError('payload does not match explicitly reviewed SHA256')
    data=pack(payload,private=load_private(a.private),target=bytes.fromhex(a.target_sha256),
        base_runtime=bytes.fromhex(a.base_runtime_sha256),world=a.world_package.read_bytes(),counter=a.counter)
    with a.output.open('xb') as out:out.write(data)
    print('SIGNED-NOT-SENT: '+digest(data).hex())
if __name__=='__main__':main()
