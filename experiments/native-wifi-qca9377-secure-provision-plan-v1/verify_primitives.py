#!/usr/bin/env python3
"""Yukabox only: pinned mature primitives, public dummy inputs, no provision IO."""
import argparse,hashlib,hmac,json,pathlib,subprocess
PINS={'monocypher.c':'f1f838cdd483bdebe0df0ff5c5ed60535e496f769c6a2f933ac4c0b114207123',
 'monocypher.h':'fcaf6ed771358bb4f40fba016f6518ae86ec02b1b877d2cc35ad92d3a26fd7b3',
 'monocypher-ed25519.c':'ce0d2f8e32ca8f66398ba5b3456cc74327c3eff14e7b950ce7d57be9025cc453',
 'monocypher-ed25519.h':'3a3035181f991a158d0e1c7567258f0bae8ba0f1f23c5512b4a1db1b3c9730ce'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--reference',type=pathlib.Path,required=True);p.add_argument('--clang',required=True);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args()
 root=pathlib.Path(__file__).resolve().parent;out=a.output.resolve();out.mkdir(parents=True,exist_ok=True);ref=a.reference.resolve()
 for n,h in PINS.items():assert sha(ref/n)==h,n
 prk=hmac.new(bytes(range(16)),bytes(range(1,33)),hashlib.sha512).digest()
 expected=hmac.new(prk,bytes(range(3,163))+b'\x01',hashlib.sha512).digest()
 (out/'hkdf-oracle.h').write_text('static const uint8_t hkdf_expected[64]={'+','.join(map(str,expected))+'};\n')
 inputs={n:sha(root/n) for n in ['primitive_test.c','verify_primitives.py']};logs=[]
 def run(cmd):
  r=subprocess.run(cmd,text=True,capture_output=True,check=True);logs.extend([json.dumps(cmd),r.stdout,r.stderr]);return r.stdout
 run([a.clang,'-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-sanitize-recover=all','-I'+str(ref),'-I'+str(out),str(root/'primitive_test.c'),str(ref/'monocypher.c'),str(ref/'monocypher-ed25519.c'),'-o',str(out/'test')])
 result=run([str(out/'test')]);assert 'PASS 38476 Monocypher dummy' in result,result
 run([a.clang,'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-I'+str(ref),'-c',str(ref/'monocypher.c'),'-o',str(out/'monocypher.obj')])
 run([a.clang,'-target','x86_64-pc-win32-coff','-ffreestanding','-fno-stack-protector','-mno-red-zone','-Os','-Wall','-Wextra','-Werror','-I'+str(ref),'-c',str(ref/'monocypher-ed25519.c'),'-o',str(out/'monocypher-ed25519.obj')])
 assert inputs=={n:sha(root/n) for n in inputs}
 version=run([a.clang,'--version']);(out/'host.log').write_text('\n'.join(logs))
 report={'status':'MONOCYPHER-DUMMY-BINDING-PRIMITIVES-ASAN-COFF-PASS','checks':38476,'source_sha256':inputs,
  'monocypher_version':'4.0.3','monocypher_commit':'ab2b16dd619ad5f6979a4fbe69cfa324a6fcc35f','reference_sha256':PINS,
  'log_sha256':sha(out/'host.log'),'compiler':version,'synthetic_only':True,'real_secret_reads':0,'signatures_created':0,
  'hkdf_sha512_independent_stdlib_oracle':True,'hardware_operations':0,'protocol_implemented':False,'device_authenticated':False,'secure_rng_verified':False,'wifi_provisioned':False}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(result.strip())
if __name__=='__main__':main()
