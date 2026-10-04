#!/usr/bin/env python3
"""No device access: pinned ath10k wire-layout differential, ASAN and COFF."""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
LINUX='6b5a2b7d9bc156e505f09e698d85d6a1547c1206'
VENDOR=Path('/home/yuka/rabbit-world/native-wifi-qca9377-v1/vendor/linux/drivers/net/wireless/ath/ath10k')
EXPECTED='e2dc499ce2865b16456d436dc55db38da93282778d8cc86d03ed07a3c37c1963'
CC=Path('/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang')
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
 out=ROOT/'runs/htc';out.mkdir(parents=True,exist_ok=True)
 raw=(VENDOR/'htc.h').read_bytes();assert sha(raw)==EXPECTED
 names=('ath10k_htc_hdr','ath10k_ath10k_htc_msg_hdr','ath10k_htc_ready','ath10k_htc_ready_extended','ath10k_htc_conn_svc','ath10k_htc_conn_svc_response','ath10k_htc_setup_complete_extended')
 structs=[]
 for name in names:
  match=re.search(r'struct '+name+r' \{.*?^\}[^;]*;',raw.decode(),re.S|re.M);assert match,name
  structs.append(match.group())
 oracle='#include <stdint.h>\ntypedef uint8_t u8;typedef uint16_t __le16;typedef uint32_t __le32;\n#define __packed __attribute__((packed))\n#define __aligned(n) __attribute__((aligned(n)))\n'+'\n'.join(structs)+'\n'
 (out/'upstream-wire.h').write_text(oracle)
 inputs={n:sha((ROOT/n).read_bytes()) for n in ('htc_wire.c','htc_wire.h','htc_wire_test.c','verify_htc.py')}
 subprocess.run([str(CC),'-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-I'+str(ROOT),'-I'+str(out),str(ROOT/'htc_wire.c'),str(ROOT/'htc_wire_test.c'),'-o',str(out/'htc-test')],check=True)
 result=subprocess.run([str(out/'htc-test')],capture_output=True,text=True,timeout=30);(out/'host.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
 subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-I'+str(ROOT),'-c',str(ROOT/'htc_wire.c'),'-o',str(out/'htc_wire.obj')],check=True)
 assert inputs=={n:sha((ROOT/n).read_bytes()) for n in inputs}
 report={'status':'HTC-WIRE-HOST-COFF-PASS','source_sha256':inputs,'reference':{'linux_commit':LINUX,'htc_h_sha256':EXPECTED,'oracle_sha256':sha(oracle.encode())},'host_log_sha256':sha((out/'host.log').read_bytes()),'build_host':'yukabox','physical_verified':False,'native_integrated':False,'scan_supported':False,'wifi_connected':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(result.stdout.strip());print(report['status'])
if __name__=='__main__':main()
