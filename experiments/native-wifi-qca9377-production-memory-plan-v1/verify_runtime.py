import pathlib,subprocess,json,hashlib,re,os
ROOT=pathlib.Path(__file__).resolve().parent
CC='/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 pin=json.loads((ROOT/'reference/pin.json').read_text());assert pin['commit']=='87f0227cb60147a26a1eeb4fb06e3b505e9c7261'
 for n in ['reference/chkstk.S','reference/x86_64/chkstk.S']:assert sha(ROOT/n)=='eadb9b028c8fc2ea1c685c61f61a84bd3defe82f8441a6845b14123de3b478c5'
 assert sha(ROOT/'reference/LLVM-LICENSE.txt')=='8d85c1057d742e597985c7d4e6320b015a9139385cff4cbae06ffc0ebe89afee'
 inputs={str(p.relative_to(ROOT)):sha(p) for p in ROOT.rglob('*') if p.is_file() and not any(n in p.parts for n in ['runs','evidence']) and p.suffix!='.md'}
 out=ROOT/'runs/runtime';out.mkdir(parents=True,exist_ok=True);logs=[];tmp=out/'compiler-tmp';tmp.mkdir(exist_ok=True);os.environ['TMPDIR']=str(tmp)
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
 ref=pathlib.Path('/home/yuka/rabbit-world/parallel-efi-rng-v1/reference/UefiSpec.h');assert sha(ref)=='411733fc1da5e084971f6a70c59b3699adee73a060fc5e7067eee3d2fb850db9'
 text=ref.read_text();bodies={}
 for name in ['EFI_BOOT_SERVICES','EFI_SYSTEM_TABLE']:
  end=text.index('} '+name+';')+len('} '+name+';');begin=text.rfind('typedef struct {',0,end);bodies[name]=text[begin:end]
 aliases=sorted(set(re.findall(r'\b(EFI_[A-Z_0-9]+)\s+[A-Za-z_][A-Za-z_0-9]*;',bodies['EFI_BOOT_SERVICES']))-{'EFI_TABLE_HEADER'})
 oracle='#include <stdint.h>\n#include <stddef.h>\ntypedef struct {uint64_t Signature;uint32_t Revision,HeaderSize,CRC32,Reserved;} EFI_TABLE_HEADER;\n#define VOID void\n'
 oracle+=''.join('typedef void (*'+name+')(void);\n' for name in aliases)+bodies['EFI_BOOT_SERVICES']+'\n'
 oracle+='typedef uint16_t CHAR16;typedef uint32_t UINT32;typedef size_t UINTN;typedef void* EFI_HANDLE;typedef struct {void*p;} EFI_SIMPLE_TEXT_INPUT_PROTOCOL,EFI_SIMPLE_TEXT_OUTPUT_PROTOCOL,EFI_RUNTIME_SERVICES,EFI_CONFIGURATION_TABLE;\n'+bodies['EFI_SYSTEM_TABLE']+'\n'
 (out/'oracle-pool.h').write_text(oracle)
 pool_host=[];pool_coff=[];inc=['-I'+str(port),'-I'+str(port/'dependencies/rng'),'-I/home/yuka/rabbit-world/parallel-provisioning-review-v1/noise-c/include','-I/home/yuka/rabbit-world/parallel-secure-provision-v1/reference','-I'+str(out)]
 for name in ['pool_owner','pool_target']:
  obj=out/(name+'.o');run([CC,'-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all',*inc,'-c',str(ROOT/(name+'.c')),'-o',str(obj)]);pool_host.append(str(obj))
  obj=out/(name+'.obj');run([CC,'-target','x86_64-pc-win32-coff','-DWIN32=1','-ffreestanding','-fno-builtin','-fno-stack-protector','-mno-red-zone','-Os','-I'+str(port/'compat'),*inc,'-c',str(ROOT/(name+'.c')),'-o',str(obj)]);pool_coff.append(str(obj))
 pool_test=out/'pool-test';run([CC,'-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all',*inc,str(ROOT/'pool_test.c'),*pool_host,*[str(p) for p in (port/'runs/port').glob('host-*.o')],'-o',str(pool_test)])
 pool_model=run([str(pool_test)]);pool_failures={str(m):run([str(pool_test),str(m)]) for m in range(1,9)}

 entry=out/'efi-smoke.obj';run([CC,'-target','x86_64-pc-win32-coff','-DWIN32=1','-ffreestanding','-fno-builtin','-fno-stack-protector','-mno-red-zone','-Os','-I'+str(port/'compat'),'-I'+str(port),'-I'+str(port/'dependencies/rng'),'-I/home/yuka/rabbit-world/parallel-provisioning-review-v1/noise-c/include','-c',str(ROOT/'efi_smoke.c'),'-o',str(entry)])
 linker=str(pathlib.Path(CC).parent/'lld');efi=out/'public-vector-runtime.efi'
 run([linker,'-flavor','link','/subsystem:efi_application','/entry:efi_main','/nodefaultlib','/machine:x64','/opt:ref','/fixed:no','/out:'+str(efi),*[str(p) for p in p_objs],*pool_coff,str(coff),str(entry)])
 entry_dump=run(['objdump','-dr',str(entry)]);assert '__chkstk' in entry_dump and 'large_stack_probe' in entry_dump
 negative_entry=out/'negative-entry.obj'
 cmd=[CC,'-target','x86_64-pc-win32-coff','-DWIN32=1','-DQCA_FORCE_NEGATIVE=1','-ffreestanding','-fno-builtin','-fno-stack-protector','-mno-red-zone','-Os','-I'+str(port/'compat'),'-I'+str(port),'-I'+str(port/'dependencies/rng'),'-I/home/yuka/rabbit-world/parallel-provisioning-review-v1/noise-c/include','-c',str(ROOT/'efi_smoke.c'),'-o',str(negative_entry)]
 run(cmd);negative=out/'negative-runtime.efi';run([linker,'-flavor','link','/subsystem:efi_application','/entry:efi_main','/nodefaultlib','/machine:x64','/opt:ref','/fixed:no','/out:'+str(negative),*[str(p) for p in p_objs],*pool_coff,str(coff),str(negative_entry)])
 ovmf=pathlib.Path('/usr/share/OVMF/OVMF_CODE_4M.fd');vars_source=pathlib.Path('/usr/share/OVMF/OVMF_VARS_4M.fd');observed={}
 def qemu_case(name,image,expected):
  folder=out/name;boot=folder/'fat/EFI/BOOT';boot.mkdir(parents=True,exist_ok=True)
  (boot/'BOOTX64.EFI').write_bytes(image.read_bytes());variables=folder/'vars.fd';variables.write_bytes(vars_source.read_bytes())
  serial=folder/'serial.log';cmd=['qemu-system-x86_64','-machine','q35','-m','128M','-display','none','-monitor','none','-serial','file:'+str(serial),'-no-reboot','-drive','if=pflash,format=raw,readonly=on,file='+str(ovmf),'-drive','if=pflash,format=raw,file='+str(variables),'-drive','format=raw,file=fat:rw:'+str(folder/'fat'),'-device','isa-debug-exit,iobase=0xf4,iosize=0x04']
  r=subprocess.run(cmd,capture_output=True,text=True,timeout=90);data=serial.read_text(errors='replace');logs.extend([json.dumps(cmd),r.stdout,r.stderr,data]);assert r.returncode==expected,(r.returncode,data,r.stderr)
  for marker in ['QEMU PUBLIC VECTOR ENTRY','ACTUAL EFI MEMORY SHIMS PASS','REAL LARGE FRAME PROBE PASS','REAL BOOTSERVICES POOL ALIGNED OWNED PASS','ACTUAL WHOLE RAW POOL ZERO BEFORE FREE OBSERVED']+(['REAL POOL DETACH WIPE FREE PASS'] if name!='free-failure' else [])+(['NK TWO PUBLISHED MESSAGES HASH AND ARENA WIPE PASS','EXPLICIT MOCK RNG CALLBACK SUCCESS FAILURE WIPE PASS'] if name!='negative' else ['DELIBERATE MAC TAG CORRUPTION']):assert marker in data,(marker,data)
  final='QEMU RUNTIME EFI COMPLETE PASS' if expected==33 else 'FREE FAILURE RETAINED NO RETRY NO BOUND DANGLING POINTER PASS' if name=='free-failure' else 'MAC FAILURE ZERO PAYLOAD FAILED STATE AND ARENA WIPE PASS';assert final in data
  observed[name]={'exit':r.returncode,'image_sha256':sha(image),'serial_sha256':sha(serial),'all_markers':True}
 failure_entry=out/'free-failure-entry.obj';failure_cmd=[v for v in cmd if v!='-DQCA_FORCE_NEGATIVE=1'];failure_cmd[failure_cmd.index(str(negative_entry))]=str(failure_entry);failure_cmd.insert(1,'-DQCA_FREE_FAILURE=1');run(failure_cmd)
 free_image=out/'free-failure-runtime.efi';run([linker,'-flavor','link','/subsystem:efi_application','/entry:efi_main','/nodefaultlib','/machine:x64','/opt:ref','/fixed:no','/out:'+str(free_image),*[str(p) for p in p_objs],*pool_coff,str(coff),str(failure_entry)])
 qemu_case('positive',efi,33);qemu_case('negative',negative,35);qemu_case('free-failure',free_image,35)
 headers=run(['objdump','-x',str(efi)]);assert 'EFI application' in headers and 'pei-x86-64' in headers
 # Static/dynamic frame observations only; callback call-chain and physical reserve are unproved.
 stack={}
 for name in ['handshakestate','hashstate']:
  obj=out/(name+'-stack.obj');run([CC,'-target','x86_64-pc-win32-coff','-DWIN32=1','-ffreestanding','-fno-builtin','-fno-stack-protector','-mno-red-zone','-Os','-fstack-usage','-I'+str(port/'compat'),'-I/home/yuka/rabbit-world/parallel-provisioning-review-v1/noise-c/include','-I/home/yuka/rabbit-world/parallel-provisioning-review-v1/noise-c/src/protocol','-c','/home/yuka/rabbit-world/parallel-provisioning-review-v1/noise-c/src/protocol/'+name+'.c','-o',str(obj)])
  su=out/(name+'-stack.su');stack[name]=su.read_text()
 (out/'host.log').write_text('\n'.join(logs));assert all(sha(ROOT/n)==h for n,h in inputs.items())
 report={'status':'QEMU-REAL-BOOTPOOL-OWNERS-WIPE-DETACH-NK-RUNTIME-PASS','llvm_commit':pin['commit'],'source_sha256':inputs,'memory_checks':int(re.search(r'PASS (\d+)',memory)[1]),'guard_checks':int(re.search(r'PASS (\d+)',guard)[1]),'host_log_sha256':sha(out/'host.log'),'coff_probe_sha256':sha(coff),'coff_ms_alias_same_address':True,'simulated_guarded_stack_bytes':65536,'probe_instruction_body_changed':False,'empty_probe':False,'actual_target_stack_verified':False,'actual_native_provider_or_owner_auth':False,'standalone_public_vector_efi_linked':True,'standalone_efi_bytes':efi.stat().st_size,'standalone_efi_sha256':sha(efi),'standalone_efi_executed':True,'efi_execution_platform':'QEMU-only q35 OVMF','qemu_cases':observed,'ovmf_code_sha256':sha(ovmf),'ovmf_vars_template_sha256':sha(vars_source),'rng_provider_explicitly_mocked':True,'actual_qemu_bootservices_pool_used':True,'pool_model_checks':int(re.search(r'PASS (\d+)',pool_model)[1]),'pool_failure_modes':list(pool_failures),'pool_raw_bytes':33407,'image_static_arena_removed':True,'edk2_uefi_spec_sha256':sha(ref),'raw_actual_rng_calls':False,'rabbit_engine_full_efi_linked':False,'port_v2_model_checks':pr['checks'],'stack_usage_observations':stack,'coff_probe_resolves_existing_symbol':True,'physical_operations':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(memory.strip());print(guard.strip());print('Actual COFF probe PASS, no physical stack/EFI claim')
if __name__=='__main__':main()
