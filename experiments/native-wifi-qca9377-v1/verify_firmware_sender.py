#!/usr/bin/env python3
"""Yukabox portable sender/receiver interop gates; Cocoa/radio are separate."""
import hashlib,json,os,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
EXP=ROOT.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
    fixtures=ROOT/'runs/firmware-chunks';base=json.loads((fixtures/'report.json').read_text())
    for name,expected in base['source_sha256'].items():
        if sha((EXP.parent/name).read_bytes())!=expected:raise ValueError('RAM gate source changed')
    for path,expected in base['crypto_provenance']['files'].items():
        if sha((fixtures/Path(path).name).read_bytes())!=expected:raise ValueError('crypto provenance changed')
    channel=ROOT/'runs/firmware-channel/report.json';report=json.loads(channel.read_text())
    for name,expected in report['source_sha256'].items():
        if sha((EXP.parent/name).read_bytes())!=expected:raise ValueError('channel gate source changed')
    out=ROOT/'runs/firmware-sender';out.mkdir(parents=True,exist_ok=True)
    inc=['-I'+str(ROOT),'-I'+str(fixtures),'-I'+str(EXP/'x86-64-uefi-runtime-supervisor-v1')]
    names=('firmware_sender_core.c','firmware_sender_test.c','firmware_channel.c','firmware_chunks.c')
    sources=[ROOT/n for n in names]+[EXP/'x86-64-uefi-runtime-supervisor-v1/sha256.c',fixtures/'monocypher.c',fixtures/'monocypher-ed25519.c']
    exe=out/'test';subprocess.run(['gcc','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',*inc,*map(str,sources),'-o',str(exe)],check=True)
    log=''
    for dataset in base['datasets']:
        directory=fixtures/dataset['name'];policy=(directory/'policy.bin').read_bytes()
        if len(policy)!=120 or policy[64:96].hex()!=dataset['sha256'] or int.from_bytes(policy[96:100],'little')!=dataset['bytes']:
            raise ValueError('fixture policy differs from reviewed dataset')
        reconstructed=b''.join((directory/f'chunk-{i}.bin').read_bytes()[224:] for i in range(dataset['chunks']))
        if len(reconstructed)!=dataset['bytes'] or sha(reconstructed)!=dataset['sha256']:raise ValueError('fixture bytes differ from reviewed dataset')
        result=subprocess.run([str(exe),str(fixtures/dataset['name'])],capture_output=True,text=True,check=True,env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1'})
        log+=result.stdout+result.stderr
    (out/'host.log').write_text(log)
    report={'status':'FIRMWARE-SENDER-RECEIVER-RESUME-HOST-SANITIZERS-PASS','source_sha256':{str((ROOT/n).relative_to(EXP.parent)):sha((ROOT/n).read_bytes()) for n in (*names,'firmware_sender_core.h','firmware_channel.h','firmware_chunks.h','verify_firmware_sender.py')},'build_host':'yukabox','host_log_sha256':sha((out/'host.log').read_bytes()),'channel_gate_sha256':sha(channel.read_bytes()),'ram_gate_sha256':sha((fixtures/'report.json').read_bytes()),'datasets':base['datasets'],'cocoa_callbacks_verified':False,'physical_transfer_verified':False,'firmware_upload_performed':False,'wifi_association':False}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status']);print(log,end='')
if __name__=='__main__':main()
