"""Pinned STOP_ONE Linux body oracle; host ASAN/COFF only on Yukabox."""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent;STA=ROOT.parent/'native-wifi-qca9377-station-scan-v1';SESSION=ROOT.parent/'native-wifi-qca9377-session-v1';VDEV=ROOT.parent/'native-wifi-qca9377-vdev-wire-v1'
REF=Path('/home/yuka/rabbit-world/wmi-init-next/reference')
CC=Path('/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang')
PIN={'wmi-tlv.c':'02309cad56513a1ef0975c9d73e568e343c874d35124f39111ddd26d8a75c5bb','wmi-tlv.h':'16c6b984177dd8c0f80dbc4df52597a6def435d8892fb55381091bdb88a258c9','wmi.h':'fff0e5749d68c461ed08e69060321942d68bdb050954c39b2a57c0045457106c'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert all(sha(REF/n)==h for n,h in PIN.items());out=ROOT/'runs/host';out.mkdir(parents=True,exist_ok=True)
 oracle='#include <stdint.h>\n#define u32 uint32_t\n#define __le32 uint32_t\n#define __packed __attribute__((packed))\n#define BIT(n) (1u<<(n))\n#define __cpu_to_le32(n) (n)\n#define WMI_TLV_CMD(g) (((g)<<12)|1)\n#define WMI_TLV_EV(g) (((g)<<12)|1)\n'
 for fn,kind,names in [('wmi-tlv.h','enum',['wmi_tlv_grp_id','wmi_tlv_cmd_id','wmi_tlv_event_id','wmi_tlv_tag']),('wmi.h','enum',['wmi_stop_scan_type','wmi_scan_event_type','wmi_scan_completion_reason']),('wmi.h','struct',['wmi_stop_scan_cmd','wmi_stop_scan_arg','wmi_scan_event'])]:
  t=(REF/fn).read_text()
  for name in names: oracle+=re.search(kind+' '+name+r'\s*\{.*?^\}[^;]*;',t,re.S|re.M)[0]+'\n'
 for macro in ['WMI_HOST_SCAN_REQ_ID_PREFIX','WMI_HOST_SCAN_REQUESTOR_ID_PREFIX']:
  oracle+=re.search(r'^#define '+macro+r'\b[^\n]*',(REF/'wmi.h').read_text(),re.M)[0]+'\n'
 oracle+='void reference_stop(uint8_t*,unsigned,unsigned);\n';(out/'oracle.h').write_text(oracle)
 c=(REF/'wmi-tlv.c').read_text();start=c.index('ath10k_wmi_tlv_op_gen_stop_scan(');c=c[start:c.index('static int ath10k_wmi_tlv_op_get_vdev_subtype',start)]
 assignments=c[c.index('cmd->req_type ='):c.index('ath10k_dbg')]
 body='''#include "oracle.h"
#include <string.h>
static void put(uint8_t*p,uint32_t n){for(unsigned j=0;j<4;j++)p[j]=(uint8_t)(n>>(j*8));}
void reference_stop(uint8_t*out,unsigned scan,unsigned request){
 struct wmi_stop_scan_arg a={.req_id=request,.req_type=WMI_SCAN_STOP_ONE,.u.scan_id=scan};const struct wmi_stop_scan_arg*arg=&a;
 struct wmi_stop_scan_cmd value={0},*cmd=&value;
 u32 scan_id=arg->u.scan_id|WMI_HOST_SCAN_REQ_ID_PREFIX,req_id=arg->req_id|WMI_HOST_SCAN_REQUESTOR_ID_PREFIX;
'''+assignments+'''
 _Static_assert(sizeof(value)==16,"stop length");
 put(out,WMI_TLV_STOP_SCAN_CMDID);put(out+4,sizeof(value)|(WMI_TLV_TAG_STRUCT_STOP_SCAN_CMD<<16));memcpy(out+8,&value,sizeof(value));}
'''
 (out/'oracle.c').write_text(body)
 sources=[ROOT/'scan_stop.c',STA/'station_scan.c',SESSION/'htc_wire.c',SESSION/'htc_credit.c',SESSION/'wmi_scan.c',SESSION/'wmi_boot_info.c',VDEV/'vdev_wire.c'];inputs=sources+[ROOT/'scan_stop.h',ROOT/'scan_stop_test.c',ROOT/'verify_stop.py',ROOT/'README.md',STA/'station_scan.h',VDEV/'vdev_wire.h']+list(SESSION.glob('*.h'))
 hashes={str(p.relative_to(ROOT.parent)):sha(p) for p in inputs};flags=['-Wall','-Wextra','-Werror',*['-I'+str(p) for p in [ROOT,STA,SESSION,VDEV,out]]]
 subprocess.run([str(CC),'-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all',*flags,*map(str,sources),str(ROOT/'scan_stop_test.c'),str(out/'oracle.c'),'-o',str(out/'test')],check=True)
 r=subprocess.run([str(out/'test')],capture_output=True,text=True,timeout=60);(out/'host.log').write_text(r.stdout+r.stderr);assert not r.returncode,r.stderr
 subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os',*flags,'-c',str(ROOT/'scan_stop.c'),'-o',str(out/'scan_stop.obj')],check=True)
 assert all(sha(ROOT.parent/n)==h for n,h in hashes.items())
 report={'status':'SCAN-STOP-PINNED-ASAN-COFF-PASS','checks':int(re.search(r'checks=(\d+)',r.stdout)[1]),'source_sha256':hashes,'reference_sha256':PIN,'linux_commit':'6b5a2b7d9bc156e505f09e698d85d6a1547c1206','oracle_sha256':sha(out/'oracle.c'),'oracle_header_sha256':sha(out/'oracle.h'),'host_log_sha256':sha(out/'host.log'),'build_host':'yukabox','native_integrated':False,'physical_verified':False,'stop_sent':False,'wifi_connected':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(r.stdout.strip())
if __name__=='__main__':main()
