#!/usr/bin/env python3
"""Yukabox secondary ATT asset channel host/COFF gates; no physical radio."""
import hashlib,json,os,subprocess
from pathlib import Path
from verify_port import CC
ROOT=Path(__file__).resolve().parent
EXP=ROOT.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
    fixtures=ROOT/'runs/firmware-chunks';base=json.loads((fixtures/'report.json').read_text())
    if base['status']!='SIGNED-RAM-CHUNKS-HOST-SANITIZERS-COFF-PASS':raise ValueError('RAM core gate required')
    for name,expected in base['source_sha256'].items():
        if sha((EXP.parent/name).read_bytes())!=expected:raise ValueError('RAM gate source changed')
    if sha((EXP/'x86-64-uefi-runtime-supervisor-v1/sha256.c').read_bytes())!=base['sha256_source']:raise ValueError('SHA implementation changed')
    for path,expected in base['crypto_provenance']['files'].items():
        if sha((fixtures/Path(path).name).read_bytes())!=expected:raise ValueError('crypto provenance changed')
    out=ROOT/'runs/firmware-channel';out.mkdir(parents=True,exist_ok=True)
    inc=['-I'+str(ROOT),'-I'+str(fixtures),'-I'+str(EXP/'x86-64-uefi-runtime-supervisor-v1')]
    names=['firmware_channel.c','firmware_gatt.c','firmware_chunks.c','firmware_channel_test.c']
    sources=[ROOT/n for n in names]+[EXP/'x86-64-uefi-runtime-supervisor-v1/sha256.c',fixtures/'monocypher.c',fixtures/'monocypher-ed25519.c']
    log=''
    for handle_base in (11,13):
        definitions=['-DQCA_FC_BASE='+str(handle_base)]
        exe=out/('test-'+str(handle_base))
        subprocess.run(['gcc','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',*definitions,*inc,*map(str,sources),'-o',str(exe)],check=True)
        for dataset in base['datasets']:
            result=subprocess.run([str(exe),str(fixtures/dataset['name'])],capture_output=True,text=True,check=True,env={**os.environ,'UBSAN_OPTIONS':'halt_on_error=1'})
            log+='handle_base='+str(handle_base)+' '+result.stdout+result.stderr
        for name in ('firmware_channel.c','firmware_gatt.c'):
            subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror',*definitions,*inc,'-c',str(ROOT/name),'-o',str(out/(name+'.'+str(handle_base)+'.obj'))],check=True)
    (out/'host.log').write_text(log)
    report={'status':'SIGNED-RAM-CHUNK-ATT-CHANNEL-HOST-COFF-PASS','build_host':'yukabox','source_sha256':{str((ROOT/n).relative_to(EXP.parent)):sha((ROOT/n).read_bytes()) for n in (*names,'firmware_channel.h','verify_firmware_channel.py')},'ram_gate_sha256':sha((fixtures/'report.json').read_bytes()),'host_log_sha256':sha((out/'host.log').read_bytes()),'datasets':base['datasets'],'handle_bases':[11,13],'legacy_handles_delegated':True,'native_driver_integrated':False,'actual_uefi_att_execution':False,'physical_bluetooth_transfer':False,'physical_bmi_compatibility':False,'firmware_upload_performed':False,'wifi_association':False}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status']);print(log,end='')
if __name__=='__main__':main()
