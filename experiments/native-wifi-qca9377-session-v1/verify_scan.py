#!/usr/bin/env python3
"""Pinned WMI-TLV scan bytes and untrusted event parsing; host only."""
import hashlib,json,re,subprocess
from pathlib import Path
from verify_htc import ROOT,VENDOR,CC,LINUX,sha
TLV=ROOT.parent/'native-wifi-qca9377-v1/runs/wmi-reference/wmi-tlv.h'
def main():
 out=ROOT/'runs/scan';out.mkdir(parents=True,exist_ok=True)
 wmi=(VENDOR/'wmi.h').read_bytes();tlv=TLV.read_bytes()
 assert sha(wmi)=='fff0e5749d68c461ed08e69060321942d68bdb050954c39b2a57c0045457106c'
 assert sha(tlv)=='16c6b984177dd8c0f80dbc4df52597a6def435d8892fb55381091bdb88a258c9'
 oracle='#include <stdint.h>\ntypedef uint8_t u8;typedef uint32_t u32;typedef uint16_t __le16;typedef uint32_t __le32;\n#define __packed __attribute__((packed))\n#define WMI_TLV_CMD(g) (((g)<<12)|1)\n#define WMI_TLV_EV(g) (((g)<<12)|1)\n'
 for kind,names,raw in (
  ('enum',('wmi_tlv_grp_id','wmi_tlv_cmd_id','wmi_tlv_event_id','wmi_tlv_tag'),tlv),
  ('struct',('wmi_mac_addr','wmi_start_scan_common','wmi_scan_event'),wmi),
  ('struct',('wmi_tlv','wmi_tlv_start_scan_cmd'),tlv)):
  for name in names:
   m=re.search(kind+' '+name+r' \{.*?^\}[^;]*;',raw.decode(),re.S|re.M);assert m,name;oracle+=m.group()+'\n'
 (out/'upstream-scan.h').write_text(oracle)
 inputs={n:sha((ROOT/n).read_bytes()) for n in ('wmi_scan.c','wmi_scan.h','wmi_scan_test.c','verify_scan.py','verify_htc.py')}
 subprocess.run([str(CC),'-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-I'+str(ROOT),'-I'+str(out),str(ROOT/'wmi_scan.c'),str(ROOT/'wmi_scan_test.c'),'-o',str(out/'scan-test')],check=True)
 result=subprocess.run([str(out/'scan-test')],capture_output=True,text=True,timeout=30);(out/'host.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
 subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-I'+str(ROOT),'-c',str(ROOT/'wmi_scan.c'),'-o',str(out/'wmi_scan.obj')],check=True)
 assert inputs=={n:sha((ROOT/n).read_bytes()) for n in inputs}
 report={'status':'WMI-PASSIVE-SCAN-WIRE-HOST-COFF-PASS','source_sha256':inputs,'reference':{'linux_commit':LINUX,'wmi_h_sha256':sha(wmi),'wmi_tlv_h_sha256':sha(tlv),'oracle_sha256':sha(oracle.encode())},'host_log_sha256':sha((out/'host.log').read_bytes()),'build_host':'yukabox','physical_verified':False,'native_integrated':False,'regulatory_configured':False,'scan_started':False,'wifi_connected':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(result.stdout.strip());print(report['status'])
if __name__=='__main__':main()
