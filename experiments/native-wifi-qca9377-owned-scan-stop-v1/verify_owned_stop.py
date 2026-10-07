"""Owned-event API host tests. No RX/MMIO hardware emulation claim here."""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent;STA=ROOT.parent/'native-wifi-qca9377-station-scan-v1';DISPATCH=ROOT.parent/'native-wifi-qca9377-station-dispatch-v1';STOP=ROOT.parent/'native-wifi-qca9377-scan-stop-v1';SESSION=ROOT.parent/'native-wifi-qca9377-session-v1';VDEV=ROOT.parent/'native-wifi-qca9377-vdev-wire-v1';RX=ROOT.parent/'native-wifi-qca9377-persistent-rx-v1'
CC=Path('/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang')
REF=Path('/home/yuka/rabbit-world/wmi-init-next/reference')
PIN={'wmi-tlv.h':'16c6b984177dd8c0f80dbc4df52597a6def435d8892fb55381091bdb88a258c9','wmi.h':'fff0e5749d68c461ed08e69060321942d68bdb050954c39b2a57c0045457106c'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert all(sha(REF/n)==h for n,h in PIN.items())
 assert sha(RX/'rx.h')=='374b7a2f5d8743b1e4f869b551edd22d6df29dae433e4cca28d4ed3c00ebe883'
 assert sha(RX/'rx.c')=='70a6c54ede04eaa10ce982b2a9bba799c5d32bdd66ee56db17a94c57b6619c48'
 out=ROOT/'runs/host';out.mkdir(parents=True,exist_ok=True)
 # Extract exact owned type, avoiding unrelated native DMA dependencies. This
 # tests the pure dispatcher ABI; whole native RX integration is separate.
 event=re.search(r'typedef struct \{\s*uint32_t completion,event;.*?\} QcaRxEvent;', (RX/'rx.h').read_text(),re.S)[0]
 (out/'rx.h').write_text('#include <stdint.h>\n'+event+'\n_Static_assert(sizeof(QcaRxEvent)==2052,"owned ABI");\n')
 oracle='#include <stdint.h>\n#define __le32 uint32_t\n#define __packed __attribute__((packed))\n#define BIT(n) (1u<<(n))\n#define WMI_TLV_CMD(g) (((g)<<12)|1)\n#define WMI_TLV_EV(g) (((g)<<12)|1)\n'
 for fn,kind,names in [('wmi-tlv.h','enum',['wmi_tlv_grp_id','wmi_tlv_cmd_id','wmi_tlv_event_id','wmi_tlv_tag']),('wmi.h','enum',['wmi_scan_event_type','wmi_scan_completion_reason']),('wmi.h','struct',['wmi_scan_event'])]:
  for name in names:oracle+=re.search(kind+' '+name+r'\s*\{.*?^\}[^;]*;',(REF/fn).read_text(),re.S|re.M)[0]+'\n'
 (out/'oracle.h').write_text(oracle)
 assert 'qca_htc_credit_receive' not in (ROOT/'owned_stop.c').read_text()
 assert 'qca_station_scan_receive' not in (ROOT/'owned_stop.c').read_text()
 assert 'qca_scan_stop_receive' not in (ROOT/'owned_stop.c').read_text()
 sources=[ROOT/'owned_stop.c',DISPATCH/'dispatch.c',STOP/'scan_stop.c',STA/'station_scan.c',SESSION/'htc_wire.c',SESSION/'htc_credit.c',SESSION/'wmi_scan.c',SESSION/'wmi_boot_info.c',VDEV/'vdev_wire.c']
 inputs=sources+[ROOT/'owned_stop.h',ROOT/'owned_stop_test.c',ROOT/'verify_owned_stop.py',DISPATCH/'dispatch.h',STOP/'scan_stop.h',ROOT/'README.md',STA/'station_scan.h',RX/'rx.h',RX/'rx.c',VDEV/'vdev_wire.h']+list(SESSION.glob('*.h'));hashes={str(p.relative_to(ROOT.parent)):sha(p) for p in inputs}
 flags=['-Wall','-Wextra','-Werror',*['-I'+str(p) for p in [ROOT,out,DISPATCH,STOP,STA,SESSION,VDEV]]]
 subprocess.run([str(CC),'-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all',*flags,*map(str,sources),str(ROOT/'owned_stop_test.c'),'-o',str(out/'test')],check=True)
 r=subprocess.run([str(out/'test')],capture_output=True,text=True,timeout=60);(out/'host.log').write_text(r.stdout+r.stderr);assert not r.returncode,r.stderr
 subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os',*flags,'-c',str(ROOT/'owned_stop.c'),'-o',str(out/'owned_stop.obj')],check=True)
 assert all(sha(ROOT.parent/n)==h for n,h in hashes.items())
 report={'status':'OWNED-SCAN-STOP-ASAN-COFF-PASS','checks':int(re.search(r'checks=(\d+)',r.stdout)[1]),'build_host':'yukabox','source_sha256':hashes,'linux_commit':'6b5a2b7d9bc156e505f09e698d85d6a1547c1206','reference_sha256':PIN,'derived_rx_abi_sha256':sha(out/'rx.h'),'oracle_sha256':sha(out/'oracle.h'),'host_log_sha256':sha(out/'host.log'),'credits_applied_only_by_rx_pump':True,'unposted_cancel_only_on_real_natural_terminal':True,'bounded_credit_starvation':True,'rollback_retained_fault':True,'completion_id_gaps_supported':True,'native_integrated':False,'physical_verified':False,'scan_sent':False,'wifi_connected':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(r.stdout.strip())
if __name__=='__main__':main()
