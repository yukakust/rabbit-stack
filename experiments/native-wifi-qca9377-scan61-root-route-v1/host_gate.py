"""Pin three offline-tested Mac helpers before signing. Never compiles or opens BLE."""
import gate
PINS={
 'native-wifi-qca9377-scan61-staging-observer-v1':'a38ed17b425a2ac09b64344df364118d45c411f7405e6d8cfd908dfef1513a0e',
 'native-wifi-qca9377-scan61-progress-monitor-v1':'50b3e7e4076c700e40da6fb65bd9238801e3cae63b9c2e193e5b61d1aa21799e',
 'native-wifi-qca9377-scan61-observer-v1':'3ee5a595e0c3d2206ab02310c03cc42095bb1aed6ce8670086c8287b444434f9'}
def checked():
 result={}
 for name,pin in PINS.items():
  root=gate.REPO/'experiments'/name;proof=root/'evidence/host-proof.json';gate.need(gate.sha(proof)==pin,'host proof changed '+name);r=gate.flow.read_json(proof)
  gate.need(not r['bluetooth_manager_started'] and not r['private_key_loads'],'offline host proof only')
  for section in ('source_sha256','compiler_input_sha256'):
   for n,h in r[section].items():
    from pathlib import Path
    p=Path(n) if Path(n).is_absolute() else (gate.REPO/n if n.startswith('experiments/') else root/n)
    gate.need(gate.sha(p)==h,'host source/input changed '+n)
  if 'compile_report' in r:exe=r['compile_report']['executable_path'];h=r['compile_report']['executable_sha256'];log='callbacks.log';lh=r['callback_log_sha256']
  elif 'reader_path' in r:exe=r['reader_path'];h=r['reader_executable_sha256'];log='host.log';lh=r['host_log_sha256']
  else:exe=r['executable'];h=r['executable_sha256'];log='host.log';lh=r['host_log_sha256']
  gate.need(gate.sha(exe)==h and gate.sha(root/'evidence'/log)==lh,'checked host executable/log changed '+name)
  result[name]=exe
 return result
if __name__=='__main__':print(checked())
