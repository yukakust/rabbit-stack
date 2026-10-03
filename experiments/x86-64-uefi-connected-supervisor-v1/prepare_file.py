#!/usr/bin/env python3
"""Wrap exact signed world/native bytes in a resumable session. No send."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import secrets
import struct
def bundle(data,kind,counter,nonce=None):
    maximum=65535 if kind==1 else 262144 if kind==2 else 0
    if type(data) is not bytes or not 1<=len(data)<=maximum or type(counter) is not int or not 1<=counter<=0xffffffff:
        raise ValueError('invalid file kind, size or counter')
    if kind==1:
        if len(data)<12 or data[:4] not in (b'RUP2',b'RUP3',b'RUP4') or struct.unpack_from('<I',data,8)[0]!=counter:
            raise ValueError('signed world header/counter mismatch')
    else:
        if len(data)<257 or data[:4]!=b'RRT3' or struct.unpack_from('<Q',data,24)[0]!=counter:
            raise ValueError('signed owner release header/counter mismatch')
    nonce=secrets.token_bytes(8) if nonce is None else nonce
    if type(nonce) is not bytes or len(nonce)!=8:raise ValueError('8-byte session required')
    digest=hashlib.sha256(data).digest()
    return {'schema_version':1,'status':'PREPARED-NOT-SENT','kind':kind,'counter':counter,
      'sha256':digest.hex(),'package_bytes':len(data),'session_base64':base64.b64encode(nonce).decode(),
      'stream_base64':base64.b64encode(digest+data).decode()}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('package',type=Path)
    p.add_argument('--kind',choices=('world','runtime'),required=True);p.add_argument('--counter',type=int,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.package.stat().st_size>(65535 if a.kind=='world' else 262144):raise ValueError('file too large')
    b=bundle(a.package.read_bytes(),1 if a.kind=='world' else 2,a.counter)
    with a.output.open('x') as out:json.dump(b,out,indent=2)
    print(f"PREPARED-NOT-SENT: {a.output}; SHA256={b['sha256']}")
    print('Header/transport checked only; Dell must independently verify signature, bounds and health.')
if __name__=='__main__':main()
