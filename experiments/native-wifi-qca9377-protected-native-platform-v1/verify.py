"""Run only on Yukabox/Linux, never compile native C on Mac."""
from pathlib import Path
import argparse,hashlib,json,os,platform,re,subprocess
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert platform.system()=='Linux','native compilation is Yukabox-only'
 p=argparse.ArgumentParser();p.add_argument('--clang',required=True);p.add_argument('--lld',required=True);a=p.parse_args()
 out=ROOT/'runs';out.mkdir(exist_ok=True);env=dict(os.environ,TMPDIR=str(out));logs=[]
 assert sha(ROOT/'oracle-boot.h')=='711f753a5655959140c92879a6120535ca1c4368a4a4173ce3487a6f31661dc5'
 def run(args):
  r=subprocess.run(args,cwd=ROOT,env=env,text=True,capture_output=True);logs.extend([json.dumps(args),r.stdout,r.stderr]);assert r.returncode==0,r.stderr;return r.stdout
 run([a.clang,'-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all','platform.c','rng_port.c','test.c','-o',str(out/'test')]);result=run([str(out/'test')]);assert 'PASS 4769' in result and 'GetRNG calls=0' in result
 for name in ('platform','rng_port','link_probe'):
  run([a.clang,'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-c',name+'.c','-o',str(out/(name+'.obj'))])
 run([a.lld,'-flavor','link','/subsystem:efi_application','/entry:link_entry','/nodefaultlib',*[ '/include:'+n for n in ('protected_arena_open','protected_arena_borrow','protected_arena_return','protected_arena_close','protected_rng_inventory')],'/out:'+str(out/'link-only.efi'),*[str(out/(n+'.obj')) for n in ('platform','rng_port','link_probe')]])
 link=run(['objdump','-p',str(out/'link-only.efi')]);assert 'DLL Name' not in link;assert re.search(r'SizeOfImage\s+00003000',link)
 (out/'complete.log').write_text('\n'.join(logs))
 report={'status':'PROTECTED-NATIVE-PLATFORM-ABI-POOL-INVENTORY-ASAN-COFF-LINK-PASS','build_host':'yukabox','checks':4769,'GetRNG_calls':0,'source_sha256':{n:sha(ROOT/n) for n in ('platform.c','platform.h','rng_port.c','rng_port.h','test.c','link_probe.c','verify.py','oracle-boot.h')},'objects_sha256':{n:sha(out/(n+'.obj')) for n in ('platform','rng_port','link_probe')},'test_executable_sha256':sha(out/'test'),'link_only_efi_sha256':sha(out/'link-only.efi'),'link_only_mapped_bytes':12288,'imports':[],'complete_log_sha256':sha(out/'complete.log'),'linked_into_native63':False,'native63_fit_verified':False,'physical_provider_approved':False,'physical_calls':0,'signing_admitted':False,'TLS_ready':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(result.strip())
if __name__=='__main__':main()
