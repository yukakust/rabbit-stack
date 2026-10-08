from pathlib import Path
import sys,subprocess,json,hashlib,os,ssl
assert sys.platform.startswith('linux'),'Native C/ASAN/COFF only Yukabox'
R=Path(__file__).resolve().parent;B=R.parent/'native-wifi-qca9377-tls13-ble-prototype-v1';O=R/'runs';O.mkdir(exist_ok=True)
C='/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=json.loads((B/'evidence/2026-10-09/freeze.json').read_text())
for n,h in f['source_sha256'].items():assert sha(B/n)==h,n
p=json.loads((R/'inputs.json').read_text());assert sha(B/'tls_config.h')==p['base_config_sha256'] and sha(B/'evidence/2026-10-09/freeze.json')==p['base_freeze_sha256']
for i in range(4):
 (R/'fixtures'/f'chain-{i}.der').write_bytes(ssl.PEM_cert_to_DER_cert((R/'fixtures'/f'served-{i}.pem').read_text()))
(R/'fixtures/root.der').write_bytes(ssl.PEM_cert_to_DER_cert((R/'fixtures/isrg-root-x2.pem').read_text()))
flags=['-std=c11','-I'+str(R),'-I'+str(B),'-I'+str(B/'vendor/include'),'-I'+str(B/'vendor/library'),'-DMBEDTLS_CONFIG_FILE="wan_config.h"']
sources=[*sorted((B/'vendor/library').glob('*.c')),B/'tls_heap.c',R/'trusted_utc.c',R/'verify_certificate.c'];objects=[];logs=[]
def run(cmd):
 a=subprocess.run(cmd,text=True,capture_output=True,timeout=120,env=dict(os.environ,TMPDIR=str(O)));logs.extend([json.dumps(cmd),a.stdout,a.stderr]);(O/'full.log').write_text('\n'.join(logs));assert a.returncode==0,a.stderr;return a.stdout
for i,p in enumerate([*sources,R/'test_verify.c']):
 o=O/('%d.o'%i);run([C,*flags,'-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-omit-frame-pointer','-c',str(p),'-o',str(o)]);objects.append(o)
run([C,'-fsanitize=address,undefined',*[str(p) for p in objects],'-o',str(O/'test')]);result=run([str(O/'test'),*[str(R/'fixtures'/('chain-%d.der'%i)) for i in range(4)],str(R/'fixtures/root.der')]);print(result,flush=True)
coff={}
for i,p in enumerate(sources):
 o=O/('%d.obj'%i);run([C,*flags,'-I'+str(R/'freestanding'),'-I'+str(B/'freestanding'),'--target=x86_64-pc-win32-coff','-U_WIN32','-U_WIN64','-U_MSC_VER','-Os','-ffreestanding','-fno-stack-protector','-mno-red-zone','-c',str(p),'-o',str(o)]);coff[o.name]=sha(o)
report={'status':'SYNTHETIC-MATURE-X509-CA-NAME-TRUSTED-UTC-P384-SHA384-ASAN-COFF-PASS','build_host':'yukabox','result':result.strip(),'source_sha256':{str(p.relative_to(R)):sha(p) for p in [R/'wan_config.h',R/'trusted_utc.h',R/'trusted_utc.c',R/'verify_certificate.h',R/'verify_certificate.c',R/'test_verify.c',R/'run.py',R/'inputs.json',R/'freestanding/time.h']},'base_freeze_sha256':sha(B/'evidence/2026-10-09/freeze.json'),'coff_object_sha256':coff,'public_chain_metadata':json.loads((R/'fixtures/metadata.json').read_text()),'physical_Dell_TLS':False,'UTC_authority_proved':False,'entropy_authority_proved':False,'TLS_client_handshake_proved':False,'native_integrated':False,'signing_admitted':False};(O/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
