#!/usr/bin/env python3
"""Pinned Linux memory-count oracle, ASAN/UBSAN and native COFF; no device."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SESSION=ROOT.parent/'native-wifi-qca9377-session-v1'
sys.path.insert(0,str(SESSION));from verify_htc import CC
sha=lambda b:hashlib.sha256(b).hexdigest()
LINUX='6b5a2b7d9bc156e505f09e698d85d6a1547c1206'
C=Path('/home/yuka/rabbit-world/wifi-bt42-v1/reference-next/wmi.c')
H=Path('/home/yuka/rabbit-world/native-wifi-qca9377-v1/vendor/linux/drivers/net/wireless/ath/ath10k/wmi.h')
C_SHA='68a4fedc3d0cd815c209dda9c0eb3aa3869bd3d35847c633e0c458ba53c320f4'
H_SHA='fff0e5749d68c461ed08e69060321942d68bdb050954c39b2a57c0045457106c'
def main():
 out=ROOT/'runs/memory';out.mkdir(parents=True,exist_ok=True)
 raw=C.read_bytes();header=H.read_bytes();assert sha(raw)==C_SHA and sha(header)==H_SHA
 text=raw.decode();start=text.index('\t\tif (num_unit_info & NUM_UNITS_IS_NUM_ACTIVE_PEERS)');end=text.index('\n\n\t\tfound = false;',start);branch=text[start:end]
 defines=[]
 for name in ('NUM_UNITS_IS_NUM_VDEVS','NUM_UNITS_IS_NUM_PEERS','NUM_UNITS_IS_NUM_ACTIVE_PEERS'):
  match=re.search(r'^#define '+name+r'\s+BIT\([0-9]+\)',header.decode(),re.M);assert match;defines.append(match.group())
 # Exact upstream expression; differential inputs remain in its safe range.
 allocation=text[text.index('static int ath10k_wmi_alloc_chunk('):text.index('static int ath10k_wmi_alloc_host_mem(')]
 expression=re.search(r'pool_size = num_units \* round_up\(unit_len, 4\);',allocation);assert expression
 oracle='#include <stdint.h>\n#define BIT(n) (1u<<(n))\n'+'\n'.join(defines)+'\nstruct oracle_resources {uint32_t max_num_vdevs,max_num_peers,num_active_peers;};\nstatic uint32_t oracle_units(struct oracle_resources*ar,uint32_t num_unit_info,uint32_t num_units){\n'+branch+'\nreturn num_units;}\n#define round_up(x,n) (((x)+(n)-1)&~((n)-1))\nstatic uint32_t oracle_bytes(uint32_t num_units,uint32_t unit_len){uint32_t pool_size;'+expression.group()+'return pool_size;}\n'
 (out/'upstream-memory-oracle.h').write_text(oracle)
 names=('memory_plan.c','memory_plan.h','memory_plan_test.c','verify_memory.py');inputs={n:sha((ROOT/n).read_bytes()) for n in names}
 deps={str(p.relative_to(ROOT.parent.parent)):sha(p.read_bytes()) for p in (SESSION/'wmi_boot_info.h',SESSION/'wmi_scan.h',SESSION/'verify_htc.py')}
 subprocess.run([str(CC),'-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all','-I'+str(ROOT),'-I'+str(SESSION),'-I'+str(out),str(ROOT/'memory_plan.c'),str(ROOT/'memory_plan_test.c'),'-o',str(out/'memory-test')],check=True)
 r=subprocess.run([str(out/'memory-test')],capture_output=True,text=True,timeout=60);(out/'host.log').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr
 cases=int(re.search(r'PLAN (\d+) pinned-source',r.stdout).group(1));assert cases>4600000
 subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-I'+str(ROOT),'-I'+str(SESSION),'-c',str(ROOT/'memory_plan.c'),'-o',str(out/'memory_plan.obj')],check=True)
 assert inputs=={n:sha((ROOT/n).read_bytes()) for n in names}
 assert deps=={n:sha((ROOT.parent.parent/n).read_bytes()) for n in deps}
 report={'status':'WMI-MEMORY-PLAN-PINNED-ORACLE-ASAN-COFF-PASS','build_host':'yukabox','cases':cases,'source_sha256':inputs,'dependency_sha256':deps,'reference':{'linux_commit':LINUX,'wmi_c_sha256':C_SHA,'wmi_h_sha256':H_SHA,'oracle_sha256':sha(oracle.encode()),'source_url':'https://kernel.googlesource.com/pub/scm/linux/kernel/git/torvalds/linux/+/'+LINUX+'/drivers/net/wireless/ath/ath10k/wmi.c'},'host_log_sha256':sha((out/'host.log').read_bytes()),'allocation_performed':False,'physical_address_checked':False,'native_integrated':False,'physical_verified':False,'wifi_connected':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(r.stdout.strip());print(report['status'])
if __name__=='__main__':main()
