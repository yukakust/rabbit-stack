from pathlib import Path
import sys,json,subprocess,hashlib
assert sys.platform.startswith('linux'),'Host C/TLS test only Yukabox'
R=Path(__file__).resolve().parent;B=R.parent/'native-wifi-qca9377-tls13-ble-prototype-v1';O=R/'runs'
C='/home/yuka/rabbit-world/unreal-yukabox-v1/engine/Engine/Extras/ThirdPartyNotUE/SDKs/HostLinux/Linux_x64/v26_clang-20.1.8-rockylinux8/x86_64-unknown-linux-gnu/bin/clang'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((O/'report.json').read_text())
for n,h in r['source_sha256'].items():assert sha(R/n)==h,n
assert sha(R/'fixtures/root.der')==r['public_chain_metadata']['anchor_der_sha256']
sources=[*sorted((B/'vendor/library').glob('*.c')),B/'tls_heap.c',R/'trusted_utc.c',R/'verify_certificate.c'];flags=['-std=c11','-I'+str(R),'-I'+str(B),'-I'+str(B/'vendor/include'),'-I'+str(B/'vendor/library'),'-DMBEDTLS_CONFIG_FILE="wan_config.h"']
subprocess.run([C,*flags,'-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-omit-frame-pointer','-c',str(R/'host_handshake.c'),'-o',str(O/'host-handshake.o')],check=True)
subprocess.run([C,'-fsanitize=address,undefined',*[str(O/(str(i)+'.o')) for i in range(len(sources))],str(O/'host-handshake.o'),'-o',str(O/'host-handshake')],check=True)
a=subprocess.run([str(O/'host-handshake'),str(R/'fixtures/root.der')],text=True,capture_output=True,timeout=20);(O/'host-handshake.log').write_text(a.stdout+a.stderr);assert a.returncode==0,a.stderr
p={'status':'YUKABOX-HOST-ACTUAL-MBEDTLS-TLS13-CA-NAME-TIME-HANDSHAKE-PASS','result':a.stdout.strip(),'source_sha256':{p.name:sha(p) for p in [R/'host_handshake.c',R/'host_handshake.py']},'verification_report_sha256':sha(O/'report.json'),'host_log_sha256':sha(O/'host-handshake.log'),'build_host':'yukabox','strong_entropy_provider':'Linux getrandom HOST HARNESS ONLY','trusted_UTC_provider':'Yukabox-host system UTC HOST HARNESS ONLY','private_Tailnet_route':True,'HTTP_route':'GET /rabbit-wifi-certificate-check read-only missing route','Funnel_changes':0,'physical_Dell':False,'native_provider_supplied':False,'credentials_or_secrets_logged':False,'Dell_to_Yukabox_proved':False};(O/'host-handshake-report.json').write_text(json.dumps(p,indent=2)+'\n');print(p['result'])
