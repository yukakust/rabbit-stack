"""Run only on Yukabox. Pinned Linux enums/structs are independent wire oracle."""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SESSION=ROOT.parent/'native-wifi-qca9377-session-v1'
VDEV=ROOT.parent/'native-wifi-qca9377-vdev-wire-v1'
REF=Path('/home/yuka/rabbit-world/wmi-init-next/reference')
CC=Path('/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang')
PIN={'wmi-tlv.h':'16c6b984177dd8c0f80dbc4df52597a6def435d8892fb55381091bdb88a258c9','wmi.h':'fff0e5749d68c461ed08e69060321942d68bdb050954c39b2a57c0045457106c','wmi-tlv.c':'02309cad56513a1ef0975c9d73e568e343c874d35124f39111ddd26d8a75c5bb'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert all(sha(REF/n)==h for n,h in PIN.items())
 out=ROOT/'runs/host';out.mkdir(parents=True,exist_ok=True)
 oracle='#include <stdint.h>\n#define u8 uint8_t\n#define u32 uint32_t\n#define __le32 uint32_t\n#define __le16 uint16_t\n#define __packed __attribute__((packed))\n#define BIT(n) (1u<<(n))\n#define WMI_TLV_CMD(g) (((g)<<12)|1)\n#define WMI_TLV_EV(g) (((g)<<12)|1)\n'
 for fn,kind,names in [('wmi-tlv.h','enum',['wmi_tlv_grp_id','wmi_tlv_cmd_id','wmi_tlv_event_id','wmi_tlv_tag']),('wmi.h','enum',['wmi_scan_event_type','wmi_scan_completion_reason','wmi_vdev_type','wmi_vdev_subtype']),('wmi.h','struct',['wmi_mac_addr','wmi_vdev_create_cmd','wmi_scan_event','wmi_start_scan_common']),('wmi-tlv.h','struct',['wmi_tlv_start_scan_cmd'])]:
  t=(REF/fn).read_text()
  for name in names: oracle+=re.search(kind+' '+name+r'\s*\{.*?^\}[^;]*;',t,re.S|re.M)[0]+'\n'
 (out/'oracle.h').write_text(oracle)
 sources=[ROOT/'station_scan.c',SESSION/'htc_wire.c',SESSION/'htc_credit.c',SESSION/'wmi_scan.c',SESSION/'wmi_boot_info.c',VDEV/'vdev_wire.c']
 inputs=sources+[ROOT/'station_scan.h',ROOT/'station_scan_test.c',ROOT/'verify_station_scan.py',ROOT/'README.md']+list(SESSION.glob('*.h'))+[VDEV/'vdev_wire.h']
 hashes={str(p.relative_to(ROOT.parent)):sha(p) for p in inputs}
 flags=['-Wall','-Wextra','-Werror','-I'+str(ROOT),'-I'+str(SESSION),'-I'+str(VDEV),'-I'+str(out)]
 subprocess.run([str(CC),'-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all',*flags,*map(str,sources),str(ROOT/'station_scan_test.c'),'-o',str(out/'test')],check=True)
 r=subprocess.run([str(out/'test')],capture_output=True,text=True,timeout=60);(out/'host.log').write_text(r.stdout+r.stderr);assert not r.returncode,r.stderr
 subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os',*flags,'-c',str(ROOT/'station_scan.c'),'-o',str(out/'station_scan.obj')],check=True)
 assert all(sha(ROOT.parent/n)==h for n,h in hashes.items())
 report={'status':'STATION-PASSIVE-SCAN-COORDINATOR-ASAN-COFF-PASS','checks':int(re.search(r'checks=(\d+)',r.stdout)[1]),'build_host':'yukabox','linux_commit':'6b5a2b7d9bc156e505f09e698d85d6a1547c1206','reference_sha256':PIN,'source_sha256':hashes,'oracle_sha256':sha(out/'oracle.h'),'host_log_sha256':sha(out/'host.log'),'native_integrated':False,'physical_verified':False,'scan_sent':False,'regulatory_approved':False,'wifi_connected':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(r.stdout.strip())
if __name__=='__main__':main()
