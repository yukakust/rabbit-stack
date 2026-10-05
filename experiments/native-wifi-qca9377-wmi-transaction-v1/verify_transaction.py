"""Pure WMI startup coordination; host tests/COFF only on Yukabox."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SESSION=ROOT.parent/'native-wifi-qca9377-session-v1';MEMORY=ROOT.parent/'native-wifi-qca9377-memory-v1';INIT=ROOT.parent/'native-wifi-qca9377-wmi-init-v1'
sys.path.insert(0,str(SESSION));from verify_htc import CC
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 out=ROOT/'runs/transaction';out.mkdir(parents=True,exist_ok=True)
 files=[ROOT/'init_transaction.c',INIT/'init_wire.c',MEMORY/'memory_plan.c',SESSION/'htc_wire.c',SESSION/'htc_credit.c',SESSION/'wmi_boot_info.c',SESSION/'wmi_scan.c']
 inputs=files+[ROOT/'init_transaction.h',ROOT/'init_transaction_test.c',ROOT/'verify_transaction.py',INIT/'init_wire.h',MEMORY/'memory_plan.h',SESSION/'htc_wire.h',SESSION/'htc_credit.h',SESSION/'htc_session.h',SESSION/'wmi_boot_info.h',SESSION/'wmi_scan.h',SESSION/'verify_htc.py']
 hashes={str(p.relative_to(ROOT.parent.parent)):sha(p.read_bytes()) for p in inputs}
 scan=out/'wmi_scan.c';scan.write_text((SESSION/'wmi_scan.c').read_text().replace('for(unsigned i=0;i<count;i++)put32(p+base+4*i,freq[i]);base+=4*count;','for(unsigned i=0;i<count;i++)put32(p+base+4*i,freq[i]);\n base+=4*count;'))
 files[-1]=scan;inc=['-I'+str(p) for p in (ROOT,INIT,MEMORY,SESSION)]
 exe=out/'transaction-test';subprocess.run([str(CC),'-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all',*inc,*map(str,files),str(ROOT/'init_transaction_test.c'),'-o',str(exe)],check=True)
 r=subprocess.run([str(exe)],capture_output=True,text=True,timeout=60);(out/'host.log').write_text(r.stdout+r.stderr);assert not r.returncode,r.stderr
 subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror',*inc,'-c',str(ROOT/'init_transaction.c'),'-o',str(out/'init_transaction.obj')],check=True)
 assert hashes=={n:sha((ROOT.parent.parent/n).read_bytes()) for n in hashes}
 report={'status':'WMI-INIT-TRANSACTION-ORDER-CREDIT-ASAN-COFF-PASS','build_host':'yukabox','checks':int(re.search(r'checks=(\d+)',r.stdout).group(1)),'source_sha256':hashes,'derived_scan_sha256':sha(scan.read_bytes()),'host_log_sha256':sha((out/'host.log').read_bytes()),'native_integrated':False,'mapping_ownership_verified':False,'resource_vector_approved':False,'physical_verified':False,'wifi_connected':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(r.stdout.strip())
if __name__=='__main__':main()
