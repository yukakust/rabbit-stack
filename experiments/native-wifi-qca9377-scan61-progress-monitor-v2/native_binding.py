"""Independent host/native UUID join. Public files only; no manager/key/state writes."""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent.parent
sys.path.insert(0,str(REPO/'experiments/native-wifi-qca9377-scan61-root-route-v1'))
import gate
compact=lambda p:''.join(Path(p).read_text().split())
def check(monitor):
 r=gate.flow.read_json(gate.CHECKED/'report.json');gate.need(gate.sha(gate.CHECKED/'report.json')==gate.REPORT,'exact61 candidate')
 for name in ('scan_gatt.c','boot_gatt.c'):gate.need(gate.sha(gate.CHECKED/name)==r['generated_compiler_sources_sha256'][name],'actual generated GATT source')
 native=compact(gate.CHECKED/'scan_gatt.c');boot=compact(gate.CHECKED/'boot_gatt.c')
 reader=REPO/'experiments/native-wifi-qca9377-scan61-observer-v1/read_scan.m';gate.need(gate.sha(reader)=='04898d22209d2ffaf4ff358a3a68de38c3e4c3d35edeff177f7f1242294f5e34','frozen full reader')
 gate.need('uuid(out+6,start==32?0x2a:0x2c);' in native and 'uuid(out+7,decl==33?0x2b:0x80+(decl-36)/2);' in native and 'elseif(h==34){qca_scan_status(value);bytes=416;}' in native,'native QSCN service2a/value2b at handle34')
 gate.need('uuid(r+7,0x23);' in boot and 'elseif(h==22){qca_boot_status(value);length=160;}' in boot,'native QWBT service22/value23')
 gate.need('idsaddObject:[CBUUIDUUIDWithString:uid(0x2b)]];' in compact(reader),'full reader exact native status UUID')
 gate.need('services[2]={0x22,0x2a},values[2]={0x23,0x2b},sizes[2]={160,416};' in ''.join(monitor.split()),'host monitor ABI differs from native status/value')
 return {'status':'HOST-MONITOR-NATIVE61-UUID-ABI-JOIN-PASS','candidate_report_sha256':gate.REPORT,'native_status_service_UUID':'2a','native_status_value_UUID':'2b','native_status_ATT_handle':34,'raw_export_service_UUID':'2c','boot_service_UUID':'22','boot_value_UUID':'23','physical_read':False,'native_source_changed':False}
if __name__=='__main__':
 result=check((ROOT/'collector.m').read_text())
 try:check((REPO/'experiments/native-wifi-qca9377-scan61-progress-monitor-v1/collector.m').read_text())
 except ValueError:result['incorrect_v1_UUID_rejected']=True
 else:raise AssertionError('wrong v1 ABI accepted')
 result['source_sha256']={str(p.relative_to(REPO)):gate.sha(p) for p in (Path(__file__),ROOT/'collector.m',gate.CHECKED/'scan_gatt.c',gate.CHECKED/'boot_gatt.c')}
 gate.flow.save(ROOT/'evidence/native-binding.json',result);print(json.dumps(result,indent=2))
