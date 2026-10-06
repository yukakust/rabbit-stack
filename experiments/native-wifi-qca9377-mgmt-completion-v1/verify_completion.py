"""Pinned Linux wire definitions; independent fixture generation on Yukabox."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SESSION=ROOT.parent/'native-wifi-qca9377-session-v1'
sys.path.insert(0,str(SESSION));from verify_htc import CC
REF=Path('/home/yuka/rabbit-world/wmi-init-next/reference')
PIN={'wmi-tlv.c':'02309cad56513a1ef0975c9d73e568e343c874d35124f39111ddd26d8a75c5bb','wmi-tlv.h':'16c6b984177dd8c0f80dbc4df52597a6def435d8892fb55381091bdb88a258c9'}
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 texts={n:(REF/n).read_text() for n in PIN};assert all(sha((REF/n).read_bytes())==h for n,h in PIN.items())
 h=texts['wmi-tlv.h'];c=texts['wmi-tlv.c']
 assert 'arg->num_reports = *bundle_tx_compl.num_reports;' in c
 assert 'arg->desc_ids = bundle_tx_compl.desc_ids;' in c and 'arg->status = bundle_tx_compl.status;' in c
 enums='\n'.join(re.search(r'enum '+n+r'\s*\{.*?\};',h,re.S)[0] for n in ['wmi_tlv_grp_id','wmi_tlv_event_id','wmi_tlv_tag'])
 struct=re.search(r'struct wmi_tlv_mgmt_tx_compl_ev\s*\{.*?\};',h,re.S)[0]
 out=ROOT/'runs/completion';out.mkdir(parents=True,exist_ok=True);oracle=out/'reference.c'
 oracle.write_text('''#include <stdint.h>
#include <string.h>
#define __le32 uint32_t
#define WMI_TLV_EV(grp_id) (((grp_id)<<12)|1)
'''+enums+'\n'+struct+'''
_Static_assert(WMI_TLV_MGMT_TX_COMPLETION_EVENTID==28678,"single event");
_Static_assert(WMI_TLV_MGMT_TX_BUNDLE_COMPLETION_EVENTID==28679,"bundle event");
_Static_assert(WMI_TLV_TAG_STRUCT_MGMT_TX_COMPL_EVENT==423,"single tag");
_Static_assert(WMI_TLV_TAG_STRUCT_MGMT_TX_COMPL_BUNDLE_EVENT==552,"bundle tag");
_Static_assert(WMI_TLV_TAG_ARRAY_UINT32==16,"array tag");
_Static_assert(sizeof(struct wmi_tlv_mgmt_tx_compl_ev)==20,"single struct");
static void put(uint8_t*p,uint32_t n){for(unsigned j=0;j<4;j++)p[j]=(uint8_t)(n>>(8*j));}
unsigned reference_bundle(uint8_t*p,unsigned count,unsigned arrays){
 memset(p,0,2048);put(p,WMI_TLV_MGMT_TX_BUNDLE_COMPLETION_EVENTID);
 put(p+4,4|(WMI_TLV_TAG_STRUCT_MGMT_TX_COMPL_BUNDLE_EVENT<<16));put(p+8,count);
 unsigned pos=12;
 for(unsigned j=0;j<arrays;j++){
  put(p+pos,4*count|(WMI_TLV_TAG_ARRAY_UINT32<<16));pos+=4;
  for(unsigned k=0;k<count;k++)put(p+pos+4*k,j==0?100+k:j==1?k%5:j==2?1000+k:0xffffff80+k);
  pos+=4*count;
 }
 return pos;
}
unsigned reference_single(uint8_t*p,uint32_t id){
 struct wmi_tlv_mgmt_tx_compl_ev v={.desc_id=id,.status=3,.pdev_id=0,.ppdu_id=77,.ack_rssi=UINT32_MAX};
 memset(p,0,2048);put(p,WMI_TLV_MGMT_TX_COMPLETION_EVENTID);
 put(p+4,sizeof(v)|(WMI_TLV_TAG_STRUCT_MGMT_TX_COMPL_EVENT<<16));memcpy(p+8,&v,sizeof(v));return 8+sizeof(v);
}
''')
 inputs=[ROOT/n for n in ['completion.c','completion.h','completion_test.c','verify_completion.py']]+[SESSION/'verify_htc.py'];hashes={str(p.relative_to(ROOT.parent.parent)):sha(p.read_bytes()) for p in inputs}
 exe=out/'completion-test'
 subprocess.run([str(CC),'-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all','-I'+str(ROOT),str(ROOT/'completion.c'),str(ROOT/'completion_test.c'),str(oracle),'-o',str(exe)],check=True)
 r=subprocess.run([str(exe)],capture_output=True,text=True,timeout=60);(out/'host.log').write_text(r.stdout+r.stderr);assert not r.returncode,r.stderr
 subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-I'+str(ROOT),'-c',str(ROOT/'completion.c'),'-o',str(out/'completion.obj')],check=True)
 assert all(sha((ROOT.parent.parent/n).read_bytes())==h for n,h in hashes.items())
 report={'status':'WMI-MGMT-COMPLETION-BOUNDS-OWNER-PLAN-ASAN-COFF-PASS','build_host':'yukabox','checks':int(re.search(r'checks=(\d+)',r.stdout)[1]),'source_sha256':hashes,'linux_commit':'6b5a2b7d9bc156e505f09e698d85d6a1547c1206','reference_sha256':PIN,'derived_oracle_sha256':sha(oracle.read_bytes()),'host_log_sha256':sha((out/'host.log').read_bytes()),'native_integrated':False,'physical_verified':False,'dma_release_implemented':False,'descriptor_generation_verified':False,'station_profile_admitted':False,'wifi_connected':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(r.stdout.strip())
if __name__=='__main__':main()
