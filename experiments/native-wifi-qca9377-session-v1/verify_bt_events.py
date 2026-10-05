#!/usr/bin/env python3
"""Actual derived BLE link + successful USB-event byte streams, host only."""
import json,sys,subprocess
from pathlib import Path
from verify_htc import ROOT,CC,sha
V1=ROOT.parent/'native-wifi-qca9377-v1'
sys.path.insert(0,str(V1))
import ble_recovery_build
def main():
 out=ROOT/'runs/bt-events';out.mkdir(parents=True,exist_ok=True)
 link=out/'derived-link.c';link.write_text(ble_recovery_build.link_source())
 inputs={name:sha((ROOT/name).read_bytes()) for name in ('bt_event_stream.c','bt_event_stream.h','bt_event_stream_test.c','verify_bt_events.py','verify_htc.py')}
 subprocess.run([str(CC),'-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all','-I'+str(ROOT),'-I'+str(ble_recovery_build.actors.LINK),str(ROOT/'bt_event_stream.c'),str(ROOT/'bt_event_stream_test.c'),str(link),'-o',str(out/'events-test')],check=True)
 r=subprocess.run([str(out/'events-test')],capture_output=True,text=True,timeout=30);(out/'host.log').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr
 subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-I'+str(ROOT),'-c',str(ROOT/'bt_event_stream.c'),'-o',str(out/'bt_event_stream.obj')],check=True)
 assert inputs=={name:sha((ROOT/name).read_bytes()) for name in inputs}
 report={'status':'BT-EVENT-STREAM-ACTUAL-LINK-HOST-COFF-PASS','build_host':'yukabox','source_sha256':inputs,'derived_link_sha256':sha(link.read_bytes()),'hci_link_h_sha256':sha((ble_recovery_build.actors.LINK/'hci_link.h').read_bytes()),'host_log_sha256':sha((out/'host.log').read_bytes()),'split_connection_event_16_plus5_verified':True,'coalesced_credit_events7_plus7_verified':True,'physical_verified':False,'native_integrated':False,'root_cause_of_physical_disconnect_proven':False,'wifi_connected':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(r.stdout.strip());print(report['status'])
if __name__=='__main__':main()
