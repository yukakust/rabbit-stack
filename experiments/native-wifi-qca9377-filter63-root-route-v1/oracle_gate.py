"""Exact actual-C model→host semantic bridge. Never a physical observation."""
import gate,json
SCOPE=gate.REPO/'experiments/native-wifi-qca9377-native63-host-oracle-v1'
EVIDENCE=SCOPE/'evidence/2026-10-08'
REPORT='535a1dc3898d2f6f2d615f3aec1804b62ff5ca641ebbba49c76196f9a626e4d3'
def checked():
 gate.need(gate.sha(EVIDENCE/'report.json')==REPORT,'actual C oracle report changed')
 r=gate.flow.read_json(EVIDENCE/'report.json');n=gate.flow.read_json(gate.PROFILE/'runs/native-host/report.json')
 gate.need(r['status']=='FROZEN63-ACTUAL-C-PRODUCER-HOST-ORACLE-ASAN-COFF-PASS' and r['fixture_kind']=='synthetic-actual-C-producer' and r['build_host']=='yukabox' and r['native_report_sha256']==gate.NATIVE_REPORT and r['native_payload_sha256']==gate.PAYLOAD,'oracle exact native63 context')
 for k in ('physical','BLE','signing_admitted','wifi_connected'):gate.need(r[k] is False,'oracle is software only '+k)
 gate.need(r['private_key_loads']==r['device_operations']==0,'no actual oracle secret/device operation')
 expected={k:v for k,v in n['compiled_fixture_sources_sha256'].items() if k!='fixture.c'}
 gate.need(r['unchanged_production_inputs_sha256']==expected and len(expected)==160,'all frozen native model inputs joined oracle')
 out=SCOPE/'runs/producer'
 for name,h in expected.items():gate.need(gate.sha(out/gate.safe(name))==h,'oracle production input changed '+name)
 for name,h in r['supplemental_exact_candidate_sources_sha256'].items():gate.need(gate.sha(out/gate.safe(name))==h and gate.sha(gate.CHECKED/gate.safe(name))==h,'oracle supplemental compiler input changed '+name)
 for name,key in (('fixture.c','instrumented_fixture_sha256'),('init_probe.obj','coff_object_sha256'),('test','test_executable_sha256')):gate.need(gate.sha(out/name)==r[key],'oracle actual compiled fixture/object changed '+name)
 gate.need(gate.sha(SCOPE/'verify_oracle.py')==r['instrumentation_source_sha256'] and gate.sha(EVIDENCE/'host.log')==r['host_log_sha256'],'oracle instrumentation/log changed')
 import classify_filter63
 for case in (0,4,2):
  name='capture-scan0-filter'+str(case)+'.json';gate.need(gate.sha(EVIDENCE/name)==r['captures_sha256'][name],'oracle C capture changed')
  raw=gate.flow.read_json(EVIDENCE/name);gate.need(raw['fixture_kind']=='synthetic-actual-C-producer' and raw['physical'] is False,'model capture must remain labelled')
  d=classify_filter63.decode.decode_capture(raw)
  gate.need(d['pipeline']['filter_tx_count']==3 and d['pipeline']['filter_tx_completed']==1,'actual count versus boolean semantic join')
  expected_result=case!=2
  gate.need(all(d[k] is expected_result for k in ('pipeline_completed','target_observed','owned_filter_version_verified')),'C→host positive/negative classification differs')
  try:classify_filter63.bindings.callback_join(raw,[])
  except ValueError:pass
  else:raise ValueError('synthetic model passed physical callback gate')
 return {'report_sha256':REPORT,'actual_C_to_host_semantic_cases':3,'physical':False,'device_operations':0}
if __name__=='__main__':print(json.dumps(checked(),indent=2))
