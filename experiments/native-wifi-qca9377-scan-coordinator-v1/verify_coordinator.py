"""Actual TX/RX/CE bookkeeping joined under explicit lower-backend model."""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent;E=ROOT.parent
NATIVE=E/'native-wifi-qca9377-persistent-tx-v1/runs/native-host'
CC=Path('/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang')
MODULES={'tx':'native-wifi-qca9377-persistent-tx-v1','rx':'native-wifi-qca9377-persistent-rx-v1','lifecycle':'native-wifi-qca9377-persistent-v1','channel_wire':'native-wifi-qca9377-channel-wire-v1','vdev_wire':'native-wifi-qca9377-vdev-wire-v1','station_scan':'native-wifi-qca9377-station-scan-v1','dispatch':'native-wifi-qca9377-station-dispatch-v1','scan_stop':'native-wifi-qca9377-scan-stop-v1','owned_stop':'native-wifi-qca9377-owned-scan-stop-v1','beacon_rx':'native-wifi-qca9377-beacon-rx-v1'}
SESSION=E/'native-wifi-qca9377-session-v1';ABI=E/'x86-64-uefi-wireless-supervisor-v1';ABI_OLD=E/'x86-64-uefi-runtime-supervisor-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'runs/model';out.mkdir(parents=True,exist_ok=True)
 c=(ROOT/'coordinator.c').read_text()
 for forbidden in ['qca_htc_credit_','qca_station_scan_prepare','qca_station_scan_post','qca_scan_stop_prepare','qca_scan_stop_post','qca_owned_scan_stop_prepare','qca_owned_scan_stop_post','qca_station_scan_receive','qca_scan_stop_receive']:
  assert forbidden not in c,forbidden
 sources=[ROOT/'coordinator.c',*[E/d/(n+'.c') for n,d in MODULES.items()],NATIVE/'wmi_boot_info.c',NATIVE/'ce_ring.c',*[SESSION/(n+'.c') for n in ['htc_wire','htc_credit','wmi_scan','beacon_info']]]
 inputs=sources+[ROOT/'coordinator.h',ROOT/'coordinator_test.c',ROOT/'verify_coordinator.py',ROOT/'README.md',ABI/'scene_abi.h',ABI_OLD/'abi.h']+list(NATIVE.glob('*.h'))+[E/d/(n+'.h') for n,d in MODULES.items()]+[SESSION/(n+'.h') for n in ['htc_wire','htc_credit','wmi_scan','beacon_info']]
 hashes={str(p.relative_to(E)):sha(p) for p in inputs}
 flags=['-Wall','-Wextra','-Werror',*['-I'+str(p) for p in [ROOT,NATIVE,ABI,ABI_OLD,*[E/d for d in MODULES.values()],SESSION]]]
 subprocess.run([str(CC),'-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all',*flags,*map(str,sources),str(ROOT/'coordinator_test.c'),'-o',str(out/'test')],check=True)
 r=subprocess.run([str(out/'test')],capture_output=True,text=True,timeout=60);(out/'host.log').write_text(r.stdout+r.stderr);assert not r.returncode,r.stderr
 subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os',*flags,'-c',str(ROOT/'coordinator.c'),'-o',str(out/'coordinator.obj')],check=True)
 assert all(sha(E/n)==h for n,h in hashes.items())
 report={'status':'SCAN-COORDINATOR-ACTUAL-TX-RX-BOOKKEEPING-MODEL-ASAN-COFF-PASS','scenarios':15,'checks':int(re.search(r'checks=(\d+)',r.stdout)[1]),'source_sha256':hashes,'host_log_sha256':sha(out/'host.log'),'build_host':'yukabox','actual_tx_rx_ce_bookkeeping':True,'lower_hardware_operating_backend_mocked':True,'full_native_entrypoints':False,'physical_verified':False,'native_integrated':False,'rf_permission_admitted':False,'candidate_generated':False,'default_policy_authority_created':False,'healthy_model_release_count':14,'epoch_mismatch_model_retains':14}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(r.stdout.strip());print(report['status'])
if __name__=='__main__':main()
