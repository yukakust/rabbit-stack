"""Pinned Linux resource assignments as independent oracle; Yukabox only."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SESSION=ROOT.parent/'native-wifi-qca9377-session-v1'
MEMORY=ROOT.parent/'native-wifi-qca9377-memory-v1'
INIT=ROOT.parent/'native-wifi-qca9377-wmi-init-v1'
sys.path.insert(0,str(SESSION));from verify_htc import CC
REF=Path('/home/yuka/rabbit-world/wmi-init-next/reference')
PIN={'wmi-tlv.c':'02309cad56513a1ef0975c9d73e568e343c874d35124f39111ddd26d8a75c5bb','wmi-tlv.h':'16c6b984177dd8c0f80dbc4df52597a6def435d8892fb55381091bdb88a258c9','hw.h':'e9658e742445aa2049078a7da8c6ee6860762cec5f5dc40a99c552e6cd6cba13','wmi.h':'fff0e5749d68c461ed08e69060321942d68bdb050954c39b2a57c0045457106c','core.c':'e36c575f6ad996d58d1cbbd0b813a9c5f350a068d18fe92882ac397b9ba722c2'}
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 texts={n:(REF/n).read_text() for n in PIN}
 assert all(sha((REF/n).read_bytes())==h for n,h in PIN.items())
 c=texts['core.c'];entry=c[c.index('.id = QCA9377_HW_1_1_DEV_VERSION,'):];entry=entry[:entry.index('\n\t},')]
 assert '.bus = ATH10K_BUS_PCI' in entry and '.num_peers =' not in entry
 skid=re.search(r'\.ast_skid_limit = (0x[0-9a-f]+)',entry)[1]
 wds=re.search(r'\.num_wds_entries = (0x[0-9a-f]+)',entry)[1]
 assert 'ar->wmi.rx_decap_mode = ATH10K_HW_TXRX_NATIVE_WIFI;' in c
 assert 'ar->htt.max_num_pending_tx = TARGET_TLV_NUM_MSDU_DESC;' in c
 assert 'ar->wow.max_num_patterns = TARGET_TLV_NUM_WOW_PATTERNS;' in c
 w=texts['wmi-tlv.c'];start=w.index('ath10k_wmi_tlv_op_gen_init(');w=w[start:];w=w[w.index('cfg->num_vdevs ='):w.index('ath10k_wmi_tlv_put_host_mem_chunks')]
 header=texts['wmi-tlv.h'];struct=re.search(r'struct wmi_tlv_resource_config\s*\{.*?\}\s*__packed;',header,re.S)[0]
 defs='\n'.join(l for l in texts['hw.h'].splitlines() if l.startswith('#define TARGET_TLV_NUM_'))
 flags='\n'.join(l for l in header.splitlines() if l.startswith(('#define WMI_TLV_FLAG_MGMT_BUNDLE_TX_COMPL','#define WMI_RSRC_CFG_FLAG_TX_ACK_RSSI')))
 base_macro=texts['wmi.h'].split('#define WMI_SERVICE_IS_ENABLED',1)[1].split('\n\n',1)[0]
 base_macro='#define WMI_SERVICE_IS_ENABLED'+base_macro
 assert base_macro.count('sizeof(u32)')==2
 # Independent enum numbering, not copying candidate service65 constant.
 enum=re.search(r'enum wmi_tlv_service\s*\{(.*?)\};',header,re.S)[1];v=-1;ids={}
 for name,value in re.findall(r'\b(WMI_TLV_\w+)\s*(?:=\s*(\d+))?\s*,',enum):
  v=int(value) if value else v+1;ids[name]=v
 assert ids['WMI_TLV_SERVICE_RX_FULL_REORDER']==65 and ids['WMI_TLV_SERVICE_TX_DATA_MGMT_ACK_RSSI']==174
 out=ROOT/'runs/resources';out.mkdir(parents=True,exist_ok=True)
 oracle=out/'reference.c'
 oracle.write_text('''#include <stdint.h>
#include <string.h>
#define __le32 uint32_t
#define u32 uint32_t
#define __le32_to_cpu(x) (x)
#define __packed __attribute__((packed))
#define __cpu_to_le32(x) (x)
#define BIT(x) (1u<<(x))
#define WMI_SERVICE_RX_FULL_REORDER 0
#define WMI_SERVICE_TX_DATA_ACK_RSSI 1
#define test_bit(bit,map) (((map)>>(bit))&1u)
'''+defs+'\n'+flags+'\n'+base_macro+'\n'+struct+'''
void reference(uint32_t out[44],const uint32_t map[32]){
 unsigned reorder=!!WMI_SERVICE_IS_ENABLED(map,65,128);
 struct {struct {unsigned num_peers,ast_skid_limit,num_wds_entries;} hw_params;
 struct {unsigned svc_map,rx_decap_mode;} wmi;
 struct {unsigned max_num_pending_tx;} htt;
 struct {unsigned max_num_patterns;} wow;} value={0},*ar=&value;
 struct wmi_tlv_resource_config storage={0},*cfg=&storage;
 _Static_assert(sizeof(storage)==176,"resource struct");
 ar->hw_params.ast_skid_limit='''+skid+''';ar->hw_params.num_wds_entries='''+wds+''';
 ar->wmi.rx_decap_mode=1;ar->wmi.svc_map=reorder;
 ar->htt.max_num_pending_tx=TARGET_TLV_NUM_MSDU_DESC;
 ar->wow.max_num_patterns=TARGET_TLV_NUM_WOW_PATTERNS;
 '''+w+'''memcpy(out,cfg,sizeof(storage));
}
''')
 inputs=[ROOT/n for n in ['resources.c','resources.h','resources_test.c','verify_resources.py']]+[MEMORY/'memory_plan.h',MEMORY/'memory_plan.c',INIT/'init_wire.c',INIT/'init_wire.h',SESSION/'wmi_boot_info.h',SESSION/'verify_htc.py']
 hashes={str(p.relative_to(ROOT.parent.parent)):sha(p.read_bytes()) for p in inputs}
 exe=out/'resources-test';inc=['-I'+str(p) for p in [ROOT,MEMORY,SESSION,INIT]]
 subprocess.run([str(CC),'-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all',*inc,str(ROOT/'resources.c'),str(INIT/'init_wire.c'),str(MEMORY/'memory_plan.c'),str(ROOT/'resources_test.c'),str(oracle),'-o',str(exe)],check=True)
 r=subprocess.run([str(exe)],capture_output=True,text=True,timeout=60);(out/'host.log').write_text(r.stdout+r.stderr);assert not r.returncode,r.stderr
 subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror',*inc,'-c',str(ROOT/'resources.c'),'-o',str(out/'resources.obj')],check=True)
 assert all(sha((ROOT.parent.parent/n).read_bytes())==h for n,h in hashes.items())
 report={'status':'QCA9377-PCI-TLV-RESOURCE-REFERENCE-ASAN-COFF-PASS','build_host':'yukabox','checks':int(re.search(r'checks=(\d+)',r.stdout)[1]),'source_sha256':hashes,'linux_commit':'6b5a2b7d9bc156e505f09e698d85d6a1547c1206','reference_sha256':PIN,'derived_oracle_sha256':sha(oracle.read_bytes()),'host_log_sha256':sha((out/'host.log').read_bytes()),'native_integrated':False,'station_profile_admitted':False,'extended_services_validated':False,'management_bundle_handler_implemented':False,'dma_owners_verified':False,'physical_verified':False,'wifi_connected':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(r.stdout.strip())
if __name__=='__main__':main()
