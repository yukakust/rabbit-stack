"""Independent signed-regdb rebuild + exact proposal/header binding; no RF gate."""
import subprocess,json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;E=ROOT.parent;POLICY=E/'native-wifi-qca9377-regulatory-policy-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 if sys.platform!='linux':raise SystemExit('Yukabox only')
 out=ROOT/'runs/policy-binding';out.mkdir(parents=True,exist_ok=True)
 clang='/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang'
 subprocess.run([sys.executable,str(POLICY/'verify_policy.py'),'--reference','/home/yuka/rabbit-world/parallel-regulatory-v1/reference','--clang',clang,'--output',str(out),'--physical52',str(E/'native-wifi-qca9377-wmi-native-v5/evidence/2026-10-07/native52-control-result')],check=True)
 proposal=POLICY/'evidence/2026-10-07/policy-proposal.json';report=json.loads((proposal.parent/'report.json').read_text());assert sha(proposal)==report['proposal_sha256']
 assert (out/'policy-proposal.json').read_bytes()==proposal.read_bytes()
 for n,h in report['sources_sha256'].items():assert sha(POLICY/n)==h
 d=json.loads(proposal.read_text());assert not d['rf_admission_granted'] and d['signature_verified']
 vec=lambda s:'{'+','.join(str(x) for x in bytes.fromhex(s))+'}'
 rows=['{'+','.join(str(c[n]) for n in ('frequency_mhz','centre1_mhz','centre2_mhz','width_mhz','flags','passive','mode','max_power_dbm','max_reg_power_dbm','antenna_gain_db'))+'}' for c in d['candidate_channels']]
 header='#ifndef RABBIT_EXACT_SCAN_POLICY_H\n#define RABBIT_EXACT_SCAN_POLICY_H\n#include "channel_wire.h"\nstatic const QcaReviewedChannelPolicy scan_policy={.version=1,.hardware_regdomain=108,.regdomain=108,.regdomain2=108,.regdomain5=108,.ctl2=255,.ctl5=255,\n.target='+vec(d['target_id'])+',.reviewed_digest='+vec(report['proposal_sha256'])+',.ruleset_digest='+vec(d['ruleset_signed_db_sha256'])+',.location_digest='+vec(d['location_sha256'])+",.alpha2={'G','E'},.count=13,.channels={"+','.join(rows)+'}};\n#endif\n'
 assert header.encode()==(ROOT/'scan_policy.h').read_bytes()
 proof={'status':'INDEPENDENT-SIGNED-REGDB-EXACT-GE-WORLD108-PROPOSAL-HEADER-PASS','proposal_sha256':sha(proposal),'header_sha256':sha(ROOT/'scan_policy.h'),'report_sha256':sha(out/'report.json'),'host_log_sha256':sha(out/'host.log'),'rf_admission_granted':False,'physical53_success_assumed':False}
 (out/'binding.json').write_text(json.dumps(proof,indent=2)+'\n');print(proof['status'])
if __name__=='__main__':main()
