"""Separate Root bounded passive trial decision; frozen evidence stays unchanged."""
import gate
from pathlib import Path
ROOT=Path(__file__).resolve().parent
AUDIT='8a2bc075fc398b3c69d60e3b9d0161da172fae66f8e7aa79c2b4de603f2ee585'
def checked():
 p=ROOT/'evidence/policy-audit.json';gate.need(gate.sha(p)==AUDIT,'primary policy audit changed')
 a=gate.flow.read_json(p);b=a['technical_source_bindings'];gate.need(b['candidate_report_sha256']==gate.REPORT and b['candidate_payload_sha256']==gate.PAYLOAD,'audit candidate differs')
 proposal=gate.REPO/a['engineering_policy']['proposal_path'];gate.need(gate.sha(proposal)==a['engineering_policy']['proposal_sha256'],'authenticated channel proposal changed')
 intent=a['command_intent'];gate.need(intent['scan_control_flags_hex']=='0x21' and not intent['add_broadcast_probe_request_present'] and intent['SSID_BSSID_probe_IE_lists']=='empty' and not intent['association_or_host_mgmt_data_TX_path'],'strict passive intent only')
 for kind in ('wmi_scan','channel'):
  gate.need(gate.sha(gate.REPO/b[kind+'_source_path'])==b[kind+'_source_sha256'],'reviewed wire source changed')
 return {'status':'ROOT61-BOUNDED-STRICT-PASSIVE-TRIAL-ADMISSION','generation':61,'candidate_report_sha256':gate.REPORT,'payload_sha256':gate.PAYLOAD,'audit_sha256':AUDIT,'primary_reference':a['primary_instrument']['gazette_url'],'channels_mhz':list(range(2412,2473,5)),'width_mhz':20,'scan_deadline_us':25000000,'active_probe_intent':False,'association':False,'credentials':False,'physical_zero_TX_verified':False,'measured_antenna_gain':False,'firmware_honors_passive_request_assumed':True,'frozen_flags_changed':False,'fresh60_release_required':True,'actual61_receipt_required_before_assets':True}
if __name__=='__main__':
 import json
 print(json.dumps(checked(),indent=2))
