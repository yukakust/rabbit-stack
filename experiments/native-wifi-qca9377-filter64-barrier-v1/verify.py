from pathlib import Path
import sys,os,tempfile,subprocess,json,hashlib
ROOT=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 if not sys.platform.startswith('linux'):raise SystemExit('Native C Yukabox only')
 out=ROOT/'runs/proof';out.mkdir(parents=True,exist_ok=True);tmp=out/'tmp';tmp.mkdir(exist_ok=True);os.environ['TMPDIR']=str(tmp);tempfile.tempdir=str(tmp);dep=ROOT/'dependencies';cc=Path('/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang');sources=[ROOT/'filter_barrier.c',*[dep/n for n in ['htc_wire.c','htc_credit.c','wmi_boot_info.c','wmi_scan.c']]];log=''
 for name in ['filter_test','timing_test']:
  cmd=[str(cc),'-I'+str(ROOT),'-I'+str(dep),'-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all',str(ROOT/(name+'.c')),*map(str,sources),'-o',str(out/name)];subprocess.run(cmd,check=True);run=subprocess.run([str(out/name)],capture_output=True,text=True,check=True);log+=run.stdout+run.stderr
 (out/'host.log').write_text(log)
 for p in sources:subprocess.run([str(cc),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-I'+str(ROOT),'-I'+str(dep),'-c',str(p),'-o',str(out/(p.stem+'.obj'))],check=True)
 report={'status':'FILTER64-STAGE3-ECHO3-OVERALL12-UNCHANGED-TX2-ASAN-COFF-PASS','source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in ROOT.rglob('*') if p.is_file() and 'runs' not in p.parts and p.suffix in ['.c','.h','.py']},'host_log_sha256':sha(out/'host.log'),'coff_objects_sha256':{p.name:sha(p) for p in out.glob('*.obj')},'physical':False,'device_operations':0};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(log,report['status'])
if __name__=='__main__':main()
