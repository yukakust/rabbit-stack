"""Read-only pinned-reference and physical52 binding check; never RF admission."""
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parent
REF=Path('/home/yuka/rabbit-world/parallel-scan-native-plan-v1/reference')
LINUX='6b5a2b7d9bc156e505f09e698d85d6a1547c1206'
PINS={'regd.c':'928582bfaa3d72574eb40a69e6bc8f268ff7d37f87de805ec21c2c24beedc5c4','regd.h':'17ddca22d3e35d396cc6dc9005f364157dc34937d609156c80c48d37c7afc73f','regd_common.h':'95eca0ec1ab9e7ea248b4b9cc4ad3081cc9f61eb036e7faa9959acb49b356941','ath10k-mac.c':'e99b6749933719a39037645385ea88be181b380f1135d62aea07c0b474a8236c','ath10k-wmi.c':'68a4fedc3d0cd815c209dda9c0eb3aa3869bd3d35847c633e0c458ba53c320f4'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 for n,h in PINS.items():assert sha(REF/n)==h,n
 refs=json.loads((ROOT/'references.json').read_text());assert {x['file']:x['sha256'] for x in refs['sources']}==PINS
 reg=(REF/'regd_common.h').read_text();regd=(REF/'regd.c').read_text();mac=(REF/'ath10k-mac.c').read_text()
 assert re.search(r'WORC_WORLD\s*=\s*0x6C',reg)
 assert re.search(r'CTRY_GEORGIA\s*=\s*268',(REF/'regd.h').read_text())
 assert '{CTRY_GEORGIA, ETSI4_WORLD, "GE"}' in reg
 assert '{WORC_WORLD, NO_CTL, NO_CTL}' in reg
 assert re.search(r'case 0x6C:\s*return &ath_world_regdom_67_68_6A_6C;',regd)
 body=mac[mac.index('static void ath10k_regd_update('):mac.index('static void ath10k_mac_update_channel_list(')]
 assert body.index('ath10k_update_channel_list(ar)')<body.index('ath10k_wmi_pdev_set_regdomain(')
 for guard in ['IEEE80211_CHAN_DISABLED','IEEE80211_CHAN_NO_IR','IEEE80211_CHAN_RADAR','ch->passive |= ch->chan_radar','channel->max_power * 2','channel->max_reg_power * 2']:
  assert guard in mac,guard
 phys=ROOT.parent/'native-wifi-qca9377-wmi-native-v5/evidence/2026-10-07/native52-control-result';report=json.loads((phys/'report.json').read_text())
 assert report['native_counter']==52 and report['status']=='PHYSICAL-NATIVE52-WMI-INIT-READY-MAC-TX-COMPLETE-ALL-OWNERS-RELEASED'
 for n,h in report['files_sha256'].items():assert sha(phys/n)==h,n
 op=json.loads((phys/'operating52.decoded.json').read_text());startup=json.loads((phys/'startup52.decoded.json').read_text())
 assert (op['regdomain'],op['low2'],op['high2'],op['low5'],op['high5'])==(108,2312,2732,4920,6100)
 assert op['service_valid']==1 and op['memory_count']==0
 assert startup['ready_seen']==startup['tx_complete']==1 and startup['error']==0
 frame=bytes.fromhex(startup['frame_hex']);assert frame[12:14]==bytes([52,0])
 boot=json.loads((phys/'boot52.decoded.json').read_text())
 assert boot['all_loader_resources_released'] and (boot['adapter_phase'],boot['cleanup_slots'],boot['dma_users'],boot['asset_pinned'])==(12,14,0,0)
 assert not report['router_connected'] and not report['ip_verified']
 out=ROOT/'runs/check';out.mkdir(parents=True,exist_ok=True)
 result={'status':'SCAN-NATIVE-REFERENCE-PLAN-CHECK-PASS','linux_commit':LINUX,'reference_sha256':PINS,'source_sha256':{n:sha(ROOT/n) for n in ['README.md','references.json','verify_plan.py']},'physical52_evidence_sha256':{n:sha(phys/n) for n in ['report.json','operating52.decoded.json','startup52.decoded.json','boot52.decoded.json']},'regdomain108':'WORC_WORLD','approved_policy_exists':False,'selected_frequencies':[],'native_integrated':False,'candidate_generated':False,'rf_admission_granted':False,'rf_command_sent':False,'wifi_connected':False,'blocker':'Missing reviewed policy provenance and native policy/channel/CE3 integration; capability bands are not channel permission.'}
 (out/'host.log').write_text('Pinned policy reference and physical52 source bindings pass. RF remains blocked; no channels selected.\n');result['host_log_sha256']=sha(out/'host.log');(out/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status']);print(result['blocker'])
if __name__=='__main__':main()
