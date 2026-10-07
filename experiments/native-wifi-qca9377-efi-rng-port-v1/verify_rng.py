#!/usr/bin/env python3
"""Pinned EDK2 ABI oracle; all native builds and fake providers on Yukabox."""
import argparse,hashlib,json,pathlib,re,subprocess
EDK='fbe0805b2091393406952e84724188f8c1941837'
PINS={'RngProtocol.h':'a803ea796a9ea8579a81b05b55abef30f4f36bd775df07c85c39b32fd70fb5b5',
 'RngGuid.h':'dce2cc8aba4a04a8388f6d163fac6f1eb667e46ad94ffe80517ae66fb540a755',
 'UefiSpec.h':'411733fc1da5e084971f6a70c59b3699adee73a060fc5e7067eee3d2fb850db9'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--reference',type=pathlib.Path,required=True);p.add_argument('--clang',required=True);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args()
 root=pathlib.Path(__file__).resolve().parent;ref=a.reference.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
 for n,h in PINS.items():assert sha(ref/n)==h,n
 (out/'Guid').mkdir(exist_ok=True);(out/'Guid/Rng.h').write_bytes((ref/'RngGuid.h').read_bytes())
 oracle='''#include <stdint.h>
#include <stddef.h>
typedef uint64_t EFI_STATUS;typedef size_t UINTN;typedef uint8_t UINT8;
typedef struct {uint32_t Data1;uint16_t Data2,Data3;uint8_t Data4[8];} EFI_GUID;
#define EFIAPI __attribute__((ms_abi))
#define IN
#define OUT
#define OPTIONAL
'''+(ref/'RngProtocol.h').read_text()
 (out/'oracle-rng.h').write_text(oracle)
 # Exact BootServices member ordering, without pretending an unvalidated
 # arbitrary table pointer is safe to dereference in a live integration.
 text=(ref/'UefiSpec.h').read_text();start=re.search(r'EFI_ALLOCATE_POOL\s+AllocatePool;',text).start();end=re.search(r'EFI_LOCATE_PROTOCOL\s+LocateProtocol;',text).start()
 assert start<end and re.search(r'EFI_FREE_POOL\s+FreePool;',text[start:end])
 finish=text.index('} EFI_BOOT_SERVICES;')+len('} EFI_BOOT_SERVICES;');begin=text.rfind('typedef struct {',0,finish)
 body=text[begin:finish];assert 'EFI_TABLE_HEADER' in body
 aliases=sorted(set(re.findall(r'\b(EFI_[A-Z_0-9]+)\s+[A-Za-z_][A-Za-z_0-9]*;',body))-{'EFI_TABLE_HEADER'})
 boot='typedef struct {uint64_t Signature;uint32_t Revision,HeaderSize,CRC32,Reserved;} EFI_TABLE_HEADER;\n#define VOID void\n'
 boot+=''.join('typedef void (*'+name+')(void);\n' for name in aliases)+body+'\n'
 (out/'oracle-boot.h').write_text(boot)
 inputs={n:sha(root/n) for n in ['rng_port.c','rng_port.h','rng_port_test.c','verify_rng.py']};logs=[]
 def run(cmd):
  r=subprocess.run(cmd,text=True,capture_output=True)
  logs.extend([json.dumps(cmd),r.stdout,r.stderr]);
  if r.returncode:raise RuntimeError(r.stderr)
  return r.stdout
 flags=['-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all','-I'+str(root),'-I'+str(out)]
 run([a.clang,*flags,str(root/'rng_port.c'),str(root/'rng_port_test.c'),'-o',str(out/'test')])
 result=run([str(out/'test')]);assert 'PASS 557 EFI RNG' in result,result
 run([a.clang,'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-I'+str(root),'-c',str(root/'rng_port.c'),'-o',str(out/'rng_port.obj')])
 version=run([a.clang,'--version']);assert inputs=={n:sha(root/n) for n in inputs}
 (out/'host.log').write_text('\n'.join(logs))
 report={'status':'EFI-RNG-PORT-BOUNDED-MOCK-ABI-ASAN-COFF-PASS','checks':557,'source_sha256':inputs,'edk2_commit':EDK,'reference_sha256':PINS,
  'oracle_sha256':sha(out/'oracle-rng.h'),'boot_layout_oracle_sha256':sha(out/'oracle-boot.h'),'log_sha256':sha(out/'host.log'),'compiler':version,
  'max_algorithm_count':16,'max_pool_bytes':256,'max_live_pool_allocations':1,
  'physical_rng_calls':0,'random_samples_exported':0,'private_key_operations':0,'provider_approved':False,
  'entropy_quality_verified':False,'native_integrated':False,'candidate_counter_assigned':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(result.strip())
if __name__=='__main__':main()
