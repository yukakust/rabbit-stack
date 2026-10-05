#!/usr/bin/env python3
"""Pinned ath10k credit cost; all native compilation on Yukabox, no device."""
import hashlib,json,re,subprocess
from pathlib import Path
from verify_htc import CC,LINUX
ROOT=Path(__file__).resolve().parent
REF=Path('/home/yuka/rabbit-world/wifi-bt42-v1/reference-next/htc.c')
REF_SHA='ba19a833a986bcdc097550aff81c620501243db3792db248da34b39c145b9629'
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 out=ROOT/'runs/credit';out.mkdir(parents=True,exist_ok=True)
 raw=REF.read_bytes();assert sha(raw)==REF_SHA
 text=raw.decode();start=text.index('static int ath10k_htc_consume_credit(');end=text.index('static void ath10k_htc_release_credit(',start)
 expression=re.search(r'credits = DIV_ROUND_UP\(len, ep->tx_credit_size\);',text[start:end]);assert expression
 oracle='#define DIV_ROUND_UP(n,d) (((n)+(d)-1)/(d))\nstruct ep_credit {unsigned tx_credit_size;};\nstatic unsigned oracle_credit_cost(unsigned len,unsigned size){struct ep_credit storage={size};struct ep_credit*ep=&storage;unsigned credits;'+expression.group()+'return credits;}\n'
 (out/'upstream-credit.h').write_text(oracle)
 names=('htc_credit.c','htc_credit.h','htc_credit_test.c','verify_credit.py','htc_wire.h','verify_htc.py')
 inputs={n:sha((ROOT/n).read_bytes()) for n in names}
 subprocess.run([str(CC),'-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all','-I'+str(ROOT),'-I'+str(out),str(ROOT/'htc_credit.c'),str(ROOT/'htc_credit_test.c'),'-o',str(out/'credit-test')],check=True)
 result=subprocess.run([str(out/'credit-test')],capture_output=True,text=True,timeout=120)
 (out/'host.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
 cases=int(re.search(r'CREDIT (\d+)',result.stdout).group(1));assert cases>90000000
 subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-I'+str(ROOT),'-c',str(ROOT/'htc_credit.c'),'-o',str(out/'htc_credit.obj')],check=True)
 assert inputs=={n:sha((ROOT/n).read_bytes()) for n in inputs}
 report={'status':'HTC-CREDIT-HOST-ASAN-COFF-PASS','build_host':'yukabox','checks':cases,'source_sha256':inputs,'reference':{'linux_commit':LINUX,'htc_c_sha256':REF_SHA,'oracle_sha256':sha(oracle.encode())},'host_log_sha256':sha((out/'host.log').read_bytes()),'native_integrated':False,'physical_verified':False,'wifi_connected':False,'scope':'pure single-owner WMI credit ledger; no DMA submission or RX replay detection'}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(result.stdout.strip());print(report['status'])
if __name__=='__main__':main()
