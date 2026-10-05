#!/usr/bin/env python3
"""Pinned INIT structs/enum/ABI oracle; all native compilation on Yukabox."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SESSION=ROOT.parent/'native-wifi-qca9377-session-v1';MEMORY=ROOT.parent/'native-wifi-qca9377-memory-v1'
sys.path.insert(0,str(SESSION));from verify_htc import CC,LINUX
sha=lambda b:hashlib.sha256(b).hexdigest()
REF=Path('/home/yuka/rabbit-world/wmi-init-next/reference')
PIN={'wmi-tlv.c':'02309cad56513a1ef0975c9d73e568e343c874d35124f39111ddd26d8a75c5bb','wmi-tlv.h':'16c6b984177dd8c0f80dbc4df52597a6def435d8892fb55381091bdb88a258c9'}
def main():
 out=ROOT/'runs/init';out.mkdir(parents=True,exist_ok=True)
 for n,h in PIN.items():assert sha((REF/n).read_bytes())==h,n
 s=(REF/'wmi-tlv.h').read_text();pieces=[]
 for name in ('wmi_tlv','wmi_tlv_abi_version','wmi_tlv_resource_config','host_memory_chunk_tlv','wmi_tlv_init_cmd'):
  match=re.search(r'struct '+name+r' \{.*?^\}[^;]*;',s,re.S|re.M);assert match,name;pieces.append(match.group())
 cmd=re.search(r'WMI_TLV_INIT_CMDID\s*=\s*0x1,',s);assert cmd;pieces.append('enum oracle_command {'+cmd.group()+'};')
 e=re.search(r'enum wmi_tlv_tag \{.*?^\};',s,re.S|re.M);assert e;pieces.append(e.group())
 lines=(REF/'wmi-tlv.c').read_text().splitlines()
 for i,line in enumerate(lines):
  if not line.startswith('#define WMI_TLV_ABI_'):continue
  macro=[line]
  while macro[-1].endswith(chr(92)):
   i+=1;macro.append(lines[i])
  pieces.append('\n'.join(macro))
 oracle='#include <stdint.h>\ntypedef uint16_t __le16;typedef uint32_t __le32;typedef uint8_t u8;\n#define __packed __attribute__((packed))\n'+'\n'.join(pieces)+'\n'
 (out/'upstream-init.h').write_text(oracle)
 source=[p for p in ROOT.iterdir() if p.is_file() and p.suffix in ('.h','.c','.py')]
 source+=[MEMORY/'memory_plan.c',MEMORY/'memory_plan.h',SESSION/'wmi_boot_info.h',SESSION/'wmi_scan.h',SESSION/'verify_htc.py']
 inputs={str(p.relative_to(ROOT.parent.parent)):sha(p.read_bytes()) for p in source}
 inc=['-I'+str(p) for p in (ROOT,SESSION,MEMORY,out)]
 subprocess.run([str(CC),'-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all',*inc,str(ROOT/'init_wire.c'),str(ROOT/'init_wire_test.c'),str(MEMORY/'memory_plan.c'),'-o',str(out/'init-test')],check=True)
 r=subprocess.run([str(out/'init-test')],capture_output=True,text=True,timeout=60);(out/'host.log').write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr
 subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror',*inc,'-c',str(ROOT/'init_wire.c'),'-o',str(out/'init_wire.obj')],check=True)
 assert inputs=={n:sha((ROOT.parent.parent/n).read_bytes()) for n in inputs}
 report={'status':'WMI-INIT-PINNED-LAYOUT-PLAN-ASAN-COFF-PASS','build_host':'yukabox','source_sha256':inputs,'reference':{'linux_commit':LINUX,'hashes':PIN,'oracle_sha256':sha(oracle.encode())},'host_log_sha256':sha((out/'host.log').read_bytes()),'native_integrated':False,'memory_allocated':False,'mapping_ownership_verified':False,'resource_vector_approved':False,'physical_verified':False,'wifi_connected':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(r.stdout.strip());print(report['status'])
if __name__=='__main__':main()
