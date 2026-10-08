#!/usr/bin/env python3
"""Mac host compile/preflight ONLY. Actual state/admission/Bluetooth route is ROOT's."""
import argparse,hashlib,json,os,platform,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent.parent
BASE=ROOT.parent/'native-wifi-qca9377-v1';NATIVE=ROOT.parent/'x86-64-uefi-runtime-supervisor-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def compile_host(test=False):
 if platform.system()!='Darwin':raise ValueError('Mac host Objective-C tool only')
 out=ROOT/'runs/control';out.mkdir(parents=True,exist_ok=True);exe=out/('host-test' if test else 'sender')
 env=os.environ.copy()
 for n in ('CPATH','C_INCLUDE_PATH','CPLUS_INCLUDE_PATH','SDKROOT','RABBIT_ASSET_PEER'):env.pop(n,None)
 plist=ROOT.parent/'x86-64-uefi-connected-supervisor-v1/FileSender-Info.plist'
 source=ROOT/('host_test.m' if test else 'sender.m')
 inputs={str(p.relative_to(REPO)):sha(p) for p in (ROOT/'sender.m',ROOT/'sequence.h',source,BASE/'firmware_sender_core.c',BASE/'firmware_sender_core.h',NATIVE/'sha256.c',NATIVE/'sha256.h',plist)}
 subprocess.run(['xcrun','--sdk','macosx','clang','-x','objective-c','-fobjc-arc','-Wall','-Wextra','-Werror','-I'+str(BASE),'-I'+str(NATIVE),'-I'+str(ROOT),str(source),str(BASE/'firmware_sender_core.c'),str(NATIVE/'sha256.c'),'-framework','Foundation','-framework','CoreBluetooth','-Wl,-sectcreate,__TEXT,__info_plist,'+str(plist),'-o',str(exe)],env=env,check=True,timeout=60)
 assert inputs=={n:sha(REPO/n) for n in inputs}
 return exe,inputs

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--preflight',action='store_true');p.add_argument('--packet',type=Path);p.add_argument('--checkpoint',type=Path);p.add_argument('--boot-log','--prefix-log',dest='boot_log',type=Path);a=p.parse_args()
 exe,inputs=compile_host();out=ROOT/'runs/control';report={'status':'HOST-OBJC-OBSERVER-COMPILED-NO-MANAGER','source_sha256':inputs,'executable_path':str(exe),'executable_sha256':sha(exe),'bluetooth_manager_started':False,'private_key_loads':0,'signatures_created':0,'native_code_modified':False,'production_admission':'ROOT separate reviewed route required'}
 if a.preflight:
  if not a.packet or not a.checkpoint:p.error('preflight requires explicit packet/checkpoint')
  checkpoint=a.checkpoint.resolve()
  if not checkpoint.is_relative_to((ROOT/'runs').resolve()) or not checkpoint.parent.is_dir() or checkpoint==a.packet.resolve():raise ValueError('offline checkpoint must be separate and stay in own runs')
  args=[str(exe),str(a.packet.resolve()),str(checkpoint),'--preflight']
  if a.boot_log:
   log=a.boot_log.resolve()
   if not log.is_relative_to((ROOT/'runs').resolve()) or not log.parent.is_dir() or log in (checkpoint,a.packet.resolve()):raise ValueError('separate own runs diagnostic path')
   args+=['--boot-log',str(log)]
  subprocess.run(args,check=True,timeout=10);report['status']='HOST-OBJC-PACKET-LAYOUT-CHECKPOINT-PREFLIGHT-NO-MANAGER';report['public_packet_signature_verified']=False
 (out/'compile-report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
if __name__=='__main__':main()
