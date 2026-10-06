"""Pinned Linux prefix policy and captured physical READY; host proof only."""
import hashlib,json,re,subprocess
from pathlib import Path
import startup_build as b
from verify_port import CC
R=b.ROOT;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=R/'runs/ready-codec';out.mkdir(parents=True,exist_ok=True);b.sources(out)
 ref=Path('/home/yuka/rabbit-world/wmi-init-next/reference')
 hashes={'wmi-tlv.h':'16c6b984177dd8c0f80dbc4df52597a6def435d8892fb88a258c9'}
 # Full exact SHA pins used by the existing independently checked components.
 pins={'wmi-tlv.h':'16c6b984177dd8c0f80dbc4df52597a6def435d8892fb55381091bdb88a258c9','wmi-tlv.c':'02309cad56513a1ef0975c9d73e568e343c874d35124f39111ddd26d8a75c5bb','wmi.h':'fff0e5749d68c461ed08e69060321942d68bdb050954c39b2a57c0045457106c'}
 for n,h in pins.items():assert sha(ref/n)==h
 h=(ref/'wmi-tlv.h').read_text();w=(ref/'wmi.h').read_text();c=(ref/'wmi-tlv.c').read_text()
 assert re.search(r'\[WMI_TLV_TAG_STRUCT_READY_EVENT\]\s*=\s*\{\s*\.min_len\s*=\s*sizeof\(struct wmi_tlv_rdy_ev\)',c)
 pull=c[c.index('static int ath10k_wmi_tlv_op_pull_rdy_ev'):];pull=pull[:pull.index('\n}\n')]
 for assignment in ['arg->status = ev->status;','arg->mac_addr = ev->mac_addr.addr;']:assert assignment in pull
 header='#include <stdint.h>\ntypedef uint32_t __le32,u32;typedef uint8_t u8;\n#define __packed __attribute__((packed))\n'
 for text,name in [(h,'wmi_tlv_abi_version'),(w,'wmi_mac_addr'),(h,'wmi_tlv_rdy_ev')]:
  m=re.search(r'struct '+name+r' \{.*?^\}[^;]*;',text,re.S|re.M);assert m;header+=m.group()+'\n'
 (out/'oracle.h').write_text(header)
 fixture=R/'ready_test.c';exe=out/'ready-test'
 subprocess.run([str(CC),'-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all','-I'+str(out),str(R/'wmi_boot_info.c'),str(out/'wmi_scan.c'),str(fixture),'-o',str(exe)],check=True)
 run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=60);(out/'host.log').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stderr
 subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-I'+str(out),'-c',str(R/'wmi_boot_info.c'),'-o',str(out/'ready.obj')],check=True)
 files=[R/'wmi_boot_info.c',R/'ready_test.c',R/'verify_ready.py',b.SESSION/'wmi_scan.c',b.SESSION/'wmi_boot_info.h',b.SESSION/'wmi_scan.h']
 d={'status':'READY-MINIMUM-PREFIX-PINNED-ASAN-COFF-PASS','checks':int(re.search(r'checks=(\d+)',run.stdout)[1]),'build_host':'yukabox','source_sha256':{str(p.relative_to(R.parent.parent)):sha(p) for p in files},'reference_sha256':pins,'oracle_sha256':sha(out/'oracle.h'),'host_log_sha256':sha(out/'host.log'),'physical_verified':False,'wifi_connected':False}
 (out/'report.json').write_text(json.dumps(d,indent=2)+'\n');print(run.stdout)
if __name__=='__main__':main()
