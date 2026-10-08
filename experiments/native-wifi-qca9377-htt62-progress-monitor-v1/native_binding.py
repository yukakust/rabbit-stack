"""Public source/ABI proof only; no manager or native compilation."""
from pathlib import Path
import hashlib, importlib.util, json, re
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def check():
 candidate=REPO/'experiments/native-wifi-qca9377-htt62-native-v1';out=candidate/'runs/checked-candidate'
 spec=importlib.util.spec_from_file_location('_htt62_gate',candidate/'checks/admission_gate.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);g=m.check()
 report=json.loads((out/'report.json').read_text())
 paths=[out/x for x in ('profile_gatt.c','boot_gatt.c','init_probe.c')]
 for p in paths:assert sha(p)==report['generated_compiler_sources_sha256'][p.name]
 compact=lambda p:''.join(p.read_text().split())
 native=compact(paths[0]);boot=compact(paths[1]);host=compact(ROOT/'collector.m')
 assert 'uuid(out+6,start==29?0x2e:0x30);' in native and 'uuid(out+7,decl==30?0x2f:0x80+(decl-33)/2);' in native and 'elseif(h==31){qca_htt_status(value);bytes=320;}' in native
 assert 'uuid(r+7,0x23);' in boot and 'elseif(h==22){qca_boot_status(value);length=160;}' in boot
 assert 'services[2]={0x22,0x2e},values[2]={0x23,0x2f},sizes[2]={160,320};' in host
 body=compact(paths[2]).split('voidqca_htt_status(uint8_tout[320]){',1)[1];fields=re.search(r'uint32_tf\[56\]=\{(.*?)\};',body).group(1).split(',')
 assert len(fields)==56 and fields[4]=='htt_actual_released()' and fields[54]=='62'
 assert fields[35:44]==['held','port.dma_users','port.claimed','wake.owned','link.owned','irq.owned','boot.owns_pin','adapter.bus.owned','adapter.access.count']
 assert fields[44:47]==['adapter.phase','adapter.channels.cleanup_slot','persistent.life.phase']
 assert 'le32(b+8+54*4)!=62' in host and 'le32(b+8+44*4)!=12||le32(b+8+45*4)!=14||le32(b+8+46*4)!=4' in host and 'for(unsignedn=35;n<=43;n++)' in host
 return {'status':'MONITOR62-ACTUAL-NATIVE-GATT-STATUS-LAYOUT-PASS','candidate':g,'source_sha256':{str(p.relative_to(REPO)):sha(p) for p in [*paths,ROOT/'collector.m',Path(__file__)]},'manager_started':False,'physical_read':False}
if __name__=='__main__':
 result=check();(ROOT/'evidence/native-binding.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'])
