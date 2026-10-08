"""Separate Root partial filter/passive scan decision; no evidence flag promotion."""
import gate,host_gate,monitor_gate,oracle_gate
AUDIT=gate.REPO/'experiments/native-wifi-qca9377-scan61-root-route-v1/evidence/policy-audit.json'
AUDIT_SHA='8a2bc075fc398b3c69d60e3b9d0161da172fae66f8e7aa79c2b4de603f2ee585'
REVIEW=gate.ROOT/'evidence/final-independent-review.json'
REVIEW_SHA='2086622c2c37b946d5ac8cdccddbaeade5d57e900165b2d8d069fa6525fb4434'
def checked():
 gate.need(len(REVIEW_SHA)==64 and gate.sha(REVIEW)==REVIEW_SHA,'final independent63 review not adopted')
 r=gate.flow.read_json(REVIEW)
 gate.need(r['status']=='FINAL63-INDEPENDENT-SOURCE-MODEL-CLOSURE-REVIEW' and not r['blocking_findings'] and r['physical_admission'] is False,'independent source review has blockers')
 gate.need(r['candidate']=={'report_sha256':gate.REPORT,'payload_sha256':gate.PAYLOAD,'native_report_sha256':gate.NATIVE_REPORT},'review candidate mismatch')
 for n,h in r['source_sha256'].items():gate.need(gate.sha(gate.REPO/gate.safe(n))==h,'reviewed source changed '+n)
 gate.need(gate.sha(AUDIT)==AUDIT_SHA,'reviewed passive GE policy changed')
 a=gate.flow.read_json(AUDIT);b=a['technical_source_bindings'];intent=a['command_intent']
 gate.need(intent['scan_control_flags_hex']=='0x21' and not intent['add_broadcast_probe_request_present'] and intent['SSID_BSSID_probe_IE_lists']=='empty' and not intent['association_or_host_mgmt_data_TX_path'],'strict passive intent')
 proposal=a['engineering_policy'];gate.need(gate.sha(gate.REPO/gate.safe(proposal['proposal_path']))==proposal['proposal_sha256'],'reviewed channel policy changed')
 for kind,new in (('wmi_scan','wmi_scan.c'),('channel','channel_wire.c')):
  gate.need(gate.sha(gate.REPO/gate.safe(b[kind+'_source_path']))==b[kind+'_source_sha256'] and gate.sha(gate.PROFILE/'components'/new)==b[kind+'_source_sha256'] and (gate.CHECKED/new).read_bytes()==(gate.PROFILE/'components'/new).read_bytes(),'passive wire source differs '+kind)
 host_gate.checked();monitor_gate.checked();oracle_gate.checked()
 return {'status':'ROOT63-BOUNDED-PARTIAL-FILTER-STRICT-PASSIVE-TRIAL-ADMISSION','generation':63,'candidate_report_sha256':gate.REPORT,'payload_sha256':gate.PAYLOAD,'independent_review_sha256':REVIEW_SHA,'inherited_policy_audit_sha256':AUDIT_SHA,'channels_mhz':list(range(2412,2473,5)),'width_mhz':20,'scan_deadline_us':25000000,'filter_echo_deadline_us':3000000,'target_ssid_hex':'6950686f6e6520283929','active_probe_intent':False,'association':False,'credentials':False,'data_plane_ready':False,'rx_ring_cfg':False,'aggregation_setup':False,'physical_zero_TX_verified':False,'firmware_honors_passive_request_assumed':True,'actual62_fresh_release_required':True,'actual63_APPLIED_required_before_assets':True,'frozen_flags_changed':False}
