#!/usr/bin/env python3
"""Prepare a signed world/file session; NEVER compiles, connects, or sends."""
import argparse
import base64
import hashlib
import json
import secrets
import sys
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

ROOT=Path(__file__).resolve().parent
V3=ROOT.parent/'x86-64-uefi-god-runtime-v3'


def compile_packet(world,counter):
    # Run this adapter in its own process; v3 compiler retains strict schema and
    # exact development Creator identity, not owner-native authority.
    sys.path.insert(0,str(V3))
    from compile_world import compile_world
    return compile_world(world,counter,Ed25519PrivateKey.from_private_bytes(bytes(range(32))))


def bundle(packet,counter,session=None):
    session=secrets.token_bytes(8) if session is None else session
    if len(session)!=8 or not 1<=len(packet)<=65535:
        raise ValueError('invalid bounded file/session')
    digest=hashlib.sha256(packet).digest()
    return {'schema_version':1,'status':'PREPARED-NOT-SENT-NO-DELL-GATT-ADAPTER',
            'counter':counter,'sha256':digest.hex(),'package_bytes':len(packet),
            'session_base64':base64.b64encode(session).decode(),
            'stream_base64':base64.b64encode(digest+packet).decode()}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('world',type=Path)
    parser.add_argument('--counter',type=int,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    candidate=bundle(compile_packet(args.world,args.counter),args.counter)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as out:json.dump(candidate,out,indent=2)
    print(f"PREPARED-NOT-SENT: {args.output}; {candidate['package_bytes']} bytes; SHA256={candidate['sha256']}")
    print('Dell GATT service and exclusive HCI event ownership are NOT installed. Do not run the Mac sender yet.')


if __name__=='__main__':main()
