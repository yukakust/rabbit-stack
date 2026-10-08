"""New benchmark using existing MinGW compiler + LTO, never native admission."""
from pathlib import Path
import sys,os,platform,importlib.util,json,hashlib,subprocess,struct
assert platform.system()=='Linux'
root=Path(__file__).resolve().parent;repo=Path(sys.argv[1]).resolve();p=repo/'experiments/native-wifi-qca9377-filter64-native-v1';d=p/'runs/checked-candidate';out=root/'runs/gcc-lto-server';out.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('_tls_lto64',p/'filter64_build.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b);a=b.checked.prior.actors
r=json.loads((d/'report.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(d/'report.json')=='37bde7009088c6a783940f642b3dfddbbe2fdeabea671fa17d7f498234f45866'
for n,h in r['generated_compiler_sources_sha256'].items():assert sha(d/n)==h,n
v=root/'source/mbedtls-3.6.7';config=root/'runs/coff-server-Oz/tls_config.h';assert config.is_file()
sources=[d/'driver.c',d/'city_core.c',d/'pci_collect.c',d/'pci_identity.c',*[d/n for n in b.FILES],d/'usb_port.c',d/'bt_event_stream.c',d/'ble_recovery_link.c',d/'diagnostic_gatt.c',a.LINK/'file_core.c',a.NATIVE/'sha256.c',d/'monocypher.c',d/'monocypher-ed25519.c',*(v/'library').glob('*.c'),*[root/n for n in ('tls_engine.c','tls_heap.c','memory_bridge.c','link_probe.c')]]
commands=[];original=subprocess.run
def capture(cmd,*args,**kwargs):
 if isinstance(cmd,list) and cmd and 'mingw32-gcc' in str(cmd[0]):
  cmd=[x if x!='-Os' else '-Oz' for x in cmd];cmd=[*cmd[:-2],'-flto','-Wno-unused-parameter','-DMBEDTLS_PLATFORM_ZEROIZE_ALT','-include',str(root/'freestanding/stdio.h'),'-I'+str(d),'-I'+str(root),'-I'+str(root/'freestanding'),'-I'+str(v/'include'),'-DMBEDTLS_CONFIG_FILE="'+str(config)+'"',*[ '-Wl,--undefined='+n for n in ('tls_ble_open','tls_ble_feed','tls_ble_drain','tls_ble_poll','tls_ble_read','tls_ble_write','tls_ble_close','tls_heap_bind','tls_heap_release','mbedtls_platform_set_calloc_free','psa_crypto_init','mbedtls_psa_crypto_free')],'-Wl,-Map='+str(out/'link.map'),*cmd[-2:]]
 commands.append(list(map(str,cmd)));result=original(cmd,*args,**kwargs)
 if hasattr(result,'stderr'):(out/'compiler.log').write_text((result.stdout or '')+(result.stderr or ''))
 return result
subprocess.run=capture
try:payload=a.compile_efi(out,'frozen64-TLS-LTO-benchmark',sources,driver=True,definitions=('SCENE_REVISION=1','QCA_CONFIG_SETUP=1','QCA_FC_BASE=13'))
except Exception as error:
 (out/'failed-commands.json').write_text(json.dumps(commands,indent=2)+'\n');print(str(error)[-1800:]);raise SystemExit(1)
finally:subprocess.run=original
for n,h in r['generated_compiler_sources_sha256'].items():assert sha(d/n)==h,n
pe=struct.unpack_from('<I',payload,60)[0];mapped=struct.unpack_from('<I',payload,pe+80)[0]
report={'status':'ACTUAL-FROZEN64-PLUS-SERVER-TLS-GCC-LTO-OZ-SIZE-BENCHMARK','commands':commands,'payload_bytes':len(payload),'mapped_bytes':mapped,'payload_sha256':hashlib.sha256(payload).hexdigest(),'file_cap_pass':len(payload)<=262144,'mapped_cap_pass':mapped<=4194304,'physical':False,'native_admission':False,'compiler_profile_changes':['GCC -Oz/-flto benchmark, not original physical source-model/compiler proof'],'TLS_attached_or_executed':False};(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ('payload_bytes','mapped_bytes','file_cap_pass','mapped_cap_pass')}))
