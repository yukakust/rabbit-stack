#!/usr/bin/env python3
"""Reproduce exact signed world bytes for a native release's world-revision binding."""
import argparse
from pathlib import Path
import sys
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from build_image import V3,load,digest

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('world',type=Path)
    parser.add_argument('--counter',type=int,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();sys.path.insert(0,str(V3))
    compiler=load('wireless_export_world',V3/'compile_world.py')
    data=compiler.compile_world(args.world,args.counter,Ed25519PrivateKey.from_private_bytes(bytes(range(32))))
    with args.output.open('xb') as out:out.write(data)
    print('WORLD BYTES SAVED, NOT SENT: '+digest(data).hex())
if __name__=='__main__':main()
