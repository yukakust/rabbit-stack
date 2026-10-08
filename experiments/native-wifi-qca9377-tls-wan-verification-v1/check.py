from pathlib import Path
import hashlib,json,ssl
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=json.loads((R/'evidence/freeze.json').read_text())
for group in ('source_sha256','evidence_sha256'):
 for n,h in f[group].items(): assert sha(R/n)==h,n
for report_name in ('report.json','host-handshake-report.json'):
 r=json.loads((R/'evidence'/report_name).read_text())
 for n,h in r['source_sha256'].items(): assert sha(R/n)==h,n
b=R.parent/'native-wifi-qca9377-tls13-ble-prototype-v1'
assert sha(b/'evidence/2026-10-09/freeze.json')==f['base_freeze_sha256']
r=json.loads((b/'evidence/2026-10-09/freeze.json').read_text())
for n,h in r['source_sha256'].items(): assert sha(b/n)==h,n
h=json.loads((R/'evidence/host-handshake-report.json').read_text())
assert sha(R/'evidence/report.json')==h['verification_report_sha256']
assert sha(R/'evidence/host-handshake.log')==h['host_log_sha256']
assert hashlib.sha256(ssl.PEM_cert_to_DER_cert((R/'fixtures/isrg-root-x2.pem').read_text())).hexdigest()=='69729b8e15a86efc177a57afb7171dfc64add28c2fca8cf1507e34453ccb1470'
for i,digest in enumerate(f['served_der_sha256']):
 assert hashlib.sha256(ssl.PEM_cert_to_DER_cert((R/'fixtures'/f'served-{i}.pem').read_text())).hexdigest()==digest
assert not h['physical_Dell'] and not h['Dell_to_Yukabox_proved']
print('WAN-MATURE-CA-NAME-UTC-SOURCE-PROOF-PINS-PASS; actual host TLS only, NOT Dell')
