from pathlib import Path
import sys,subprocess,os,json,hashlib
assert sys.platform.startswith('linux')
r=Path(__file__).resolve().parent;c=r/'runs/checked-candidate';o=r/'runs/host-model';o.mkdir(parents=True,exist_ok=True);cc=sys.argv[1];logs=[]
def run(cmd):
 p=subprocess.run(cmd,text=True,capture_output=True,cwd=o,env=dict(os.environ,TMPDIR=str(o)));logs.extend([json.dumps(cmd),p.stdout,p.stderr]);(o/'full.log').write_text('\n'.join(logs));assert not p.returncode,p.stderr;return p.stdout
run([cc,'-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all','-I'+str(r),'-I'+str(c),*[str(r/f) for f in ('test_probe65.c','inventory.c','platform.c','rng_port.c')],'-Wl,--wrap=inv_cpuid_native','-o',str(o/'test')]);result=run([str(o/'test')]);print(result)
ref=Path('/home/yuka/rabbit-world/parallel-filter64-native-v1/source');link=ref/'experiments/uefi-bluetooth-file-transfer-v1/file_core.c'
# Exact file core path is obtained from the retained builder, not a success stub.
import importlib.util
spec=importlib.util.spec_from_file_location('i65_builder',r/'native_build.py');builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder);link=builder.b.checked.prior.actors.LINK/'file_core.c';sha_source=builder.b.checked.prior.actors.NATIVE/'sha256.c'
run([cc,'-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all','-I'+str(c),'-I'+str(link.parent),'-I'+str(sha_source.parent),str(r/'test_gatt65.c'),str(c/'diagnostic_gatt.c'),str(link),str(sha_source),'-o',str(o/'gatt-test')]);gatt_result=run([str(o/'gatt-test'),str(o/'fixture-0.bin')]);print(gatt_result)
for f in ('probe65.c','inventory.c','platform.c','rng_port.c','city_arena.c'):run([cc,'-target','x86_64-pc-win32-coff','-Oz','-ffreestanding','-fno-stack-protector','-mno-red-zone','-I'+str(r),'-I'+str(c),'-c',str(r/f),'-o',str(o/(Path(f).stem+'.obj'))])
report={'status':'INVENTORY65-ACTUAL-PROBE-GETINFO-OWNERSHIP-ASAN-COFF-PASS','physical_admission':False,'real_host_cpuid_calls':0,'GetRNG_RDSEED_MSR_calls':0,'result':result,'actual_gatt_result':gatt_result,'coff_units':5,'source_sha256':{str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest() for p in r.rglob('*') if p.is_file() and not set(p.parts)&{'runs','evidence','__pycache__'}},'generated_headers_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (c/'inventory65_hashes.h',c/'pci_collect.h')},'artifacts_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in o.iterdir() if p.is_file() and p.name!='report.json'}};(o/'report.json').write_text(json.dumps(report,indent=2)+'\n')
