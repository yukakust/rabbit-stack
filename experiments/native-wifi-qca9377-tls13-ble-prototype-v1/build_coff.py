"""Genuine freestanding library units, not success/crypto stubs. Yukabox only."""
from pathlib import Path
import sys,platform,subprocess,os,json
assert platform.system()=='Linux'
root=Path(__file__).resolve().parent;v=root/'source/mbedtls-3.6.7';variant=sys.argv[2] if len(sys.argv)>2 else 'both-Os';assert variant in ('both-Os','both-Oz','server-Oz','client-Oz');out=root/'runs'/('coff' if variant=='both-Os' else 'coff-'+variant);out.mkdir(parents=True,exist_ok=True);log=[]
config=(root/'tls_config.h').read_text()
if variant.startswith('server'):config=config.replace('#define MBEDTLS_SSL_CLI_C\n','')
if variant.startswith('client'):config=config.replace('#define MBEDTLS_SSL_SRV_C\n','')
(out/'tls_config.h').write_text(config)
for p in [*(v/'library').glob('*.c'),root/'tls_engine.c',root/'tls_heap.c']:
 cmd=[sys.argv[1],'-target','x86_64-pc-win32-coff','-U_WIN32','-U_WIN64','-U_MSC_VER','-ffreestanding','-fno-stack-protector','-mno-red-zone','-ffunction-sections','-fdata-sections','-Oz' if variant.endswith('Oz') else '-Os','-I'+str(root/'freestanding'),'-I'+str(root),'-I'+str(v/'include'),'-DMBEDTLS_CONFIG_FILE="'+str(out/'tls_config.h')+'"','-c',str(p),'-o',str(out/(p.stem+'.obj'))]
 r=subprocess.run(cmd,text=True,capture_output=True,env=dict(os.environ,TMPDIR=str(out)));log.extend([json.dumps(cmd),r.stdout,r.stderr]);
 if r.returncode:(out/'compile.log').write_text('\n'.join(log));raise RuntimeError(r.stderr)
(out/'compile.log').write_text('\n'.join(log));print('All genuine COFF units compiled',len(list(out.glob('*.obj'))))
