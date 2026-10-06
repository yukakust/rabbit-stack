"""Pinned common-prefix layout and metadata, no radio or memory allocation."""
import hashlib,json,re,subprocess
from pathlib import Path
import operating_build as build
from verify_port import CC
ROOT=build.ROOT
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 out=ROOT/'runs/layout-host';out.mkdir(parents=True,exist_ok=True);build.sources(out)
 raw=Path('/home/yuka/rabbit-world/wmi-init-next/reference/wmi-tlv.h').read_bytes();assert sha(raw)=='16c6b984177dd8c0f80dbc4df52597a6def435d8892fb55381091bdb88a258c9'
 header='#include <stdint.h>\ntypedef uint32_t __le32;typedef uint8_t u8;\n#define __packed __attribute__((packed))\n'
 for name in ('wmi_tlv_abi_version','wmi_tlv_hw_bd_info','wmi_tlv_svc_rdy_ev'):
  m=re.search(r'struct '+name+r' \{.*?^\}[^;]*;',raw.decode(),re.S|re.M);assert m;header+=m.group()+'\n'
 (out/'upstream-layout.h').write_text(header)
 files=[ROOT/'wmi_boot_info.c',out/'wmi_scan.c',ROOT/'layout_test.c'];exe=out/'layout-test'
 subprocess.run([str(CC),'-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all','-I'+str(out),*map(str,files),'-o',str(exe)],check=True)
 r=subprocess.run([str(exe)],capture_output=True,text=True,timeout=60);(out/'host.log').write_text(r.stdout+r.stderr);assert not r.returncode,r.stderr
 subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-I'+str(out),'-c',str(ROOT/'wmi_boot_info.c'),'-o',str(out/'wmi_boot_info.obj')],check=True)
 inputs=[ROOT/'wmi_boot_info.c',ROOT/'layout_test.c',ROOT/'verify_layout.py',ROOT/'operating_build.py',build.SESSION/'wmi_boot_info.h',build.SESSION/'wmi_scan.c',build.SESSION/'wmi_scan.h']
 report={'status':'SERVICE-READY-COMMON-PREFIX-MEMORY-ASAN-COFF-PASS','checks':int(re.search(r'checks=(\d+)',r.stdout).group(1)),'build_host':'yukabox','source_sha256':{str(p.relative_to(ROOT.parent.parent)):sha(p.read_bytes()) for p in inputs},'reference_sha256':sha(raw),'oracle_sha256':sha(header.encode()),'host_log_sha256':sha((out/'host.log').read_bytes()),'native_integrated':False,'memory_allocated':False,'regulatory_approved':False,'physical_verified':False,'wifi_connected':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(r.stdout.strip())
if __name__=='__main__':main()
