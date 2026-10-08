"""Pinned Mac monitor and generated native62 ABI; no real manager."""
from pathlib import Path
import importlib.util
import gate
ROOT=gate.REPO/'experiments/native-wifi-qca9377-htt62-progress-monitor-v1'
PROOF='a8b5899ae01874690df88604a4a06986929658eee33a82aa75609ae7f472ee0a'
BINDING='8c0f84f34ed1be58d1c988d998f1dc6350076eb69748e25feeb4fefe553d927e'
def checked():
 gate.need(gate.sha(ROOT/'evidence/host-proof.json')==PROOF and gate.sha(ROOT/'evidence/native-binding.json')==BINDING,'monitor proof changed')
 r=gate.flow.read_json(ROOT/'evidence/host-proof.json');b=gate.flow.read_json(ROOT/'evidence/native-binding.json')
 gate.need(not r['bluetooth_manager_started'] and r['writes']==0 and r['private_key_loads']==0 and b['candidate']['report_sha256']==gate.REPORT,'host proof scope')
 for n,h in r['source_sha256'].items():gate.need(gate.sha(ROOT/gate.safe(n))==h,'monitor source changed')
 for n,h in r['compiler_input_sha256'].items():gate.need(gate.sha(n)==h,'compiler input changed')
 for n,h in b['source_sha256'].items():gate.need(gate.sha(gate.REPO/gate.safe(n))==h,'native ABI source changed')
 gate.need(gate.sha(r['executable'])==r['executable_sha256'] and gate.sha(ROOT/'evidence/host.log')==r['host_log_sha256'],'monitor executable/log changed')
 spec=importlib.util.spec_from_file_location('_htt62_monitor_abi',ROOT/'native_binding.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.check()
 return r['executable']
if __name__=='__main__':print(checked())
