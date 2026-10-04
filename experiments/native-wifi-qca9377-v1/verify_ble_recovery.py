"""Yukabox failure reproduction + sanitized link + separate actual UEFI profile."""
import argparse
import subprocess
from pathlib import Path
import ble_recovery_build as build
import reboot_recovery as recovery
flow = recovery.flow


def fixture(source):
    # Inject the exact observed orphan + unknown-handle disconnect before the
    # normal connection. Baseline stays silent; candidate issues advertise-on.
    source = build.one(source, ' if(conn_event){', '''
 static unsigned lost_event;
 if(conn_event&&resets>=3&&*n){
  if(!lost_event){uint8_t e[5]={0,0,0x48,0,1};copy(p,e,5);*n=5;lost_event=1;return 0;}
  if(lost_event==1){uint8_t e[6]={5,4,0,3,0,0x13};copy(p,e,6);*n=6;lost_event=2;conn_event=0;advertising=0;return 0;}
 }
 if(conn_event){''')
    return source


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    p.add_argument('--owner-public',type=Path,required=True);a=p.parse_args()
    out=a.output;out.mkdir(parents=True,exist_ok=False)
    fixed=out/'fixed-link.c';fixed.write_text(build.link_source())
    logs=''
    for name,source,defs in [('baseline',build.actors.LINK/'hci_link.c',['-DBASELINE']),('fixed',fixed,[])]:
        exe=out/name
        subprocess.run(['cc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all',
            '-I'+str(build.actors.LINK),'-I'+str(build.actors.NATIVE),str(build.ROOT/'test_ble_recovery.c'),str(source),*defs,'-o',str(exe)],check=True)
        subprocess.run([str(exe)],check=True);logs+=name+': PASS\n'
    (out/'host.log').write_text(logs)
    _,_,crypto=recovery.engine.prepare(out,a.owner_public.read_bytes())
    payload=build.compile_driver(out,crypto)
    if build.compile_driver(out,crypto)!=payload:raise ValueError('native builds differ')
    (out/'payload.efi').write_bytes(payload)
    gate=flow.actors_module('actors_gate')
    gates=[gate.qemu_gate(out,payload),gate.qemu_gate(out,payload,True,test_transform=fixture)]
    names=('ble_recovery_build.py','test_ble_recovery.c','verify_ble_recovery.py')
    report={'status':'BLE-UNTRACKED-DISCONNECT-RECOVERY-GATES-PASS','build_host':'yukabox',
        'payload_sha256':flow.sha(payload),'source_sha256':{n:flow.sha((build.ROOT/n).read_bytes()) for n in names},
        'host_log_sha256':flow.sha((out/'host.log').read_bytes()),'gates':gates,
        'baseline_lost_advertising_reproduced':True,'fixed_restarts_advertising':True,
        'known_live_foreign_handle_preserved':True,'two_native_builds':True,
        'bootstrap_changed':False,'physical_transfer':False,'physical_recovery':False,
        'event_reassembly_added':False,'root_cause_of_missing_connection_header_known':False}
    flow.save(out/'report.json',report);print(report['status'],report['payload_sha256'])


if __name__=='__main__':main()
