"""Independent genuine role/Oz sizing; no crypto success or native admission."""
from pathlib import Path
import platform,os,subprocess,sys,json,struct
assert platform.system()=='Linux'
root=Path(__file__).resolve().parent;clang=sys.argv[1];lld=sys.argv[2];native=Path(sys.argv[3]);v=root/'source/mbedtls-3.6.7';results=[]
roots=('tls_ble_open','tls_ble_feed','tls_ble_drain','tls_ble_poll','tls_ble_read','tls_ble_write','tls_ble_close','tls_heap_bind','tls_heap_release','mbedtls_platform_set_calloc_free','psa_crypto_init','mbedtls_psa_crypto_free')
for variant in ('both-Oz','server-Oz','client-Oz'):
 out=root/'runs'/('coff-'+variant);log=[];env=dict(os.environ,TMPDIR=str(out),PYTHONDONTWRITEBYTECODE='1');out.mkdir(parents=True,exist_ok=True)
 def run(cmd):
  r=subprocess.run(cmd,cwd=root,text=True,capture_output=True,env=env);log.extend([json.dumps(cmd),r.stdout,r.stderr]);(out/'variant.log').write_text('\n'.join(log));assert r.returncode==0,r.stderr;return r.stdout
 run([sys.executable,str(root/'build_coff.py'),clang,variant])
 for name in ('memory_bridge','link_probe'):
  run([clang,'-target','x86_64-pc-win32-coff','-U_WIN32','-U_WIN64','-U_MSC_VER','-ffreestanding','-fno-stack-protector','-mno-red-zone','-ffunction-sections','-fdata-sections','-Oz','-I'+str(root/'freestanding'),'-I'+str(root),'-I'+str(v/'include'),'-DMBEDTLS_CONFIG_FILE="'+str(out/'tls_config.h')+'"','-c',str(root/(name+'.c')),'-o',str(out/(name+'.obj'))])
 image=out/'tls-link-only.efi';run([lld,'-flavor','link','/subsystem:efi_application','/entry:tls_link_entry','/nodefaultlib','/opt:ref',*['/include:'+n for n in roots],'/out:'+str(image),*[str(p) for p in out.glob('*.obj')]])
 blob=image.read_bytes();pe=struct.unpack_from('<I',blob,60)[0];mapped=struct.unpack_from('<I',blob,pe+80)[0]
 run([sys.executable,str(root/'measure_combined.py'),str(native),variant]);combo=json.loads((root/'runs'/('combined-'+variant)/'report.json').read_text());result={'variant':variant,'standalone_file':len(blob),'standalone_mapped':mapped,'combined_file':combo['payload_bytes'],'combined_mapped':combo['mapped_bytes'],'both_caps':combo['file_cap_pass'] and combo['mapped_cap_pass']};results.append(result);print(json.dumps(result),flush=True)
(root/'runs/variants.json').write_text(json.dumps(results,indent=2)+'\n')
