"""Read-only frozen64 source composition with new unused TLS roots; no admission."""
from pathlib import Path
import sys,os,platform,importlib.util,json,hashlib,subprocess,struct
assert platform.system()=='Linux'
root=Path(__file__).resolve().parent;repo=Path(sys.argv[1]).resolve();profile=repo/'experiments/native-wifi-qca9377-filter64-native-v1';checked=profile/'runs/checked-candidate';variant=sys.argv[2] if len(sys.argv)>2 else 'both-Os';assert variant in ('both-Os','both-Oz','server-Oz','client-Oz');objects=root/'runs'/('coff' if variant=='both-Os' else 'coff-'+variant);out=root/'runs'/('combined' if variant=='both-Os' else 'combined-'+variant);out.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('_tls_measure_frozen64',profile/'filter64_build.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b);a=b.checked.prior.actors
r=json.loads((checked/'report.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(checked/'report.json')=='37bde7009088c6a783940f642b3dfddbbe2fdeabea671fa17d7f498234f45866'
for n,h in r['generated_compiler_sources_sha256'].items():assert sha(checked/n)==h,n
sources=[checked/'driver.c',checked/'city_core.c',checked/'pci_collect.c',checked/'pci_identity.c',*[checked/n for n in b.FILES],checked/'usb_port.c',checked/'bt_event_stream.c',checked/'ble_recovery_link.c',checked/'diagnostic_gatt.c',a.LINK/'file_core.c',a.NATIVE/'sha256.c',checked/'monocypher.c',checked/'monocypher-ed25519.c']
commands=[];original=subprocess.run
def capture(cmd,*args,**kwargs):
 if isinstance(cmd,list) and cmd and 'mingw32-gcc' in str(cmd[0]):
  cmd=[*cmd[:-2],'-I'+str(checked),*[str(p) for p in objects.glob('*.obj')],*[ '-Wl,--undefined='+n for n in ('tls_ble_open','tls_ble_feed','tls_ble_drain','tls_ble_poll','tls_ble_read','tls_ble_write','tls_ble_close','tls_heap_bind','tls_heap_release','mbedtls_platform_set_calloc_free','psa_crypto_init','mbedtls_psa_crypto_free')],*cmd[-2:]]
 commands.append(list(map(str,cmd)));return original(cmd,*args,**kwargs)
subprocess.run=capture
try:payload=a.compile_efi(out,'native64-plus-TLS-measure',sources,driver=True,definitions=('SCENE_REVISION=1','QCA_CONFIG_SETUP=1','QCA_FC_BASE=13'))
finally:subprocess.run=original
for n,h in r['generated_compiler_sources_sha256'].items():assert sha(checked/n)==h,n
pe=struct.unpack_from('<I',payload,60)[0];mapped=struct.unpack_from('<I',payload,pe+80)[0]
report={'status':'ACTUAL-FROZEN64-PLUS-TLS-UNUSED-ROOTS-SIZE-ASSESSMENT','commands':commands,'frozen64_report_sha256':sha(checked/'report.json'),'frozen_generated_sources_sha256':r['generated_compiler_sources_sha256'],'payload_bytes':len(payload),'mapped_bytes':mapped,'payload_sha256':hashlib.sha256(payload).hexdigest(),'file_cap_pass':len(payload)<=262144,'mapped_cap_pass':mapped<=4194304,'physical':False,'native_admission':False,'TLS_attached_or_executed':False}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('Combined actual file/mapped',len(payload),mapped,'caps',report['file_cap_pass'],report['mapped_cap_pass'])
