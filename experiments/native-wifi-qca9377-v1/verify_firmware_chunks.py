#!/usr/bin/env python3
"""Yukabox RAM assembly gates; never accesses an owner key or physical device."""
import argparse,hashlib,json,os,shutil,struct,subprocess
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
from firmware_chunk_format import packets,MAX
from verify_port import CC
ROOT=Path(__file__).resolve().parent
EXP=ROOT.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--firmware',type=Path,required=True);a=parser.parse_args()
    out=ROOT/'runs/firmware-chunks';out.mkdir(parents=True,exist_ok=True)
    provenance=json.loads((EXP/'x86-64-uefi-god-runtime-v1/crypto-provenance.json').read_text())
    cached=ROOT/'runs/bmi-profile'
    for path,expected in provenance['files'].items():
        source=cached/Path(path).name
        if sha(source.read_bytes())!=expected:raise ValueError('pinned crypto mismatch: '+path)
        shutil.copyfile(source,out/source.name)
    inc=['-I'+str(ROOT),'-I'+str(EXP/'x86-64-uefi-runtime-supervisor-v1'),'-I'+str(out)]
    sources=[ROOT/'firmware_chunks.c',ROOT/'firmware_chunks_test.c',EXP/'x86-64-uefi-runtime-supervisor-v1/sha256.c',out/'monocypher.c',out/'monocypher-ed25519.c']
    exe=out/'test'
    subprocess.run(['gcc','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',*inc,*map(str,sources),'-o',str(exe)],check=True)
    subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror',*inc,'-c',str(ROOT/'firmware_chunks.c'),'-o',str(out/'firmware_chunks.obj')],check=True)
    firmware=a.firmware.read_bytes()
    materials=json.loads((ROOT/'evidence/2026-10-04/materials.json').read_text())
    expected=materials['files']['firmware/ath10k/QCA9377/hw1.0/firmware-6.bin']
    if len(firmware)!=expected['bytes'] or sha(firmware)!=expected['sha256']:raise ValueError('reviewed firmware bytes required')
    private=Ed25519PrivateKey.from_private_bytes(bytes([97])*32)
    other=Ed25519PrivateKey.from_private_bytes(bytes([98])*32)
    public=private.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
    target=hashlib.sha256(b'RAM HOST FIXTURE ONLY; NOT PHYSICAL QCA IDENTITY').digest()
    log='';datasets=[]
    for name,data in [(f'length-{n}',bytes((i*17+3)%256 for i in range(n))) for n in (1,65535,65536,65537,MAX)]+[('reviewed-container',firmware)]:
        directory=out/name;directory.mkdir(exist_ok=True)
        params=dict(target=target,generation=15,target_type=7,target_version=0x05020001,kind=1)
        parts=packets(data,private,**params)
        (directory/'policy.bin').write_bytes(public+target+hashlib.sha256(data).digest()+struct.pack('<IIIIQ',len(data),7,0x05020001,1,15))
        for i,packet in enumerate(parts):(directory/f'chunk-{i}.bin').write_bytes(packet)
        (directory/'wrong-key.bin').write_bytes(packets(data,other,**params)[0])
        for field,value,label in [('generation',16,'generation'),('target_type',8,'type'),('target_version',0x05020002,'version'),('kind',2,'kind'),('target',bytes([42])*32,'target')]:
            altered={**params,field:value};(directory/f'wrong-{label}.bin').write_bytes(packets(data,private,**altered)[0])
        result=subprocess.run([str(exe),str(directory)],capture_output=True,text=True,check=True,env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1'})
        log+=result.stdout+result.stderr
        datasets.append({'name':name,'bytes':len(data),'chunks':len(parts),'sha256':sha(data),'largest_packet':max(map(len,parts))})
    (out/'host.log').write_text(log)
    names=('firmware_chunks.c','firmware_chunks.h','firmware_chunks_test.c','firmware_chunk_format.py','verify_firmware_chunks.py')
    report={'status':'SIGNED-RAM-CHUNKS-HOST-SANITIZERS-COFF-PASS','build_host':'yukabox','source_sha256':{str((ROOT/n).relative_to(EXP.parent)):sha((ROOT/n).read_bytes()) for n in names},'sha256_source':sha((EXP/'x86-64-uefi-runtime-supervisor-v1/sha256.c').read_bytes()),'crypto_provenance':provenance,'host_log_sha256':sha((out/'host.log').read_bytes()),'datasets':datasets,'fixture_key_only':True,'physical_bmi_compatibility':False,'owner_signing_performed':False,'bluetooth_receiver_integrated':False,'firmware_upload_performed':False,'wifi_association':False}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status']);print(log,end='')
if __name__=='__main__':main()
