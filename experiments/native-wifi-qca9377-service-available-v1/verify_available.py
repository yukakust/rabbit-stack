"""Hash-pinned WMI enum oracle and captured CE2 payload; Yukabox only."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;SESSION=ROOT.parent/'native-wifi-qca9377-session-v1'
sys.path.insert(0,str(SESSION));from verify_htc import CC
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 out=ROOT/'runs/available';out.mkdir(parents=True,exist_ok=True);ref=Path('/home/yuka/rabbit-world/wmi-init-next/reference')
 raw=(ref/'wmi-tlv.h').read_bytes();code=(ref/'wmi-tlv.c').read_bytes()
 assert sha(raw)=='16c6b984177dd8c0f80dbc4df52597a6def435d8892fb55381091bdb88a258c9'
 assert sha(code)=='02309cad56513a1ef0975c9d73e568e343c874d35124f39111ddd26d8a75c5bb'
 header='#define WMI_TLV_EV(grp) (((grp)<<12)|1)\n'
 for name in ('wmi_tlv_grp_id','wmi_tlv_event_id','wmi_tlv_tag'):
  match=re.search(r'enum '+name+r' \{.*?^\};',raw.decode(),re.S|re.M);assert match;header+=match.group()+'\n'
 (out/'upstream-available.h').write_text(header)
 inputs={str(p.relative_to(ROOT.parent.parent)):sha(p.read_bytes()) for p in [*ROOT.glob('*.c'),*ROOT.glob('*.h'),*ROOT.glob('*.py'),SESSION/'verify_htc.py']}
 exe=out/'available-test';subprocess.run([str(CC),'-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all','-I'+str(out),str(ROOT/'available.c'),str(ROOT/'available_test.c'),'-o',str(exe)],check=True)
 r=subprocess.run([str(exe)],capture_output=True,text=True,timeout=60);(out/'host.log').write_text(r.stdout+r.stderr);assert not r.returncode,r.stderr
 subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-c',str(ROOT/'available.c'),'-o',str(out/'available.obj')],check=True)
 assert inputs=={n:sha((ROOT.parent.parent/n).read_bytes()) for n in inputs}
 report={'status':'ACTUAL-SERVICE-AVAILABLE-PINNED-ENUM-ASAN-COFF-PASS','checks':7198,'build_host':'yukabox','source_sha256':inputs,'reference':{'linux_commit':'6b5a2b7d9bc156e505f09e698d85d6a1547c1206','wmi_tlv_h':sha(raw),'wmi_tlv_c':sha(code),'oracle_sha256':sha(header.encode())},'host_log_sha256':sha((out/'host.log').read_bytes()),'native_integrated':False,'physical_verified':False,'wifi_connected':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(r.stdout.strip())
if __name__=='__main__':main()
