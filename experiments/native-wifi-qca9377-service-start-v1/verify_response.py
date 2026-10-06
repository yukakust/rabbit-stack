"""Pinned struct oracle and actual Dell response; Yukabox ASAN/COFF only."""
import hashlib,json,re,subprocess
from pathlib import Path
import operating_build as build
from verify_port import CC
ROOT=build.ROOT
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 out=ROOT/'runs/response-host';out.mkdir(parents=True,exist_ok=True);build.sources(out)
 ref=Path('/home/yuka/rabbit-world/native-wifi-qca9377-v1/vendor/linux/drivers/net/wireless/ath/ath10k/htc.h');raw=ref.read_bytes()
 assert sha(raw)=='e2dc499ce2865b16456d436dc55db38da93282778d8cc86d03ed07a3c37c1963'
 names=('ath10k_htc_hdr','ath10k_ath10k_htc_msg_hdr','ath10k_htc_conn_svc_response')
 header='#include <stdint.h>\ntypedef uint8_t u8;typedef uint16_t __le16;typedef uint32_t __le32;\n#define __packed __attribute__((packed))\n#define __aligned(n) __attribute__((aligned(n)))\n'
 for name in names:
  match=re.search(r'struct '+name+r' \{.*?^\}[^;]*;',raw.decode(),re.S|re.M);assert match;header+=match.group()+'\n'
 (out/'upstream-wire.h').write_text(header)
 exe=out/'response-test';files=['htc_wire.c','htc_session.c','htc_credit.c','htc_control.c']
 subprocess.run([str(CC),'-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all','-I'+str(out),str(ROOT/'connect_response_test.c'),*[str(out/n) for n in files],'-o',str(exe)],check=True)
 r=subprocess.run([str(exe)],capture_output=True,text=True,timeout=60);(out/'host.log').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr
 subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-I'+str(out),'-c',str(out/'htc_wire.c'),'-o',str(out/'htc_wire.obj')],check=True)
 report={'status':'ACTUAL-CONNECT-RESPONSE-PINNED-CORE-ASAN-COFF-PASS','checks':5186,'linux_commit':'6b5a2b7d9bc156e505f09e698d85d6a1547c1206','reference_sha256':sha(raw),'oracle_sha256':sha(header.encode()),'host_log_sha256':sha((out/'host.log').read_bytes()),'build_host':'yukabox','physical_verified':False,'source_sha256':{str(p.relative_to(ROOT.parent.parent)):sha(p.read_bytes()) for p in [ROOT/'htc_wire.c',ROOT/'connect_response_test.c',ROOT/'verify_response.py',ROOT/'operating_build.py']}}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(r.stdout.strip())
if __name__=='__main__':main()
