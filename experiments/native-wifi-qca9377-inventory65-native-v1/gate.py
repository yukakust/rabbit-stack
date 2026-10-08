"""Strict offline software proof, NEVER physical/key/operation admission."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent
BASE64_REPORT='37bde7009088c6a783940f642b3dfddbbe2fdeabea671fa17d7f498234f45866'
BASE64_PAYLOAD='d40efd8c0b08a9289f0caaa64d931519a253559c53ef732af8961ed91ad49965'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(x,s):
 if not x:raise ValueError(s)
def checked(root=R):
 r=Path(root);c=r/'runs/checked-candidate';report=json.loads((c/'report.json').read_text());host=json.loads((r/'runs/host-model/report.json').read_text());q=json.loads((c/'qemu-report.json').read_text());rep=json.loads((c/'reproduction.json').read_text())
 need(report['status']=='UNSIGNED-INVENTORY65-CPU-GETINFO-NORF-NATIVE-PROJECTION' and report['native_counter']==65 and report['generation_reserved'] is False and report['physical_admission'] is False and report['entropy_approved'] is False and type(report['GetRNG_RDSEED_MSR_calls']) is int and report['GetRNG_RDSEED_MSR_calls']==0,'unreserved/software/noentropy')
 need(report['base64_report_sha256']==BASE64_REPORT,'exact actual64 reference')
 need(sha(c/'payload.efi')==report['payload_sha256'] and (c/'payload.efi').stat().st_size==report['payload_bytes']<=262144 and 0<report['mapped_bytes']<=4194304,'actual file/hash/caps')
 for name,d in report['source_sha256'].items():need(sha(r/name)==d,'source '+name)
 for name,d in report['generated_sources_sha256'].items():need(sha(c/name)==d,'generated '+name)
 need(sha(c/'rng65-provenance.obj')==report['rng_code_object_sha256'],'compiled RNG code')
 allowed={'driver.c','city_core.c','city_display.c','diagnostic_gatt.c'}
 for name,d in report['base64_generated_sha256'].items():
  if name not in allowed:need(sha(c/name)==d,'protected base64 source '+name)
 need(host['status']=='INVENTORY65-ACTUAL-PROBE-GETINFO-OWNERSHIP-ASAN-COFF-PASS' and host['physical_admission'] is False and host['GetRNG_RDSEED_MSR_calls']==0 and host['coff_units']==5,'real model gates')
 for name,d in host['source_sha256'].items():need(sha(r/name)==d,'model source '+name)
 for name,d in host['artifacts_sha256'].items():need(sha(r/'runs/host-model'/name)==d,'model artifact '+name)
 need(q['status']=='INVENTORY65-EXACT-WORLD19-NORMAL-EMPTY-QEMU-PASS' and q['payload_sha256']==report['payload_sha256'] and q['physical_admission'] is False and len(q['gates'])==2,'normalEMPTY actual')
 need(q['test_source_sha256']==sha(r/'verify_qemu.py'),'QEMU source')
 for i,g in enumerate(q['gates']):
  need(g['status']=='EXACT-ACTORS-QEMU-LOAD-SNAPSHOTS-CLOCK-FULLSCREEN-RESTORE-REJECTION-PASS' and g['payload_sha256']==report['payload_sha256'] and g['empty_boot'] is bool(i) and g['physical_verified'] is False,'world/replacement/rejection')
  matches=[p for p in c.rglob('observed.log') if sha(p)==g['observed_log_sha256']];need(bool(matches),'retained actual QEMU log')
 need(rep['payload_sha256']==[report['payload_sha256']]*3,'three actual builds')
 need(report['world_package_sha256']=='89ffda340552cf33a4c732597388f4fea358d47b0850f7720bdce51a2b3968b7','world19')
 # Source64 USB/HCI bytes remain exact; the NEW diagnostic driver never calls WLAN.
 driver=(c/'driver.c').read_text();need('qca_collect(st);qca_start(st' not in driver and 'qca_poll(began/1000)' not in driver and 'qca_stop()' not in driver,'no RF reachability from callbacks')
 d=(c/'diagnostic_gatt.c').read_text();need('qca_filter64_att(s->mtu' not in d and 'qca_ram_att(s->mtu' not in d,'no high WLAN/asset route')
 return {'status':'INVENTORY65-OFFLINE-SOURCE-MODEL-WORLD19-CLOSURE-PASS','physical_admission':False,'generation_reserved':False,'payload_sha256':report['payload_sha256'],'payload_bytes':report['payload_bytes'],'mapped_bytes':report['mapped_bytes'],'required_root_physical_gates':['actual64 complete classified receipt/raw/all14released','fresh64 RFS+world19 under correct operation lock','archive/retire64 before exactlyonce65 signing','compiled65 owner/target/source bindings'],'entropy_approved':False}
if __name__=='__main__':print(json.dumps(checked(),indent=2))
