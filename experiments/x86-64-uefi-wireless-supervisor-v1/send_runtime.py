#!/usr/bin/env python3
"""Mac-only RPv3 native release sender. Never signs generated/LLM code."""
import argparse
import fcntl
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
from send_progress import Progress, run_logged, resumable_source
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
    return resumable_source(source)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('release',type=Path)
    for name in ('owner-public','world-package'): parser.add_argument('--'+name,type=Path,required=True)
    for name in ('target-sha256','base-runtime-sha256'): parser.add_argument('--'+name,required=True)
    parser.add_argument('--minimum-counter',type=int,required=True)
    parser.add_argument('--send',action='store_true',help='explicitly advertise reviewed signed native release')
    parser.add_argument('--progress',type=Path,help='local journal; default runs/transfer-RELEASE_SHA256.json')
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--resume',action='store_true',help='probe saved checkpoint; ONLY same Dell boot/world/base')
    mode.add_argument('--restart-after-reboot',action='store_true',help='discard local progress after an explicitly confirmed Dell reboot')
    parser.add_argument('--frame-ms',type=int,default=450,help='advertisement duration, 450..2000 ms')
    parser.add_argument('--max-block-attempts',type=int,default=8,help='1..100 attempts, then stop with saved progress')
    args=parser.parse_args()
    if not 450<=args.frame_ms<=2000 or not 1<=args.max_block_attempts<=100:
        parser.error('frame-ms must be 450..2000; max-block-attempts must be 1..100')
    if args.release.stat().st_size>MAX_BYTES: raise UpdateError('release too large')
    if args.world_package.stat().st_size>65535: raise UpdateError('world too large')
    data=args.release.read_bytes()
    owner=args.owner_public.read_bytes()
    if args.send and owner==TEST_OWNER:raise UpdateError('public QEMU fixture releases must never be advertised to physical devices')
    candidate=verify(data,target=bytes.fromhex(args.target_sha256),owner=owner,
                     base_runtime=bytes.fromhex(args.base_runtime_sha256),world=args.world_package.read_bytes(),counter=args.minimum_counter)
    bundle=encode_segments(data);hash=runtime_transport.fnv(data);transfer=hash&255 or 1
    minimum=sum(len(s)*args.frame_ms/1000+1.8 for s in bundle['segments'])
    print(f'VERIFIED-NOT-SENT: release={candidate.identity.hex()}; payload={digest(candidate.payload).hex()}; counter={candidate.counter}')
    print(f'BLOCKS={len(bundle["segments"])}; minimum={minimum:.1f}s; native update requires separately provisioned bootstrap')
    if not args.send:return 0
    xcrun=shutil.which('xcrun')
    if not xcrun:raise UpdateError('Mac xcrun/CoreBluetooth required')
    identity={'release_sha256':digest(data).hex(),'owner_sha256':digest(owner).hex(),
              'world_sha256':digest(args.world_package.read_bytes()).hex(),
              'target_sha256':args.target_sha256.lower(),'base_sha256':args.base_runtime_sha256.lower(),
              'counter':candidate.counter,'transport':'RPv3-32-chunk-checkpoints', 'hashes':bundle['hashes']}
    path=args.progress or ROOT/'runs'/('transfer-'+digest(data).hex()+'.json')
    if path.suffix!='.json' or path.resolve() in {args.release.resolve(),args.owner_public.resolve(),args.world_package.resolve()}:
        raise UpdateError('progress must be a separate .json file, not a release/key/world')
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.with_suffix('.lock').open('a') as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:raise UpdateError('another sender owns this progress journal')
        journal=Progress(path,identity,bundle['hashes'],args.resume,args.restart_after_reboot)
        if journal.complete:
            print('ALREADY RECEIPTED: local cached result, NOT a fresh Dell observation. No packet sent.');return 0
        journal.configure(bundle,args.frame_ms,args.max_block_attempts)
        return transmit(xcrun,bundle,transfer,hash,journal,minimum*(args.max_block_attempts+1)+120)

def transmit(xcrun,bundle,transfer,hash,journal,timeout):
    with tempfile.TemporaryDirectory(prefix='rabbit-native-send-') as temporary:
        directory=Path(temporary);source=directory/'sender.m';exe=directory/'sender';frames=directory/'frames.json'
        source.write_text(sender_source());frames.write_text(json.dumps(bundle))
        environment=os.environ.copy()
        for name in ('CPATH','C_INCLUDE_PATH','CPLUS_INCLUDE_PATH','SDKROOT'):environment.pop(name,None)
        legacy=ROOT.parent/'x86-64-uefi-ble-program-loader-v0'
        subprocess.run([xcrun,'--sdk','macosx','clang','-fobjc-arc',str(source),'-o',str(exe),'-framework','Foundation',
                        '-framework','CoreBluetooth','-Xlinker','-sectcreate','-Xlinker','__TEXT','-Xlinker','__info_plist',
                        '-Xlinker',str(legacy/'RabbitColorCommand-Info.plist')],env=environment,check=True)
        return run_logged([str(exe),f'{transfer:02X}',f'{hash:08X}',str(frames)],journal,timeout)
if __name__=='__main__':
    try: raise SystemExit(main())
    except (ValueError,OSError,subprocess.CalledProcessError) as error:
        print('FAIL: '+str(error),file=sys.stderr); raise SystemExit(2)
