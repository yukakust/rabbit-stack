#!/usr/bin/env python3
"""Mac-only RPv3 native release sender. Never signs generated/LLM code."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import uuid
from build_image import ROOT,V3,load,replace,digest,TEST_OWNER
from release import verify,UpdateError,MAX_BYTES
runtime_transport=load('wireless_runtime_transport',ROOT.parent/'runtime-update-contract-v1/transport.py')

def encode_segments(data,block_chunks=32):
    if type(block_chunks) is not int or not 1<=block_chunks<=64: raise ValueError('invalid checkpoint block size')
    frames=runtime_transport.encode(data);chunks=frames[1:-1];segments=[];hashes=[]
    for start in range(0,len(chunks),block_chunks):
        end=min(start+block_chunks,len(chunks));length=min(end*6,len(data));hash=runtime_transport.fnv(data[:length])
        block=([frames[0]] if start==0 else [])+chunks[start:end]
        block.append(runtime_transport.frame(3,frames[0][3],end,hash.to_bytes(4,'big')))
        segments.append([str(uuid.UUID(bytes=f)).upper() for f in block]);hashes.append(f'{hash:08X}')
    return {'segments':segments,'hashes':hashes}

def sender_source():
    # Import the original bounded world sender in a fresh process, so its legacy
    # package/transport module names cannot collide with runtime envelope helpers.
    source=subprocess.check_output([sys.executable,'-c','import send_package; print(send_package.sender_source(),end="")'],cwd=V3,text=True)
    source=replace(source,'segments.count > 342','segments.count > 1366')
    if source.count('bytes[2] != 0x11')!=2: raise ValueError('reviewed sender family markers changed')
    source=source.replace('bytes[2] != 0x11','(bytes[2] != 0x21 && bytes[2] != 0x22 && bytes[2] != 0x23)')
    source=replace(source,'        if (self.segment+1 < self.segments.count) {','''        if (bytes[2]==0x23) {
            fprintf(stderr,"RUNTIME REJECTED: old engine retained (receipt is unauthenticated)\\n");
            [self.timer invalidate]; [self.peripheral stopAdvertising]; [central stopScan]; exit(3);
        }
        BOOL finalBlock=(self.segment+1==self.segments.count);
        if (bytes[2] != (finalBlock ? 0x21 : 0x22)) continue;
        if (self.segment+1 < self.segments.count) {''')
    source=source.replace('ACK RECEIVED: TRANSFER=','RUNTIME APPLIED RECEIPT (NOT ATTESTATION): TRANSFER=')
    return source

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('release',type=Path)
    for name in ('owner-public','world-package'): parser.add_argument('--'+name,type=Path,required=True)
    for name in ('target-sha256','base-runtime-sha256'): parser.add_argument('--'+name,required=True)
    parser.add_argument('--minimum-counter',type=int,required=True)
    parser.add_argument('--send',action='store_true',help='explicitly advertise reviewed signed native release')
    args=parser.parse_args()
    if args.release.stat().st_size>MAX_BYTES: raise UpdateError('release too large')
    if args.world_package.stat().st_size>65535: raise UpdateError('world too large')
    data=args.release.read_bytes()
    owner=args.owner_public.read_bytes()
    if args.send and owner==TEST_OWNER:raise UpdateError('public QEMU fixture releases must never be advertised to physical devices')
    candidate=verify(data,target=bytes.fromhex(args.target_sha256),owner=owner,
                     base_runtime=bytes.fromhex(args.base_runtime_sha256),world=args.world_package.read_bytes(),counter=args.minimum_counter)
    bundle=encode_segments(data);hash=runtime_transport.fnv(data);transfer=hash&255 or 1
    minimum=sum(len(s)*.45+1.8 for s in bundle['segments'])
    print(f'VERIFIED-NOT-SENT: release={candidate.identity.hex()}; payload={digest(candidate.payload).hex()}; counter={candidate.counter}')
    print(f'BLOCKS={len(bundle["segments"])}; minimum={minimum:.1f}s; native update requires separately provisioned bootstrap')
    if not args.send:return 0
    xcrun=shutil.which('xcrun')
    if not xcrun:raise UpdateError('Mac xcrun/CoreBluetooth required')
    with tempfile.TemporaryDirectory(prefix='rabbit-native-send-') as temporary:
        directory=Path(temporary);source=directory/'sender.m';exe=directory/'sender';frames=directory/'frames.json'
        source.write_text(sender_source());frames.write_text(json.dumps(bundle))
        environment=os.environ.copy()
        for name in ('CPATH','C_INCLUDE_PATH','CPLUS_INCLUDE_PATH','SDKROOT'):environment.pop(name,None)
        legacy=ROOT.parent/'x86-64-uefi-ble-program-loader-v0'
        subprocess.run([xcrun,'--sdk','macosx','clang','-fobjc-arc',str(source),'-o',str(exe),'-framework','Foundation',
                        '-framework','CoreBluetooth','-Xlinker','-sectcreate','-Xlinker','__TEXT','-Xlinker','__info_plist',
                        '-Xlinker',str(legacy/'RabbitColorCommand-Info.plist')],env=environment,check=True)
        try:return subprocess.run([str(exe),f'{transfer:02X}',f'{hash:08X}',str(frames)],timeout=minimum*3+120).returncode
        except subprocess.TimeoutExpired:print('TIMEOUT: no exact final receipt; delivery unknown');return 4
        except KeyboardInterrupt:return 130
if __name__=='__main__': raise SystemExit(main())
