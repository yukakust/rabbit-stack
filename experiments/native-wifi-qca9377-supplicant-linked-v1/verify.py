#!/usr/bin/env python3
"""Yukabox only: real mature WPA core, ASAN host interop, honest COFF ABI gap."""
import argparse,hashlib,json,pathlib,subprocess,tarfile,os,shlex
ARCHIVE='912ea06f74e30a8e36fbb68064d6cdff218d8d591db0fc5d75dee6c81ac7fc0a'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--reference',type=pathlib.Path,required=True);p.add_argument('--clang',required=True);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args();r=pathlib.Path(__file__).resolve().parent;o=a.output.resolve();o.mkdir(parents=True,exist_ok=True)
 assert str(o).startswith('/home/yuka/rabbit-world/parallel-supplicant-linked-v1/')
 assert sha(a.reference/'wpa_supplicant-2.11.tar.gz')==ARCHIVE
 with tarfile.open(a.reference/'wpa_supplicant-2.11.tar.gz') as t:
  for m in t.getmembers():
   if m.isfile():assert (a.reference/m.name).read_bytes()==t.extractfile(m).read()
 src=a.reference/'wpa_supplicant-2.11/src'
 units=['rsn_supp/wpa.c','rsn_supp/wpa_ie.c','rsn_supp/pmksa_cache.c','ap/wpa_auth.c','ap/wpa_auth_ie.c','ap/pmksa_cache_auth.c','common/wpa_common.c','utils/os_unix.c','utils/eloop.c','utils/common.c','utils/wpabuf.c','utils/wpa_debug.c','crypto/crypto_openssl.c','crypto/sha1-prf.c','crypto/sha256-prf.c','crypto/sha1-tprf.c','common/ieee802_11_common.c','radius/radius.c']
 flags=['-O1','-g','-ffunction-sections','-fdata-sections','-fsanitize=address,undefined','-DCONFIG_NO_STDOUT_DEBUG','-DCONFIG_NO_WPA_MSG','-DCONFIG_NO_TKIP','-DCONFIG_NO_RANDOM_POOL','-DCONFIG_SHA256','-isystem',str(src),'-isystem',str(src/'utils'),'-Wno-deprecated-declarations']
 local={n:sha(r/n) for n in ('interop.c','verify.py')};tmp=o/'tmp';tmp.mkdir(exist_ok=True);env=os.environ.copy();env['TMPDIR']=str(tmp)
 for n in ('CPATH','C_INCLUDE_PATH','CPLUS_INCLUDE_PATH','SDKROOT'):env.pop(n,None)
 obj=o/'objects';obj.mkdir(exist_ok=True);logs=[];dependencies={};objects=[]
 def run(cmd,check=True,timeout=60):
  b=subprocess.run(cmd,capture_output=True,text=True,env=env,timeout=timeout);logs.extend([json.dumps(cmd),b.stdout,b.stderr]);
  if check:assert b.returncode==0,b.stderr
  return b
 for i,source in enumerate([r/'interop.c',*[src/n for n in units]]):
  output=obj/f'{i}.o';dep=obj/f'{i}.d';cmd=[a.clang,*flags,'-MD','-MF',str(dep),'-c',str(source),'-o',str(output)]
  if i==0:cmd[1:1]=['-Wall','-Wextra','-Werror']
  run(cmd);objects.append(output)
  text=dep.read_text().replace('\\\n',' ');names=shlex.split(text.split(':',1)[1]);
  for n in names:
   f=pathlib.Path(n).resolve();dependencies[str(f)]=sha(f)
 libraries=[pathlib.Path('/lib/x86_64-linux-gnu/libcrypto.so.3'),pathlib.Path('/lib/x86_64-linux-gnu/libz.so.1'),pathlib.Path('/lib/x86_64-linux-gnu/libzstd.so.1')]
 run([a.clang,'-fsanitize=address,undefined',*[str(x) for x in objects],'-Wl,--gc-sections','-Wl,--wrap=os_get_random','-Wl,-rpath-link,/lib/x86_64-linux-gnu',*[str(x) for x in libraries],'-o',str(o/'interop')])
 undefined=run(['nm','-u',str(o/'interop')]).stdout
 assert not any(x.startswith(('wpa_','pmksa_','eloop_')) for x in [line.split()[-1] for line in undefined.splitlines()])
 core_abi=run(['nm','-u',str(objects[1])]).stdout
 (o/'core-undefined.log').write_text(core_abi);(o/'dynamic-imports.log').write_text(undefined)
 ld=run(['ldd',str(o/'interop')]).stdout;(o/'ldd.log').write_text(ld)
 for line in ld.splitlines():
  if '=>' in line:
   name=line.split('=>',1)[1].strip().split()[0]
   if name.startswith('/'):
    f=pathlib.Path(name).resolve();dependencies[str(f)]=sha(f)
 results=[]
 for mode in range(10):
  q=run([str(o/'interop'),str(mode)],check=False,timeout=10);(o/f'mode-{mode}.log').write_text(q.stdout+q.stderr);assert q.returncode==0,str(mode)+q.stdout+q.stderr;assert 'PASS; synthetic only' in q.stdout;results.append({'mode':mode,'summary':q.stdout.strip(),'log_sha256':sha(o/f'mode-{mode}.log')})
 coff=run([a.clang,'-target','x86_64-pc-win32-coff','-ffreestanding','-DCONFIG_NO_STDOUT_DEBUG','-DCONFIG_NO_WPA_MSG','-DCONFIG_NO_TKIP','-DCONFIG_NO_RANDOM_POOL','-isystem',str(src),'-isystem',str(src/'utils'),'-c',str(src/'rsn_supp/wpa.c'),'-o',str(o/'unported-wpa.obj')],check=False)
 (o/'COFF-attempt.log').write_text(coff.stdout+coff.stderr)
 assert local=={n:sha(r/n) for n in local};assert dependencies=={n:sha(pathlib.Path(n)) for n in dependencies}
 version=run(['openssl','version']).stdout.strip();compiler=run([a.clang,'--version']).stdout.strip();(o/'build-and-tests.log').write_text('\n'.join(logs))
 report={'status':'HOST-MATURE-RSN-SUPPLICANT-AUTHENTICATOR-LINKED-INTEROP-PASS','archive_sha256':ARCHIVE,'compiled_mature_units':len(units),'compiled_sources':{n:sha(src/n) for n in units},'local_sources':local,'compiled_headers_and_runtime_dependencies_sha256':dependencies,'object_sha256':{str(x.relative_to(o)):sha(x) for x in objects},'executable_sha256':sha(o/'interop'),'compiler':compiler,'openssl_version':version,'interop_scenarios':results,'core_ELF_undefined_symbols':sorted(line.split()[-1] for line in core_abi.splitlines()),'host_dynamic_imports_log_sha256':sha(o/'dynamic-imports.log'),'build_and_test_log_sha256':sha(o/'build-and-tests.log'),'real_crypto_backend':'unedited hostap crypto_openssl + actual system OpenSSL; host only','RNG':'explicit public deterministic os_get_random fixture wrapper, never native entropy','timers':'actual unedited upstream eloop + real host monotonic/time APIs; fixture bounded termination','driver':'synthetic confirmed key-storage model and ambiguous-installed timeout model, no firmware acknowledgment claim','physical_verified':False,'credential_reads':0,'owner_key_reads':0,'state_operations':0,'host_linked':True,'full_4way_handshake_tested':True,'PTK_no_reinstall_tested':True,'GTK_rekey_and_no_reinstall_tested':True,'ambiguous_install_quarantine_tested':True,'local_controlled_port_gate_tested':True,'freestanding_COFF_object_compiled':coff.returncode==0,'freestanding_COFF_linked':False,'COFF_actual_attempt_returncode':coff.returncode,'COFF_actual_attempt_log_sha256':sha(o/'COFF-attempt.log'),'native_deployment_admitted':False,'known_security_baseline_gap':'official2026-2 PMKSA network context/AKMP fix not applied to historical2.11; no production credentials permitted','AP_authorized_is_not_local_key_confirmation':True}
 (o/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('\n'.join(x['summary'] for x in results));print('COFF attempted',coff.returncode,'report',sha(o/'report.json'));print(report['status'])
if __name__=='__main__':main()
