from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=json.loads((R/'evidence/freeze.json').read_text());assert f['source_sha256']=={name:sha(R/name) for name in f['source_sha256']}
a=json.loads((R/'evidence/report.json').read_text());assert sha(R/'evidence/report.json')==f['report_sha256'];assert a['build_host']=='yukabox';assert a['host_result'].startswith('PASS 368 SYNTHETIC')
assert not any(a[k] for k in ('physical_wifi','physical_IP','actual_network_traffic','signing_admitted','key_loads'))
assert a['source_sha256']=={name:sha(R/name) for name in a['source_sha256']}
old=json.loads((R.parent/'native-wifi-qca9377-network-nosys-v1/upstream-pin.json').read_text());assert a['upstream_commit']==old['commit']
for name,value in old['upstream_files_sha256'].items():assert sha(R/'vendor'/name)==value
new=json.loads((R/'vendor/tcp-dns-upstream.json').read_text())
for name,value in new.items():assert sha(R/'vendor/src/core'/name)==value['sha256'];assert '/'+old['commit']+'/' in value['url']
assert sha(R/'dhcp_policy.c')==sha(R.parent/'native-wifi-qca9377-network-nosys-v1/dhcp_policy.c')
assert sha(R/'evidence/host.log')==a['host_log_sha256']
print('FROZEN SOFTWARE TCP/DNS/DHCP/ARP/BIO SOURCE CLOSURE PASS; NO PHYSICAL IP/HTTPS PROOF')
