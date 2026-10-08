"""Public-only frozen host/native ABI proof for corrected read-only monitor."""
import gate,importlib.util
ROOT=gate.REPO/'experiments/native-wifi-qca9377-scan61-progress-monitor-v2'
PROOF='41adef14f69e07b893b062bf86be9060fa56241e4c02c885ab005c7269779023'
BINDING='6d61b383c4392864e162b77abdc1a095cbec2d928e815e9f64fe441665c88696'
def checked():
 gate.need(gate.sha(ROOT/'evidence/host-proof.json')==PROOF and gate.sha(ROOT/'evidence/native-binding.json')==BINDING,'corrected monitor proof changed')
 r=gate.flow.read_json(ROOT/'evidence/host-proof.json');b=gate.flow.read_json(ROOT/'evidence/native-binding.json')
 gate.need(not r['bluetooth_manager_started'] and not r['private_key_loads'] and r['writes']==0 and b['incorrect_v1_UUID_rejected'] and b['candidate_report_sha256']==gate.REPORT,'offline corrected monitor proof')
 for n,h in r['source_sha256'].items():gate.need(gate.sha(ROOT/gate.safe(n))==h,'monitor source changed')
 for n,h in r['compiler_input_sha256'].items():gate.need(gate.sha(n)==h,'monitor compiler input changed')
 for n,h in b['source_sha256'].items():gate.need(gate.sha(gate.REPO/gate.safe(n))==h,'native ABI input changed')
 gate.need(gate.sha(r['executable'])==r['executable_sha256'] and gate.sha(ROOT/'evidence/host.log')==r['host_log_sha256'],'corrected executable/log changed')
 spec=importlib.util.spec_from_file_location('_monitor61_native_binding',ROOT/'native_binding.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.check((ROOT/'collector.m').read_text())
 return r['executable']
if __name__=='__main__':print(checked())
