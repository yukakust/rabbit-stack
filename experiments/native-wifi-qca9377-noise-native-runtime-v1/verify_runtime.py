import pathlib,subprocess,json,hashlib,re
ROOT=pathlib.Path(__file__).resolve().parent
CC='/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 pin=json.loads((ROOT/'reference/pin.json').read_text());assert pin['commit']=='87f0227cb60147a26a1eeb4fb06e3b505e9c7261'
 for n in ['reference/chkstk.S','reference/x86_64/chkstk.S']:assert sha(ROOT/n)=='eadb9b028c8fc2ea1c685c61f61a84bd3defe82f8441a6845b14123de3b478c5'
 assert sha(ROOT/'reference/LLVM-LICENSE.txt')=='8d85c1057d742e597985c7d4e6320b015a9139385cff4cbae06ffc0ebe89afee'
 inputs={str(p.relative_to(ROOT)):sha(p) for p in ROOT.rglob('*') if p.is_file() and not any(n in p.parts for n in ['runs','evidence']) and p.suffix!='.md'}
 out=ROOT/'runs/runtime';out.mkdir(parents=True,exist_ok=True);logs=[]
 def run(cmd):
  r=subprocess.run(cmd,capture_output=True,text=True,timeout=120);logs.extend([json.dumps(cmd),r.stdout,r.stderr]);assert not r.returncode,r.stderr;return r.stdout
 rename=['-Dmemcpy=qca_memcpy','-Dmemset=qca_memset','-Dmemcmp=qca_memcmp','-Dmemchr=qca_memchr','-Dstrlen=qca_strlen']
 m=out/'memory.o';run([CC,'-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-builtin',*rename,'-c',str(ROOT/'native_memory.c'),'-o',str(m)])
 san=out/'memory-test';run([CC,'-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all',str(ROOT/'runtime_test.c'),str(ROOT/'chkstk_bridge.S'),str(ROOT/'probe_call.S'),str(m),'-o',str(san)]);memory=run([str(san),'memory'])
 plain=out/'memory-plain.o';run([CC,'-O1','-fno-builtin',*rename,'-c',str(ROOT/'native_memory.c'),'-o',str(plain)])
 probe=out/'probe-test';run([CC,'-O1',str(ROOT/'runtime_test.c'),str(ROOT/'chkstk_bridge.S'),str(ROOT/'probe_call.S'),str(plain),'-o',str(probe)]);guard=run([str(probe)])
 coff=out/'chkstk.obj';run([CC,'-target','x86_64-pc-win32-coff','-c',str(ROOT/'chkstk_bridge.S'),'-o',str(coff)]);symbol=run(['nm',str(coff)]);symbol_addresses={l.split()[-1]:l.split()[0] for l in symbol.splitlines() if len(l.split())==3};assert symbol_addresses['__chkstk']==symbol_addresses['___chkstk_ms']
 port=ROOT/'dependencies/port';run(['python3',str(port/'verify_port.py')]);pr=json.loads((port/'runs/port/report.json').read_text())
 p_objs=sorted((port/'runs/port').glob('coff-*.obj'),key=lambda p:int(p.stem.split('-')[1]))
 entry=out/'efi-smoke.obj';run([CC,'-target','x86_64-pc-win32-coff','-DWIN32=1','-ffreestanding','-fno-builtin','-fno-stack-protector','-mno-red-zone','-Os','-I'+str(port/'compat'),'-I'+str(port),'-I'+str(port/'dependencies/rng'),'-I/home/yuka/rabbit-world/parallel-provisioning-review-v1/noise-c/include','-c',str(ROOT/'efi_smoke.c'),'-o',str(entry)])
 linker=str(pathlib.Path(CC).parent/'lld');efi=out/'public-vector-runtime.efi'
 run([linker,'-flavor','link','/subsystem:efi_application','/entry:efi_main','/nodefaultlib','/machine:x64','/opt:ref','/fixed:no','/out:'+str(efi),*[str(p) for p in p_objs],str(coff),str(entry)])
 headers=run(['objdump','-x',str(efi)]);assert 'EFI application' in headers and 'pei-x86-64' in headers
 # Static/dynamic frame observations only; callback call-chain and physical reserve are unproved.
 stack={}
 for name in ['handshakestate','hashstate']:
  obj=out/(name+'-stack.obj');run([CC,'-target','x86_64-pc-win32-coff','-DWIN32=1','-ffreestanding','-fno-builtin','-fno-stack-protector','-mno-red-zone','-Os','-fstack-usage','-I'+str(port/'compat'),'-I/home/yuka/rabbit-world/parallel-provisioning-review-v1/noise-c/include','-I/home/yuka/rabbit-world/parallel-provisioning-review-v1/noise-c/src/protocol','-c','/home/yuka/rabbit-world/parallel-provisioning-review-v1/noise-c/src/protocol/'+name+'.c','-o',str(obj)])
  su=out/(name+'-stack.su');stack[name]=su.read_text()
 (out/'host.log').write_text('\n'.join(logs));assert all(sha(ROOT/n)==h for n,h in inputs.items())
 report={'status':'LLVM-REAL-CHKSTK-GUARD-AND-MEMORY-ORACLE-ASAN-COFF-PASS','llvm_commit':pin['commit'],'source_sha256':inputs,'memory_checks':int(re.search(r'PASS (\d+)',memory)[1]),'guard_checks':int(re.search(r'PASS (\d+)',guard)[1]),'host_log_sha256':sha(out/'host.log'),'coff_probe_sha256':sha(coff),'coff_ms_alias_same_address':True,'simulated_guarded_stack_bytes':65536,'probe_instruction_body_changed':False,'empty_probe':False,'actual_target_stack_verified':False,'actual_native_provider_or_owner_auth':False,'standalone_public_vector_efi_linked':True,'standalone_efi_bytes':efi.stat().st_size,'standalone_efi_sha256':sha(efi),'standalone_efi_executed':False,'rabbit_engine_full_efi_linked':False,'port_v2_model_checks':pr['checks'],'stack_usage_observations':stack,'coff_probe_resolves_existing_symbol':True,'physical_operations':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(memory.strip());print(guard.strip());print('Actual COFF probe PASS, no physical stack/EFI claim')
if __name__=='__main__':main()
