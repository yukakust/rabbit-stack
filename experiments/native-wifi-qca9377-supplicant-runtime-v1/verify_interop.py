#!/usr/bin/env python3
"""Yukabox only: real mature WPA core, ASAN host interop, honest COFF ABI gap."""
import argparse,hashlib,json,pathlib,subprocess,tarfile,os,shlex
ARCHIVE='912ea06f74e30a8e36fbb68064d6cdff218d8d591db0fc5d75dee6c81ac7fc0a'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--reference',type=pathlib.Path,required=True);p.add_argument('--clang',required=True);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args();r=pathlib.Path(__file__).resolve().parent;o=a.output.resolve();o.mkdir(parents=True,exist_ok=True)
 assert str(o).startswith('/home/yuka/rabbit-world/parallel-supplicant-runtime-v1/')
 assert sha(pathlib.Path('/home/yuka/rabbit-world/parallel-security-v1/reference/wpa_supplicant-2.11.tar.gz'))==ARCHIVE
 with tarfile.open('/home/yuka/rabbit-world/parallel-security-v1/reference/wpa_supplicant-2.11.tar.gz') as t:
  for m in t.getmembers():
   if m.isfile() and not m.name.endswith('/src/rsn_supp/wpa.c'):assert (a.reference/m.name).read_bytes()==t.extractfile(m).read()
  original=t.extractfile('wpa_supplicant-2.11/src/rsn_supp/wpa.c').read()
  old=b"sm->own_addr, pmkid,\n\t\t\t\t\t\tNULL, 0);";new=b"sm->own_addr, pmkid,\n\t\t\t\t\t\tsm->network_ctx, sm->key_mgmt);"
  assert original.count(old)==1
  assert (a.reference/'wpa_supplicant-2.11/src/rsn_supp/wpa.c').read_bytes()==original.replace(old,new)
 src=a.reference/'wpa_supplicant-2.11/src'
 units=['rsn_supp/wpa.c','rsn_supp/wpa_ie.c','rsn_supp/pmksa_cache.c','ap/wpa_auth.c','ap/wpa_auth_ie.c','ap/pmksa_cache_auth.c','common/wpa_common.c','utils/common.c','utils/wpabuf.c','utils/wpa_debug.c','crypto/aes-internal.c','crypto/aes-internal-enc.c','crypto/aes-internal-dec.c','crypto/aes-wrap.c','crypto/aes-unwrap.c','crypto/aes-omac1.c','crypto/sha1.c','crypto/sha1-internal.c','crypto/sha1-pbkdf2.c','crypto/sha256.c','crypto/sha256-internal.c','crypto/md5.c','crypto/md5-internal.c','crypto/rc4.c','crypto/sha1-prf.c','crypto/sha256-prf.c','crypto/sha1-tprf.c','common/ieee802_11_common.c','radius/radius.c']
 flags=['-DOS_NO_C_LIB_DEFINES','-fno-builtin','-O1','-g','-ffunction-sections','-fdata-sections','-fsanitize=address,undefined','-DCONFIG_NO_STDOUT_DEBUG','-DCONFIG_NO_WPA_MSG','-DCONFIG_NO_TKIP','-DCONFIG_NO_RANDOM_POOL','-DCONFIG_SHA256','-DCONFIG_CRYPTO_INTERNAL','-isystem',str(src),'-isystem',str(src/'utils'),'-Wno-deprecated-declarations']
 local={n:sha(r/n) for n in ('interop.c','runtime.c','runtime.h','primitives.c','verify_interop.py')};tmp=o/'tmp';tmp.mkdir(exist_ok=True);env=os.environ.copy();env['TMPDIR']=str(tmp)
 for n in ('CPATH','C_INCLUDE_PATH','CPLUS_INCLUDE_PATH','SDKROOT'):env.pop(n,None)
 obj=o/'objects';obj.mkdir(exist_ok=True);logs=[];dependencies={};objects=[]
 def run(cmd,check=True,timeout=60):
  b=subprocess.run(cmd,capture_output=True,text=True,env=env,timeout=timeout);logs.extend([json.dumps(cmd),b.stdout,b.stderr]);
  if check:assert b.returncode==0,b.stderr
  return b
 for i,source in enumerate([r/'interop.c',r/'runtime.c',r/'primitives.c',*[src/n for n in units]]):
  output=obj/f'{i}.o';dep=obj/f'{i}.d';cmd=[a.clang,*flags,'-MD','-MF',str(dep),'-c',str(source),'-o',str(output)]
  if i==0:cmd[1:1]=['-Wall','-Wextra','-Werror']
  if source.name=='pmksa_cache.c':cmd[1:1]=['-DIEEE8021X_EAPOL']
  run(cmd);objects.append(output)
  text=dep.read_text().replace('\\\n',' ');names=shlex.split(text.split(':',1)[1]);
  for n in names:
   f=pathlib.Path(n).resolve();dependencies[str(f)]=sha(f)
 libraries=[]
 run([a.clang,'-fsanitize=address,undefined',*[str(x) for x in objects],'-Wl,--gc-sections','-Wl,-rpath-link,/lib/x86_64-linux-gnu',*[str(x) for x in libraries],'-o',str(o/'interop')])
 undefined=run(['nm','-u',str(o/'interop')]).stdout
 assert not any(x.startswith(('wpa_','pmksa_','eloop_')) for x in [line.split()[-1] for line in undefined.splitlines()])
 core_abi=run(['nm','-u',str(objects[3])]).stdout
 (o/'core-undefined.log').write_text(core_abi);(o/'dynamic-imports.log').write_text(undefined)
 ld=run(['ldd',str(o/'interop')]).stdout;assert 'libcrypto' not in ld and 'libssl' not in ld;(o/'ldd.log').write_text(ld)
 for line in ld.splitlines():
  if '=>' in line:
   name=line.split('=>',1)[1].strip().split()[0]
   if name.startswith('/'):
    f=pathlib.Path(name).resolve();dependencies[str(f)]=sha(f)
 results=[]
 for mode in range(13):
  q=run([str(o/'interop'),str(mode)],check=False,timeout=10);(o/f'mode-{mode}.log').write_text(q.stdout+q.stderr);assert q.returncode==0,str(mode)+q.stdout+q.stderr;assert 'PASS; synthetic only' in q.stdout;results.append({'mode':mode,'summary':q.stdout.strip(),'log_sha256':sha(o/f'mode-{mode}.log')})
 coff=run([a.clang,'-target','x86_64-pc-win32-coff','-ffreestanding','-DCONFIG_NO_STDOUT_DEBUG','-DCONFIG_NO_WPA_MSG','-DCONFIG_NO_TKIP','-DCONFIG_NO_RANDOM_POOL','-isystem',str(src),'-isystem',str(src/'utils'),'-c',str(src/'rsn_supp/wpa.c'),'-o',str(o/'unported-wpa.obj')],check=False)
 (o/'COFF-attempt.log').write_text(coff.stdout+coff.stderr)
 assert local=={n:sha(r/n) for n in local};assert dependencies=={n:sha(pathlib.Path(n)) for n in dependencies}
 version='not linked; hostap internal portable crypto';compiler=run([a.clang,'--version']).stdout.strip();(o/'build-and-tests.log').write_text('\n'.join(logs))
 inputs=o/'compiled-inputs';inputs.mkdir(exist_ok=True);compiled_inputs={}
 for i,(name,pin) in enumerate(sorted(dependencies.items())):
  f=pathlib.Path(name)
  if f.suffix not in ('.c','.h'):continue
  assert str(f).startswith((str(src),str(r),'/usr/include/',str(pathlib.Path(a.clang).parent.parent)))
  target=inputs/(str(i)+f.suffix);target.write_bytes(f.read_bytes());assert sha(target)==pin;compiled_inputs[str(target.relative_to(o))]={'source_path':name,'sha256':pin}
 report={'compiled_fixture_sources_sha256':compiled_inputs,'status':'HOST-PATCHED-RSN-NATIVE-PLATFORM-INTEROP-PASS','archive_sha256':ARCHIVE,'compiled_mature_units':len(units),'compiled_sources':{n:sha(src/n) for n in units},'local_sources':local,'compiled_headers_and_runtime_dependencies_sha256':dependencies,'object_sha256':{str(x.relative_to(o)):sha(x) for x in objects},'executable_sha256':sha(o/'interop'),'compiler':compiler,'openssl_version':version,'interop_scenarios':results,'core_ELF_undefined_symbols':sorted(line.split()[-1] for line in core_abi.splitlines()),'host_dynamic_imports_log_sha256':sha(o/'dynamic-imports.log'),'build_and_test_log_sha256':sha(o/'build-and-tests.log'),'real_crypto_backend':'actual hostap portable internal AES/hash/HMAC/PBKDF2, no OpenSSL library linked','RNG':'explicit public deterministic os_get_random fixture wrapper, never native entropy','timers':'new bounded owned runtime timer queue driven by actual host monotonic/wall providers; no os_unix/hosted eloop linked','driver':'synthetic confirmed key-storage model and ambiguous-installed timeout model, no firmware acknowledgment claim','physical_verified':False,'credential_reads':0,'owner_key_reads':0,'state_operations':0,'host_linked':True,'full_4way_handshake_tested':True,'PTK_no_reinstall_tested':True,'GTK_rekey_and_no_reinstall_tested':True,'ambiguous_install_quarantine_tested':True,'local_controlled_port_gate_tested':True,'unadapted_upstream_direct_COFF_object_compiled':coff.returncode==0,'unadapted_upstream_direct_COFF_linked':False,'COFF_actual_attempt_returncode':coff.returncode,'COFF_actual_attempt_log_sha256':sha(o/'COFF-attempt.log'),'native_deployment_admitted':False,'known_security_baseline_gap':'exact official2026-2 PMKSA fix applied with zero fuzz; no broader current baseline approval or physical credential admission', 'official_patch_sha256':sha(r/'copied/official-pmksa.patch'), 'PMKSA_fix_applied':True,'PMKSA_actual_M1_regression_modes':[10,11,12],'PMKSA_cache_unit_enabled':True,'unavailable_driver_PMKSA_offload':'returns unsupported -1; no fake success','unavailable_enterprise_reauthentication':'failclosed quarantine callback; no enterprise handshake claim','public_crypto_vectors':['RFC3394-4.1 wrap/unwrap/tamper','RFC2202-case1 HMACSHA1','RFC4231-case1 HMACSHA256'],'AP_authorized_is_not_local_key_confirmation':True}
 (o/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('\n'.join(x['summary'] for x in results));print('COFF attempted',coff.returncode,'report',sha(o/'report.json'));print(report['status'])
if __name__=='__main__':main()
