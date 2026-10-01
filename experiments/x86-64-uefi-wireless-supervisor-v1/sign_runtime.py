#!/usr/bin/env python3
"""Owner-local explicit reviewed release signing; never invokes Bluetooth."""
import argparse
from pathlib import Path
from release import pack,digest,UpdateError,MAX_BYTES
from owner_key import load_private

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('private','payload','world-package','output'):parser.add_argument('--'+name,type=Path,required=True)
    for name in ('target-sha256','base-runtime-sha256','reviewed-payload-sha256'):parser.add_argument('--'+name,required=True)
    parser.add_argument('--counter',type=int,required=True);args=parser.parse_args()
    if args.payload.stat().st_size>MAX_BYTES-256 or args.world_package.stat().st_size>65535:raise UpdateError('payload/world exceeds budget')
    payload=args.payload.read_bytes()
    if digest(payload).hex()!=args.reviewed_payload_sha256.lower():raise UpdateError('payload differs from explicitly reviewed SHA256')
    data=pack(payload,private=load_private(args.private),target=bytes.fromhex(args.target_sha256),
              base_runtime=bytes.fromhex(args.base_runtime_sha256),world=args.world_package.read_bytes(),counter=args.counter)
    with args.output.open('xb') as out:out.write(data)
    print('SIGNED-NOT-SENT: '+digest(data).hex())
if __name__=='__main__': main()
