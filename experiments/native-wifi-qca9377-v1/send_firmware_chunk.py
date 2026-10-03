#!/usr/bin/env python3
"""Compile-only by default; send one previously owner-signed RAM chunk on Mac."""
import argparse,hashlib,json,os,platform,struct,subprocess,tempfile
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
import diagnostic_build
ROOT=Path(__file__).resolve().parent
engine=diagnostic_build.actors.engine
flow=engine.flow
def validate(packet,public):
    if not 224<len(packet)<=65760 or len(public)!=32 or packet[:8]!=b'RABFW001' or any(packet[140:160]):
        raise ValueError('bounded signed asset envelope required')
    total,offset,length,chunk,generation,kind_type,version,kind=struct.unpack_from('<IIIIQIII',packet,104)
    if not 0<total<=2097152 or offset>=total or offset%65536 or chunk!=65536 or length!=min(65536,total-offset) or length!=len(packet)-224:
        raise ValueError('invalid bounded chunk layout')
    if not generation or kind not in (1,2) or not 0<kind_type<0xffffffff or not 0<version<0xffffffff or not any(packet[8:40]) or not any(packet[40:72]):
        raise ValueError('exact reviewed policy context required')
    if hashlib.sha256(packet[224:]).digest()!=packet[72:104]:raise ValueError('chunk body hash mismatch')
    Ed25519PublicKey.from_public_bytes(public).verify(packet[160:224],packet[:160])
    return {'packet_sha256':hashlib.sha256(packet).hexdigest(),'asset_sha256':packet[40:72].hex(),'offset':offset,'asset_bytes':total,'generation':generation,'target_type':kind_type,'target_version':version,'kind':kind}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('packet',nargs='?',type=Path)
    modes=p.add_mutually_exclusive_group();modes.add_argument('--send',action='store_true');modes.add_argument('--query-only',action='store_true');modes.add_argument('--preflight',action='store_true')
    p.add_argument('--checkpoint',type=Path)
    p.add_argument('--state',type=Path,default=ROOT.parent/'x86-64-uefi-connected-supervisor-v1/runs/text-world/state.json')
    p.add_argument('--owner-public',type=Path,default=Path.home()/'.rabbit-owner/runtime.pub')
    a=p.parse_args()
    if (a.send or a.query_only or a.preflight) and not a.packet:p.error('saved signed chunk packet required')
    if platform.system()!='Darwin':raise RuntimeError('Mac CoreBluetooth controller requires Apple SDK')
    out=ROOT/'runs/mac-control';out.mkdir(parents=True,exist_ok=True);exe=out/'firmware-sender'
    native=ROOT.parent/'x86-64-uefi-runtime-supervisor-v1';plist=ROOT.parent/'x86-64-uefi-connected-supervisor-v1/FileSender-Info.plist'
    env=os.environ.copy()
    for name in ('CPATH','C_INCLUDE_PATH','CPLUS_INCLUDE_PATH','SDKROOT'):env.pop(name,None)
    subprocess.run(['xcrun','--sdk','macosx','clang','-fobjc-arc','-Wall','-Wextra','-Werror','-I'+str(ROOT),'-I'+str(native),str(ROOT/'mac_firmware_sender.m'),str(ROOT/'firmware_sender_core.c'),str(native/'sha256.c'),'-framework','Foundation','-framework','CoreBluetooth','-Wl,-sectcreate,__TEXT,__info_plist,'+str(plist),'-o',str(exe)],env=env,check=True,timeout=60)
    print('MAC ASSET SENDER COMPILED; no private key or firmware activation',flush=True)
    if not a.send and not a.query_only and not a.preflight:print('NOT SENT: no Bluetooth manager started');return 0
    if a.packet.stat().st_size>65760:raise ValueError('packet exceeds bound')
    if a.preflight:
        packet=a.packet.read_bytes();validate(packet,a.owner_public.read_bytes())
        checkpoint=(a.checkpoint or a.packet.with_suffix(a.packet.suffix+'.checkpoint.json')).resolve()
        if checkpoint==a.packet.resolve():raise ValueError('checkpoint must not overwrite packet')
        return subprocess.run([str(exe),str(a.packet.resolve()),str(checkpoint),'--preflight'],env=env,timeout=10).returncode
    with flow.state_lock(a.state):
        state=flow.read_json(a.state);flow.current(state)
        if state.get('pending') or state.get('native_pending') or state.get('recovery_pending'):raise ValueError('preserve pending world/native session; no competing radio operation')
        gate_path=Path(state['engine']['installed_gate']);gate=engine.gate_check(gate_path)
        if flow.sha(gate_path.read_bytes())!=state['engine']['installed_gate_sha256']:raise ValueError('installed owner gate changed')
        public=a.owner_public.read_bytes()
        if flow.sha(public)!=gate['owner_public_sha256']:raise ValueError('owner identity differs from installed gate')
        packet=a.packet.read_bytes();context=validate(packet,public);print(json.dumps(context,sort_keys=True),flush=True)
        checkpoint=(a.checkpoint or a.packet.with_suffix(a.packet.suffix+'.checkpoint.json')).resolve()
        if checkpoint==a.packet.resolve():raise ValueError('checkpoint must not overwrite immutable packet')
        if not checkpoint.parent.is_dir():raise ValueError('checkpoint parent required')
        with tempfile.TemporaryDirectory(prefix='signed-asset-',dir=out) as temporary:
            immutable=Path(temporary)/'packet.bin';immutable.write_bytes(packet);immutable.chmod(0o400)
            command=[str(exe),str(immutable),str(checkpoint),'--send' if a.send else '--query-only']
            try:return subprocess.run(command,env=env,timeout=250,pass_fds=() if flow.LOCK_FD is None else (flow.LOCK_FD,)).returncode
            except subprocess.TimeoutExpired:
                print('OUTCOME UNCONFIRMED: retain exact packet/checkpoint; query before retry');return 1
if __name__=='__main__':raise SystemExit(main())
