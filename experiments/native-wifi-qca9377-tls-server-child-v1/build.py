from pathlib import Path
import subprocess,platform,json,hashlib,os,sys
assert platform.system()=='Linux','Native only Yukabox'
r=Path(__file__).resolve().parent;v=r/'vendor';o=r/'runs/checked';o.mkdir(parents=True,exist_ok=True);cc=sys.argv[1];log=[];env=dict(os.environ,TMPDIR=str(o))
def run(cmd):
 p=subprocess.run(cmd,text=True,capture_output=True,env=env);log.extend([json.dumps(cmd),p.stdout,p.stderr]);(o/'full.log').write_text('\n'.join(log));assert p.returncode==0,p.stderr;return p.stdout
src=[*sorted((v/'library').glob('*.c')),r/'tls_engine.c',r/'tls_heap.c',r/'child.c'];inc=['-I'+str(r),'-I'+str(v/'include'),'-DMBEDTLS_CONFIG_FILE="tls_config.h"'];objs=[]
for p in [*src,v/'tests/src/certs.c',r/'test_child.c']:
 obj=o/(p.stem+'.o');run([cc,'-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all',*inc,'-I'+str(v/'library'),'-I'+str(v/'tests/include'),'-c',str(p),'-o',str(obj)]);objs.append(obj)
run([cc,'-fsanitize=address,undefined',*[str(p) for p in objs],'-o',str(o/'test')]);result=run([str(o/'test')]);print(result)
run([cc,'-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all',*inc,'-I'+str(v/'tests/include'),'-c',str(r/'test_tls.c'),'-o',str(o/'test_tls.o')])
run([cc,'-fsanitize=address,undefined',*[str(p) for p in objs if p.name not in ('child.o','test_child.o')],str(o/'test_tls.o'),'-o',str(o/'test_original')]);original_result=run([str(o/'test_original')]);print(original_result)
config=(r/'tls_config.h').read_text().replace('#define MBEDTLS_SSL_CLI_C\n','');(o/'server_config.h').write_text(config);coff=[]
for p in [*src,r/'memory_bridge.c']:
 obj=o/(p.stem+'.obj');run([cc,'-target','x86_64-pc-win32-coff','-U_WIN32','-U_WIN64','-U_MSC_VER','-ffreestanding','-fno-stack-protector','-mno-red-zone','-ffunction-sections','-fdata-sections','-Oz','-I'+str(r/'freestanding'),'-I'+str(r),'-I'+str(v/'include'),'-DMBEDTLS_CONFIG_FILE="'+str(o/'server_config.h')+'"','-c',str(p),'-o',str(obj)]);coff.append(obj)
lld=Path(cc).parent/'lld';run([str(lld),'-flavor','link','/nodefaultlib','/subsystem:efi_boot_service_driver','/entry:tls_child_entry','/opt:ref','/machine:x64','/out:'+str(o/'tls-child.efi'),*[str(p) for p in coff]])
pe=(o/'tls-child.efi').read_bytes();off=int.from_bytes(pe[60:64],'little');mapped=int.from_bytes(pe[off+24+56:off+24+60],'little');assert len(pe)<=262144 and mapped+2224128<=4194304
report={'status':'TLS13-GENUINE-SERVER-PRIVATE-UEFI-REGISTRATION-ASAN-COFF-PASS','physical_admission':False,'synthetic_firmware':True,'synthetic_entropy_only':True,'result':result,'original_result':original_result,'coff_units':len(coff),'payload_bytes':len(pe),'mapped_bytes':mapped,'payload_sha256':hashlib.sha256(pe).hexdigest(),'parent_projection_mapped':2224128,'aggregate_projection':mapped+2224128,'parent_exact_admission_not_claimed':True,'source_sha256':{str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest() for p in r.rglob('*') if p.is_file() and 'runs' not in p.parts and 'evidence' not in p.parts},'artifacts':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in o.iterdir() if p.is_file() and p.name!='report.json'}}
(o/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('actual PE file/mapped/aggregate',len(pe),mapped,mapped+2224128)
