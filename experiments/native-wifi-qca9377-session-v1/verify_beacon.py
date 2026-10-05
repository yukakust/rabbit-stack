#!/usr/bin/env python3
"""Pinned 802.11 layout oracle, untrusted frame tests and native COFF; host only."""
import json,re,subprocess
from verify_htc import ROOT,CC,LINUX,sha
EXPECTED='572535ac04d9dda668501b0233746d0e5c143195d85c02ed3be2532a37c0e8d7'
def main():
 raw=(ROOT/'runs/reference/ieee80211.h').read_bytes();assert sha(raw)==EXPECTED
 text=raw.decode();out=ROOT/'runs/beacon';out.mkdir(parents=True,exist_ok=True)
 oracle='#include <stdint.h>\n#define ETH_ALEN 6\n#define __packed __attribute__((packed))\ntypedef uint8_t u8;typedef uint16_t __le16;typedef uint64_t __le64;\n'
 for name in ('IEEE80211_STYPE_BEACON','IEEE80211_STYPE_PROBE_RESP','WLAN_CAPABILITY_PRIVACY'):
  m=re.search(r'^#define '+name+r'\b[^\n]+',text,re.M);assert m,name;oracle+=m.group()+'\n'
 for name in ('WLAN_EID_SSID','WLAN_EID_DS_PARAMS','WLAN_EID_RSN','WLAN_EID_HT_OPERATION'):
  m=re.search(r'\b'+name+r'\s*=\s*([0-9]+)',text);assert m,name;oracle+='#define '+name+' '+m[1]+'\n'
 start=text.index('struct ieee80211_mgmt {');common_end=text.index('\tunion {',start)
 oracle+=text[start:common_end]+' union {\n'
 for name in ('beacon','probe_resp'):
  end=text.index('} __packed '+name+';',common_end)+len('} __packed '+name+';')
  begin=text.rfind('\t\tstruct {',common_end,end);assert begin>common_end;oracle+=text[begin:end]+'\n'
 oracle+=' } u;\n} __packed;\n';(out/'upstream-beacon.h').write_text(oracle)
 names=('beacon_info.c','beacon_info.h','beacon_info_test.c','verify_beacon.py','verify_htc.py')
 inputs={name:sha((ROOT/name).read_bytes()) for name in names}
 subprocess.run([str(CC),'-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all','-I'+str(ROOT),'-I'+str(out),str(ROOT/'beacon_info.c'),str(ROOT/'beacon_info_test.c'),'-o',str(out/'beacon-test')],check=True)
 r=subprocess.run([str(out/'beacon-test')],capture_output=True,text=True,timeout=30);(out/'host.log').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr
 subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-I'+str(ROOT),'-c',str(ROOT/'beacon_info.c'),'-o',str(out/'beacon_info.obj')],check=True)
 assert inputs=={name:sha((ROOT/name).read_bytes()) for name in names}
 report={'status':'BEACON-PROBE-BOUNDED-INFO-HOST-COFF-PASS','build_host':'yukabox','source_sha256':inputs,'reference':{'linux_commit':LINUX,'ieee80211_h_sha256':EXPECTED,'oracle_sha256':sha(oracle.encode())},'host_log_sha256':sha((out/'host.log').read_bytes()),'opaque_rsn_only':True,'physical_verified':False,'native_integrated':False,'radio_scanned':False,'security_validated':False,'wifi_connected':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(r.stdout.strip());print(report['status'])
if __name__=='__main__':main()
