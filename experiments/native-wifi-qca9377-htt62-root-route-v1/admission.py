"""Root narrow version query decision, separate from frozen model evidence."""
import gate, host_gate, monitor_gate
REVIEW=gate.REPO/'experiments/native-wifi-qca9377-htt62-next-step-review-v1/evidence/review.json'
REVIEW_SHA='d5c9326db81a1870d1df3b374a8255b19d9fd1bdb6638665f7669d55e58c14dc'
def checked():
 gate.need(gate.sha(REVIEW)==REVIEW_SHA,'independent native review changed')
 r=gate.flow.read_json(REVIEW)
 gate.need(r['candidate']['report_sha256']==gate.REPORT and r['candidate']['payload_sha256']==gate.PAYLOAD and not r['lifetime_review']['native_blocking_bug_demonstrated_by_this_review'],'review candidate mismatch')
 for n,h in r['source_sha256'].items():gate.need(gate.sha(gate.REPO/gate.safe(n))==h,'reviewed source changed')
 host_gate.checked();monitor_gate.checked()
 return {'status':'ROOT62-BOUNDED-NON-RF-VERSION-QUERY-TRIAL-ADMISSION','generation':62,'candidate_report_sha256':gate.REPORT,'payload_sha256':gate.PAYLOAD,'review_sha256':REVIEW_SHA,'bounded_query_us':3000000,'RF_request':False,'scan':False,'association':False,'credentials':False,'data_plane_ready':False,'actual61_fresh_release_required':True,'actual62_APPLIED_required_before_assets':True,'frozen_flags_changed':False}
