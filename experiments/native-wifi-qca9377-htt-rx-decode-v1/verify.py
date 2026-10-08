"""Linux/Yukabox isolated pure component proof; no device/state/key APIs."""
from pathlib import Path
import os,sys,subprocess,json,hashlib
R=Path(__file__).resolve().parent
CC=Path('/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert sys.platform.startswith('linux'),'C/ASAN/COFF only on Yukabox'
 temp=Path('/home/yuka/rabbit-world/parallel-htt-rx-decode-v1/tmp');temp.mkdir(parents=True,exist_ok=True);env=os.environ.copy();env['TMPDIR']=str(temp)
 for n in ('CPATH','C_INCLUDE_PATH','CPLUS_INCLUDE_PATH','SDKROOT'):env.pop(n,None)
 references=json.loads((R/'references.json').read_text())
 for n,h in references['files'].items():assert sha(R/'references'/n)==h
 source={str(p.relative_to(R)):sha(p) for p in [*R.glob('*.py'),*R.glob('*.c'),*R.glob('*.h'),R/'references.json',R/'README.md',*list((R/'references').iterdir())] if p.is_file()};out=R/'runs';out.mkdir(exist_ok=True)
 subprocess.run([sys.executable,str(R/'prepare_oracle.py')],check=True,env=env)
 subprocess.run([str(CC),'-std=gnu11','-Wall','-Wextra','-Werror',str(out/'oracle.c'),'-o',str(out/'oracle')],check=True,env=env)
 oracle=subprocess.run([str(out/'oracle')],capture_output=True,text=True,check=True).stdout;values={k:int(v) for k,v in (x.split('=') for x in oracle.splitlines())};assert values['desc_size']==values['payload']==300 and values['attention']==4 and values['frag']==8 and values['msdu_start']==24 and values['msdu_end']==40 and values['inord_hdr']==7 and values['paddr32']==8
 inputs={n:sha(R/n) for n in ('test.c','rx_decode.c','rx_decode.h','runs/oracle.c','runs/oracle_types.h')}
 subprocess.run([str(CC),'-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-omit-frame-pointer',str(R/'test.c'),str(R/'rx_decode.c'),'-o',str(out/'test')],check=True,env=env)
 test=subprocess.run([str(out/'test')],capture_output=True,text=True,check=True,env={**env,'ASAN_OPTIONS':'detect_leaks=1','UBSAN_OPTIONS':'halt_on_error=1'});assert 'PASS 705' in test.stdout
 subprocess.run([str(CC),'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-c',str(R/'rx_decode.c'),'-o',str(out/'rx_decode.obj')],check=True,env=env)
 assert inputs=={n:sha(R/n) for n in inputs} and source=={n:sha(R/n) for n in source}
 log=oracle+test.stdout+test.stderr;(out/'host.log').write_text(log)
 report={'status':'PURE-HTT3.56-TLV-RX-ABI-OWNERSHIP-FRAME-ASAN-COFF-PASS','build_host':'yukabox','cases':705,'source_sha256':source,'compiled_inputs_sha256':inputs,'primary_references':references,'oracle':values,'compiler_sha256':sha(CC),'host_log_sha256':sha(out/'host.log'),'coff_object_sha256':sha(out/'rx_decode.obj'),'coff_linked':False,'native_integration':False,'physical_verified':False,'device_operations':0,'private_key_accesses':0,'provisional_generation':None,'service65_physical_proof':False,'fragment_reorder_fifo_integration':False,'unknown_raw_preserved':True};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],report['cases'],sha(out/'report.json'))
if __name__=='__main__':main()
