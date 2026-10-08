from pathlib import Path
import hashlib,json,subprocess,os
import make_interop
R=Path(__file__).resolve().parent;tree=R/'runs/tree';out=R/'runs/interop';out.mkdir(parents=True,exist_ok=True)
CC='/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
units=['rsn_supp/wpa.c','rsn_supp/wpa_ie.c','rsn_supp/pmksa_cache.c','ap/wpa_auth.c','ap/wpa_auth_ie.c','ap/pmksa_cache_auth.c','common/wpa_common.c','utils/common.c','utils/wpabuf.c','utils/wpa_debug.c','crypto/aes-internal.c','crypto/aes-internal-enc.c','crypto/aes-internal-dec.c','crypto/aes-wrap.c','crypto/aes-unwrap.c','crypto/aes-omac1.c','crypto/sha1.c','crypto/sha1-internal.c','crypto/sha1-pbkdf2.c','crypto/sha256.c','crypto/sha256-internal.c','crypto/md5.c','crypto/md5-internal.c','crypto/rc4.c','crypto/sha1-prf.c','crypto/sha256-prf.c','crypto/sha1-tprf.c','common/ieee802_11_common.c','radius/radius.c']
fixture=out/'fixture.c';fixture.write_text(make_interop.source())
flags=['-I'+str(R),'-I'+str(R/'platform'),'-DOS_NO_C_LIB_DEFINES','-DRABBIT_RSN_CHILD_MODEL','-fno-builtin','-O1','-g','-ffunction-sections','-fdata-sections','-fsanitize=address,undefined','-fno-sanitize-recover=all','-DCONFIG_NO_STDOUT_DEBUG','-DCONFIG_NO_WPA_MSG','-DCONFIG_NO_TKIP','-DCONFIG_NO_RANDOM_POOL','-DCONFIG_SHA256','-DCONFIG_CRYPTO_INTERNAL','-isystem',str(tree),'-isystem',str(tree/'utils'),'-Wno-deprecated-declarations']
objects=[];log=''
for j,p in enumerate([fixture,R/'child.c',R/'platform/runtime.c',R/'platform/primitives.c',R/'platform/adapter.c',*[tree/n for n in units]]):
 o=out/f'{j}.o';cmd=[CC,*flags,*(['-DIEEE8021X_EAPOL'] if p.name=='pmksa_cache.c' else []),'-c',str(p),'-o',str(o)];run=subprocess.run(cmd,capture_output=True,text=True);log+=json.dumps(cmd)+'\n'+run.stdout+run.stderr;(out/'compile.log').write_text(log);assert run.returncode==0,run.stderr;objects.append(o)
subprocess.run([CC,'-fsanitize=address,undefined',*map(str,objects),'-Wl,--gc-sections','-o',str(out/'test')],check=True)
results=[]
for mode in [*range(13),20,21,22,23]:
 p=subprocess.run([str(out/'test'),str(mode)],capture_output=True,text=True,timeout=15);(out/f'mode-{mode}.log').write_text(p.stdout+p.stderr);assert p.returncode==0,str(mode)+p.stdout+p.stderr;results.append({'mode':mode,'log_sha256':sha(out/f'mode-{mode}.log')});print(p.stdout.strip())
report={'status':'GENUINE-ROLE2-CHILD-ABI-MATURE-ASAN-INTEROP-PASS','fixture_kind':'synthetic-actual-mature-C-child-dispatch','modes':results,'actual_child_UEFI_entry_fake_protocol':True,'actual_child_OPEN_EAPOL_POLL_CLOSE':True,'physical':False,'real_radio_key_confirmation':False,'test_sha256':sha(out/'test'),'fixture_sha256':sha(fixture),'compile_log_sha256':sha(out/'compile.log'),'child_source_sha256':sha(R/'child.c'),'child_header_sha256':sha(R/'child.h'),'driver':'explicit synthetic-public-key-storage callbacks, not actual SEC_IND','RNG':'explicit insecure public fixture, not production'}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
