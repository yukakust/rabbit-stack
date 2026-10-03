#!/usr/bin/env python3
"""Offline Cocoa packet/checkpoint checks. Never starts a Bluetooth manager."""
import hashlib,json,subprocess
from pathlib import Path
from send_firmware_chunk import validate
ROOT=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
    subprocess.run(['python3',str(ROOT/'send_firmware_chunk.py')],check=True)
    fixture=ROOT/'runs/mac-control/firmware-fixture';packet=fixture/'chunk-0.bin';data=packet.read_bytes();public=(fixture/'policy.bin').read_bytes()[:32]
    validate(data,public)
    for offset in (8,104,128,140,160,224):
        bad=bytearray(data);bad[offset]^=1
        try:validate(bytes(bad),public)
        except Exception:pass
        else:raise AssertionError('tampered signed packet accepted')
    exe=ROOT/'runs/mac-control/firmware-sender';checkpoint=fixture/'offline-checkpoint.json';checkpoint.unlink(missing_ok=True)
    def run(expected):
        result=subprocess.run([str(exe),str(packet),str(checkpoint),'--preflight'],capture_output=True,text=True)
        assert result.returncode==expected,(result.stdout,result.stderr)
        return result.stdout+result.stderr
    log=run(0);good={'packet_sha256':sha(data),'floor':200,'attempted':1};checkpoint.write_text(json.dumps(good));log+=run(0);assert json.loads(checkpoint.read_text())==good
    bad_cases=[{**good,'floor':-1},{**good,'floor':len(data)+1},{**good,'floor':2.5},{**good,'attempted':2},{**good,'attempted':0.5},{**good,'packet_sha256':'0'*64},{**good,'extra':1},[],None]
    for bad in bad_cases:
        checkpoint.write_text(json.dumps(bad));before=checkpoint.read_bytes();log+=run(2);assert checkpoint.read_bytes()==before
    checkpoint.write_text('invalid JSON');log+=run(2)
    checkpoint.write_text(json.dumps(good));log+=run(0)
    out=ROOT/'evidence/2026-10-04/firmware-sender';out.mkdir(parents=True,exist_ok=True);(out/'mac-offline.log').write_text(log)
    names=('mac_firmware_sender.m','firmware_sender_core.c','firmware_sender_core.h','send_firmware_chunk.py','verify_mac_firmware_sender.py')
    report={'status':'MAC-COCOA-COMPILE-OFFLINE-PACKET-CHECKPOINT-PASS','source_sha256':{str((ROOT/n).relative_to(ROOT.parent.parent)):sha((ROOT/n).read_bytes()) for n in names},'build_host':'Mac','fixture_packet_sha256':sha(data),'host_log_sha256':sha((out/'mac-offline.log').read_bytes()),'private_key_accessed':False,'bluetooth_manager_started':False,'cocoa_radio_callbacks_verified':False,'physical_transfer_verified':False}
    (out/'mac-offline-report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
if __name__=='__main__':main()
