from pathlib import Path
import sys,os,tempfile,subprocess,json,hashlib
ROOT=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 if not sys.platform.startswith('linux'):raise SystemExit('Native C only Yukabox')
 out=ROOT/'runs/proof';out.mkdir(parents=True,exist_ok=True);tmp=out/'tmp';tmp.mkdir(exist_ok=True);os.environ['TMPDIR']=str(tmp);tempfile.tempdir=str(tmp)
 cc=Path('/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang');dep=ROOT/'copied';files=[ROOT/'timing_test.c',dep/'filter_barrier.c',dep/'htc_wire.c',dep/'htc_credit.c',dep/'wmi_boot_info.c',dep/'wmi_scan.c'];cmd=[str(cc),'-I'+str(dep),'-Wall','-Wextra','-Werror','-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all',*map(str,files),'-o',str(out/'test')];subprocess.run(cmd,check=True);run=subprocess.run([str(out/'test')],capture_output=True,text=True,check=True);(out/'host.log').write_text(run.stdout+run.stderr)
 coff=[str(cc),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-I'+str(dep),'-c',str(dep/'filter_barrier.c'),'-o',str(out/'filter_barrier.obj')];subprocess.run(coff,check=True)
 report={'status':'FROZEN63-TIMING-REVIEW-REPLAY-ASAN-COFF-PASS','synthetic_timing_only':True,'physical_echo_bytes_reused':True,'physical_arrival_timestamp_unknown':True,'scenarios':3,'copied_source_sha256':{p.name:sha(p) for p in dep.iterdir()},'test_source_sha256':sha(ROOT/'timing_test.c'),'compile_command':cmd,'coff_command':coff,'coff_sha256':sha(out/'filter_barrier.obj'),'host_log_sha256':sha(out/'host.log'),'production64_implemented':False,'device_operations':0,'physical_admission':False};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
if __name__=='__main__':main()
