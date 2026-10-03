#!/usr/bin/env python3
"""Compile/check Mac sender without radio by default. --send is explicit."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile
import uuid
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'ble-connected-file-transfer-v1/mac_file_sender.m'
def validate(bundle):
    if type(bundle) is not dict or bundle.get('schema_version')!=1:raise ValueError('wrong bundle schema')
    kind=bundle.get('kind',1);counter=bundle.get('counter')
    if type(kind) is not int or kind not in (1,2) or type(counter) is not int or not 1<=counter<=0xffffffff:raise ValueError('invalid kind/counter')
    data=base64.b64decode(bundle['stream_base64'],validate=True);nonce=base64.b64decode(bundle['session_base64'],validate=True)
    if len(nonce)!=8 or not 32<len(data)<=32+(65535 if kind==1 else 262144) or hashlib.sha256(data[32:]).digest()!=data[:32]:raise ValueError('bad bounded stream/session/SHA256')
    # One receipt identity: caller cannot label bytes with another counter/kind.
    from prepare_file import bundle as prepare
    prepare(data[32:],kind,counter,nonce)
    return bundle
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('bundle',nargs='?',type=Path)
    mode=p.add_mutually_exclusive_group()
    mode.add_argument('--send',action='store_true')
    mode.add_argument('--query-only',action='store_true',help='read current file status without BEGIN/DATA/COMMIT/ABORT')
    mode.add_argument('--abort-only',action='store_true',help='abort only the exact saved staging session after read-only check; no DATA/COMMIT')
    p.add_argument('--peripheral',help='known macOS peripheral UUID; query-only cached connection, no scan')
    p.add_argument('--chunk-bytes',type=int,help='bounded DATA payload bytes per write, 1..240; default240')
    p.add_argument('--data-delay-ms',type=int,help='staging-only diagnostic pause between DATA writes, 1..100ms')
    p.add_argument('--stage-only-bytes',type=int,help='stop after a receiver-confirmed prefix, WITHOUT COMMIT')
    a=p.parse_args()
    if a.data_delay_ms is not None and (not a.send or a.stage_only_bytes is None or not 1<=a.data_delay_ms<=100):p.error('--data-delay-ms requires --send, --stage-only-bytes and 1..100ms')
    if a.chunk_bytes is not None and (not a.send or not 1<=a.chunk_bytes<=240):p.error('--chunk-bytes requires --send and 1..240 bytes')
    if a.peripheral:
        if not a.query_only:p.error('--peripheral requires --query-only')
        try:a.peripheral=str(uuid.UUID(a.peripheral))
        except ValueError:p.error('invalid peripheral UUID')
    if (a.send or a.query_only or a.abort_only) and a.bundle is None:p.error('radio modes need a saved session bundle')
    if a.stage_only_bytes is not None and not a.send:p.error('--stage-only-bytes requires --send')
    if a.bundle:
        if a.bundle.stat().st_size>400000:raise ValueError('bundle too large')
        saved=validate(json.loads(a.bundle.read_text()))
        if a.stage_only_bytes is not None and not 0<a.stage_only_bytes<len(base64.b64decode(saved['stream_base64'])):
            p.error('--stage-only-bytes must be positive and smaller than the stream')
    if platform.system()!='Darwin':raise RuntimeError('Mac compilation requires macOS/Apple SDK; not verified on Linux')
    xcrun=shutil.which('xcrun')
    if not xcrun:raise RuntimeError('Apple command line tools required')
    env=os.environ.copy()
    for name in ('CPATH','C_INCLUDE_PATH','CPLUS_INCLUDE_PATH','SDKROOT'):env.pop(name,None)
    with tempfile.TemporaryDirectory(prefix='rabbit-connected-sender-') as temporary:
        executable=Path(temporary)/'rabbit-file'
        subprocess.run([xcrun,'--sdk','macosx','clang','-fobjc-arc',
            '-Werror=incompatible-property-type','-Werror=objc-property-synthesis',str(SOURCE),'-o',str(executable),
            '-framework','Foundation','-framework','CoreBluetooth','-Xlinker','-sectcreate',
            '-Xlinker','__TEXT','-Xlinker','__info_plist','-Xlinker',str(ROOT/'FileSender-Info.plist')],env=env,check=True,timeout=60)
        print('MAC SENDER COMPILED; SOURCE SHA256='+hashlib.sha256(SOURCE.read_bytes()).hexdigest(),flush=True)
        print('STATUS VALIDATOR SHA256='+hashlib.sha256((SOURCE.parent/'sender_status.h').read_bytes()).hexdigest(),flush=True)
        if not a.send and not a.query_only and not a.abort_only:print('NOT SENT: compile-only, no Bluetooth manager started');return 0
        command=[str(executable),str(a.bundle.resolve())]
        if a.stage_only_bytes is not None:command.append(str(a.stage_only_bytes))
        if a.query_only:command.append('--query-only')
        if a.peripheral:command.extend(['--peripheral',a.peripheral])
        if a.abort_only:command.append('--abort-only')
        if a.chunk_bytes is not None:command.extend(['--chunk-bytes',str(a.chunk_bytes)])
        if a.data_delay_ms is not None:command.extend(['--data-delay-ms',str(a.data_delay_ms)])
        try:return subprocess.run(command,env=env,timeout=310).returncode
        except KeyboardInterrupt:print('STOPPED: rerun the SAME saved session; outcome not assumed');return 130
if __name__=='__main__':raise SystemExit(main())
