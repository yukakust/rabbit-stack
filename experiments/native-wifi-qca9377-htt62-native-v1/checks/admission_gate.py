"""Pure public technical gate. Never physical admission/state/key/Bluetooth."""
import json,hashlib,struct
from pathlib import Path
REPO=Path(__file__).resolve().parents[3];ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def check(out=None,baseline=None):
 out=(out or ROOT/'runs/checked-candidate').resolve();r=json.loads((out/'report.json').read_text());npath=ROOT/'runs/native-host/report.json';n=json.loads(npath.read_text())
 assert r['status']=='HTT62-REPEATED-EFI-QEMU-WORLD19-DIAGNOSTIC-PASS' and r['native_counter']==62
 assert r['build_host']=='yukabox' and r['physical_verified'] is False and r['signing_admitted'] is False
 assert r['request_is_rf'] is False and r['duplicate_HTT_CONNECT'] is False and r['htt_dataplane_ready'] is False
 assert r['world_package_sha256']=='89ffda340552cf33a4c732597388f4fea358d47b0850f7720bdce51a2b3968b7'
 for name,h in r['source_sha256'].items():
  p=Path(name);assert not p.is_absolute() and '..' not in p.parts and name.startswith('experiments/');assert sha(REPO/p)==h,name
 for name,h in r['generated_compiler_sources_sha256'].items():assert sha(out/name)==h,name
 assert sha(out/'reproduction.json')==r['reproduction_sha256'];rep=json.loads((out/'reproduction.json').read_text());assert rep['inputs']==r['source_sha256'] and rep['payload_sha256']==r['payload_sha256']
 assert n['status']=='HTT62-ACTUAL-PRODUCTION-AUTHENTICATED-IE6-VERSION-RAW-ASAN-COFF-PASS' and n['scenarios']==24
 assert sha(npath)==r['native_report_sha256'] and sha(npath.with_name('host.log'))==n['host_log_sha256']
 for name,h in n['source_sha256'].items():assert sha(REPO/name)==h,name
 for name,h in n['compiled_fixture_sources_sha256'].items():assert sha(npath.parent/name)==h,name
 blob=(out/'payload.efi').read_bytes();pe=struct.unpack_from('<I',blob,60)[0];mapped=struct.unpack_from('<I',blob,pe+80)[0]
 assert len(blob)==r['payload_bytes']<=262144 and mapped==r['mapped_bytes']<=4194304 and sha(out/'payload.efi')==r['payload_sha256']
 assert r['receiver_policy']['generation']==62 and r['receiver_policy']['owner']=='622b248c42829ad066e5ae428ea30e955c750e4c3f221553bb346254e82545ac' and r['receiver_policy']['target']=='363d751288df7b47295f9c7a5250c3b41db24efd1a43a4bd348f00744c6bc7e9'
 assert r['host_checks']['roof_cat_timing'] is True and r['host_checks']['host_ticks']==120 and r['host_checks']['adversarial_camera_frames']==16 and r['host_checks']['sanitizers'] is True
 assert sha(out/'world19-source.json')==r['world_source_sha256']
 assert sha(out/'htt-version62.efi')==r['payload_sha256'] and rep['status']=='HTT62-THREE-BUILDS-IDENTICAL'
 assert len(r['gates'])==2
 for g in r['gates']:
  assert g['payload_sha256']==r['payload_sha256'] and g['physical_verified'] is False
  path=out/('actors-empty-boot-qemu' if g['empty_boot'] else 'actors-qemu');assert sha(path/'observed.log')==g['observed_log_sha256'] and json.loads((path/'report.json').read_text())==g
 baseline=baseline or REPO/'experiments/native-wifi-qca9377-fullboot60-native-v1/runs/checked-candidate';b=json.loads((baseline/'report.json').read_text())
 for name,h in b['source_sha256'].items():assert sha(REPO/name)==h,name
 for name in ('driver.c','usb_port.c','ble_recovery_link.c','bt_event_stream.c','firmware_channel.c','firmware_port.c','firmware_chunks.c'):assert (out/name).read_bytes()==(baseline/name).read_bytes(),name
 return {'status':'HTT62-PUBLIC-SOURCE-CLOSED-TECHNICAL-GATE-PASS','report_sha256':sha(out/'report.json'),'payload_sha256':r['payload_sha256'],'native_report_sha256':sha(npath),'gate_source_sha256':sha(Path(__file__)),'source_count':len(r['source_sha256']),'generated_count':len(r['generated_compiler_sources_sha256']),'physical_admission':False,'actual61_raw_release_review_required':True,'new_counter_reserved':False,'device_operations':0,'key_accesses':0,'request_is_rf':False}
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--baseline',type=Path);a=ap.parse_args();print(json.dumps(check(baseline=a.baseline),indent=2))
