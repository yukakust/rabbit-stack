"""Independent pinned Linux structs/enums/CREATE assignments; Yukabox only."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SESSION=ROOT.parent/'native-wifi-qca9377-session-v1'
sys.path.insert(0,str(SESSION));from verify_htc import CC
REF=Path('/home/yuka/rabbit-world/wmi-init-next/reference')
PIN={'wmi-tlv.c':'02309cad56513a1ef0975c9d73e568e343c874d35124f39111ddd26d8a75c5bb','wmi-tlv.h':'16c6b984177dd8c0f80dbc4df52597a6def435d8892fb55381091bdb88a258c9','wmi.h':'fff0e5749d68c461ed08e69060321942d68bdb050954c39b2a57c0045457106c'}
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 texts={n:(REF/n).read_text() for n in PIN};assert all(sha((REF/n).read_bytes())==h for n,h in PIN.items())
 h=texts['wmi-tlv.h'];w=texts['wmi.h'];c=texts['wmi-tlv.c']
 enums='\n'.join(re.search(r'enum '+n+r'\s*\{.*?\};',h,re.S)[0] for n in ['wmi_tlv_grp_id','wmi_tlv_cmd_id','wmi_tlv_tag'])
 enums+='\n'+re.search(r'enum wmi_vdev_type\s*\{.*?\};',w,re.S)[0]+'\n'+re.search(r'enum wmi_vdev_subtype\s*\{.*?\};',w,re.S)[0]
 structs='\n'.join(re.search(r'struct '+n+r'\s*\{.*?\n\} __packed;',w,re.S)[0] for n in ['wmi_mac_addr','wmi_vdev_create_cmd','wmi_vdev_stop_cmd','wmi_vdev_delete_cmd'])
 out=ROOT/'runs/vdev';out.mkdir(parents=True,exist_ok=True);oracle=out/'reference.c'
 body=c[c.index('ath10k_wmi_tlv_op_gen_vdev_create('):];body=body[body.index('cmd->vdev_id ='):body.index('ath10k_dbg')]
 oracle.write_text('''#include <stdint.h>
#include <string.h>
#define __le32 uint32_t
#define u8 uint8_t
#define u32 uint32_t
#define __packed __attribute__((packed))
#define __cpu_to_le32(x) (x)
#define ether_addr_copy(a,b) memcpy(a,b,6)
#define WMI_TLV_CMD(grp_id) (((grp_id)<<12)|1)
'''+enums+'\n'+structs+'''
static void put(uint8_t*p,uint32_t n){for(unsigned j=0;j<4;j++)p[j]=(uint8_t)(n>>(8*j));}
unsigned reference(uint8_t*out,unsigned which,unsigned vdev_id,const uint8_t mac_addr[6]){
 if(which==0){
  struct wmi_vdev_create_cmd value={0},*cmd=&value;
  enum wmi_vdev_type vdev_type=WMI_VDEV_TYPE_STA;
  enum wmi_vdev_subtype vdev_subtype=WMI_VDEV_SUBTYPE_NONE;
  _Static_assert(sizeof(value)==20,"create size");
 '''+body+'''
  put(out,WMI_TLV_VDEV_CREATE_CMDID);put(out+4,sizeof(value)|(WMI_TLV_TAG_STRUCT_VDEV_CREATE_CMD<<16));memcpy(out+8,&value,sizeof(value));return 8+sizeof(value);
 }
 if(which==1){struct wmi_vdev_stop_cmd value={.vdev_id=vdev_id};put(out,WMI_TLV_VDEV_STOP_CMDID);put(out+4,sizeof(value)|(WMI_TLV_TAG_STRUCT_VDEV_STOP_CMD<<16));memcpy(out+8,&value,sizeof(value));return 8+sizeof(value);}
 struct wmi_vdev_delete_cmd value={.vdev_id=vdev_id};put(out,WMI_TLV_VDEV_DELETE_CMDID);put(out+4,sizeof(value)|(WMI_TLV_TAG_STRUCT_VDEV_DELETE_CMD<<16));memcpy(out+8,&value,sizeof(value));return 8+sizeof(value);
}
''')
 inputs=[ROOT/n for n in ['vdev_wire.c','vdev_wire.h','vdev_test.c','verify_vdev.py']]+[SESSION/'verify_htc.py'];hashes={str(p.relative_to(ROOT.parent.parent)):sha(p.read_bytes()) for p in inputs}
 exe=out/'vdev-test';subprocess.run([str(CC),'-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all','-I'+str(ROOT),str(ROOT/'vdev_wire.c'),str(ROOT/'vdev_test.c'),str(oracle),'-o',str(exe)],check=True)
 r=subprocess.run([str(exe)],capture_output=True,text=True,timeout=60);(out/'host.log').write_text(r.stdout+r.stderr);assert not r.returncode,r.stderr
 subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-I'+str(ROOT),'-c',str(ROOT/'vdev_wire.c'),'-o',str(out/'vdev_wire.obj')],check=True)
 assert all(sha((ROOT.parent.parent/n).read_bytes())==h for n,h in hashes.items())
 report={'status':'STA-VDEV-PINNED-WIRE-ASAN-COFF-PASS','build_host':'yukabox','checks':int(re.search(r'checks=(\d+)',r.stdout)[1]),'source_sha256':hashes,'reference_sha256':PIN,'linux_commit':'6b5a2b7d9bc156e505f09e698d85d6a1547c1206','derived_oracle_sha256':sha(oracle.read_bytes()),'host_log_sha256':sha((out/'host.log').read_bytes()),'native_integrated':False,'physical_verified':False,'firmware_command_sent':False,'scan':False,'wifi_connected':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(r.stdout.strip())
if __name__=='__main__':main()
